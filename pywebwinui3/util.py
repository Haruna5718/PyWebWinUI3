import ctypes
import logging
import threading
import winreg
import xml.etree.ElementTree
from functools import lru_cache
from typing import Any, Callable
import re
from ctypes import wintypes

from .event import PathEvent, Event

logger = logging.getLogger('pywebwinui3.util')

ACCENT_REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent"
REG_NOTIFY_CHANGE_LAST_SET = 0x00000004
WAIT_OBJECT_0 = 0x00000000
WAIT_FAILED = 0xFFFFFFFF
INFINITE = 0xFFFFFFFF

_advapi32 = ctypes.WinDLL("Advapi32", use_last_error=True)
_kernel32 = ctypes.WinDLL("Kernel32", use_last_error=True)

_advapi32.RegNotifyChangeKeyValue.argtypes = [
	wintypes.HKEY,
	wintypes.BOOL,
	wintypes.DWORD,
	wintypes.HANDLE,
	wintypes.BOOL,
]
_advapi32.RegNotifyChangeKeyValue.restype = wintypes.LONG

_kernel32.CreateEventW.argtypes = [
	wintypes.LPVOID,
	wintypes.BOOL,
	wintypes.BOOL,
	wintypes.LPCWSTR,
]
_kernel32.CreateEventW.restype = wintypes.HANDLE

_kernel32.SetEvent.argtypes = [wintypes.HANDLE]
_kernel32.SetEvent.restype = wintypes.BOOL

_kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
_kernel32.CloseHandle.restype = wintypes.BOOL

_kernel32.WaitForMultipleObjects.argtypes = [
	wintypes.DWORD,
	ctypes.POINTER(wintypes.HANDLE),
	wintypes.BOOL,
	wintypes.DWORD,
]
_kernel32.WaitForMultipleObjects.restype = wintypes.DWORD

DEFAULT_ACCENT_PALETTE = [
	"#99ebff",
	"#00ccff",
	"#0099ff",
	"#0078d4",
	"#005fb8",
	"#004a92",
	"#003966",
	"#00264a",
]

def xamlToJson(element: xml.etree.ElementTree.Element):
	return {
		"tag":element.tag,
		"attr":element.attrib,
		"text":(element.text or "").strip(),
		"child":[xamlToJson(e) for e in element]
	}

def loadPage(filePath: str):
	return xamlToJson(xml.etree.ElementTree.parse(filePath).getroot())

class SyncDict(dict):
	def __init__(self, init:dict=None, event:PathEvent=None, sync:Callable=None):
		super().__init__(init or {})
		self.event = event or PathEvent()
		self.sync = sync

	@staticmethod
	@lru_cache(maxsize=512)
	def _parsePath(key:str):
		if not isinstance(key, str) or "[" not in key:
			return None
		start = key.find("[")
		root = key[:start]
		if not root:
			return None
		tokens = [root]
		index = start
		while index < len(key):
			if key[index] != "[":
				return None
			end = key.find("]", index + 1)
			if end == -1:
				return None
			raw = key[index + 1:end].strip()
			if not raw:
				return None
			if re.fullmatch(r"\d+", raw):
				tokens.append(int(raw))
			elif len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "'\"":
				tokens.append(raw[1:-1])
			else:
				tokens.append(raw)
			index = end + 1
		return tokens

	@staticmethod
	def _cloneContainer(value, nextToken):
		if isinstance(value, list):
			return list(value)
		if isinstance(value, dict):
			return dict(value)
		return [] if isinstance(nextToken, int) else {}

	def _getPathValue(self, key:str, default=None):
		tokens = self._parsePath(key)
		if not tokens:
			return self.get(key, default)
		current = self
		try:
			for token in tokens:
				current = current[token]
			return current
		except (KeyError, IndexError, TypeError):
			return default

	def _setPathValue(self, key:str, value:Any):
		tokens = self._parsePath(key)
		if not tokens:
			return False

		root, *segments = tokens
		if not segments:
			super().__setitem__(root, value)
			return True

		source = super().get(root)
		cloned = self._cloneContainer(source, segments[0])
		cursor = cloned
		sourceCursor = source

		for index, token in enumerate(segments[:-1]):
			nextToken = segments[index + 1]
			if isinstance(sourceCursor, list) and isinstance(token, int) and 0 <= token < len(sourceCursor):
				sourceValue = sourceCursor[token]
			elif isinstance(sourceCursor, dict):
				sourceValue = sourceCursor.get(token)
			else:
				sourceValue = None

			child = self._cloneContainer(sourceValue, nextToken)
			if isinstance(cursor, list) and isinstance(token, int):
				while len(cursor) <= token:
					cursor.append(None)
				cursor[token] = child
			else:
				cursor[token] = child
			cursor = child
			sourceCursor = sourceValue

		lastToken = segments[-1]
		if isinstance(cursor, list) and isinstance(lastToken, int):
			while len(cursor) <= lastToken:
				cursor.append(None)
			cursor[lastToken] = value
		else:
			cursor[lastToken] = value

		super().__setitem__(root, cloned)
		return True

	def _sync(self, key, before, after, sync):
		if sync and self.sync:
			self.sync(key, after)
		self.event.set(key, before, after)

	def __setitem__(self, key:str, value:Any, sync=True):
		before = self._getPathValue(key, None)
		if not self._setPathValue(key, value):
			super().__setitem__(key, value)
		self._sync(key, before, value, sync)
		return value

	def set(self, key:str, value:Any, sync=True):
		return self.__setitem__(key, value, sync)
	
	def append(self, key:str, value:Any, sync=True):
		before = list(self.get(key,[]))
		self.setdefault(key,[]).append(value)
		self._sync(key, before, self.get(key), sync)
		return self[key]
	
	def remove(self, key:str, value:Any, sync=True):
		before = list(self.get(key,[]))
		self.setdefault(key,[]).remove(value)
		self._sync(key, before, self.get(key), sync)
		return self[key]
		
class AccentColorWatcher:
	def __init__(self, event:Event=None):
		self.event = event or Event()
		self.palette = self.getSystemAccentColor()
		self._watch_thread: threading.Thread | None = None
		self._stop_event_handle: int | None = None

	@staticmethod
	def getSystemAccentColor():
		try:
			with winreg.OpenKey(winreg.HKEY_CURRENT_USER, ACCENT_REGISTRY_PATH) as key:
				p, _ = winreg.QueryValueEx(key, "AccentPalette")
		except OSError:
			return DEFAULT_ACCENT_PALETTE.copy()
		return [f"#{p[i]:02x}{p[i+1]:02x}{p[i+2]:02x}" for i in range(0,len(p),4)]

	@staticmethod
	def _create_event_handle():
		handle = _kernel32.CreateEventW(None, False, False, None)
		if not handle:
			raise ctypes.WinError(ctypes.get_last_error())
		return int(handle)

	@staticmethod
	def _close_handle(handle: int | None):
		if handle:
			_kernel32.CloseHandle(handle)

	def _watch_loop(self, stop_event_handle: int):
		change_event_handle = None
		try:
			with winreg.OpenKey(
				winreg.HKEY_CURRENT_USER,
				ACCENT_REGISTRY_PATH,
				0,
				winreg.KEY_READ | winreg.KEY_NOTIFY,
			) as key:
				change_event_handle = self._create_event_handle()
				wait_handles = (wintypes.HANDLE * 2)(change_event_handle, stop_event_handle)
				key_handle = wintypes.HKEY(int(key.handle))
				while True:
					result = _advapi32.RegNotifyChangeKeyValue(
						key_handle,
						False,
						REG_NOTIFY_CHANGE_LAST_SET,
						wintypes.HANDLE(change_event_handle),
						True,
					)
					if result != 0:
						logger.debug("Accent watcher registry notification failed: %s", result)
						break

					wait_result = _kernel32.WaitForMultipleObjects(2, wait_handles, False, INFINITE)
					if wait_result == WAIT_OBJECT_0:
						self.refresh()
						continue
					if wait_result == WAIT_OBJECT_0 + 1:
						break

					logger.debug("Accent watcher wait failed: %s", wait_result)
					break
		except Exception:
			logger.debug("Accent watcher stopped unexpectedly", exc_info=True)
		finally:
			self._close_handle(change_event_handle)
			self._close_handle(stop_event_handle)
			if self._stop_event_handle == stop_event_handle:
				self._stop_event_handle = None
			self._watch_thread = None

	def refresh(self):
		if self.palette != (color := self.getSystemAccentColor()):
			self.palette = color
			self.event.set(self.palette)

	def start(self):
		self.refresh()
		if self._watch_thread and self._watch_thread.is_alive():
			return

		try:
			self._stop_event_handle = self._create_event_handle()
		except Exception:
			logger.debug("Failed to start accent watcher", exc_info=True)
			return

		self._watch_thread = threading.Thread(
			target=self._watch_loop,
			args=(self._stop_event_handle,),
			daemon=True,
			name="AccentColorWatcher",
		)
		self._watch_thread.start()
		logger.debug("Accent watcher initialized")

	def stop(self):
		if self._stop_event_handle:
			_kernel32.SetEvent(wintypes.HANDLE(self._stop_event_handle))

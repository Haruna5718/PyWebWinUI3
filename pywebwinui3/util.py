import xml.etree.ElementTree
from typing import Any, Callable
import winreg
import logging
import re

from .event import PathEvent, Event

logger = logging.getLogger('pywebwinui3.util')

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
		self.theme_event = Event()
		self.palette = self.getSystemAccentColor()
		self.theme = self.getSystemTheme()

	@staticmethod
	def getSystemAccentColor():
		try:
			with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent") as key:
				p, _ = winreg.QueryValueEx(key, "AccentPalette")
		except OSError:
			return DEFAULT_ACCENT_PALETTE.copy()
		return [f"#{p[i]:02x}{p[i+1]:02x}{p[i+2]:02x}" for i in range(0,len(p),4)]

	@staticmethod
	def getSystemTheme():
		try:
			with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
				t, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
		except OSError:
			return "dark"
		return "light" if t else "dark"

	def refresh(self):
		if self.palette != (color := self.getSystemAccentColor()):
			self.palette = color
			self.event.set(self.palette)
		if self.theme != (theme := self.getSystemTheme()):
			self.theme = theme
			self.theme_event.set(self.theme)

	def start(self):
		self.refresh()
		logger.debug("Accent watcher initialized")

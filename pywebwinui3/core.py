from __future__ import annotations

import importlib
import json
import logging
import sys
import threading
from pathlib import Path

import webview
from hPyT import title_bar

from .event import Event, PathEvent
from .type import Status
from .util import AccentColorWatcher, SyncDict, loadPage

logger = logging.getLogger("pywebwinui3")
core_logger = logging.getLogger("pywebwinui3.core")

DEFAULT_WINDOW_WIDTH = 900
DEFAULT_WINDOW_HEIGHT = 600
DEFAULT_WINDOW_MIN_WIDTH = 100
DEFAULT_WINDOW_MIN_HEIGHT = 100


class _JsApi:
	def _init(self, main:MainWindow):
		self.init = main._init_payload
		self.frontendReady = main._frontend_ready_callback
		self.syncValue = main.syncValue
		self.syncValues = main._sync_values
		self.pin = main.pin
		self.minimize = main.minimize
		self.destroy = main.destroy
		self.resolveResource = main.resolveResource


class WindowEvents:
	def __init__(self) -> None:
		self.windowReady = Event()
		self.closed = Event()
		self.accentColorChange = Event()
		self.valueChange = PathEvent()


class MainWindow:
	def __init__(self, title: str, icon: str | None = None):
		self.rootPath = Path(sys._getframe(1).f_code.co_filename).parent.resolve()
		self.packagePath = Path(__file__).parent.resolve() / "web"

		self.accent = AccentColorWatcher()
		self.events = WindowEvents()
		self.api = _JsApi()
		self._title = title
		self._frontend_ready = False
		self._setup_fired = False
		self._minimum_width = DEFAULT_WINDOW_MIN_WIDTH
		self._minimum_height = DEFAULT_WINDOW_MIN_HEIGHT
		self._sync_lock = threading.Lock()
		self._pending_sync: dict[str, object] = {}

		self.values = SyncDict(
			{
				"system_title": title,
				"system_icon": icon,
				"system_theme": "system",
				"system_accent": self.accent.palette,
				"system_pages": None,
				"system_settings": None,
				"system_nofication": [],
				"system_pin": False,
			}
		)
		self.values.sync = self.queue_sync_value

		self._window = webview.create_window(
			self._current_title(),
			self._entry_path().as_uri(),
			js_api=self.api,
			background_color="#202020",
			text_select=True,
			width=DEFAULT_WINDOW_WIDTH,
			height=DEFAULT_WINDOW_HEIGHT,
			min_size=(self._minimum_width, self._minimum_height),
			on_top=bool(self.values.get("system_pin", False)),
		)
		self.show = self._window.show
		self.restore = self._window.restore
		self.hide = self._window.hide
		self.destroy = self._window.destroy
		self.minimize = self._window.minimize
		self.api._init(self)
		self._window.events.before_show += self._before_show
		self._window.events.closed += self._on_closed

		core_logger.debug("Window created")

		self.events.accentColorChange = self.accent.event
		self.events.valueChange = self.values.event
		self.events.accentColorChange += lambda palette: self.values.set("system_accent", palette)

	def _event_decorator(self, event: Event | PathEvent, value=None):
		def decorator(func):
			if value is None:
				event.__iadd__(func)
			else:
				event.__iadd__((value, func))
			return func

		return decorator

	def onValueChange(self, key):
		return self._event_decorator(self.events.valueChange, key)

	def onAccentColorChange(self):
		return self._event_decorator(self.events.accentColorChange)

	def onSetup(self):
		return self._event_decorator(self.events.windowReady)

	def onExit(self):
		return self._event_decorator(self.events.closed)

	def notice(self, level: Status, title: str, description: str, item: dict | None = None):
		self.values["system_nofication"] = [
			*(self.values["system_nofication"] or []),
			[level, title, description, item],
		]

	def pin(self, state: bool):
		state = bool(state)
		self.values.set("system_pin", state)
		self.set_on_top(state)
		return state

	def syncValue(self, key, value):
		return self.values.set(key, value, False)

	def addSettings(self, pageFile: str | Path | None = None, pageData: dict | None = None):
		if pageFile and not pageData:
			pageData = loadPage(pageFile)
		logger.debug("Setting page: %s", pageData["attr"]["path"])
		self.values["system_settings"] = pageData

	def addPage(self, pageFile: str | Path | None = None, pageData: dict | None = None):
		if pageFile and not pageData:
			pageData = loadPage(pageFile)
		logger.debug("Page added: %s", pageData["attr"]["path"])
		self.values["system_pages"] = {
			**(self.values["system_pages"] or {}),
			pageData["attr"]["path"]: pageData,
		}

	def resolve_path(self, value: str | Path | None) -> Path | None:
		if value is None:
			return None

		path = Path(value)
		if path.is_absolute():
			return path

		root_candidate = self.rootPath / path
		if root_candidate.exists():
			return root_candidate.resolve()

		package_candidate = self.packagePath / path
		if package_candidate.exists():
			return package_candidate.resolve()

		return root_candidate.resolve()

	def _current_title(self):
		return self.values.get("system_title", self._title)

	def _entry_path(self) -> Path:
		entry = (Path(self.packagePath) / "index.html").resolve()
		if not entry.is_file():
			raise FileNotFoundError(f"Frontend entry not found: {entry}")
		return entry

	def _before_show(self):
		try:
			hwnd = self._window.native.Handle.ToInt64()
			title_bar.hide(hwnd)
		except Exception:
			core_logger.debug("Failed to hide title bar", exc_info=True)

	def _on_closed(self):
		self.events.closed.set()

	def _dispatch_or_defer_sync(self, key: str, value):
		with self._sync_lock:
			if not self._frontend_ready:
				self._pending_sync[key] = value
				return

		self._dispatch_sync_value(key, value)

	def _dispatch_sync_value(self, key: str, value):
		if key == "system_title":
			try:
				self._window.title = str(value or self._title)
			except Exception:
				core_logger.debug("Failed to update window title", exc_info=True)

		script = f"window.syncValue({json.dumps(key, ensure_ascii=False)}, {json.dumps(value, ensure_ascii=False)}, false)"
		try:
			self._window.evaluate_js(script)
		except Exception:
			with self._sync_lock:
				self._pending_sync[key] = value
			core_logger.debug("Failed to sync value %s", key, exc_info=True)

	def queue_sync_value(self, key: str, value):
		self._dispatch_or_defer_sync(key, value)

	def _init_payload(self):
		return dict(self.values)

	def _sync_values(self, values: dict[str, object]):
		if not isinstance(values, dict):
			return

		for key, value in values.items():
			self.syncValue(key, value)

	def _frontend_ready_callback(self):
		if self._frontend_ready:
			return

		self._frontend_ready = True

		with self._sync_lock:
			pending_sync = tuple(self._pending_sync.items())
			self._pending_sync.clear()

		for key, value in pending_sync:
			self._dispatch_sync_value(key, value)

		if not self._setup_fired:
			self._setup_fired = True
			self.events.windowReady.set()

	def set_on_top(self, state: bool):
		state = bool(state)
		try:
			native = getattr(self._window, "native", None)
			if native is None:
				self._window.on_top = state
				return

			action_type = getattr(importlib.import_module("System"), "Action")

			def _apply():
				self._window.on_top = state

			if native.InvokeRequired:
				native.BeginInvoke(action_type(_apply))
			else:
				_apply()
		except Exception:
			core_logger.debug("Failed to set window on top", exc_info=True)

	def get_window_size(self) -> tuple[int, int]:
		width = int(getattr(self._window, "initial_width", DEFAULT_WINDOW_WIDTH))
		height = int(getattr(self._window, "initial_height", DEFAULT_WINDOW_HEIGHT))

		try:
			if self._window.events.shown.is_set():
				width = int(self._window.width)
				height = int(self._window.height)
		except Exception:
			core_logger.debug("Failed to read window size", exc_info=True)

		return width, height

	def resolveResource(self, value: str):
		if not isinstance(value, (str, Path)):
			return ""

		raw_value = str(value).strip()
		if not raw_value:
			return ""

		lowered = raw_value.lower()
		if lowered.startswith(("http://", "https://", "file://", "data:", "about:")):
			return raw_value

		resolved = self.resolve_path(raw_value)
		if resolved is None or not resolved.exists() or not resolved.is_file():
			return raw_value

		return resolved.resolve().as_uri()

	def start(
		self,
		debug: bool = False,
		*,
		hidden: bool = False,
		on_top: bool | None = None,
		width: int | None = None,
		height: int | None = None,
		min_width=900,
		min_height=600,
	):
		self.accent.start()
		self._minimum_width = max(1, int(min_width))
		self._minimum_height = max(1, int(min_height))
		self._window.min_size = (self._minimum_width, self._minimum_height)
		self._window.hidden = bool(hidden)

		if width is not None and height is not None:
			width = max(self._minimum_width, int(width))
			height = max(self._minimum_height, int(height))
			self._window.initial_width = width
			self._window.initial_height = height

		if on_top is not None:
			self._window.on_top = bool(on_top)

		webview.start(debug=debug, gui="edgechromium")

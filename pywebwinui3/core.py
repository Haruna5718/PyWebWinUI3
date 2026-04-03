from __future__ import annotations

import inspect
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from .event import Event
from .type import Status
from .util import AccentColorWatcher, SyncDict, loadPage

logger = logging.getLogger("pywebwinui3")

from .qt import WebviewAPI

DEFAULT_WINDOW_WIDTH = 900
DEFAULT_WINDOW_HEIGHT = 600
DEFAULT_WINDOW_MIN_WIDTH = 100
DEFAULT_WINDOW_MIN_HEIGHT = 100
ABSOLUTE_WINDOW_MIN_WIDTH = 1
ABSOLUTE_WINDOW_MIN_HEIGHT = 1


class WindowEvents:
	def __init__(self) -> None:
		self.windowReady = Event()
		self.closed = Event()
		self.accentColorChange = Event()
		self.themeChange = Event()
		self.valueChange = Event()


class MainWindow:
	def __init__(self, title: str, icon: str | None = None):
		self.rootPath = Path(inspect.currentframe().f_back.f_code.co_filename).parent.resolve()
		self.packagePath = Path(__file__).parent.resolve() / "web"
		self._title = title
		self._icon = icon

		self.accent = AccentColorWatcher()
		self.events = WindowEvents()
		self.api = WebviewAPI(self, self._title, self._icon)

		self.values = SyncDict(
			{
				"system_title": title,
				"system_icon": icon,
				"system_theme": "system",
				"system_theme_resolved": self.accent.theme,
				"system_accent": self.accent.palette,
				"system_pages": None,
				"system_settings": None,
				"system_nofication": [],
				"system_pin": False,
				"system_window_width": 900,
				"system_window_height": 600,
			}
		)
		self.values.sync = self.api.queue_sync_value

		self.events.accentColorChange = self.accent.event
		self.events.themeChange = self.accent.theme_event
		self.events.valueChange = self.values.event
		self.events.accentColorChange += lambda palette: self.values.set("system_accent", palette)
		self.events.themeChange += lambda theme: self.values.set("system_theme_resolved", theme)

	def onValueChange(self, key):
		def decorator(func):
			self.events.valueChange += (key, func)
			return func

		return decorator

	def onAccentColorChange(self):
		def decorator(func):
			self.events.accentColorChange += func
			return func

		return decorator

	def onThemeChange(self):
		def decorator(func):
			self.events.themeChange += func
			return func

		return decorator

	def onSetup(self):
		def decorator(func):
			self.events.windowReady += func
			return func

		return decorator

	def onExit(self):
		def decorator(func):
			self.events.closed += func
			return func

		return decorator

	def notice(self, level: Status, title: str, description: str, item: dict | None = None):
		self.values["system_nofication"] = [
			*(self.values["system_nofication"] or []),
			[level, title, description, item],
		]

	def init(self) -> dict:
		return dict(self.values)

	def pin(self, state: bool):
		state = bool(state)
		self.values.set("system_pin", state, self.api is not None)
		if self.api is not None:
			self.api.set_on_top(state)
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

	def resolve_resource_url(self, value):
		if not isinstance(value, (str, Path)):
			return value

		raw_value = str(value).strip()
		if not raw_value:
			return value

		lowered = raw_value.lower()
		if lowered.startswith(("http://", "https://", "file://", "data:", "qrc://", "qrc:", "about:")):
			return raw_value

		resolved = self.resolve_path(raw_value)
		if resolved is None or not resolved.exists():
			return raw_value

		return resolved.as_uri()

	def start(self, debug: bool = False, min_width=900, min_height=600):
		# if self.api is not None and getattr(self.api, "_window", None) is not None:
		self.api.set_window_minimum_size(min_width, min_height)
		self.accent.start()
		self.api.start(debug=debug)

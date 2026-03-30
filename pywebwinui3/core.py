from __future__ import annotations

import inspect
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from .event import Event
from .type import Status
from .util import AccentColorWatcher, SyncDict, loadPage

logger = logging.getLogger("pywebwinui3")

if TYPE_CHECKING:
	from .qt import WebviewAPI

DEFAULT_WINDOW_WIDTH = 900
DEFAULT_WINDOW_HEIGHT = 600
DEFAULT_WINDOW_MIN_WIDTH = 100
DEFAULT_WINDOW_MIN_HEIGHT = 100
ABSOLUTE_WINDOW_MIN_WIDTH = 1
ABSOLUTE_WINDOW_MIN_HEIGHT = 1


class WindowEvents:
	def __init__(self) -> None:
		self._pywebviewready = Event()
		self.closed = Event()
		self.accentColorChange = Event()
		self.themeChange = Event()
		self.valueChange = Event()


class MainWindow:
	def __init__(self, title: str, icon: str | None = None):
		caller = inspect.currentframe().f_back
		self.rootPath = Path(caller.f_code.co_filename).parent.resolve()
		self.packagePath = Path(__file__).parent.resolve() / "web"
		self._title = title
		self._icon = icon

		self.accent = AccentColorWatcher()
		self.events = WindowEvents()
		self._api: WebviewAPI | None = None
		self._window_min_width = DEFAULT_WINDOW_MIN_WIDTH
		self._window_min_height = DEFAULT_WINDOW_MIN_HEIGHT

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
				"system_window_width": DEFAULT_WINDOW_WIDTH,
				"system_window_height": DEFAULT_WINDOW_HEIGHT,
			}
		)
		self.values.sync = self._queue_sync_value

		self.events.accentColorChange = self.accent.event
		self.events.themeChange = self.accent.theme_event
		self.events.valueChange = self.values.event
		self.events.accentColorChange += lambda palette: self.values.set("system_accent", palette)
		self.events.themeChange += lambda theme: self.values.set("system_theme_resolved", theme)

	@staticmethod
	def _normalize_notice_level(level) -> int:
		try:
			return int(level)
		except (TypeError, ValueError):
			name = str(getattr(level, "name", level)).split(".")[-1]
			return int(getattr(Status, name, Status.Critical))

	@classmethod
	def _normalize_notice_entry(cls, entry) -> list:
		if not isinstance(entry, (list, tuple)):
			return [int(Status.Critical), "", str(entry or ""), None]

		level, title, description, item, *_ = [*entry, None, None, None, None]
		return [cls._normalize_notice_level(level), title or "", description or "", item]

	@classmethod
	def _normalize_notice_items(cls, items) -> list[list]:
		return [cls._normalize_notice_entry(entry) for entry in items or []]

	@property
	def api(self) -> WebviewAPI:
		if self._api is None:
			from .qt import WebviewAPI

			self._api = WebviewAPI(self, self._title, self._icon)
		return self._api

	def _queue_sync_value(self, key, value):
		if self._api is None:
			return
		self._api.queue_sync_value(key, value)

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
			self.events._pywebviewready += func
			return func

		return decorator

	def onExit(self):
		def decorator(func):
			self.events.closed += func
			return func

		return decorator

	def notice(self, level: Status, title: str, description: str, item: dict | None = None):
		self.values["system_nofication"] = [
			*self._normalize_notice_items(self.values["system_nofication"]),
			self._normalize_notice_entry([level, title, description, item]),
		]

	def init(self) -> dict:
		if self.values.get("system_nofication"):
			self.values.set("system_nofication", self._normalize_notice_items(self.values["system_nofication"]), False)
		return dict(self.values)

	def pin(self, state: bool):
		state = bool(state)
		self.values.set("system_pin", state, self._api is not None)
		if self._api is not None:
			self._api.set_on_top(state)
		return state

	def _normalize_window_dimension(self, value, default: int, minimum: int, fallback=None) -> int:
		minimum = max(1, int(minimum))

		try:
			fallback_value = int(round(float(fallback)))
		except (TypeError, ValueError):
			fallback_value = default

		fallback_value = max(minimum, fallback_value)

		try:
			normalized = int(round(float(value)))
		except (TypeError, ValueError):
			return fallback_value

		return max(minimum, normalized)

	def get_window_min_size_values(self, min_width=None, min_height=None) -> tuple[int, int]:
		current_min_width = self._window_min_width
		current_min_height = self._window_min_height

		resolved_min_width = self._normalize_window_dimension(
			current_min_width if min_width is None else min_width,
			DEFAULT_WINDOW_MIN_WIDTH,
			ABSOLUTE_WINDOW_MIN_WIDTH,
			current_min_width,
		)
		resolved_min_height = self._normalize_window_dimension(
			current_min_height if min_height is None else min_height,
			DEFAULT_WINDOW_MIN_HEIGHT,
			ABSOLUTE_WINDOW_MIN_HEIGHT,
			current_min_height,
		)
		return resolved_min_width, resolved_min_height

	def set_window_min_size(self, min_width=None, min_height=None) -> tuple[int, int]:
		resolved_min_width, resolved_min_height = self.get_window_min_size_values(min_width, min_height)
		self._window_min_width = resolved_min_width
		self._window_min_height = resolved_min_height
		return resolved_min_width, resolved_min_height

	def get_window_size_values(self, width=None, height=None) -> tuple[int, int]:
		current_width = self.values.get("system_window_width")
		current_height = self.values.get("system_window_height")
		minimum_width, minimum_height = self.get_window_min_size_values()

		resolved_width = self._normalize_window_dimension(
			current_width if width is None else width,
			DEFAULT_WINDOW_WIDTH,
			minimum_width,
			current_width,
		)
		resolved_height = self._normalize_window_dimension(
			current_height if height is None else height,
			DEFAULT_WINDOW_HEIGHT,
			minimum_height,
			current_height,
		)
		return resolved_width, resolved_height

	def sync_window_size(self, width, height, sync: bool = True) -> tuple[int, int]:
		resolved_width, resolved_height = self.get_window_size_values(width, height)

		if self.values.get("system_window_width") != resolved_width:
			self.values.set("system_window_width", resolved_width, sync)
		if self.values.get("system_window_height") != resolved_height:
			self.values.set("system_window_height", resolved_height, sync)

		return resolved_width, resolved_height

	def sync_window_min_size(self, min_width, min_height, sync: bool = True) -> tuple[int, int, int, int]:
		resolved_min_width, resolved_min_height = self.set_window_min_size(min_width, min_height)

		resolved_width, resolved_height = self.sync_window_size(
			self.values.get("system_window_width"),
			self.values.get("system_window_height"),
			sync,
		)
		return resolved_min_width, resolved_min_height, resolved_width, resolved_height

	def syncValue(self, key, value):
		if key in {"system_window_width", "system_window_height"}:
			return self.sync_window_size(
				value if key == "system_window_width" else self.values.get("system_window_width"),
				value if key == "system_window_height" else self.values.get("system_window_height"),
				False,
			)[0 if key == "system_window_width" else 1]
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

	def start(self, debug: bool = False, min_width=None, min_height=None):
		if min_width is not None or min_height is not None:
			resolved_min_width, resolved_min_height, _, _ = self.sync_window_min_size(
				self._window_min_width if min_width is None else min_width,
				self._window_min_height if min_height is None else min_height,
				sync=False,
			)
			if self._api is not None and getattr(self._api, "_window", None) is not None:
				self._api.set_window_minimum_size(resolved_min_width, resolved_min_height)
		self.accent.start()
		self.api.start(debug=debug)

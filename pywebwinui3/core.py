from __future__ import annotations

import ctypes
import importlib
import json
import logging
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from ctypes import wintypes

import webview
from hPyT import title_bar, window_dwm

from .event import Event, PathEvent
from .type import Status
from .util import AccentColorWatcher, SyncDict, loadPage

logger = logging.getLogger("pywebwinui3")
core_logger = logging.getLogger("pywebwinui3.core")

DEFAULT_WINDOW_WIDTH = 900
DEFAULT_WINDOW_HEIGHT = 600
DEFAULT_WINDOW_MIN_WIDTH = 100
DEFAULT_WINDOW_MIN_HEIGHT = 100


def _virtual_host_origin(root_name: str, suffix: str) -> str:
	return f"https://{root_name}.{suffix}"


class _Point(ctypes.Structure):
	_fields_ = [
		("x", ctypes.c_long),
		("y", ctypes.c_long),
	]

_user32 = ctypes.WinDLL("user32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_uxtheme = ctypes.WinDLL("uxtheme", use_last_error=True)

_kernel32.GetProcAddress.argtypes = [wintypes.HMODULE, wintypes.LPCSTR]
_kernel32.GetProcAddress.restype = ctypes.c_void_p
_user32.ReleaseCapture.argtypes = []
_user32.ReleaseCapture.restype = ctypes.c_bool
_user32.GetCursorPos.argtypes = [ctypes.POINTER(_Point)]
_user32.GetCursorPos.restype = ctypes.c_bool
_user32.GetSystemMenu.argtypes = [ctypes.c_void_p, ctypes.c_bool]
_user32.GetSystemMenu.restype = ctypes.c_void_p
_user32.IsZoomed.argtypes = [ctypes.c_void_p]
_user32.IsZoomed.restype = ctypes.c_bool
_user32.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
_user32.PostMessageW.restype = ctypes.c_bool
_user32.SendMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
_user32.SendMessageW.restype = ctypes.c_ssize_t
_user32.SetForegroundWindow.argtypes = [ctypes.c_void_p]
_user32.SetForegroundWindow.restype = ctypes.c_bool
_user32.ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
_user32.ShowWindow.restype = ctypes.c_bool
_user32.TrackPopupMenu.argtypes = [
	ctypes.c_void_p,
	ctypes.c_uint,
	ctypes.c_int,
	ctypes.c_int,
	ctypes.c_int,
	ctypes.c_void_p,
	ctypes.c_void_p,
]
_user32.TrackPopupMenu.restype = ctypes.c_uint


def _load_ordinal_function(module, ordinal: int, restype, argtypes):
	address = _kernel32.GetProcAddress(
		wintypes.HMODULE(module._handle),
		ctypes.cast(ctypes.c_void_p(ordinal), wintypes.LPCSTR),
	)
	if not address:
		return None
	function = ctypes.WINFUNCTYPE(restype, *argtypes)(address)
	function.argtypes = argtypes
	function.restype = restype
	return function


_allow_dark_mode_for_window = (
	_load_ordinal_function(_uxtheme, 145, ctypes.c_bool, [ctypes.c_void_p, ctypes.c_bool])
	or _load_ordinal_function(_uxtheme, 133, ctypes.c_bool, [ctypes.c_void_p, ctypes.c_bool])
)
_set_preferred_app_mode = _load_ordinal_function(_uxtheme, 135, ctypes.c_int, [ctypes.c_int])
_flush_menu_themes = _load_ordinal_function(_uxtheme, 136, None, [])


def _apply_menu_theme_support(theme: str | None, hwnd: int | None = None):
	if _set_preferred_app_mode is None:
		return False
	try:
		normalized = str(theme or "system").casefold()
		if normalized == "dark":
			mode = 2  # ForceDark
			allow_dark = True
		elif normalized == "light":
			mode = 3  # ForceLight
			allow_dark = False
		else:
			mode = 1  # AllowDark
			allow_dark = True

		_set_preferred_app_mode(mode)
		if hwnd is not None and _allow_dark_mode_for_window is not None:
			_allow_dark_mode_for_window(hwnd, allow_dark)
		if _flush_menu_themes is not None:
			_flush_menu_themes()
		return True
	except Exception:
		core_logger.debug("Failed to apply menu theme support", exc_info=True)
		return False


class _JsApi:
	def _init(self, main:MainWindow):
		self.init = main._init_payload
		self.frontendReady = main._frontend_ready_callback
		self.syncValue = main.syncValue
		self.syncValues = main._sync_values
		self.pin = main.pin
		self.startWindowDrag = main.startWindowDrag
		self.toggleWindowMaximize = main.toggleWindowMaximize
		self.showWindowSystemMenu = main.showWindowSystemMenu
		self.minimize = main.minimize
		self.destroy = main.destroy
		self.resolveResource = main.resolveResource


class WindowEvents:
	def __init__(self) -> None:
		self.windowReady = Event()
		self.closing = Event()
		self.closed = Event()
		self.accentColorChange = Event()
		self.valueChange = PathEvent()


class MainWindow:
	virtual_host_suffix = "pywebwinui"

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
		self._defer_window_chrome = False
		self._startup_cloaked = False
		self._sync_lock = threading.Lock()
		self._pending_sync: dict[str, object] = {}
		self._sync_event = threading.Event()
		self._sync_thread: threading.Thread | None = None
		self._virtual_host_handlers: dict[str, object] = {}
		self._ui_origin = _virtual_host_origin("package", self.virtual_host_suffix)
		self._resource_roots: list[tuple[str, Path]] = [
			("root", self.rootPath),
			("package", self.packagePath),
		]

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
				"system_maximized": False,
			}
		)
		self.values.sync = self.queue_sync_value
		_apply_menu_theme_support(self.values.get("system_theme"))

		self._window = webview.create_window(
			self.values.get("system_title", self._title),
			"about:blank",
			js_api=self.api,
			background_color="#202020",
			text_select=True,
			width=DEFAULT_WINDOW_WIDTH,
			height=DEFAULT_WINDOW_HEIGHT,
			min_size=(self._minimum_width, self._minimum_height),
			on_top=bool(self.values.get("system_pin", False)),
		)
		self.show = self._show_window
		self.restore = self._restore_window
		self.hide = self._hide_window
		self.destroy = self._destroy_window
		self.minimize = self._minimize_window
		self.api._init(self)
		self._window.events.before_show += self._before_show
		self._window.events.closing += self._on_closing
		self._window.events.closed += self._on_closed
		self._window.events.maximized += self._on_window_maximized_state
		self._window.events.restored += self._on_window_restored_state
		self._window.events.restored += self._on_window_restored

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

	def onClosing(self):
		return self._event_decorator(self.events.closing)

	def onExit(self):
		return self._event_decorator(self.events.closed)

	def notice(
		self,
		level: Status,
		title: str,
		description: str,
		item: dict | None = None,
		*,
		key: str | None = None,
	):
		notifications = list(self.values["system_nofication"] or [])
		notification = [key, level, title, description, item] if key is not None else [level, title, description, item]

		if key is not None:
			for index, current in enumerate(notifications):
				if len(current) == 5 and current[0] == key:
					notifications[index] = notification
					break
			else:
				notifications.append(notification)
		else:
			notifications.append(notification)

		self.values["system_nofication"] = notifications

	def pin(self, state: bool):
		state = bool(state)
		self.values.set("system_pin", state)
		self.set_on_top(state)
		return state

	def syncValue(self, key, value):
		if key == "system_theme":
			_apply_menu_theme_support(value, self._window_handle())
		return self.values.set(key, value, False)

	def addSettings(self, pageFile: str | Path | None = None, pageData: dict | None = None):
		if pageFile and not pageData:
			pageData = loadPage(pageFile)
		logger.debug("Setting page: %s", pageData["attr"]["path"])
		self.values["system_settings"] = pageData

	def addPage(self, pageFile: str | Path | None = None, pageData: dict | None = None):
		if pageFile and not pageData:
			pageData = loadPage(pageFile)
		page_path = str(pageData["attr"]["path"])
		logger.debug("Page added: %s", page_path)
		if self.values["system_pages"] is None:
			self.values["system_pages"] = {}
		self.values.set(f"system_pages[{json.dumps(page_path, ensure_ascii=False)}]", pageData)

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

	def _window_handle(self) -> int | None:
		try:
			native = getattr(self._window, "native", None)
			if native is None:
				return None
			return int(native.Handle.ToInt64())
		except Exception:
			return None

	def _entry_path(self) -> Path:
		entry = (Path(self.packagePath) / "index.html").resolve()
		if not entry.is_file():
			raise FileNotFoundError(f"Frontend entry not found: {entry}")
		return entry

	def _resource_url(self, path: Path) -> str:
		path = path.resolve()
		for name, base_path in sorted(self._resource_roots, key=lambda item: len(item[1].parts), reverse=True):
			try:
				relative = path.relative_to(base_path)
			except ValueError:
				continue

			return f"{_virtual_host_origin(name, self.virtual_host_suffix)}/{relative.as_posix()}"

		raise ValueError(f"Path is outside of registered resource roots: {path}")

	def _map_virtual_hosts(self, core_webview):
		parameter = core_webview.GetType().GetMethod("SetVirtualHostNameToFolderMapping").GetParameters()[2]
		access_kind = next(
			value for value in parameter.ParameterType.GetEnumValues()
			if str(value) == "DenyCors"
		)

		for name, base_path in self._resource_roots:
			core_webview.SetVirtualHostNameToFolderMapping(
				f"{name}.{self.virtual_host_suffix}",
				str(base_path),
				access_kind,
			)

	def _configure_virtual_host_window(self, window, target_url: str, *, show: bool = False):
		native = getattr(window, "native", None)
		browser = getattr(native, "browser", None)
		webview_control = getattr(browser, "webview", None)
		if native is None or browser is None or webview_control is None:
			core_logger.debug("WebView2 is unavailable for virtual host mapping")
			return

		def load_mapped_url(core_webview):
			self._map_virtual_hosts(core_webview)
			browser.load_url(target_url)
			if show:
				window.show()

		def on_initialized(_, args):
			try:
				if not args.IsSuccess:
					core_logger.error("WebView2 initialization failed before virtual host mapping")
					return
				load_mapped_url(webview_control.CoreWebView2)
			except Exception:
				core_logger.error("Failed to configure WebView2 virtual host mapping", exc_info=True)
			finally:
				try:
					webview_control.CoreWebView2InitializationCompleted -= on_initialized
				except Exception:
					pass
				self._virtual_host_handlers.pop(window.uid, None)

		def configure():
			try:
				core_webview = webview_control.CoreWebView2
			except Exception:
				core_webview = None
			if core_webview is not None:
				load_mapped_url(core_webview)
				return
			self._virtual_host_handlers[window.uid] = on_initialized
			webview_control.CoreWebView2InitializationCompleted += on_initialized

		try:
			self._invoke_native_sync(native, configure)
		except Exception:
			core_logger.error("Failed to configure WebView2 virtual host mapping", exc_info=True)

	def createResourceWindow(self, title: str, url: str, **kwargs):
		keep_hidden = bool(kwargs.pop("hidden", False))
		window = webview.create_window(title, "about:blank", hidden=True, **kwargs)
		self._configure_virtual_host_window(window, url, show=not keep_hidden)
		return window

	def _before_show(self):
		try:
			self._configure_virtual_host_window(self._window, self._resource_url(self._entry_path()))
			hwnd = self._window.native.Handle.ToInt64()
			_apply_menu_theme_support(self.values.get("system_theme"), hwnd)
			if self._defer_window_chrome:
				window_dwm.toggle_cloak(hwnd, True)
				self._startup_cloaked = True
			else:
				title_bar.hide(hwnd)
				self._set_window_maximized_state(bool(_user32.IsZoomed(hwnd)), sync=False)
		except Exception:
			core_logger.debug("Failed to hide title bar", exc_info=True)

	def _invoke_native(self, native, callback):
		action_type = getattr(importlib.import_module("System"), "Action")
		if native.InvokeRequired:
			native.BeginInvoke(action_type(callback))
		else:
			callback()

	def _invoke_native_sync(self, native, callback):
		action_type = getattr(importlib.import_module("System"), "Action")
		if native.InvokeRequired:
			native.Invoke(action_type(callback))
		else:
			callback()

	def _invoke_native_later(self, native, callback, delay: float):
		timer = threading.Timer(delay, lambda: self._invoke_native(native, callback))
		timer.daemon = True
		timer.start()

	def _on_window_maximized_state(self, *_):
		self._set_window_maximized_state(True)

	def _on_window_restored_state(self, *_):
		self._set_window_maximized_state(False)

	def _on_window_restored(self):
		self._ensure_window_chrome()
		self._refresh_client_layout()

	def _ensure_window_chrome(self, delay: float = 0.08):
		if not self._defer_window_chrome:
			return

		self._defer_window_chrome = False
		native = getattr(self._window, "native", None)
		if native is None:
			return

		def _apply():
			try:
				hwnd = int(native.Handle.ToInt64())
				_apply_menu_theme_support(self.values.get("system_theme"), hwnd)
				if self._startup_cloaked:
					window_dwm.toggle_cloak(hwnd, False)
					self._startup_cloaked = False
				try:
					title_bar.unhide(hwnd)
				except Exception:
					pass
				title_bar.hide(hwnd)
				self._set_window_maximized_state(bool(_user32.IsZoomed(hwnd)), sync=False)
			except Exception:
				core_logger.debug("Failed to ensure window chrome", exc_info=True)

		self._invoke_native_later(native, _apply, delay)

	def _refresh_client_layout(self, delay: float = 0.08):
		native = getattr(self._window, "native", None)
		if native is None:
			return

		forms = importlib.import_module("System.Windows.Forms")

		def _apply():
			try:
				native.SuspendLayout()
				webview_control = getattr(native, "webview", None)
				if webview_control is not None:
					webview_control.Dock = forms.DockStyle.Fill
					webview_control.Bounds = native.ClientRectangle
					webview_control.BringToFront()
					webview_control.Invalidate()
					webview_control.Update()
				native.PerformLayout()
				native.Invalidate(True)
				native.Refresh()
			except Exception:
				core_logger.debug("Failed to refresh client layout", exc_info=True)
			finally:
				try:
					native.ResumeLayout(True)
				except Exception:
					pass

		self._invoke_native_later(native, _apply, delay)

	def _show_window(self):
		native = getattr(self._window, "native", None)
		if native is None:
			self._window.show()
		else:
			self._invoke_native_sync(native, self._window.show)
		self._ensure_window_chrome()
		self._refresh_client_layout()

	def _restore_window(self):
		native = getattr(self._window, "native", None)
		if native is None:
			self._window.restore()
		else:
			self._invoke_native_sync(native, self._window.restore)
		self._ensure_window_chrome()
		self._refresh_client_layout()

	def _hide_window(self):
		native = getattr(self._window, "native", None)
		if native is None:
			self._window.hide()
			return
		self._invoke_native_sync(native, self._window.hide)

	def _destroy_window(self):
		native = getattr(self._window, "native", None)
		if native is None:
			self._window.destroy()
			return
		self._invoke_native_sync(native, self._window.destroy)

	def _minimize_window(self):
		native = getattr(self._window, "native", None)
		if native is None:
			self._window.minimize()
			return
		self._invoke_native_sync(native, self._window.minimize)

	def _on_closing(self, *_):
		return not self.events.closing.set()

	def _on_closed(self):
		self.accent.stop()
		with self._sync_lock:
			self._pending_sync.clear()
		self._sync_event.set()
		self._virtual_host_handlers.clear()
		self.events.closed.set()

	def _dispatch_sync_values(self, values: dict[str, object]):
		if not values:
			return

		if "system_title" in values:
			try:
				self._window.title = str(values["system_title"] or self._title)
			except Exception:
				core_logger.debug("Failed to update window title", exc_info=True)

		native = getattr(self._window, "native", None)
		browser = getattr(native, "browser", None)
		webview2 = getattr(browser, "webview", None)
		if native is None or webview2 is None:
			core_logger.debug("WebView2 is unavailable for UI sync")
			return

		try:
			message = json.dumps(
				{"type": "pywebwinui3.sync", "values": values},
				ensure_ascii=False,
			)

			def post_message():
				try:
					core_webview = webview2.CoreWebView2
					if core_webview is not None:
						core_webview.PostWebMessageAsJson(message)
				except Exception:
					core_logger.debug("Failed to post UI sync message", exc_info=True)

			self._invoke_native(native, post_message)
		except Exception:
			core_logger.debug("Failed to queue UI sync message", exc_info=True)

	def queue_sync_value(self, key: str, value):
		with self._sync_lock:
			self._pending_sync[key] = value
			frontend_ready = self._frontend_ready

		if not frontend_ready:
			return
		self._ensure_sync_worker()
		self._sync_event.set()

	def _ensure_sync_worker(self):
		if self._sync_thread and self._sync_thread.is_alive():
			return
		self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True, name="PyWebWinUI3-Sync")
		self._sync_thread.start()

	def _sync_loop(self):
		while True:
			self._sync_event.wait()
			while True:
				with self._sync_lock:
					if not self._pending_sync:
						self._sync_event.clear()
						break
					pending = dict(self._pending_sync)
					self._pending_sync.clear()

				self._dispatch_sync_values(pending)

	def _set_window_maximized_state(self, value: bool, *, sync: bool = True):
		value = bool(value)
		if self.values.get("system_maximized") == value:
			return
		self.values.set("system_maximized", value, False)
		if sync:
			timer = threading.Timer(0.01, lambda: self.queue_sync_value("system_maximized", value))
			timer.daemon = True
			timer.start()

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

		self._ensure_sync_worker()
		self._sync_event.set()

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

			def _apply():
				self._window.on_top = state

			self._invoke_native(native, _apply)
		except Exception:
			core_logger.debug("Failed to set window on top", exc_info=True)

	def startWindowDrag(self):
		try:
			native = getattr(self._window, "native", None)
			if native is None:
				return

			def _apply():
				hwnd = int(native.Handle.ToInt64())
				_user32.ReleaseCapture()
				_user32.SendMessageW(hwnd, 0x00A1, 2, 0)  # WM_NCLBUTTONDOWN, HTCAPTION

			self._invoke_native(native, _apply)
		except Exception:
			core_logger.debug("Failed to start system window drag", exc_info=True)

	def toggleWindowMaximize(self):
		try:
			native = getattr(self._window, "native", None)
			if native is None:
				return

			def _apply():
				hwnd = int(native.Handle.ToInt64())
				is_zoomed = bool(_user32.IsZoomed(hwnd))
				command = 9 if is_zoomed else 3  # SW_RESTORE / SW_MAXIMIZE
				_user32.ShowWindow(hwnd, command)

			self._invoke_native(native, _apply)
		except Exception:
			core_logger.debug("Failed to toggle window maximize", exc_info=True)

	def showWindowSystemMenu(self):
		try:
			native = getattr(self._window, "native", None)
			if native is None:
				return

			def _apply():
				hwnd = int(native.Handle.ToInt64())
				menu = _user32.GetSystemMenu(hwnd, False)
				if not menu:
					return
				_apply_menu_theme_support(self.values.get("system_theme"), hwnd)

				cursor = _Point()
				if not _user32.GetCursorPos(ctypes.byref(cursor)):
					return

				_user32.SetForegroundWindow(hwnd)
				command = _user32.TrackPopupMenu(
					menu,
					0x0100 | 0x0002,  # TPM_RETURNCMD | TPM_RIGHTBUTTON
					cursor.x,
					cursor.y,
					0,
					hwnd,
					None,
				)
				if command:
					_user32.PostMessageW(hwnd, 0x0112, command, 0)  # WM_SYSCOMMAND
				_user32.PostMessageW(hwnd, 0x0000, 0, 0)  # WM_NULL

			self._invoke_native(native, _apply)
		except Exception:
			core_logger.debug("Failed to show window system menu", exc_info=True)

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

		parsed = urlparse(raw_value)
		path_value = parsed.path or raw_value
		resolved = self.resolve_path(path_value)
		if resolved is None or not resolved.exists() or not resolved.is_file():
			return raw_value

		resource_url = self._resource_url(resolved)
		if not parsed.scheme and (parsed.query or parsed.fragment):
			resource_parts = urlparse(resource_url)
			resource_url = urlunparse(
				(
					resource_parts.scheme,
					resource_parts.netloc,
					resource_parts.path,
					resource_parts.params,
					parsed.query,
					parsed.fragment,
				)
			)

		return resource_url

	def start(
		self,
		debug: bool = False,
		*,
		hidden: bool = False,
		minimized: bool = False,
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
		self._defer_window_chrome = bool(hidden or minimized)
		self._window.hidden = bool(hidden)
		self._window.minimized = bool(minimized and not hidden)

		if width is not None and height is not None:
			width = max(self._minimum_width, int(width))
			height = max(self._minimum_height, int(height))
			self._window.initial_width = width
			self._window.initial_height = height

		if on_top is not None:
			self._window.on_top = bool(on_top)

		webview.start(debug=debug, gui="edgechromium")

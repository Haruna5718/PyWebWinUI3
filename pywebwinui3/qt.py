from __future__ import annotations

import ctypes
import json
import logging
import os
import sys
import threading
from pathlib import Path
from ctypes import wintypes

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QColor, QCursor, QDesktopServices, QIcon, QKeySequence, QShortcut
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineContextMenuRequest, QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
import win32api
import win32con
import win32gui
import win32gui_struct

logger = logging.getLogger("pywebwinui3.qt")

_uxtheme = ctypes.windll.uxtheme
_get_proc_address = ctypes.windll.kernel32.GetProcAddress
_get_proc_address.restype = ctypes.c_void_p
_get_proc_address.argtypes = [ctypes.c_void_p, ctypes.c_void_p]


def _get_ordinal_proc(module, ordinal: int, restype, argtypes):
	address = _get_proc_address(module._handle, ctypes.c_void_p(ordinal))
	if not address:
		return None
	return ctypes.WINFUNCTYPE(restype, *argtypes)(address)


_set_preferred_app_mode = _get_ordinal_proc(_uxtheme, 135, ctypes.c_int, [ctypes.c_int])
_flush_menu_themes = _get_ordinal_proc(_uxtheme, 136, None, [])
_allow_dark_mode_for_window = _get_ordinal_proc(_uxtheme, 133, wintypes.BOOL, [wintypes.HWND, wintypes.BOOL])


def _apply_native_menu_theme(dark: bool, hwnd: int | None = None):
	if _set_preferred_app_mode is not None:
		_set_preferred_app_mode(2 if dark else 3)
	if hwnd is not None and _allow_dark_mode_for_window is not None:
		_allow_dark_mode_for_window(hwnd, bool(dark))
	if _flush_menu_themes is not None:
		_flush_menu_themes()


def open_url(url: str | QUrl) -> bool:
	if (raw := url if isinstance(url, str) else url.toString()):
		if (parsed:=QUrl(raw)).isValid() and QDesktopServices.openUrl(parsed):
			return True
		try:
			os.startfile(raw)
			return True
		except OSError:
			logger.debug("Fallback shell open failed for %s", raw, exc_info=True)
	return False

class MARGINS(ctypes.Structure):
	_fields_ = [
		("cxLeftWidth", ctypes.c_int),
		("cxRightWidth", ctypes.c_int),
		("cyTopHeight", ctypes.c_int),
		("cyBottomHeight", ctypes.c_int),
	]


class MSG(ctypes.Structure):
	_fields_ = [
		("hwnd", wintypes.HWND),
		("message", wintypes.UINT),
		("wParam", wintypes.WPARAM),
		("lParam", wintypes.LPARAM),
		("time", wintypes.DWORD),
		("pt", wintypes.POINT),
	]

def _read_resize_border_thickness():
	return (
		win32api.GetSystemMetrics(win32con.SM_CXSIZEFRAME)
		+ win32api.GetSystemMetrics(92)
	) / 2

class ExternalAwarePage(QWebEnginePage):
	def _is_same_document_fragment(self, url: QUrl) -> bool:
		current = self.url()
		return (
			bool(url.fragment())
			and current.isValid()
			and url.scheme() == current.scheme()
			and url.host() == current.host()
			and url.port() == current.port()
			and url.path() == current.path()
			and url.query() == current.query()
		)

	def acceptNavigationRequest(self, url, navigation_type, ismain_frame):
		if (
			ismain_frame
			and navigation_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked
			and url.scheme() not in {"about", "data", "file", "qrc"}
		):
			if self._is_same_document_fragment(url):
				return super().acceptNavigationRequest(url, navigation_type, ismain_frame)
			open_url(url)
			return False
		return super().acceptNavigationRequest(url, navigation_type, ismain_frame)

	def createWindow(self, _):
		page = QWebEnginePage(self.profile(), self)

		def open_and_cleanup(url):
			open_url(url)
			page.deleteLater()

		page.urlChanged.connect(open_and_cleanup)
		return page

class FramelessWindow(QMainWindow):
	closed = Signal()

	EDGE_MAP = [
		"left",
		"right",
		"top",
		"bottom",
		"top-left",
		"top-right",
		"bottom-left",
		"bottom-right",
	]
	CURSOR_MAP = {
		"left": Qt.CursorShape.SizeHorCursor,
		"right": Qt.CursorShape.SizeHorCursor,
		"top": Qt.CursorShape.SizeVerCursor,
		"bottom": Qt.CursorShape.SizeVerCursor,
		"top-left": Qt.CursorShape.SizeFDiagCursor,
		"bottom-right": Qt.CursorShape.SizeFDiagCursor,
		"top-right": Qt.CursorShape.SizeBDiagCursor,
		"bottom-left": Qt.CursorShape.SizeBDiagCursor,
	}

	def __init__(self, api, page_path: Path, title: str, icon_path: Path | None, debug: bool = False):
		super().__init__()
		self.api = api
		self.page_path = page_path
		self._native_frame_ready = False
		self._resize_edge_name: str | None = None
		self._resize_origin: QPoint | None = None
		self._resize_geometry: QRect | None = None
		self._active_resize_cursor = None
		self._resize_border = _read_resize_border_thickness()
		self._debug_tools_view: QWebEngineView | None = None
		self._debug_tools_page: QWebEnginePage | None = None

		self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
		self.setWindowTitle(title)
		self.resize(self.api.main.values.get("system_window_width"), self.api.main.values.get("system_window_height"))
		self.setMouseTracking(True)

		if icon_path and icon_path.exists():
			self.setWindowIcon(QIcon(str(icon_path)))

		self.view = QWebEngineView(self)
		self.page = ExternalAwarePage(self.view)
		self._apply_window_background()

		settings = self.page.settings()
		settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
		settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
		settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
		settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
		settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)

		self.channel = QWebChannel(self.page)
		self.channel.registerObject("backend", api)
		self.page.setWebChannel(self.channel)

		self.view.setPage(self.page)
		self.setCentralWidget(self.view)
		self.view.setMouseTracking(True)
		self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.view.customContextMenuRequested.connect(self._show_context_menu)
		self.page.loadFinished.connect(self._handle_load_finished)
		QApplication.instance().installEventFilter(self)

		if not self.page_path.is_file():
			raise FileNotFoundError(f"Frontend entry not found: {self.page_path}")

		if debug:
			debug_shortcut = QShortcut(QKeySequence("F12"), self)
			debug_shortcut.activated.connect(self.toggle_devtools)
			inspector_shortcut = QShortcut(QKeySequence("Ctrl+Shift+I"), self)
			inspector_shortcut.activated.connect(self.toggle_devtools)
			self._debug_shortcuts = (debug_shortcut, inspector_shortcut)

		self.view.setUrl(QUrl.fromLocalFile(str(self.page_path)))

	def showEvent(self, event):
		super().showEvent(event)
		self._refresh_resize_border()
		self._ensure_native_frame()

	def resizeEvent(self, event):
		super().resizeEvent(event)
		self.api.main.values.set("system_window_width", self.width(), False)
		self.api.main.values.set("system_window_height", self.height(), False)

	def nativeEvent(self, event_type, message):
		try:
			msg = MSG.from_address(int(message))
		except (TypeError, ValueError, OSError):
			return super().nativeEvent(event_type, message)

		if msg.message == win32con.WM_SETTINGCHANGE:
			self.api.main.accent.refresh()

		return super().nativeEvent(event_type, message)

	def closeEvent(self, event):
		app = QApplication.instance()
		if app is not None:
			app.removeEventFilter(self)
		self._set_resize_cursor(None)
		self.hide()
		if self._debug_tools_view is not None:
			self._debug_tools_view.close()
		QTimer.singleShot(0, self.closed.emit)
		super().closeEvent(event)

	def _maximize_native(self):
		self._ensure_native_frame()
		win32gui.ShowWindow(self._hwnd(), win32con.SW_MAXIMIZE)

	def _restore_native(self):
		self._ensure_native_frame()
		win32gui.ShowWindow(self._hwnd(), win32con.SW_RESTORE)

	def _start_native_move(self):
		handle = self.windowHandle()
		if handle is not None and handle.startSystemMove():
			return
		win32gui.ReleaseCapture()
		win32api.SendMessage(self._hwnd(), win32con.WM_NCLBUTTONDOWN, win32con.HTCAPTION, 0)

	def _hwnd(self) -> int:
		return int(self.winId())

	def _ensure_native_frame(self):
		if self._native_frame_ready:
			return

		hwnd = self._hwnd()
		style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
		style |= (
			win32con.WS_THICKFRAME
			| win32con.WS_MINIMIZEBOX
			| win32con.WS_MAXIMIZEBOX
			| win32con.WS_SYSMENU
		)
		win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

		ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
		ex_style |= win32con.WS_EX_APPWINDOW
		win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

		if sys.getwindowsversion().build >= 22000:
			dark_mode = wintypes.BOOL(self._resolved_theme() == "dark")
			ctypes.windll.dwmapi.DwmSetWindowAttribute(
				hwnd,
				20,
				ctypes.byref(dark_mode),
				ctypes.sizeof(dark_mode),
			)

			disable_transitions = wintypes.BOOL(True)
			ctypes.windll.dwmapi.DwmSetWindowAttribute(
				hwnd,
				3,
				ctypes.byref(disable_transitions),
				ctypes.sizeof(disable_transitions),
			)

			corners = ctypes.c_int(2)
			ctypes.windll.dwmapi.DwmSetWindowAttribute(
				hwnd,
				33,
				ctypes.byref(corners),
				ctypes.sizeof(corners),
			)

		margins = MARGINS(1, 1, 1, 1)
		ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))

		win32gui.SetWindowPos(
			hwnd,
			0,
			0,
			0,
			0,
			0,
			win32con.SWP_NOMOVE
			| win32con.SWP_NOSIZE
			| win32con.SWP_NOZORDER
			| win32con.SWP_NOACTIVATE
			| win32con.SWP_FRAMECHANGED,
		)
		_apply_native_menu_theme(self._resolved_theme() == "dark", hwnd)
		self._native_frame_ready = True

	def _refresh_resize_border(self):
		self._resize_border = _read_resize_border_thickness()

	def _resolved_theme(self) -> str:
		values = self.api.main.values
		theme = values.get("system_theme") or "system"
		if theme == "system":
			theme = values.get("system_theme_resolved") or "dark"
		return theme if theme in {"light", "dark"} else "dark"

	def _apply_window_background(self):
		self.page.setBackgroundColor(QColor("#f3f3f3"if self._resolved_theme() == "light" else "#202020"))

	def _handle_load_finished(self, _ok: bool):
		self._apply_window_background()

	def _sync_view_geometry(self):
		return

	def _show_context_menu(self, pos: QPoint):
		request = self.view.lastContextMenuRequest()
		if request is not None and request.isContentEditable():
			edit_flags = request.editFlags()
			self._exec_native_menu(
				self.view.mapToGlobal(pos),
				[
					(0x5000, "Undo", bool(edit_flags & QWebEngineContextMenuRequest.EditFlag.CanUndo), False, lambda: self.page.triggerAction(QWebEnginePage.WebAction.Undo)),
					(0x5001, "Redo", bool(edit_flags & QWebEngineContextMenuRequest.EditFlag.CanRedo), False, lambda: self.page.triggerAction(QWebEnginePage.WebAction.Redo)),
					None,
					(0x5002, "Cut", bool(edit_flags & QWebEngineContextMenuRequest.EditFlag.CanCut), False, lambda: self.page.triggerAction(QWebEnginePage.WebAction.Cut)),
					(0x5013, "Copy", bool(edit_flags & QWebEngineContextMenuRequest.EditFlag.CanCopy), False, lambda: self.page.triggerAction(QWebEnginePage.WebAction.Copy)),
					(0x5014, "Paste", bool(edit_flags & QWebEngineContextMenuRequest.EditFlag.CanPaste), False, lambda: self.page.triggerAction(QWebEnginePage.WebAction.Paste)),
					None,
					(0x5015, "Select All", bool(edit_flags & QWebEngineContextMenuRequest.EditFlag.CanSelectAll), False, lambda: self.page.triggerAction(QWebEnginePage.WebAction.SelectAll)),
				],
			)
			return

		self._exec_native_menu(
			self.view.mapToGlobal(pos),
			[
				(0x5010, "Back", self.page.action(QWebEnginePage.WebAction.Back).isEnabled(), False, lambda: self.page.triggerAction(QWebEnginePage.WebAction.Back)),
				(0x5011, "Forward", self.page.action(QWebEnginePage.WebAction.Forward).isEnabled(), False, lambda: self.page.triggerAction(QWebEnginePage.WebAction.Forward)),
				(0x5012, "Reload", True, False, lambda: self.page.triggerAction(QWebEnginePage.WebAction.Reload)),
			],
		)

	def _exec_native_menu(self, global_pos: QPoint, items):
		menu = win32gui.CreatePopupMenu()
		callbacks = {}
		try:
			win32gui.SetMenuInfo(menu, win32gui_struct.PackMENUINFO(dwStyle=win32con.MNS_CHECKORBMP))
			for item in items:
				if item is None:
					win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
					continue

				command_id, label, enabled, checked, callback, *extra = item
				bitmap = extra[0] if extra else None
				flags = win32con.MF_STRING
				if not enabled:
					flags |= win32con.MF_GRAYED
				if checked:
					flags |= win32con.MF_CHECKED
				win32gui.AppendMenu(menu, flags, command_id, label)
				if bitmap is not None:
					packed, _extras = win32gui_struct.PackMENUITEMINFO(hbmpItem=bitmap)
					win32gui.SetMenuItemInfo(menu, command_id, False, packed)
				callbacks[command_id] = callback

			hwnd = self._hwnd()
			win32gui.SetForegroundWindow(hwnd)
			command = win32gui.TrackPopupMenu(
				menu,
				win32con.TPM_RETURNCMD | win32con.TPM_NONOTIFY | win32con.TPM_RIGHTBUTTON,
				global_pos.x(),
				global_pos.y(),
				0,
				hwnd,
				None,
			)
			win32gui.PostMessage(hwnd, win32con.WM_NULL, 0, 0)

			callback = callbacks.get(command)
			if command and callback is not None:
				callback()
		finally:
			win32gui.DestroyMenu(menu)

	def _open_devtools(self):
		if self._debug_tools_view is None:
			self._debug_tools_view = QWebEngineView()
			self._debug_tools_page = QWebEnginePage(self.page.profile(), self._debug_tools_view)
			self._debug_tools_view.setPage(self._debug_tools_page)
			self.page.setDevToolsPage(self._debug_tools_page)
			self._debug_tools_view.setWindowTitle(f"{self.windowTitle()} DevTools")
			self._debug_tools_view.resize(600, 800)

		self._debug_tools_view.show()
		self._debug_tools_view.raise_()
		self._debug_tools_view.activateWindow()

	@Slot()
	def toggle_devtools(self):
		if self._debug_tools_view is None or not self._debug_tools_view.isVisible():
			self._open_devtools()
			return

		self._debug_tools_view.hide()

	def _belongs_to_window(self, watched) -> bool:
		if watched in {self, self.view}:
			return True
		if isinstance(watched, QWidget):
			return watched.window() is self
		return False

	def _is_native_maximized(self) -> bool:
		try:
			return bool(win32gui.IsZoomed(self._hwnd()))
		except Exception:
			return self.isMaximized()

	def _is_effectively_maximized(self) -> bool:
		state = self.windowState()
		return bool(state & Qt.WindowState.WindowMaximized) or self._is_native_maximized()

	def _edge_from_pos(self, pos: QPoint, size) -> str | None:
		if self._is_effectively_maximized():
			return None

		border = self._resize_border
		on_left = 0 <= pos.x() < border
		on_right = size.width() - border <= pos.x() < size.width()
		on_top = 0 <= pos.y() < border
		on_bottom = size.height() - border <= pos.y() < size.height()

		if on_top and on_left:
			return "top-left"
		if on_top and on_right:
			return "top-right"
		if on_bottom and on_left:
			return "bottom-left"
		if on_bottom and on_right:
			return "bottom-right"
		if on_left:
			return "left"
		if on_right:
			return "right"
		if on_top:
			return "top"
		if on_bottom:
			return "bottom"
		return None

	def _set_resize_cursor(self, edge_name: str | None):
		cursor = self.CURSOR_MAP.get(edge_name)
		if cursor == self._active_resize_cursor:
			return

		app = QApplication.instance()
		if app is None:
			self._active_resize_cursor = cursor
			return

		if cursor is None:
			if self._active_resize_cursor is not None:
				app.restoreOverrideCursor()
			self._active_resize_cursor = None
			return

		qcursor = QCursor(cursor)
		if self._active_resize_cursor is None:
			app.setOverrideCursor(qcursor)
		else:
			app.changeOverrideCursor(qcursor)
		self._active_resize_cursor = cursor

	def _begin_resize(self, edge_name: str, global_pos: QPoint):
		self._refresh_resize_border()
		self._resize_edge_name = edge_name
		self._resize_origin = QPoint(global_pos)
		self._resize_geometry = QRect(self.geometry())
		self._set_resize_cursor(edge_name)
		self.grabMouse()

	def _apply_resize(self, global_pos: QPoint):
		if self._resize_edge_name is None or self._resize_origin is None or self._resize_geometry is None:
			return

		self._set_resize_cursor(self._resize_edge_name)
		dx = global_pos.x() - self._resize_origin.x()
		dy = global_pos.y() - self._resize_origin.y()
		geometry = QRect(self._resize_geometry)
		minimum_width = max(self.minimumWidth(), 1)
		minimum_height = max(self.minimumHeight(), 1)

		if "left" in self._resize_edge_name:
			max_left = geometry.right() - minimum_width + 1
			geometry.setLeft(min(geometry.left() + dx, max_left))
		if "right" in self._resize_edge_name:
			min_right = geometry.left() + minimum_width - 1
			geometry.setRight(max(geometry.right() + dx, min_right))
		if "top" in self._resize_edge_name:
			max_top = geometry.bottom() - minimum_height + 1
			geometry.setTop(min(geometry.top() + dy, max_top))
		if "bottom" in self._resize_edge_name:
			min_bottom = geometry.top() + minimum_height - 1
			geometry.setBottom(max(geometry.bottom() + dy, min_bottom))

		if self.geometry() != geometry:
			self.setGeometry(geometry)

	def _end_resize(self):
		if self._resize_edge_name is None:
			return

		self._resize_edge_name = None
		self._resize_origin = None
		self._resize_geometry = None
		self.releaseMouse()
		self._set_resize_cursor(None)

	def eventFilter(self, watched:QObject, event:QEvent):
		if event.type() not in {
			QEvent.Type.MouseButtonPress,
			QEvent.Type.MouseButtonRelease,
			QEvent.Type.MouseMove,
		}:
			return super().eventFilter(watched, event)

		if not hasattr(event, "globalPosition"):
			return super().eventFilter(watched, event)

		if self._resize_edge_name is None and not self._belongs_to_window(watched):
			self._set_resize_cursor(None)
			return super().eventFilter(watched, event)

		global_pos = event.globalPosition().toPoint()
		local_pos = self.mapFromGlobal(global_pos)

		if self._resize_edge_name is None and not self.rect().contains(local_pos):
			self._set_resize_cursor(None)
			return super().eventFilter(watched, event)

		edge_name = self._edge_from_pos(local_pos, self.size())

		if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton and edge_name:
			self._begin_resize(edge_name, global_pos)
			event.accept()
			return True

		if event.type() == QEvent.Type.MouseMove:
			if self._resize_edge_name is not None:
				self._apply_resize(global_pos)
				event.accept()
				return True

			self._set_resize_cursor(edge_name)
			return False

		if event.type() == QEvent.Type.MouseButtonRelease and self._resize_edge_name is not None:
			self._end_resize()
			event.accept()
			return True

		return super().eventFilter(watched, event)

	@Slot()
	def minimize(self):
		self.showMinimized()

	@Slot()
	def close_window(self):
		self.close()

	@Slot(bool)
	def set_on_top(self, state: bool):
		self._ensure_native_frame()
		win32gui.SetWindowPos(
			self._hwnd(),
			win32con.HWND_TOPMOST if state else win32con.HWND_NOTOPMOST,
			0,
			0,
			0,
			0,
			win32con.SWP_NOMOVE
			| win32con.SWP_NOSIZE
			| win32con.SWP_NOOWNERZORDER
			| win32con.SWP_NOACTIVATE,
		)
		if state:
			self.raise_()

	@Slot()
	def start_window_drag(self):
		self._ensure_native_frame()
		self._start_native_move()

	@Slot(str)
	def start_window_resize(self, edge_name: str):
		if edge_name not in self.EDGE_MAP:
			return

		self._begin_resize(edge_name, QCursor.pos())

	@Slot()
	def toggle_maximize(self):
		if self._is_effectively_maximized():
			self._restore_native()
			return
		self._maximize_native()

	@Slot()
	def show_window_menu(self):
		pinned = bool(self.api.main.values.get("system_pin"))
		maximized = self._is_effectively_maximized()
		self._exec_native_menu(
			QCursor.pos(),
			[
				(0x5020, "Pin", True, pinned, lambda: self.api.main.pin(not pinned)),
				(win32con.SC_MINIMIZE, "Minimize", True, False, self.minimize, win32con.HBMMENU_POPUP_MINIMIZE),
				(
					win32con.SC_RESTORE if maximized else win32con.SC_MAXIMIZE,
					"Restore" if maximized else "Maximize",
					True,
					False,
					self.toggle_maximize,
					win32con.HBMMENU_POPUP_RESTORE if maximized else win32con.HBMMENU_POPUP_MAXIMIZE,
				),
				None,
				(win32con.SC_CLOSE, "Close", True, False, self.close_window, win32con.HBMMENU_POPUP_CLOSE),
			],
		)

	@Slot(int, int)
	def apply_window_size(self, width: int, height: int):
		width = max(self.minimumWidth(), int(width))
		height = max(self.minimumHeight(), int(height))

		if self._is_effectively_maximized():
			self._restore_native()

		if self.width() == width and self.height() == height:
			return

		self.resize(width, height)

	def apply_minimum_window_size(self, width: int, height: int):
		width = max(1, int(width))
		height = max(1, int(height))

		if self.minimumWidth() == width and self.minimumHeight() == height:
			return

		self.setMinimumSize(width, height)
		if not self._is_effectively_maximized():
			self.resize(max(self.width(), width), max(self.height(), height))

class WebviewAPI(QObject):
	WINDOW_SIZE_KEYS = frozenset({"system_window_width", "system_window_height"})

	dispatch_sync_requested = Signal(str, "QVariant")
	close_requested = Signal()
	minimize_requested = Signal()
	set_on_top_requested = Signal(bool)
	resize_window_requested = Signal(int, int)
	start_drag_requested = Signal()
	start_resize_requested = Signal(str)
	toggle_maximize_requested = Signal()
	show_window_menu_requested = Signal()

	def __init__(self, main_window, title: str, icon: str | None):
		super().__init__()
		self.main = main_window
		self._title = title
		self._icon = icon

		self._app = None
		self._owns_app = False
		self._window = None
		self._frontend_ready = False
		self._setup_fired = False
		self._sync_lock = threading.Lock()
		self._pending_sync: dict[str, object] = {}
		self.dispatch_sync_requested.connect(self._dispatch_sync_value, Qt.ConnectionType.QueuedConnection)

	def ensure_runtime(self, debug: bool = False):
		if self._window is not None:
			return

		app = QApplication.instance()
		if app is None:
			QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL, True)
			QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
			app = QApplication(sys.argv)
			self._owns_app = True

		self._app = app
		resolved_theme = self.main.values.get("system_theme") or "system"
		if resolved_theme == "system":
			resolved_theme = self.main.values.get("system_theme_resolved") or "dark"
		_apply_native_menu_theme(resolved_theme == "dark")

		icon_path = self.main.resolve_path(self._icon)
		title = self.main.values.get("system_title") or self._title

		self._window = FramelessWindow(self, self.main.packagePath / "index.html", title, icon_path, debug=debug)
		self._window.closed.connect(self.main.events.closed.set)
		self.close_requested.connect(self._window.close_window)
		self.minimize_requested.connect(self._window.minimize)
		self.set_on_top_requested.connect(self._window.set_on_top)
		self.resize_window_requested.connect(self._window.apply_window_size)
		self.start_drag_requested.connect(self._window.start_window_drag)
		self.start_resize_requested.connect(self._window.start_window_resize)
		self.toggle_maximize_requested.connect(self._window.toggle_maximize)
		self.show_window_menu_requested.connect(self._window.show_window_menu)

		# self.main.sync_window_size(self._window.width(), self._window.height(), sync=False)
		self.main.values.set("system_window_width", self._window.width(), False)
		self.main.values.set("system_window_height", self._window.height(), False)

		if self.main.values.get("system_pin"):
			self._window.set_on_top(True)

		self._window.show()

		logger.debug("Window created")

	def start(self, debug: bool = False):
		self.ensure_runtime(debug=debug)
		if self._owns_app:
			self._app.exec()

	def set_on_top(self, state: bool):
		self.ensure_runtime()
		self.set_on_top_requested.emit(state)

	def set_window_minimum_size(self, width: int, height: int):
		self.ensure_runtime()
		if self._window is not None:
			self._window.apply_minimum_window_size(width, height)

	def queue_sync_value(self, key: str, value):
		if key in self.WINDOW_SIZE_KEYS:
			width, height = self.main.sync_window_size(
				value if key == "system_window_width" else self.main.values.get("system_window_width"),
				value if key == "system_window_height" else self.main.values.get("system_window_height"),
				False,
			)

			if self._window is not None:
				self.resize_window_requested.emit(width, height)

			self._dispatch_or_defer_sync("system_window_width", width)
			self._dispatch_or_defer_sync("system_window_height", height)
			return

		self._dispatch_or_defer_sync(key, value)

	def _dispatch_or_defer_sync(self, key: str, value):
		with self._sync_lock:
			if not self._frontend_ready or self._window is None:
				self._pending_sync[key] = value
				return

		self.dispatch_sync_requested.emit(key, value)

	@Slot(result="QVariant")
	def init(self):
		return dict(self.main.values)

	@Slot()
	def frontendReady(self):
		if self._frontend_ready:
			return

		self._frontend_ready = True

		with self._sync_lock:
			pending_sync = tuple(self._pending_sync.items())
			self._pending_sync.clear()

		for key, value in pending_sync:
			self.dispatch_sync_requested.emit(key, value)

		if not self._setup_fired:
			self._setup_fired = True
			self.main.events.windowReady.set()

	@Slot(str, "QVariant")
	def syncValue(self, key: str, value):
		if key in self.WINDOW_SIZE_KEYS:
			width, height = self.main.sync_window_size(
				value if key == "system_window_width" else self.main.values.get("system_window_width"),
				value if key == "system_window_height" else self.main.values.get("system_window_height"),
				False,
			)
			self.resize_window_requested.emit(width, height)
			self._dispatch_or_defer_sync("system_window_width", width)
			self._dispatch_or_defer_sync("system_window_height", height)
			return

		self.main.syncValue(key, value)

	@Slot("QVariantMap")
	def syncValues(self, values):
		width = values.get("system_window_width", self.main.values.get("system_window_width"))
		height = values.get("system_window_height", self.main.values.get("system_window_height"))
		has_window_size_update = any(key in self.WINDOW_SIZE_KEYS for key in values)

		for key, value in values.items():
			if key in self.WINDOW_SIZE_KEYS:
				continue
			self.main.syncValue(key, value)

		if has_window_size_update:
			resolved_width, resolved_height = self.main.sync_window_size(width, height, False)
			self.resize_window_requested.emit(resolved_width, resolved_height)
			self._dispatch_or_defer_sync("system_window_width", resolved_width)
			self._dispatch_or_defer_sync("system_window_height", resolved_height)

	@Slot(bool)
	def pin(self, state: bool):
		self.main.pin(state)

	@Slot()
	def minimize(self):
		self.minimize_requested.emit()

	@Slot()
	def destroy(self):
		self.close_requested.emit()

	@Slot()
	def startWindowDrag(self):
		self.start_drag_requested.emit()

	@Slot(str)
	def startWindowResize(self, edge_name: str):
		self.start_resize_requested.emit(edge_name)

	@Slot()
	def toggleMaximize(self):
		self.toggle_maximize_requested.emit()

	@Slot()
	def showWindowMenu(self):
		self.show_window_menu_requested.emit()

	@Slot(str)
	def openExternal(self, url: str):
		open_url(url)

	@Slot(str, result=str)
	def resolveResource(self, value: str):
		resolved = self.main.resolve_resource_url(value)
		return "" if resolved is None else str(resolved)

	@Slot(str, "QVariant")
	def _dispatch_sync_value(self, key: str, value):
		if self._window is None:
			with self._sync_lock:
				self._pending_sync[key] = value
			return

		if key == "system_title":
			self._window.setWindowTitle(str(value or self._title))
		if key in {"system_theme", "system_theme_resolved"}:
			self._window._apply_window_background()

		script = f"window.syncValue({json.dumps(key, ensure_ascii=False)}, {json.dumps(value, ensure_ascii=False)}, false)"
		self._window.page.runJavaScript(script)

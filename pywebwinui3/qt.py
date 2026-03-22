from __future__ import annotations

import ctypes
import json
import logging
import os
import sys
import threading
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QColor, QCursor, QDesktopServices, QIcon, QKeySequence, QShortcut
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
import win32api
import win32con
import win32gui

logger = logging.getLogger("pywebwinui3.qt")

class MARGINS(ctypes.Structure):
	_fields_ = [
		("cxLeftWidth", ctypes.c_int),
		("cxRightWidth", ctypes.c_int),
		("cyTopHeight", ctypes.c_int),
		("cyBottomHeight", ctypes.c_int),
	]

def _read_resize_border_thickness() -> int:
	return max(
		8,
		win32api.GetSystemMetrics(win32con.SM_CXSIZEFRAME)
		+ win32api.GetSystemMetrics(getattr(win32con, "SM_CXPADDEDBORDER", 92)),
	)

class ExternalAwarePage(QWebEnginePage):
	def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
		if (
			is_main_frame
			and navigation_type == QWebEnginePage.NavigationTypeLinkClicked
			and url.scheme() not in {"about", "data", "file", "qrc"}
		):
			QDesktopServices.openUrl(url)
			return False
		return super().acceptNavigationRequest(url, navigation_type, is_main_frame)

	def createWindow(self, _):
		page = QWebEnginePage(self.profile(), self)

		def open_and_cleanup(url):
			QDesktopServices.openUrl(url)
			page.deleteLater()

		page.urlChanged.connect(open_and_cleanup)
		return page


class FramelessWindow(QMainWindow):
	closed = Signal()
	page_loaded = Signal(bool)

	EDGE_MAP = {
		"left": (Qt.LeftEdge, win32con.HTLEFT),
		"right": (Qt.RightEdge, win32con.HTRIGHT),
		"top": (Qt.TopEdge, win32con.HTTOP),
		"bottom": (Qt.BottomEdge, win32con.HTBOTTOM),
		"top-left": (Qt.TopEdge | Qt.LeftEdge, win32con.HTTOPLEFT),
		"top-right": (Qt.TopEdge | Qt.RightEdge, win32con.HTTOPRIGHT),
		"bottom-left": (Qt.BottomEdge | Qt.LeftEdge, win32con.HTBOTTOMLEFT),
		"bottom-right": (Qt.BottomEdge | Qt.RightEdge, win32con.HTBOTTOMRIGHT),
	}
	CURSOR_MAP = {
		"left": Qt.SizeHorCursor,
		"right": Qt.SizeHorCursor,
		"top": Qt.SizeVerCursor,
		"bottom": Qt.SizeVerCursor,
		"top-left": Qt.SizeFDiagCursor,
		"bottom-right": Qt.SizeFDiagCursor,
		"top-right": Qt.SizeBDiagCursor,
		"bottom-left": Qt.SizeBDiagCursor,
	}

	def __init__(self, api, page_path: Path, title: str, icon_path: Path | None, debug: bool = False):
		super().__init__()
		self.api = api
		self.page_path = page_path
		self._native_frame_ready = False
		self._resize_edge_name: str | None = None
		self._resize_origin: QPoint | None = None
		self._resize_geometry: QRect | None = None
		self._pending_resize_geometry: QRect | None = None
		self._resize_commit_scheduled = False
		self._active_resize_cursor = None
		self._resize_border = _read_resize_border_thickness()
		self._debug_tools_view: QWebEngineView | None = None
		self._debug_tools_page: QWebEnginePage | None = None

		self.setWindowFlag(Qt.FramelessWindowHint, True)
		self.setWindowTitle(title)
		minimum_width, minimum_height = self.api._main.get_window_min_size_values()
		self.setMinimumSize(minimum_width, minimum_height)
		initial_width, initial_height = self.api._main.get_window_size_values()
		self.resize(initial_width, initial_height)
		self.setMouseTracking(True)

		if icon_path and icon_path.exists():
			self.setWindowIcon(QIcon(str(icon_path)))

		self.view = QWebEngineView(self)
		self.page = ExternalAwarePage(self.view)
		self._apply_window_background()

		settings = self.page.settings()
		settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
		settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
		settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
		if debug:
			developer_extras = getattr(QWebEngineSettings, "DeveloperExtrasEnabled", None)
			if developer_extras is None and hasattr(QWebEngineSettings, "WebAttribute"):
				developer_extras = getattr(QWebEngineSettings.WebAttribute, "DeveloperExtrasEnabled", None)
			if developer_extras is not None:
				settings.setAttribute(developer_extras, True)

		self.channel = QWebChannel(self.page)
		self.channel.registerObject("backend", api)
		self.page.setWebChannel(self.channel)

		self.view.setPage(self.page)
		self.setCentralWidget(self.view)
		self.view.setMouseTracking(True)
		self.page.loadFinished.connect(self._handle_load_finished)
		QApplication.instance().installEventFilter(self)
		self._sync_view_geometry()

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
		self._sync_view_geometry()
		self.view.update()
		self.api.sync_window_size_from_window(self.width(), self.height())

	def closeEvent(self, event):
		app = QApplication.instance()
		if app is not None:
			app.removeEventFilter(self)
		self._set_resize_cursor(None)
		if self._debug_tools_view is not None:
			self._debug_tools_view.close()
		self.closed.emit()
		super().closeEvent(event)

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

		if hasattr(win32gui, "GetClassLong") and hasattr(win32gui, "SetClassLong"):
			class_style = win32gui.GetClassLong(hwnd, win32con.GCL_STYLE)
			win32gui.SetClassLong(hwnd, win32con.GCL_STYLE, class_style | getattr(win32con, "CS_DROPSHADOW", 0x00020000))

		policy = ctypes.c_int(2)
		ctypes.windll.dwmapi.DwmSetWindowAttribute(
			hwnd,
			3,
			ctypes.byref(policy),
			ctypes.sizeof(policy),
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
		self._native_frame_ready = True

	def _refresh_resize_border(self):
		self._resize_border = _read_resize_border_thickness()

	def _resolved_theme(self) -> str:
		values = self.api._main.values
		theme = values.get("system_theme") or "system"
		if theme == "system":
			theme = values.get("system_theme_resolved") or "dark"
		return theme if theme in {"light", "dark"} else "dark"

	def _background_color(self) -> QColor:
		return QColor("#f3f3f3") if self._resolved_theme() == "light" else QColor("#202020")

	def _apply_window_background(self):
		color = self._background_color()
		self.page.setBackgroundColor(color)
		self.setStyleSheet(f"background-color: {color.name()};")
		if hasattr(self, "view"):
			self.view.setStyleSheet(f"background-color: {color.name()};")

	def _handle_load_finished(self, _ok: bool):
		self._apply_window_background()
		self.page_loaded.emit(_ok)

	def _sync_view_geometry(self):
		rect = self.contentsRect()
		if self.view.geometry() != rect:
			self.view.setGeometry(rect)
		self.view.updateGeometry()

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

	def _edge_from_pos(self, pos: QPoint, size) -> str | None:
		if self.isMaximized():
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
		self.grabMouse()

	def _apply_resize(self, global_pos: QPoint):
		if self._resize_edge_name is None or self._resize_origin is None or self._resize_geometry is None:
			return

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

		self._pending_resize_geometry = geometry
		if self._resize_commit_scheduled:
			return

		self._resize_commit_scheduled = True
		QTimer.singleShot(0, self._commit_pending_resize)

	def _commit_pending_resize(self):
		self._resize_commit_scheduled = False
		geometry = self._pending_resize_geometry
		self._pending_resize_geometry = None
		if geometry is None or self.geometry() == geometry:
			return

		self.setGeometry(geometry)

	def _end_resize(self):
		if self._resize_edge_name is None:
			return

		self._commit_pending_resize()

		self._resize_edge_name = None
		self._resize_origin = None
		self._resize_geometry = None
		self.releaseMouse()
		self._set_resize_cursor(None)

	def eventFilter(self, watched, event):
		if event.type() not in {
			QEvent.Type.MouseButtonPress,
			QEvent.Type.MouseButtonRelease,
			QEvent.Type.MouseMove,
		}:
			return super().eventFilter(watched, event)

		if not hasattr(event, "globalPosition"):
			return super().eventFilter(watched, event)

		if self._resize_edge_name is None and not self._belongs_to_window(watched):
			return super().eventFilter(watched, event)

		global_pos = event.globalPosition().toPoint()
		local_pos = self.mapFromGlobal(global_pos)

		if self._resize_edge_name is None and not self.rect().contains(local_pos):
			self._set_resize_cursor(None)
			return super().eventFilter(watched, event)

		edge_name = self._edge_from_pos(local_pos, self.size())

		if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.LeftButton and edge_name:
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
		win32gui.ReleaseCapture()
		win32api.SendMessage(self._hwnd(), win32con.WM_NCLBUTTONDOWN, win32con.HTCAPTION, 0)

	@Slot(str)
	def start_window_resize(self, edge_name: str):
		if edge_name not in self.EDGE_MAP:
			return

		self._begin_resize(edge_name, QCursor.pos())

	@Slot()
	def toggle_maximize(self):
		if self.isMaximized():
			self.showNormal()
			return
		self.showMaximized()

	@Slot(int, int)
	def apply_window_size(self, width: int, height: int):
		width = max(self.minimumWidth(), int(width))
		height = max(self.minimumHeight(), int(height))

		if self.isMaximized():
			self.showNormal()

		if self.width() == width and self.height() == height:
			return

		self.resize(width, height)

	def apply_minimum_window_size(self, width: int, height: int):
		width = max(1, int(width))
		height = max(1, int(height))

		if self.minimumWidth() == width and self.minimumHeight() == height:
			return

		self.setMinimumSize(width, height)
		if not self.isMaximized():
			self.resize(max(self.width(), width), max(self.height(), height))

class WebviewAPI(QObject):
	WINDOW_SIZE_KEYS = frozenset({"system_window_width", "system_window_height"})

	flush_sync_requested = Signal()
	close_requested = Signal()
	minimize_requested = Signal()
	set_on_top_requested = Signal(bool)
	resize_window_requested = Signal(int, int)
	start_drag_requested = Signal()
	start_resize_requested = Signal(str)
	toggle_maximize_requested = Signal()

	def __init__(self, main_window, title: str, icon: str | None):
		super().__init__()
		self._main = main_window
		self._title = title
		self._icon = icon

		self._app = None
		self._owns_app = False
		self._window = None
		self._frontend_ready = False
		self._page_loaded = False
		self._window_shown = False
		self._setup_fired = False
		self._flush_scheduled = False
		self._sync_lock = threading.Lock()
		self._pending_sync: dict[str, object] = {}
		self._debug_mode = False

		self.flush_sync_requested.connect(self._flush_pending_sync, Qt.ConnectionType.QueuedConnection)

	def ensure_runtime(self, debug: bool = False):
		if self._window is not None:
			return

		self._debug_mode = debug
		app = QApplication.instance()
		if app is None:
			QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
			app = QApplication(sys.argv)
			self._owns_app = True

		self._app = app

		icon_path = self._main.resolve_path(self._icon)
		page_override = os.environ.get("PYWEBWINUI3_PAGE_OVERRIDE")
		page_path = Path(page_override).resolve() if page_override else self._main.packagePath / "index.html"
		title = self._main.values.get("system_title") or self._title

		self._window = FramelessWindow(self, page_path, title, icon_path, debug=debug)
		self._window.closed.connect(self._main.events.closed.set)
		self._window.page_loaded.connect(self._on_page_loaded)
		self.close_requested.connect(self._window.close_window)
		self.minimize_requested.connect(self._window.minimize)
		self.set_on_top_requested.connect(self._window.set_on_top)
		self.resize_window_requested.connect(self._window.apply_window_size)
		self.start_drag_requested.connect(self._window.start_window_drag)
		self.start_resize_requested.connect(self._window.start_window_resize)
		self.toggle_maximize_requested.connect(self._window.toggle_maximize)

		self._main.sync_window_size(self._window.width(), self._window.height(), sync=False)

		if self._main.values.get("system_pin"):
			self._window.set_on_top(True)

		if self._debug_mode and not self._window_shown:
			self._window.show()
			self._window_shown = True

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
			width, height = self._main.sync_window_size(
				value if key == "system_window_width" else self._main.values.get("system_window_width"),
				value if key == "system_window_height" else self._main.values.get("system_window_height"),
				False,
			)

			if self._window is not None:
				self.resize_window_requested.emit(width, height)

			self._queue_sync_patch(
				{
					"system_window_width": width,
					"system_window_height": height,
				}
			)
			return

		self._queue_sync_patch({key: value})

	def _queue_sync_patch(self, patch: dict[str, object]):
		if not patch:
			return

		with self._sync_lock:
			self._pending_sync.update(patch)
			if not self._frontend_ready or self._window is None:
				return
			if self._flush_scheduled:
				return
			self._flush_scheduled = True

		self.flush_sync_requested.emit()

	def sync_window_size_from_window(self, width: int, height: int):
		width, height = self._main.sync_window_size(width, height, False)
		self._queue_sync_patch(
			{
				"system_window_width": width,
				"system_window_height": height,
			}
		)

	@Slot(result="QVariant")
	def init(self):
		return dict(self._main.values)

	@Slot()
	def frontendReady(self):
		if self._frontend_ready:
			return

		self._frontend_ready = True
		self._maybe_show_window()

		with self._sync_lock:
			should_flush = bool(self._pending_sync)
			if should_flush:
				self._flush_scheduled = True

		if should_flush:
			self.flush_sync_requested.emit()

		if not self._setup_fired:
			self._setup_fired = True
			self._main.events._pywebviewready.set()

	@Slot(bool)
	def _on_page_loaded(self, ok: bool):
		self._page_loaded = ok
		self._maybe_show_window()

	def _maybe_show_window(self):
		if self._window is None or self._window_shown:
			return
		if self._debug_mode:
			self._window.show()
			self._window_shown = True
			return
		if not self._page_loaded or not self._frontend_ready:
			return

		self._window.show()
		self._window_shown = True

	@Slot(str, "QVariant")
	def syncValue(self, key: str, value):
		if key in self.WINDOW_SIZE_KEYS:
			width, height = self._main.sync_window_size(
				value if key == "system_window_width" else self._main.values.get("system_window_width"),
				value if key == "system_window_height" else self._main.values.get("system_window_height"),
				False,
			)
			self.resize_window_requested.emit(width, height)
			self._queue_sync_patch(
				{
					"system_window_width": width,
					"system_window_height": height,
				}
			)
			return

		self._main.syncValue(key, value)

	@Slot("QVariantMap")
	def syncValues(self, values):
		width = values.get("system_window_width", self._main.values.get("system_window_width"))
		height = values.get("system_window_height", self._main.values.get("system_window_height"))
		has_window_size_update = any(key in self.WINDOW_SIZE_KEYS for key in values)

		for key, value in values.items():
			if key in self.WINDOW_SIZE_KEYS:
				continue
			self._main.syncValue(key, value)

		if has_window_size_update:
			resolved_width, resolved_height = self._main.sync_window_size(width, height, False)
			self.resize_window_requested.emit(resolved_width, resolved_height)
			self._queue_sync_patch(
				{
					"system_window_width": resolved_width,
					"system_window_height": resolved_height,
				}
			)

	@Slot(bool)
	def pin(self, state: bool):
		self._main.pin(state)

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

	@Slot(str)
	def openExternal(self, url: str):
		QDesktopServices.openUrl(QUrl(url))

	@Slot(str, result=str)
	def resolveResource(self, value: str):
		resolved = self._main.resolve_resource_url(value)
		return "" if resolved is None else str(resolved)

	@Slot()
	def _flush_pending_sync(self):
		if self._window is None:
			return

		with self._sync_lock:
			patch = dict(self._pending_sync)
			self._pending_sync.clear()
			self._flush_scheduled = False

		if not patch:
			return

		if "system_title" in patch:
			self._window.setWindowTitle(str(patch["system_title"] or self._title))
		if "system_theme" in patch or "system_theme_resolved" in patch:
			self._window._apply_window_background()

		script = f"window.applyBackendPatch({json.dumps(patch, ensure_ascii=False)})"
		self._window.page.runJavaScript(script)

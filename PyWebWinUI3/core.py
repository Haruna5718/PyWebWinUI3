from __future__ import annotations

import webview
import threading
import mimetypes
import json
import winreg
import win32con
import win32gui
import win32api
import xml.etree.ElementTree
from pathlib import Path
import logging

logger = logging.getLogger("pywebwinui3")
logger.setLevel(logging.DEBUG)

def getSystemAccentColor():
	with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent") as key:
		p, _ = winreg.QueryValueEx(key, "AccentPalette")
	return [f"#{p[i]:02x}{p[i+1]:02x}{p[i+2]:02x}" for i in range(0,len(p),4)]

def systemMessageListener(callback):
	def eventHandler(hwnd, msg, wparam, lparam):
		if msg == win32con.WM_SETTINGCHANGE:
			callback(getSystemAccentColor())
		return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
	wc = win32gui.WNDCLASS()
	hinst = win32api.GetModuleHandle(None)
	wc.lpszClassName = "SystemMessageListener"
	wc.lpfnWndProc = eventHandler
	classAtom = win32gui.RegisterClass(wc)
	win32gui.CreateWindow(classAtom, wc.lpszClassName, 0, 0, 0, 0, 0, 0, 0, hinst, None)
	threading.Thread(target=win32gui.PumpMessages, daemon=True).start()
	logger.debug("System message listener started")

def XamlToJson(Element: xml.etree.ElementTree.Element):
	return {
		"tag":Element.tag,
		"attr":Element.attrib,
		"text":(Element.text or "").strip(),
		"child":list(map(XamlToJson,Element))
	}

def loadPage(FilePath: str|Path):
	try:
		return XamlToJson(xml.etree.ElementTree.parse(FilePath).getroot())
	except FileNotFoundError:
		return logger.error(f"Failed to load page: {FilePath} not found")
	except xml.etree.ElementTree.ParseError as e:
		return logger.error(f"Failed to load page {FilePath}: {e}")
	
class Notice:
	Information = 0
	Attention = 0
	Success = 1
	Warning = 2
	Error = 3
	Critical = 3

class MainWindow:
	def __init__(self, title, debug=False, url:str|Path=None, log:str|Path=None):
		self.url = url or (Path(__file__).parent/"web"/"index.html").absolute()
		self._window: webview.Window = None
		self.debug = debug
		self.values = {
			"system.title": title,
			"system.theme": "system",
			"system.color": getSystemAccentColor(),
			"system.pages": None,
			"system.settings": None,
			"system.nofication": []
		}
		self.events:dict[str,any] = {}

		logging.basicConfig(
			level=logging.DEBUG,
			format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
			datefmt="%H:%M:%S",
			handlers=[
				*([logging.FileHandler(log, mode="w", encoding="utf-8")] if log else []),
				logging.StreamHandler()
			]
		)

	def notice(self, level:int, title:str, description:str):
		self.setValue('system.nofication', [*self.values["system.nofication"],[level,title,description]])

	def setup(self):
		systemMessageListener(self.themeChanged)
	
	def init(self):
		return {
			**self.values,
			"system.isOnTop": self._window.on_top,
		}
	
	def onValueChange(self, valueName):
		def decorator(func):
			self.events.setdefault("setValue", {}).setdefault(valueName, []).append(func)
			return func
		return decorator

	def setValue(self, key, value, sync=True):
		self.values[key]=value
		if sync and self._window:
			threading.Thread(target=lambda: self._window.evaluate_js(f"window.setValue('{key}', {json.dumps(value)}, false)"), daemon=True).start()
			logger.debug(f"Value synced: {key}")
		for event in self.events.get("setValue",{}).get(key,[]):
			event(key,value)

	def themeChanged(self, color):
		if color != self.values['system.color']:
			logger.debug("Accent color change detected")
			self.setValue('system.color', color)

	def ontop(self, State:bool):
		threading.Thread(target=lambda: setattr(self._window, "on_top", State), daemon=True).start()
		return self.setValue('system.isOnTop', self._window.on_top)
	
	def addSettings(self, pageData:dict[str, str|dict|list]):
		if not pageData:
			return logger.error("Invalid page data provided")
		logger.debug(f"Page added: {pageData.get('attr').get('path')}")
		return self.setValue('system.settings', pageData)

	def addPage(self, pageData:dict[str, str|dict|list]):
		if not pageData:
			return logger.error("Invalid page data provided")
		logger.debug(f"Page added: {pageData.get('attr').get('path')}")
		return self.setValue('system.pages', {
			**(self.values["system.pages"] or {}),
			pageData.get("attr").get("path"):pageData
		})

	def start(self, page=None):
		logging.getLogger("pywebview").setLevel(logging.DEBUG)
		self._window = webview.create_window(self.values["system.title"], f"{self.url}#{page}", js_api=self, background_color="#202020", frameless=True, easy_drag=False, draggable=True, text_select=True, width=900, height=600)
		logger.debug("window created")
		mimetypes.add_type("application/javascript", ".js")
		self.destroy = self._window.destroy
		self.minimize = self._window.minimize
		webview.start(self.setup,debug=self.debug)
import webview
import threading
import mimetypes
import json
import xml.etree.ElementTree
from pathlib import Path
import logging
import fnmatch
import win32con
import base64

logger = logging.getLogger("pywebwinui3")

def getSystemAccentColor():
	import winreg
	with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent") as key:
		p, _ = winreg.QueryValueEx(key, "AccentPalette")
	return [f"#{p[i]:02x}{p[i+1]:02x}{p[i+2]:02x}" for i in range(0,len(p),4)]

def systemMessageListener(callback):
	import win32gui
	import win32api
	wc = win32gui.WNDCLASS()
	hinst = win32api.GetModuleHandle(None)
	wc.lpszClassName = "SystemMessageListener"
	def eventHandler(hwnd, msg, wparam, lparam):
		callback(hwnd, msg, wparam, lparam)
		return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
	wc.lpfnWndProc = eventHandler
	classAtom = win32gui.RegisterClass(wc)
	win32gui.CreateWindow(classAtom, wc.lpszClassName, 0, 0, 0, 0, 0, 0, 0, hinst, None)
	logger.debug("System message listener started")
	win32gui.PumpMessages()

def XamlToJson(element: xml.etree.ElementTree.Element):
	return {
		"tag":element.tag,
		"attr":element.attrib,
		"text":(element.text or "").strip(),
		"child":[XamlToJson(e) for e in element]
	}

def loadPage(filePath: str|Path):
	try:
		return XamlToJson(xml.etree.ElementTree.parse(filePath).getroot())
	except FileNotFoundError:
		return logger.error(f"Failed to load page: {filePath} not found")
	except xml.etree.ElementTree.ParseError as e:
		return logger.error(f"Failed to load page {filePath}: {e}")
	
class Notice:
	Accent = 0
	Information = 0
	Attention = 0
	Green = 1
	Success = 1
	Online = 1
	Yellow = 2
	Warning = 2
	Caution = 2
	Red = 3
	Error = 3
	Critical = 3
	Gray = 4
	Offline = 4

class Color:
	class Accent:
		Default = "var(--AccentFillColorDefaultBrush)"
		Secondary = "var(--AccentFillColorSecondaryBrush)"
		Tertiary = "var(--AccentFillColorTertiaryBrush)"
		Background = "var(--AccentFillColorBackgroundBrush)"
	class Text:
		Primary = "var(--TextFillColorPrimaryBrush)"
		Secondary = "var(--TextFillColorSecondaryBrush)"
		Tertiary = "var(--TextFillColorTertiaryBrush)"
		Disabled = "var(--TextFillColorDisabledBrush)"
		class OnAccent:
			Primary = "var(--TextOnAccentFillColorPrimaryBrush)"
			Secondary = "var(--TextOnAccentFillColorSecondaryBrush)"
			Disabled = "var(--TextOnAccentFillColorDisabledBrush)"
			Selected = "var(--TextOnAccentFillColorSelectedTextBrush)"
	class Signal:
		Success = "var(--SystemFillColorSuccessBrush)"
		Caution = "var(--SystemFillColorCautionBrush)"
		Critical = "var(--SystemFillColorCriticalBrush)"
		Attention = "var(--AccentFillColorSecondaryBrush)" # Accent.Secondary
		Neutral = "var(--TextFillColorTertiaryBrush)" # Text.Tertiary
		class Background:
			Success = "var(--SystemFillColorSuccessBackgroundBrush)"
			Caution = "var(--SystemFillColorCautionBackgroundBrush)"
			Critical = "var(--SystemFillColorCriticalBackgroundBrush)"
			Attention = "var(--AccentFillColorBackgroundBrush)" # Accent.Background
			Neutral = "var(--AccentFillColorBackgroundBrush)" # Accent.Background

class MainWindow:
	def __init__(self, title, url:str|Path=None):
		self.url = str(url or (Path(__file__).parent/"web"/"index.html").absolute())
		self.api = WebviewAPI(self)
		self.events:dict[str, list|function] = {}
		self.values = {
			"system.title": title,
			"system.icon": None,
			"system.theme": "system",
			"system.color": getSystemAccentColor(),
			"system.pages": None,
			"system.settings": None,
			"system.nofication": []
		}

	def onValueChange(self, valueName):
		def decorator(func):
			self.events.setdefault("setValue", {}).setdefault(valueName, []).append(func)
			return func
		return decorator
	
	def onSetup(self):
		def decorator(func):
			self.events.setdefault("setup", []).append(func)
			return func
		return decorator
	
	def onExit(self):
		def decorator(func):
			if self.api._window:
				self.api._window.events.closed += func
			else:
				self.events.setdefault("exit", []).append(func)
			return func
		return decorator

	def notice(self, level:int, title:str, description:str):
		self.setValue('system.nofication', [*self.values["system.nofication"],[level,title,description]])

	def _setup(self):
		threading.Thread(target=systemMessageListener, args=(self._systemMessageHandler,), daemon=True).start()
		for _ in range(len(self.events.get("exit", []))):
			self.api._window.events.closed += self.events.get("exit").pop()
		for event in self.events.get("setup",[]):
			threading.Thread(target=event, daemon=True).start()
		for _ in range(len(self.events.get("setupImage", []))):
			threading.Thread(target=self.setupImage, args=(self.events.get("setupImage").pop(),), daemon=True).start()

	def init(self):
		return {
			**self.values,
			"system.isOnTop": self.api._window.on_top,
		}
	
	def getValue(self, key, default=None):
		return self.values.get(key, default)

	def setValue(self, key, value, sync=True, broadcast=True):
		beforevalue = self.values.get(key,None)
		self.values[key]=value
		if self.api._window:
			if sync:
				self.api._window.evaluate_js(f"window.setValue('{key}', {json.dumps(value)}, false)")
			if broadcast:
				for pattern, callbacks in list(self.events.get("setValue",{}).items()):
					if fnmatch.fnmatch(key, pattern):
						for callback in callbacks:
							threading.Thread(target=callback, args=(key, beforevalue, value,), daemon=True).start()
		return value

	def _systemMessageHandler(self, hwnd, msg, wparam, lparam):
		if msg == win32con.WM_SETTINGCHANGE:
			if self.getValue('system.color')!=(color:=getSystemAccentColor()):
				self.setValue('system.color', color)
				logger.debug("Accent color change detected")
	
	def setupImage(self, path:str):
		self.api._window.evaluate_js(f"window.imageCache[{json.dumps(path)}]={json.dumps(self.api.getImage(path))}")

	def _imagePreload(self, node: dict, refPath:Path):
		if "source" in node["attr"]:
			sourcePath = Path(node["attr"]["source"])
			node["attr"]["source"] = str((sourcePath if sourcePath.is_absolute() else refPath/sourcePath).resolve())
			if self.api._window:
				self.setupImage(node["attr"]["source"])
			else:
				self.events.setdefault("setupImage", []).append(node["attr"]["source"])
		node["child"] = [self._imagePreload(c, refPath) for c in node["child"]]
		return node

	def addSettings(self, pageFile:str|Path=None, pageData:dict[str, str|dict|list]=None, imagePreload=True):
		if pageFile and not pageData:
			pageData = loadPage(pageFile)
		if imagePreload:
			pageData = self._imagePreload(pageData,Path(pageFile).parent)
		if not pageData:
			return logger.error("Invalid page data provided")
		logger.debug(f"Page added: {pageData.get('attr').get('path')}")
		return self.setValue('system.settings', pageData)

	def addPage(self, pageFile:str|Path=None, pageData:dict[str, str|dict|list]=None, imagePreload=True):
		if pageFile and not pageData:
			pageData = loadPage(pageFile)
		if imagePreload:
			pageData = self._imagePreload(pageData,Path(pageFile).parent)
		if not pageData:
			return logger.error("Invalid page data provided")
		logger.debug(f"Page added: {pageData.get('attr').get('path')}")
		return self.setValue('system.pages', {
			**(self.values["system.pages"] or {}),
			pageData.get("attr").get("path"):pageData
		})

	def start(self, page=None, debug=False):
		self.api.initWindow(webview.create_window(self.values["system.title"], f"{self.url}#{page}", js_api=self.api, background_color="#202020", frameless=True, easy_drag=False, draggable=True, text_select=True, width=900, height=600))
		logger.debug("Window created")
		mimetypes.add_type("application/javascript", ".js")
		webview.start(self._setup,debug=debug)

class WebviewAPI:
	def __init__(self, mainClass:MainWindow):
		self._window: webview.Window = None
		self.init = mainClass.init
		self.setValue = mainClass.setValue

	def initWindow(self, window):
		self._window = window
		self.destroy = self._window.destroy
		self.minimize = self._window.minimize

	def setTop(self, State:bool):
		threading.Thread(target=lambda: setattr(self._window, "on_top", State), daemon=True).start()
		return self.setValue('system.isOnTop', self._window.on_top)
	
	def getImage(self, path: str|Path) -> str:
		path = Path(path)
		if not path.exists() or not path.is_file():
			return ""
		with open(path, "rb") as f:
			image = f"data:image/{Path(path).suffix.lstrip('.')};base64,{base64.b64encode(f.read()).decode('utf-8')}"
			logger.debug(f"image loaded: {path}")
			return image
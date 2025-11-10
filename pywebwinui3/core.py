import webview
import threading
import json
import xml.etree.ElementTree
from pathlib import Path
import logging
import win32con
import bottle
import inspect

from .event import PathEvent, EventContainer

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
	
class MainWindow:
	def __init__(self, title):
		self.running = False
		self.api = WebviewAPI(self)
		self.events = EventContainer()
		self.events.setValue = PathEvent()
		self.server = bottle.Bottle()
		self.basePath = Path(inspect.currentframe().f_back.f_code.co_filename).parent.resolve()
		self.values = {
			"system.title": title,
			"system.icon": None,
			"system.theme": "system",
			"system.color": getSystemAccentColor(),
			"system.pages": None,
			"system.settings": None,
			"system.nofication": []
		}
		self.api.initWindow(webview.create_window(
			self.values["system.title"],
			self.server,
			js_api=self.api,
			background_color="#202020",
			frameless=True,
			easy_drag=False,
			draggable=True,
			text_select=True,
			width=900,
			height=600
		))
		logger.debug("Window created")

	def onValueChange(self, valueName):
		def decorator(func):
			self.events.setValue.append(valueName,func)
			return func
		return decorator
	
	def onSetup(self):
		def decorator(func):
			self.api._window.events._pywebviewready += func
			return func
		return decorator
	
	def onExit(self):
		def decorator(func):
			self.api._window.events.closed += func
			return func
		return decorator

	def notice(self, level:int, title:str, description:str):
		self.setValue('system.nofication', [*self.values["system.nofication"],[level,title,description]])

	def _setup(self):
		threading.Thread(target=systemMessageListener, args=(self._systemMessageHandler,), daemon=True).start()

	def init(self):
		self.running = True
		return {
			**self.values,
			"system.isOnTop": self.api._window.on_top,
		}
	
	def getValue(self, key, default=None):
		return self.values.get(key, default)

	def setValue(self, key, value, sync=True, broadcast=True):
		beforevalue = self.values.get(key,None)
		self.values[key]=value
		if self.running:
			if sync:
				self.api._window.evaluate_js(f"window.setValue('{key}', {json.dumps(value)}, false)")
			if broadcast:
				self.events.setValue.set(key,key,beforevalue,value)
		return value

	def _systemMessageHandler(self, hwnd, msg, wparam, lparam):
		if msg == win32con.WM_SETTINGCHANGE:
			if self.getValue('system.color')!=(color:=getSystemAccentColor()):
				self.setValue('system.color', color)
				logger.debug("Accent color change detected")
	
	def setupImage(self, path:str):
		logger.debug(f"Image preload: {path}")
		self.api._window.evaluate_js(f"fetch('/file/{path}')")
		pass

	def _imagePreload(self, node: dict):
		if "source" in node["attr"]:
			self.api._window.events._pywebviewready += lambda: self.setupImage(node['attr']['source'])
		[self._imagePreload(i) for i in node["child"]]

	def addSettings(self, pageFile:str|Path=None, pageData:dict[str, str|dict|list]=None,imagePreload=True):
		if pageFile and not pageData:
			pageData = loadPage(pageFile)
		if not pageData:
			return logger.error("Invalid page data provided")
		if imagePreload:
			self._imagePreload(pageData)
		logger.debug(f"Page added: {pageData.get('attr').get('path')}")
		return self.setValue('system.settings', pageData)

	def addPage(self, pageFile:str|Path=None, pageData:dict[str, str|dict|list]=None,imagePreload=True):
		if pageFile and not pageData:
			pageData = loadPage(pageFile)
		if not pageData:
			return logger.error("Invalid page data provided")
		if imagePreload:
			self._imagePreload(pageData)
		logger.debug(f"Page added: {pageData.get('attr').get('path')}")
		return self.setValue('system.pages', {
			**(self.values["system.pages"] or {}),
			pageData.get("attr").get("path"):pageData
		})

	def start(self, debug=False):
		@self.server.route('/')
		@self.server.route('/PYWEBWINUI3/<filepath:path>')
		def web(filepath=None):
			return bottle.static_file(filepath or "index.html", root=str(Path(__file__).resolve().relative_to(self.basePath).parent/("web/PYWEBWINUI3" if filepath else "web")))
		
		@self.server.route('/<filepath:path>')
		def file(filepath):
			return bottle.static_file(filepath, root=str(self.basePath))
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
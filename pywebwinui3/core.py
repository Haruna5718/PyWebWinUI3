import webview
import json
from pathlib import Path
import logging
import bottle
import inspect
import threading

from .util import AccentColorWatcher, SyncDict, loadPage
from .type import Status

logger = logging.getLogger("pywebwinui3")

class MainWindow:
	def __init__(self, title:str, icon:str=None):
		self.server = bottle.Bottle()
		self.accent = AccentColorWatcher()
		self.api = WebviewAPI(self, title)

		self.values = SyncDict({
			"system_title": title,
			"system_icon": icon,
			"system_theme": "system",
			"system_accent": self.accent.palette,
			"system_pages": None,
			"system_settings": None,
			"system_nofication": [],
			"system_pin": self.api._window.on_top
		})

		self.events = self.api._window.events
		self.events.accentColorChange = self.accent.event
		self.events.valueChange = self.values.event

		self.rootPath = Path(inspect.currentframe().f_back.f_code.co_filename).parent.resolve()
		self.packagePath = Path(__file__).parent.resolve()/"web"

	def onValueChange(self, key):
		def decorator(func):
			self.events.valueChange += (key,func)
			return func
		return decorator
	
	def onAccentColorChange(self):
		def decorator(func):
			self.events.accentColorChange += func
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

	def notice(self, level:Status, title:str, description:str, item:dict=None):
		self.values['system_nofication'] = [*self.values["system_nofication"],[level,title,description,item]]

	def _setup(self):
		self.values.sync = lambda k,v: self.api._window.evaluate_js(f"window.syncValue('{k}',{json.dumps(v)},false)")

	def init(self):
		return self.values
	
	def pin(self, state:bool):
		threading.Thread(target=lambda: setattr(self.api._window, "on_top", state), daemon=True).start()
		return self.values.set('system_pin',state)

	def syncValue(self, key, value):
		return self.values.set(key,value,False)

	def addSettings(self, pageFile:str|Path=None, pageData:dict[str, str|dict|list]=None):
		if pageFile and not pageData:
			pageData = loadPage(pageFile)
		logger.debug(f"Setting page: {pageData['attr']['path']}")
		self.values['system_settings'] = pageData

	def addPage(self, pageFile:str|Path=None, pageData:dict[str, str|dict|list]=None):
		if pageFile and not pageData:
			pageData = loadPage(pageFile)
		logger.debug(f"Page added: {pageData['attr']['path']}")
		self.values['system_pages'] = {
			**(self.values["system_pages"] or {}),
			pageData["attr"]["path"]:pageData
		}
	
	def routeFile(self, filepath="index.html"):
		if (self.packagePath/filepath).is_file():
			return bottle.static_file(filepath, root=self.packagePath)
		if (self.rootPath/filepath).is_file():
			return bottle.static_file(filepath, root=self.rootPath)

	def start(self, debug=False):
		self.server.route('/',callback=self.routeFile)
		self.server.route('/<filepath:path>',callback=self.routeFile)
		
		self.accent.start()

		webview.start(self._setup,debug=debug)

class WebviewAPI:
	def __init__(self, mainClass:MainWindow, title:str):
		self._window = webview.create_window(
			title,
			mainClass.server,
			# "http://localhost:5173/",
			js_api=self,
			background_color="#202020",
			frameless=True,
			easy_drag=False,
			draggable=True,
			text_select=True,
			width=900,
			height=600
		)

		logger.debug("Window created")

		self.destroy = self._window.destroy
		self.minimize = self._window.minimize

		self.pin = mainClass.pin
		self.init = mainClass.init
		self.syncValue = mainClass.syncValue
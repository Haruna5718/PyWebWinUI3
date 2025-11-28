import webview
import json
from pathlib import Path
import logging
import bottle
import inspect
import threading

from .util import AccentColorWatcher, SyncDict, absolutePath, loadPage
from .type import Status

logger = logging.getLogger("pywebwinui3")

	
class MainWindow:
	def __init__(self, title:str, icon:str=None):
		self.server = bottle.Bottle()
		self.accent = AccentColorWatcher()
		self.api = WebviewAPI(self, title, self.server)

		self.values = SyncDict({
			"system_title": title,
			"system_icon": icon,
			"system_theme": "system",
			"system_accent": self.accent.palette,
			"system_pages": None,
			"system_settings": None,
			"system_nofication": [],
			"system_isOnTop": self.api._window.on_top
		})

		self.events = self.api._window.events
		self.events.accentColorChange = self.accent.event
		self.events.valueChange = self.values.event

		self.basePath = Path(inspect.currentframe().f_back.f_code.co_filename).parent.resolve()

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

	def syncValue(self, key, value):
		self.values.__setitem__(key,value,False)

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
	
	def serverRouteRoot(self):
		return bottle.static_file("index.html", root=absolutePath(Path(__file__).parent/("web")))
	
	def serverRouteResource(self,filepath):
		return bottle.static_file(filepath, root=absolutePath(Path(__file__).parent/("web/PYWEBWINUI3")))

	def serverRouteFile(self,filepath):
			return bottle.static_file(filepath, root=str(self.basePath))

	def start(self, debug=False):
		self.server.route('/',callback=self.serverRouteRoot)
		self.server.route('/PYWEBWINUI3/<filepath:path>',callback=self.serverRouteResource)
		self.server.route('/<filepath:path>',callback=self.serverRouteFile)
		
		self.accent.start()
		webview.start(self._setup,debug=debug)

class WebviewAPI:
	def __init__(self, mainClass:MainWindow, title:str, server:bottle.Bottle):
		self._window = webview.create_window(
			title,
			server,
			# "http://localhost:3000/",
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

		self.init = mainClass.init
		self.syncValue = mainClass.syncValue

	def setTop(self, State:bool):
		threading.Thread(target=lambda: setattr(self._window, "on_top", State), daemon=True).start()
		return self.setValue('system.isOnTop', self._window.on_top)
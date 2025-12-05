import xml.etree.ElementTree
from typing import Any, Callable
import threading
import win32con
import win32gui
import win32api
import logging

from .event import PathEvent, Event

logger = logging.getLogger('pywebwinui3.util')

def xamlToJson(element: xml.etree.ElementTree.Element):
	return {
		"tag":element.tag,
		"attr":element.attrib,
		"text":(element.text or "").strip(),
		"child":[xamlToJson(e) for e in element]
	}

def loadPage(filePath: str):
	return xamlToJson(xml.etree.ElementTree.parse(filePath).getroot())

class SyncDict(dict):
    def __init__(self, init:dict=None, event:PathEvent=None, sync:Callable=None):
        super().__init__(init or {})
        self.event = event or PathEvent()
        self.sync = sync

    def _sync(self, key, before, after, sync):
        if sync and self.sync:
            self.sync(key, after)
        self.event.set(key, before, after)

    def __setitem__(self, key:str, value:Any, sync=True):
        before = self.get(key, None)
        super().__setitem__(key, value)
        self._sync(key, before, value, sync)

    def set(self, key:str, value:Any, sync=True):
        self.__setitem__(key, value, sync)
        return value
    
    def append(self, key:str, value:Any, sync=True):
        before = list(self.get(key,[]))
        self.setdefault(key,[]).append(value)
        self._sync(key, before, self.get(key), sync)
        return self[key]
    
    def remove(self, key:str, value:Any, sync=True):
        before = list(self.get(key,[]))
        self.setdefault(key,[]).remove(value)
        self._sync(key, before, self.get(key), sync)
        return self[key]
        
class AccentColorWatcher:
    def __init__(self, event:Event=None):
        self.event = event or Event()
        self.palette = self.getSystemAccentColor()

    @staticmethod
    def getSystemAccentColor():
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent") as key:
            p, _ = winreg.QueryValueEx(key, "AccentPalette")
        return [f"#{p[i]:02x}{p[i+1]:02x}{p[i+2]:02x}" for i in range(0,len(p),4)]
    
    def systemMessageListener(self):
        wc = win32gui.WNDCLASS()
        wc.lpszClassName = "SystemMessageListener"
        wc.lpfnWndProc = self.systemMessageHandler
        win32gui.CreateWindow(win32gui.RegisterClass(wc), wc.lpszClassName, 0, 0, 0, 0, 0, 0, 0, win32api.GetModuleHandle(None), None)
        win32gui.PumpMessages()

    def systemMessageHandler(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_SETTINGCHANGE:
            if self.palette!=(color:=self.getSystemAccentColor()):
                self.palette = color
                self.event.set(self.palette)
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def start(self):
        threading.Thread(target=self.systemMessageListener, daemon=True).start()
        logger.debug("System message listener started")
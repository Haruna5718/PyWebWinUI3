import xml.etree.ElementTree
from typing import Callable
import threading
import win32con
import win32gui
import win32api
import logging
import pathlib

from .event import PathEvent, Event

logger = logging.getLogger('pywebwinui3.util')

def absolutePath(path:str|pathlib.Path=None):
    return str(pathlib.Path(path).resolve()) if path else None

def xamlToJson(element: xml.etree.ElementTree.Element):
	return {
		"tag":element.tag,
		"attr":element.attrib,
		"text":(element.text or "").strip(),
		"child":[xamlToJson(e) for e in element]
	}

def loadPage(filePath: str|pathlib.Path):
	try:
		return xamlToJson(xml.etree.ElementTree.parse(filePath).getroot())
	except FileNotFoundError:
		return logger.error(f"Failed to load page: {filePath} not found")
	except xml.etree.ElementTree.ParseError as e:
		return logger.error(f"Failed to load page {filePath}: {e}")

class SyncDict(dict):
    def __init__(self, init:dict={}, event:PathEvent=None, sync:Callable=None):
        super().__init__(init)
        self.event = event or PathEvent()
        self.sync = sync

    def __setitem__(self, key, value, sync=True):
        if sync and self.sync:
            self.sync(key,value)
        self.event.set(key,self.get(key,None),value)
        super().__setitem__(key, value)

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
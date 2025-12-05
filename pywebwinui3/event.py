import logging
import fnmatch
import threading
import traceback
from typing import Any, Callable

logger = logging.getLogger('pywebwinui3.eventmanager')

class Event:
	def __init__(self) -> None:
		self.items: list[Callable[..., Any]] = []

	def set(self, *args: Any):
		for func in self.items[:]:
			try:
				threading.Thread(target=func, args=(*args,), daemon=True).start()
			except:
				logger.error(traceback.format_exc())

	def __add__(self, item: Callable[..., Any]):
		self.items.append(item)
		return self

	def __sub__(self, item: Callable[..., Any]):
		self.items.remove(item)
		return self

	def __iadd__(self, item: Callable[..., Any]):
		self.items.append(item)
		return self

	def __isub__(self, item: Callable[..., Any]):
		self.items.remove(item)
		return self

	def __len__(self) -> int:
		return len(self.items)
	
class PathEvent:
	def __init__(self) -> None:
		self.items: dict[str,Event] = {}

	def set(self, target:str, *args: Any):
		events = self.items.items()
		for key,event in events:
			if fnmatch.fnmatch(target, key):
				try:
					threading.Thread(target=event.set, args=(target, *args), daemon=True).start()
				except:
					logger.error(traceback.format_exc())

	def __add__(self, item: list):
		self.items.setdefault(item[0], Event()).__iadd__(item[1])
		return self

	def __sub__(self, item: list):
		self.items.setdefault(item[0], Event()).__isub__(item[1])
		return self

	def __iadd__(self, item: list):
		self.items.setdefault(item[0], Event()).__iadd__(item[1])
		return self

	def __isub__(self, item: list):
		self.items.setdefault(item[0], Event()).__isub__(item[1])
		return self

	def __len__(self) -> int:
		return len(self.items)
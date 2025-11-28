import logging
import threading
import fnmatch
from typing import Any, Callable

logger = logging.getLogger('pywebwinui3.eventmanager')

class Event:
	def __init__(self) -> None:
		self.items: list[Callable[..., Any]] = []

	def set(self, *args: Any, **kwargs: Any):
		def execute():
			for func in self.items:
				try:
					func(*args, **kwargs)
				except Exception as e:
					logger.error(e)

		threading.Thread(target=execute,daemon=True).start()

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

	def set(self, target:str, *args: Any, **kwargs: Any):
		def execute():
			for key,event in self.items.items():
				if fnmatch.fnmatch(target, key):
					try:
						event.set(target, *args, **kwargs)
					except Exception as e:
						logger.error(e)

		threading.Thread(target=execute, daemon=True).start()

	def __add__(self, item: list):
		self.items.setdefault(item[0], Event()).__iadd__(item[1])
		return self

	def __sub__(self, item: list):
		self.items.setdefault(item[0], Event()).__isub__(item[1])
		event -= item[1]
		return self

	def __iadd__(self, item: list):
		self.items.setdefault(item[0], Event()).__iadd__(item[1])
		return self

	def __isub__(self, item: list):
		self.items.setdefault(item[0], Event()).__isub__(item[1])
		return self

	def __len__(self) -> int:
		return len(self.items)
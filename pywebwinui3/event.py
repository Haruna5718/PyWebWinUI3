import logging
import threading
import fnmatch
from typing import Any, Callable

logger = logging.getLogger('pywebwinui3.eventmanager')

class EventContainer:
	pass

class Event:
	def __init__(self) -> None:
		self.items: list[Callable[..., Any]] = []
		self.event = threading.Event()

	def set(self, *args: Any, **kwargs: Any):
		def execute():
			for func in self.items:
				try:
					func(*args, **kwargs)
				except Exception as e:
					logger.error(e)

		threading.Thread(target=execute,daemon=True).start()

		self.event.set()

	def is_set(self):
		return self.event.is_set()

	def wait(self, timeout: float | None = None):
		return self.event.wait(timeout)

	def clear(self) -> None:
		return self.event.clear()

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
		self.event = threading.Event()

	def set(self, target:str, *args: Any, **kwargs: Any):
		def execute():
			for key,event in self.items.items():
				if fnmatch.fnmatch(target, key):
					try:
						event.set(*args, **kwargs)
					except Exception as e:
						logger.error(e)

		threading.Thread(target=execute, daemon=True).start()

		self.event.set()

	def is_set(self):
		return self.event.is_set()

	def wait(self, timeout: float | None = None):
		return self.event.wait(timeout)

	def clear(self):
		return self.event.clear()

	def append(self, key, item: Callable[..., Any]):
		self.items.setdefault(key, Event()).__iadd__(item)
		return self

	def remove(self, key, item: Callable[..., Any]):
		self.items.setdefault(key, Event()).__isub__(item)
		event -= item
		return self
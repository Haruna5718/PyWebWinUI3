from __future__ import annotations

import atexit
import fnmatch
import logging
import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

logger = logging.getLogger("pywebwinui3.eventmanager")

_EVENT_WORKERS = max(4, min(32, (os.cpu_count() or 1) * 4))
_EVENT_EXECUTOR = ThreadPoolExecutor(
	max_workers=_EVENT_WORKERS,
	thread_name_prefix="pywebwinui3-event",
)
atexit.register(lambda: _EVENT_EXECUTOR.shutdown(wait=False))


def _call_listener(func: Callable[..., Any], args: tuple[Any, ...]):
	try:
		func(*args)
	except Exception:
		logger.error(traceback.format_exc())


class Event:
	def __init__(self) -> None:
		self.items: list[Callable[..., Any]] = []

	def set(self, *args: Any):
		listeners = tuple(self.items)
		if not listeners:
			return

		for func in listeners:
			try:
				_EVENT_EXECUTOR.submit(_call_listener, func, args)
			except Exception:
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
		self.items: dict[str, Event] = {}

	def set(self, target: str, *args: Any):
		if not self.items:
			return

		for key, event in tuple(self.items.items()):
			if not fnmatch.fnmatch(target, key):
				continue

			try:
				event.set(target, *args)
			except Exception:
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

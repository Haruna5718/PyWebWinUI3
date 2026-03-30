from __future__ import annotations

import fnmatch
import logging
import traceback
from typing import Any, Callable

logger = logging.getLogger("pywebwinui3.eventmanager")


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
				_call_listener(func, args)
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
		self.exact_items: dict[str, Event] = {}
		self.pattern_items: dict[str, Event] = {}

	@staticmethod
	def _is_pattern(target: str) -> bool:
		return any(char in target for char in "*?[]")

	def _bucket(self, target: str) -> dict[str, Event]:
		return self.pattern_items if self._is_pattern(target) else self.exact_items

	def set(self, target: str, *args: Any):
		if not self.exact_items and not self.pattern_items:
			return

		exact_event = self.exact_items.get(target)
		if exact_event is not None:
			try:
				exact_event.set(target, *args)
			except Exception:
				logger.error(traceback.format_exc())

		for key, event in tuple(self.pattern_items.items()):
			try:
				if fnmatch.fnmatch(target, key):
					event.set(target, *args)
			except Exception:
				logger.error(traceback.format_exc())

	def __add__(self, item: list):
		self._bucket(item[0]).setdefault(item[0], Event()).__iadd__(item[1])
		return self

	def __sub__(self, item: list):
		self._bucket(item[0]).setdefault(item[0], Event()).__isub__(item[1])
		return self

	def __iadd__(self, item: list):
		self._bucket(item[0]).setdefault(item[0], Event()).__iadd__(item[1])
		return self

	def __isub__(self, item: list):
		self._bucket(item[0]).setdefault(item[0], Event()).__isub__(item[1])
		return self

	def __len__(self) -> int:
		return len(self.exact_items) + len(self.pattern_items)

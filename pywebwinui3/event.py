from __future__ import annotations

import re
import fnmatch
import logging
import traceback
from typing import Any, Callable

logger = logging.getLogger("pywebwinui3.eventmanager")

class Event:
	def __init__(self) -> None:
		self.items: list[Callable[..., Any]] = []

	def set(self, *args: Any):
		listeners = tuple(self.items)
		if not listeners:
			return

		for func in listeners:
			try:
				func(*args)
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
		self._compiled_patterns: dict[str, re.Pattern[str]] = {}
		self._pattern_cache: dict[str, tuple[Event, ...]] = {}

	@staticmethod
	def _is_pattern(target: str) -> bool:
		return any(char in target for char in "*?[]")

	def _bucket(self, target: str) -> dict[str, Event]:
		return self.pattern_items if self._is_pattern(target) else self.exact_items

	def _clear_pattern_cache(self) -> None:
		self._pattern_cache.clear()

	def _compile_pattern(self, pattern: str) -> re.Pattern[str]:
		regex = self._compiled_patterns.get(pattern)
		if regex is None:
			regex = re.compile(fnmatch.translate(pattern))
			self._compiled_patterns[pattern] = regex
		return regex

	def _get_pattern_events(self, target: str) -> tuple[Event, ...]:
		cached = self._pattern_cache.get(target)
		if cached is not None:
			return cached

		matched_events: list[Event] = []
		for key, event in tuple(self.pattern_items.items()):
			try:
				if self._compile_pattern(key).match(target):
					matched_events.append(event)
			except Exception:
				logger.error(traceback.format_exc())

		result = tuple(matched_events)
		self._pattern_cache[target] = result
		return result

	def set(self, target: str, *args: Any):
		if not self.exact_items and not self.pattern_items:
			return

		exact_event = self.exact_items.get(target)
		if exact_event is not None:
			try:
				exact_event.set(target, *args)
			except Exception:
				logger.error(traceback.format_exc())

		for event in self._get_pattern_events(target):
			try:
				event.set(target, *args)
			except Exception:
				logger.error(traceback.format_exc())

	def __add__(self, item: list):
		target, callback = item[0], item[1]
		bucket = self._bucket(target)
		bucket.setdefault(target, Event()).__iadd__(callback)

		if self._is_pattern(target):
			self._compiled_patterns.setdefault(target, self._compile_pattern(target))
			self._clear_pattern_cache()

		return self

	def __sub__(self, item: list):
		target, callback = item[0], item[1]
		bucket = self._bucket(target)
		bucket.setdefault(target, Event()).__isub__(callback)

		if self._is_pattern(target):
			self._clear_pattern_cache()

		return self

	def __iadd__(self, item: list):
		target, callback = item[0], item[1]
		bucket = self._bucket(target)
		bucket.setdefault(target, Event()).__iadd__(callback)

		if self._is_pattern(target):
			self._compiled_patterns.setdefault(target, self._compile_pattern(target))
			self._clear_pattern_cache()

		return self

	def __isub__(self, item: list):
		target, callback = item[0], item[1]
		bucket = self._bucket(target)
		bucket.setdefault(target, Event()).__isub__(callback)

		if self._is_pattern(target):
			self._clear_pattern_cache()

		return self

	def __len__(self) -> int:
		return len(self.exact_items) + len(self.pattern_items)
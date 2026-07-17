from __future__ import annotations

import re
import fnmatch
import logging
from typing import Any, Callable

logger = logging.getLogger("pywebwinui3.eventmanager")

class Event:
	def __init__(self) -> None:
		self.items: list[Callable[..., Any]] = []

	def set(self, *args: Any):
		result = False
		for func in tuple(self.items):
			try:
				result = bool(func(*args)) or result
			except Exception:
				logger.exception("Event callback failed")
		return result

	def _add(self, item: Callable[..., Any]):
		self.items.append(item)
		return self

	def _remove(self, item: Callable[..., Any]):
		self.items.remove(item)
		return self

	def __add__(self, item: Callable[..., Any]):
		return self._add(item)

	def __sub__(self, item: Callable[..., Any]):
		return self._remove(item)

	def __iadd__(self, item: Callable[..., Any]):
		return self._add(item)

	def __isub__(self, item: Callable[..., Any]):
		return self._remove(item)

	def __len__(self) -> int:
		return len(self.items)


class PathEvent:
	_PATTERN_CACHE_LIMIT = 512

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
				logger.exception("Pattern match failed")

		result = tuple(matched_events)
		if len(self._pattern_cache) >= self._PATTERN_CACHE_LIMIT:
			self._pattern_cache.clear()
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
				logger.exception("Exact path callback failed")

		for event in self._get_pattern_events(target):
			try:
				event.set(target, *args)
			except Exception:
				logger.exception("Pattern path callback failed")

	def _modify(self, item: list, remove: bool):
		target, callback = item[0], item[1]
		bucket = self._bucket(target)
		event = bucket.setdefault(target, Event())

		if remove:
			event -= callback
		else:
			event += callback

		if self._is_pattern(target):
			if not remove:
				self._compiled_patterns.setdefault(target, self._compile_pattern(target))
			self._clear_pattern_cache()

		return self

	def __add__(self, item: list):
		return self._modify(item, False)

	def __sub__(self, item: list):
		return self._modify(item, True)

	def __iadd__(self, item: list):
		return self._modify(item, False)

	def __isub__(self, item: list):
		return self._modify(item, True)

	def __len__(self) -> int:
		return len(self.exact_items) + len(self.pattern_items)

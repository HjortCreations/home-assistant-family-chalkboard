"""Persistent Home Assistant storage for Family Chalkboard."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from copy import deepcopy
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION
from .model import DEFAULT_STATE, InvalidState, validate_state

_LOGGER = logging.getLogger(__name__)
StateListener = Callable[[dict[str, Any]], None]


class BoardStore:
    """Own and persist one shared family chalkboard."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the board store."""
        self._store = Store[dict[str, Any]](
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
            atomic_writes=True,
        )
        self._state = deepcopy(DEFAULT_STATE)
        self._lock = asyncio.Lock()
        self._listeners: set[StateListener] = set()

    @property
    def state(self) -> dict[str, Any]:
        """Return a defensive copy of the current state."""
        return deepcopy(self._state)

    async def async_load(self) -> None:
        """Load and validate the stored board."""
        stored = await self._store.async_load()
        if stored is None:
            return
        try:
            self._state = validate_state(stored)
        except InvalidState:
            _LOGGER.exception(
                "Stored chalkboard state is invalid; starting with an empty board"
            )

    async def async_save(self, state: Any) -> dict[str, Any]:
        """Validate, save, and broadcast a new state."""
        normalized = validate_state(state)
        async with self._lock:
            await self._store.async_save(normalized)
            self._state = normalized

        snapshot = self.state
        for listener in tuple(self._listeners):
            listener(snapshot)
        return snapshot

    @callback
    def async_subscribe(self, listener: StateListener) -> Callable[[], None]:
        """Subscribe to state updates."""
        self._listeners.add(listener)

        @callback
        def unsubscribe() -> None:
            self._listeners.discard(listener)

        return unsubscribe

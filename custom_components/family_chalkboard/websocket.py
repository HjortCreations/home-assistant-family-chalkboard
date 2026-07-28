"""Authenticated WebSocket API for Family Chalkboard."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import (
    DATA_STORE,
    DOMAIN,
    WS_GET_STATE,
    WS_SAVE_STATE,
    WS_SUBSCRIBE_STATE,
)
from .model import InvalidState
from .storage import BoardStore


def _get_store(hass: HomeAssistant) -> BoardStore:
    """Return the configured board store."""
    return hass.data[DOMAIN][DATA_STORE]


@websocket_api.websocket_command({vol.Required("type"): WS_GET_STATE})
@callback
def websocket_get_state(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the current board state."""
    connection.send_result(msg["id"], _get_store(hass).state)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SAVE_STATE,
        vol.Required("state"): dict,
    }
)
@websocket_api.async_response
async def websocket_save_state(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Validate and persist board state."""
    try:
        state = await _get_store(hass).async_save(msg["state"])
    except InvalidState as error:
        connection.send_error(msg["id"], "invalid_state", str(error))
        return
    connection.send_result(msg["id"], state)


@websocket_api.websocket_command({vol.Required("type"): WS_SUBSCRIBE_STATE})
@callback
def websocket_subscribe_state(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Subscribe a frontend to live board updates."""

    @callback
    def forward_state(state: dict[str, Any]) -> None:
        connection.send_message(websocket_api.event_message(msg["id"], state))

    connection.subscriptions[msg["id"]] = _get_store(hass).async_subscribe(
        forward_state
    )
    connection.send_result(msg["id"])


@callback
def async_register_websocket_commands(hass: HomeAssistant) -> None:
    """Register all Family Chalkboard WebSocket commands."""
    websocket_api.async_register_command(hass, websocket_get_state)
    websocket_api.async_register_command(hass, websocket_save_state)
    websocket_api.async_register_command(hass, websocket_subscribe_state)

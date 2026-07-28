"""Home Assistant integration for Family Chalkboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import (
    DATA_FRONTEND_REGISTERED,
    DATA_STORE,
    DATA_WEBSOCKET_REGISTERED,
    DOMAIN,
    NAME,
    PANEL_COMPONENT_NAME,
    PANEL_STATIC_URL,
    PANEL_URL_PATH,
)
from .storage import BoardStore
from .websocket import async_register_websocket_commands

FRONTEND_DIR = Path(__file__).parent / "frontend"
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Prepare shared integration data."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Family Chalkboard from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    store = BoardStore(hass)
    await store.async_load()
    domain_data[DATA_STORE] = store

    if not domain_data.get(DATA_WEBSOCKET_REGISTERED):
        async_register_websocket_commands(hass)
        domain_data[DATA_WEBSOCKET_REGISTERED] = True

    if not domain_data.get(DATA_FRONTEND_REGISTERED):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    PANEL_STATIC_URL,
                    str(FRONTEND_DIR),
                    cache_headers=False,
                )
            ]
        )
        domain_data[DATA_FRONTEND_REGISTERED] = True

    if not frontend.async_panel_exists(hass, PANEL_URL_PATH):
        await panel_custom.async_register_panel(
            hass=hass,
            frontend_url_path=PANEL_URL_PATH,
            webcomponent_name=PANEL_COMPONENT_NAME,
            sidebar_title=NAME,
            sidebar_icon="mdi:draw",
            module_url=f"{PANEL_STATIC_URL}/family-chalkboard-panel.js",
            embed_iframe=False,
            require_admin=False,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the config entry and remove its panel."""
    if frontend.async_panel_exists(hass, PANEL_URL_PATH):
        frontend.async_remove_panel(hass, PANEL_URL_PATH)
    return True

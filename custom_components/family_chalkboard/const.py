"""Constants for Family Chalkboard."""

from typing import Final

DOMAIN: Final = "family_chalkboard"
NAME: Final = "Family Chalkboard"

PANEL_URL_PATH: Final = "family-chalkboard"
PANEL_COMPONENT_NAME: Final = "family-chalkboard-panel"
PANEL_STATIC_URL: Final = "/family_chalkboard_static"

STORAGE_KEY: Final = "family_chalkboard.board"
STORAGE_VERSION: Final = 1

WS_GET_STATE: Final = "family_chalkboard/state/get"
WS_SAVE_STATE: Final = "family_chalkboard/state/save"
WS_SUBSCRIBE_STATE: Final = "family_chalkboard/state/subscribe"

DATA_STORE: Final = "store"
DATA_FRONTEND_REGISTERED: Final = "frontend_registered"
DATA_WEBSOCKET_REGISTERED: Final = "websocket_registered"

# Changelog

## 1.3.0b1 — 2026-08-17

- Establish the opt-in prerelease channel used for testing the exact HACS
  installation and update path before changes are promoted to a stable release.

## 1.2.1 — 2026-08-17

- Keep the drawing area visible when Home Assistant does not give the custom
  panel an explicit height.
- Size the panel to the remaining viewport below Home Assistant's header.

## 1.2.0 — 2026-08-16

- Responsive board format that is detected from the available drawing area.
- Proportion-preserving **Fit** mode across portrait and landscape screens.
- Optional per-browser **Fill** mode for people who prefer to use the entire area.
- Full-height layouts on short and non-kiosk screens without page scrolling.
- A compact 50/50 header and family-note row on wide landscape screens.
- Backward-compatible migration of version 1 board data.

## 1.1.0 — 2026-07-28

- HACS-compatible Home Assistant custom integration.
- One-click config flow and automatically registered sidebar panel.
- Authenticated Home Assistant WebSocket API.
- Shared storage in Home Assistant with live updates across open screens.
- English and Swedish setup translations.
- HACS and Hassfest validation workflows.

## 1.0.0 — 2026-07-28

- Touch and pen drawing with five chalk colors and three line widths.
- Eraser, undo, and protected clear action.
- Shared family note.
- Durable, atomic JSON persistence.
- English and Swedish interface.
- Home Assistant iframe example.
- Docker and hardened systemd installation options.
- Network allowlist and strict state validation.

# Home Assistant Family Chalkboard

[![CI](https://github.com/HjortCreations/home-assistant-family-chalkboard/actions/workflows/ci.yml/badge.svg)](https://github.com/HjortCreations/home-assistant-family-chalkboard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-gold.svg)](LICENSE)

A touch-first family chalkboard for Home Assistant dashboards and wall-mounted
kiosks. Draw with a finger or stylus, leave a short note, and keep everything
saved on the server across reloads and restarts.

![Family Chalkboard running in a portrait browser](docs/screenshot.png)

## Why this exists

Home Assistant has excellent controls, calendars, and task lists, but a shared
wall display sometimes needs something less structured: a quick handwritten
message, a child's drawing, or a note that the whole household can see.

Family Chalkboard is deliberately small:

- no JavaScript framework;
- no Python packages;
- one shared board;
- one atomic JSON state file;
- suitable for a Raspberry Pi or another always-on home server.

## Features

- Finger, stylus, and mouse drawing
- Five chalk colors and three line widths
- Eraser and undo
- Shared family note
- Clear confirmation to prevent accidental deletion
- Automatic server-side saving
- Responsive portrait and landscape layouts
- English and Swedish interface
- Strict payload validation and configurable write allowlist
- Health endpoint for containers and monitoring
- Docker Compose and hardened systemd examples

## Quick start with Docker Compose

```bash
git clone https://github.com/HjortCreations/home-assistant-family-chalkboard.git
cd home-assistant-family-chalkboard
docker compose up -d --build
```

Open `http://YOUR_SERVER_IP:8765/`.

Board data is stored in the Docker volume `chalkboard-data`.

## Quick start with Python

Python 3.11 or later is recommended. No packages need to be installed.

```bash
git clone https://github.com/HjortCreations/home-assistant-family-chalkboard.git
cd home-assistant-family-chalkboard
python src/chalkboard_server.py
```

The default address is `http://0.0.0.0:8765/`, and the state file is written to
`./data/board.json`.

## Install as a systemd service

On Debian, Raspberry Pi OS, and similar distributions:

```bash
sudo ./scripts/install-systemd.sh
```

The installer copies the app to `/opt/family-chalkboard`, installs the included
unit, and enables it immediately. State is stored in
`/var/lib/family-chalkboard/board.json`.

Check it with:

```bash
systemctl status family-chalkboard
curl http://127.0.0.1:8765/health
```

## Add it to Home Assistant

Add a Webpage card to a dashboard:

```yaml
type: iframe
url: http://YOUR_SERVER_IP:8765/?lang=en
aspect_ratio: 165%
```

Use `?lang=sv` for Swedish. Without a language parameter, the app follows the
browser language.

For a wall display, a dedicated panel or subview provides the most drawing
space. A regular Home Assistant button can navigate to that view:

```yaml
type: button
name: Chalkboard
icon: mdi:draw
tap_action:
  action: navigate
  navigation_path: /your-dashboard/chalkboard
```

### HTTPS note

Browsers block an HTTP iframe inside an HTTPS Home Assistant page. If Home
Assistant is served over HTTPS, expose Family Chalkboard through an HTTPS
reverse proxy as well. A local kiosk that loads both services over HTTP does
not have this mixed-content restriction.

## Configuration

Settings can be supplied as command-line flags or environment variables.

| Purpose | Flag | Environment variable | Default |
| --- | --- | --- | --- |
| Listen address | `--host` | `CHALKBOARD_HOST` | `0.0.0.0` |
| Port | `--port` | `CHALKBOARD_PORT` | `8765` |
| Data directory | `--data-dir` | `CHALKBOARD_DATA_DIR` | `./data` |
| Networks allowed to save | `--allowed-networks` | `CHALKBOARD_ALLOWED_NETWORKS` | Loopback and private networks |
| Request logging | `--verbose` | `CHALKBOARD_VERBOSE=true` | Off |

Example:

```bash
python src/chalkboard_server.py \
  --host 0.0.0.0 \
  --port 9000 \
  --data-dir /srv/chalkboard \
  --allowed-networks 127.0.0.0/8,192.168.1.0/24
```

The allowlist controls **writes**. Anyone who can reach the HTTP port can read
the board, which is necessary for a Home Assistant iframe.

## Backups

Back up the single `board.json` file in your configured data directory. Docker
Compose stores it in the `chalkboard-data` volume. Writes are validated,
serialized, flushed, and atomically replaced to reduce the risk of partial
state after a power loss.

## Security

This project is designed for a trusted home network and has no built-in user
accounts. Do not expose it directly to the public internet. For remote access,
use an authenticated HTTPS reverse proxy or a trusted VPN.

See [SECURITY.md](SECURITY.md) for the security model.

## Development

Run the test suite:

```bash
python -m unittest discover -s tests -v
python scripts/check_frontend.py
```

The project intentionally avoids runtime dependencies. Please keep changes
focused and include screenshots for interface updates.

## Limitations

- The board is shared and uses last-write-wins behavior.
- It is not a HACS card or a Home Assistant add-on.
- There is no built-in authentication or user history.
- Very large, long-lived drawings will eventually reach the configured state
  limits and should be cleared.

## License

[MIT](LICENSE) © 2026 Per Hjort

# Security

The HACS integration uses Home Assistant's authenticated WebSocket connection.
Only users who are signed in to Home Assistant can read or change its board.
Its state is stored in Home Assistant's protected `.storage` directory.

The standalone server is designed for a trusted home network. It intentionally
has no user accounts or built-in authentication. By default, only loopback,
RFC 1918 private IPv4 networks, and private IPv6 networks may write its board
state. Read access is available to any client that can reach the HTTP port.

Do not expose the standalone server directly to the public internet. If remote
access is required, place it behind an authenticated HTTPS reverse proxy or a
trusted VPN.

To report a vulnerability privately, use GitHub's private vulnerability
reporting feature for this repository.

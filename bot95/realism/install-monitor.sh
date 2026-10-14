#!/usr/bin/env bash
set -euo pipefail
STAGE="${1:?staging directory required}"
test "$(id -u)" = 0
test -x /opt/bot95-protected/node
id bot95-protected >/dev/null
# Refuse to overwrite an unexpected proxy configuration.
python3 - <<'PY'
from pathlib import Path
text=Path('/etc/caddy/Caddyfile').read_text()
lines=[line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith('#')]
expected=['107.174.203.201.sslip.io {','encode gzip','reverse_proxy 127.0.0.1:8080','}']
if lines != expected:
    raise SystemExit('Unexpected Caddy configuration; nothing installed.')
PY
install -d -m 755 /opt/bot95-monitor
install -d -o bot95-protected -g bot95-protected -m 755 /opt/bot95-monitor/public
install -m 644 "$STAGE/monitor-publish.cjs" /opt/bot95-monitor/monitor-publish.cjs
install -m 644 "$STAGE/monitor.html" /opt/bot95-monitor/public/index.html
install -m 644 "$STAGE/bot95-monitor.service" /etc/systemd/system/bot95-monitor.service
install -m 644 "$STAGE/bot95-monitor.timer" /etc/systemd/system/bot95-monitor.timer
caddy validate --config "$STAGE/Caddyfile.monitor" --adapter caddyfile
systemctl daemon-reload
systemctl start bot95-monitor.service
test -s /opt/bot95-monitor/public/status.json
systemctl enable --now bot95-monitor.timer
BACKUP="/etc/caddy/Caddyfile.before-protected-$(date -u +%Y%m%dT%H%M%SZ)"
cp -p /etc/caddy/Caddyfile "$BACKUP"
install -m 644 "$STAGE/Caddyfile.monitor" /etc/caddy/Caddyfile
if ! systemctl reload caddy; then
    cp -p "$BACKUP" /etc/caddy/Caddyfile
    systemctl reload caddy
    echo "Caddy reload failed; original configuration restored." >&2
    exit 1
fi
echo "Monitor installed; Caddy backup: $BACKUP"
systemctl is-active bot95-monitor.timer bot95-protected bot95-rapide caddy limitless-pulse

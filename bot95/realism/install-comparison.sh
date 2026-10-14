#!/usr/bin/env bash
set -euo pipefail
STAGE="${1:?staging directory required}"
test "$(id -u)" = 0
test -x /opt/bot95-protected/node
id bot95 >/dev/null
install -d -m 755 /opt/bot95-comparison
install -d -m 700 -o bot95 -g bot95 /opt/bot95-comparison/data
install -d -m 755 -o bot95 -g bot95 /opt/bot95-comparison/public
for file in official-m10.cjs official-execution.cjs recorded-comparison.cjs recording-events.cjs settle-recorded.cjs comparison-service.cjs; do
  install -m 644 "$STAGE/$file" "/opt/bot95-comparison/$file"
done
install -m 644 "$STAGE/bot95-comparison.service" /etc/systemd/system/
install -m 644 "$STAGE/bot95-comparison.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl restart bot95-comparison.service
systemctl enable --now bot95-comparison.timer

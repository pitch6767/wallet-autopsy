#!/usr/bin/env bash
# Installation UNIQUE du bot95 rapide sur le VPS de Dublin (à lancer en root). Fantôme uniquement : aucun ordre, aucune clé de portefeuille.
# Ne touche à rien d'autre sur le serveur (arb-bot, event_arb restent intacts). N'ouvre aucun port.
set -euo pipefail
TOKEN="${1:?jeton manquant}"
# 1. Node.js 22 PRIVÉ dans /opt/bot95-rapide/node (le Node du système, s'il existe, n'est pas touché)
id bot95 >/dev/null 2>&1 || useradd --system --create-home --home-dir /opt/bot95-rapide --shell /usr/sbin/nologin bot95
mkdir -p /opt/bot95-rapide/node
ARCH=$(uname -m); case "$ARCH" in x86_64) NA=x64;; aarch64) NA=arm64;; *) echo "architecture $ARCH non prévue"; exit 1;; esac
curl -fsSL "https://nodejs.org/dist/v22.11.0/node-v22.11.0-linux-$NA.tar.xz" | tar -xJ -C /opt/bot95-rapide/node --strip-components=1
NODE=/opt/bot95-rapide/node/bin/node
# 2. horloge : on vérifie seulement qu'elle est synchronisée (rien n'est installé)
timedatectl show -p NTPSynchronized || true
# 3. utilisateur dédié, sans droits root, sans accès aux autres bots
id bot95 >/dev/null 2>&1 || useradd --system --create-home --home-dir /opt/bot95-rapide --shell /usr/sbin/nologin bot95
mkdir -p /opt/bot95-rapide
curl -fsSL -H "x-rapide: $TOKEN" https://bot95.pitch67.workers.dev/api/rapide/launcher -o /opt/bot95-rapide/launcher.js
printf 'BOT95_RAPIDE_TOKEN=%s\nBOT95_DIR=/opt/bot95-rapide\n' "$TOKEN" > /etc/bot95-rapide.env
chown -R bot95:bot95 /opt/bot95-rapide; chown root:bot95 /etc/bot95-rapide.env; chmod 640 /etc/bot95-rapide.env
# 4. service systemd (redémarre seul, y compris après chaque mise à jour du code)
cat > /etc/systemd/system/bot95-rapide.service <<SVC
[Unit]
Description=bot95 rapide (fantome, mesure de vitesse)
After=network-online.target
Wants=network-online.target
[Service]
User=bot95
Group=bot95
EnvironmentFile=/etc/bot95-rapide.env
WorkingDirectory=/opt/bot95-rapide
ExecStart=$NODE /opt/bot95-rapide/launcher.js
Restart=always
RestartSec=3
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/opt/bot95-rapide
ProtectHome=true
PrivateTmp=true
MemoryMax=400M
CPUQuota=60%
[Install]
WantedBy=multi-user.target
SVC
systemctl daemon-reload
systemctl enable --now bot95-rapide
sleep 15
echo "=== node"; $NODE --version
echo "=== horloge"; timedatectl
echo "=== service"; systemctl --no-pager status bot95-rapide | head -12
echo "=== journal"; journalctl -u bot95-rapide --no-pager -n 20
echo "=== latence vers Polymarket"; for i in 1 2 3 4 5; do curl -s -o /dev/null -w "%{time_connect} %{time_starttransfer}\n" https://clob.polymarket.com/time; done

#!/usr/bin/env bash
# Installation UNIQUE de la copie de bot95 sur le serveur de Dublin (à lancer en root). 26.10.2026.
# N'envoie AUCUN ordre : elle calcule les stratégies comme bot95 et envoie des signaux au bot de trading local (127.0.0.1:8090).
# Utilise le Node privé déjà installé pour le labo rapide (/opt/bot95-rapide/node). N'ouvre aucun port vers l'extérieur.
# Usage : bash installer.sh <BOT_SIGNAL_TOKEN>   (le même jeton que dans /etc/btcbot.env du bot de trading)
set -euo pipefail
JETON="${1:?jeton manquant}"
[ -x /opt/bot95-rapide/node/bin/node ] || { echo "Node du labo rapide introuvable"; exit 1; }
id bot95d >/dev/null 2>&1 || useradd --system --create-home --home-dir /opt/bot95-dublin --shell /usr/sbin/nologin bot95d
mkdir -p /opt/bot95-dublin/etat
# copie privée de Node (le dossier du labo rapide n'est pas lisible par bot95d)
rm -rf /opt/bot95-dublin/node; cp -a /opt/bot95-rapide/node /opt/bot95-dublin/node
NODE=/opt/bot95-dublin/node/bin/node; NPM=/opt/bot95-dublin/node/bin/npm
B=https://raw.githubusercontent.com/pitch6767/wallet-autopsy/main/bot95/dublin
curl -fsSL $B/package.json -o /opt/bot95-dublin/package.json
curl -fsSL $B/lanceur.mjs -o /opt/bot95-dublin/lanceur.mjs
cd /opt/bot95-dublin && PATH=/opt/bot95-dublin/node/bin:$PATH $NPM install --no-audit --no-fund --omit=dev
printf 'BOT_SIGNAL_TOKEN=%s\nSIGNAL_NUMS=101,201,121,28,119\nBOT95_DUBLIN_DIR=/opt/bot95-dublin\n' "$JETON" > /etc/bot95-dublin.env
chown -R bot95d:bot95d /opt/bot95-dublin; chown root:bot95d /etc/bot95-dublin.env; chmod 640 /etc/bot95-dublin.env
cat > /etc/systemd/system/bot95-dublin.service <<SVC
[Unit]
Description=bot95 copie de Dublin (signaux des stratégies numérotées vers le bot de trading)
After=network-online.target
Wants=network-online.target
[Service]
User=bot95d
Group=bot95d
EnvironmentFile=/etc/bot95-dublin.env
WorkingDirectory=/opt/bot95-dublin
ExecStart=$NODE /opt/bot95-dublin/lanceur.mjs
Restart=always
RestartSec=5
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/opt/bot95-dublin
ProtectHome=true
PrivateTmp=true
MemoryMax=3000M
[Install]
WantedBy=multi-user.target
SVC
# le labo rapide annonce ses achats BY1 à la copie locale (même jeton)
grep -q '^BOT95_LOCAL_URL=' /etc/bot95-rapide.env || printf 'BOT95_LOCAL_URL=http://127.0.0.1:8787\nBOT95_LOCAL_TOKEN=%s\n' "$JETON" >> /etc/bot95-rapide.env
systemctl daemon-reload
systemctl enable --now bot95-dublin
systemctl restart bot95-rapide
sleep 20; systemctl --no-pager status bot95-dublin | head -12; curl -s -m 10 http://127.0.0.1:8787/api/signaux_live | head -c 300; echo

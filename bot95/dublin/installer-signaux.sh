#!/usr/bin/env bash
# 29.10.2026 — installation du moteur de signaux LOCAL sur le serveur de Dublin (à lancer en root). Aucun ordre, aucune clé.
# Usage : bash installer-signaux.sh
set -euo pipefail
NODE_SRC=/opt/bot95-dublin/node; [ -x $NODE_SRC/bin/node ] || NODE_SRC=/opt/bot95-rapide/node
[ -x $NODE_SRC/bin/node ] || { echo "Node introuvable"; exit 1; }
id moteur >/dev/null 2>&1 || useradd --system --create-home --home-dir /opt/moteur-signaux --shell /usr/sbin/nologin moteur
mkdir -p /opt/moteur-signaux/etat
rm -rf /opt/moteur-signaux/node; cp -a $NODE_SRC /opt/moteur-signaux/node
B=https://raw.githubusercontent.com/pitch6767/wallet-autopsy/main/bot95/dublin
curl -fsSL $B/package.json -o /opt/moteur-signaux/package.json
curl -fsSL $B/lanceur-signaux.mjs -o /opt/moteur-signaux/lanceur-signaux.mjs
cd /opt/moteur-signaux && PATH=/opt/moteur-signaux/node/bin:$PATH ./node/bin/npm install --no-audit --no-fund --omit=dev
printf 'SIGNAL_NUMS=101,201,121,28,119\nMOTEUR_DIR=/opt/moteur-signaux\nMOTEUR_PORT=8788\n' > /etc/moteur-signaux.env
chown -R moteur:moteur /opt/moteur-signaux; chown root:moteur /etc/moteur-signaux.env; chmod 640 /etc/moteur-signaux.env
cat > /etc/systemd/system/moteur-signaux.service <<SVC
[Unit]
Description=Moteur de signaux local (stratégies numérotées) pour le bot de trading
After=network-online.target
Wants=network-online.target
[Service]
User=moteur
Group=moteur
EnvironmentFile=/etc/moteur-signaux.env
WorkingDirectory=/opt/moteur-signaux
ExecStart=/opt/moteur-signaux/node/bin/node /opt/moteur-signaux/lanceur-signaux.mjs
Restart=always
RestartSec=3
Nice=-5
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/opt/moteur-signaux
ProtectHome=true
PrivateTmp=true
MemoryMax=2000M
[Install]
WantedBy=multi-user.target
SVC
systemctl daemon-reload
systemctl enable --now moteur-signaux
sleep 25; systemctl --no-pager status moteur-signaux | head -12
curl -s -m 10 http://127.0.0.1:8788/api/cle_signaux | head -c 200; echo
curl -s -m 10 http://127.0.0.1:8788/api/statut | head -c 600; echo

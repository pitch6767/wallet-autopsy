# 12.11.2026 : les réponses du bot sont-elles compressées ? taille des données (lecture seule)
import urllib.request, time
for u in ["https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis=2026-11-12T00:00:00Z", "https://72-11-157-70.sslip.io/"]:
    a = time.time(); r = urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse", "accept-encoding": "gzip, br"}), timeout=60); b = r.read()
    print(u, "| encodage :", r.headers.get("content-encoding"), "| octets reçus :", len(b), "| serveur :", r.headers.get("server"), "| http :", r.version, "|", round(time.time() - a, 2), "s")

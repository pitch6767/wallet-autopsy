# 12.11.2026 : affichage lent / vide de l'onglet Trades — temps de réponse du serveur du bot pendant 90 s (lecture seule)
import time, urllib.request
def t(u):
    a = time.time()
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=90) as r: r.read(); s = r.status
    except Exception as e: s = str(e)[:40]
    return round(time.time() - a, 2), s
B = "https://72-11-157-70.sslip.io/api"
print("santé (sans calcul) | état garde-fous :")
for k in range(45):
    print(time.strftime("%H:%M:%S"), t(B + "/healthz"), t(B + "/bot/banc/etat"), flush=True); time.sleep(1)
print("banc trades (calcul complet) :", t(B + "/bot/banc/trades?depuis=2026-11-12T00:00:00Z"))
print("banc decisions :", t(B + "/bot/banc/decisions?depuis=2026-11-12T00:00:00Z"))

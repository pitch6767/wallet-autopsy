# 12.11.2026 : affichage « — » une fois sur deux — le serveur répond-il toujours pareil ? (lecture seule)
import time, urllib.request, json, collections
def g(u):
    a = time.time()
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60) as r: b = r.read(); s = r.status
    except urllib.error.HTTPError as e: b = e.read(); s = e.code
    except Exception as e: b = b""; s = str(e)[:40]
    return round(time.time() - a, 2), s, b
B = "https://72-11-157-70.sslip.io/api"
V = collections.Counter(); C = collections.Counter(); lents = []
for k in range(60):
    d, s, b = g(B + "/bot/banc/etat")
    try: v = json.loads(b).get("version")
    except Exception: v = "pas du JSON: " + b[:60].decode(errors="replace")
    V[v] += 1
    d2, s2, b2 = g(B + "/bot/bilan"); C[(s2, b2[:50].decode(errors="replace"))] += 1
    if d > 1 or d2 > 1: lents.append((time.strftime("%H:%M:%S"), d, d2))
    time.sleep(0.5)
print("versions :", dict(V)); print("bilan sans connexion :", dict(C)); print("réponses > 1 s :", lents)

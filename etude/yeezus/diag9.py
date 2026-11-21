import urllib.request, json, time
U="https://veille.pitch67.workers.dev"
def g(p,t=90):
    try: return urllib.request.urlopen(urllib.request.Request(U+p, headers={"user-agent":"curl/8"}), timeout=t).read().decode()
    except Exception as e: return "ERR "+str(e)
print("ETAT1", g("/api/etat")[:300])
print("TICK", g("/tick"))
d=json.loads(g("/api/etat")); print("DIAG", d["diag"], "init", sum(1 for w in d["wallets"] if w["last_sig"]), "events", len(d["events"]))
time.sleep(70); d=json.loads(g("/api/etat")); print("DIAG2", d["diag"], "init", sum(1 for w in d["wallets"] if w["last_sig"]))
# v6

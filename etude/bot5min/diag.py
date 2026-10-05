import urllib.request, json
for p in ["/api/etat", "/api/reel/etat"]:
    try:
        r = urllib.request.urlopen(urllib.request.Request("https://bot95.pitch67.workers.dev"+p, headers={"User-Agent":"x"}), timeout=30).read().decode()
        print(p, r[:1500])
    except Exception as e:
        print(p, "ERREUR", e, getattr(e, "read", lambda: b"")()[:800])

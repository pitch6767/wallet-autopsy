# 12.11.2026 12 h 43 : la page du bot en ligne contient-elle 600013 dans la liste courte du banc ? — lecture seule
import urllib.request, re, json
B = "https://72-11-157-70.sslip.io"
def txt(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60) as r: return r.read().decode("utf8", "ignore")
h = txt(B + "/"); js = re.findall(r'src="([^"]+\.js)"', h); print("scripts :", js)
for j in js:
    s = txt(B + j if j.startswith("/") else B + "/" + j)
    i = s.find("6e5,"); k = s.find("600005")
    print(j, "taille", len(s), "| contient 600013 :", "600013" in s, "| contient 600005 :", "600005" in s, "| jackpot :", "jackpot" in s, "| Tout afficher :", "Tout afficher" in s)
    for m in re.finditer(r"new Set\(\[[^\]]{0,300}\]\)", s):
        if "2172" in m.group(0) or "2171" in m.group(0): print("  liste :", m.group(0)[:300])
try:
    st = json.loads(txt(B + "/api/bot/state")); print("état :", {k: st.get(k) for k in ("isRunning",)})
except Exception as e: print("état", repr(e))

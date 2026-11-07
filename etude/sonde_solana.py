# 07.11.2026 : sonde — l'étude naissance tourne 7 min ici, tout affiché dans le journal, pour voir où elle bloque.
import threading, time, os, sys
s = open("etude/bot5min/bubble_naissance.py", encoding="utf-8").read()
s = s.replace("DUREE = 4 * 3600 + 30 * 60", "DUREE = 420").replace('"etude/bot5min/bubble_naissance_resultats.json"', '"etude/sonde_naissance.json"')
s = s.replace("git add etude/bot5min/ && git commit -qm 'Étude naissance : sauvegarde intermédiaire [skip ci]'", "git add etude/sonde_naissance.json && git commit -qm 'Sonde naissance : test sauvegarde [skip ci]'")
def garde():
    time.sleep(500); print("=== arrêt de garde, appels :", G.get("appels"), flush=True); os._exit(0)
G = {"__name__": "__main__"}; threading.Thread(target=garde, daemon=True).start()
exec(s, G)

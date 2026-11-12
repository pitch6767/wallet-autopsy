# 12.11.2026 18:35 : page du bot bloquée sur le rond de chargement (iPhone) — ouverture réelle de la page, sans connexion (lecture seule)
import subprocess, sys, time
r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "playwright"], capture_output=True, text=True); print("pip", r.returncode, r.stderr[-300:])
r = subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], capture_output=True, text=True); print("install", r.returncode, r.stderr[-300:])
import importlib, site
importlib.invalidate_caches(); sys.path += [site.getusersitepackages()] + site.getsitepackages()
r = subprocess.run([sys.executable, "-m", "pip", "show", "-f", "playwright"], capture_output=True, text=True); print([l for l in r.stdout.splitlines() if l.startswith("Location")])
for l in r.stdout.splitlines():
    if l.startswith("Location:"): sys.path.insert(0, l.split(": ", 1)[1])
try:
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
      b = p.chromium.launch(); c = b.new_context(**p.devices["iPhone 13"]); pg = c.new_page()
      ev = []; t0 = time.time()
      pg.on("console", lambda m: ev.append(f"{time.time()-t0:5.1f}s console {m.type}: {m.text[:200]}"))
      pg.on("pageerror", lambda e: ev.append(f"{time.time()-t0:5.1f}s ERREUR JS: {str(e)[:300]}"))
      pg.on("requestfinished", lambda r: ev.append(f"{time.time()-t0:5.1f}s ok {r.response().status if r.response() else '?'} {r.url[:90]}"))
      pg.on("requestfailed", lambda r: ev.append(f"{time.time()-t0:5.1f}s ÉCHEC {r.url[:90]} {r.failure}"))
      pg.goto("https://72-11-157-70.sslip.io/", wait_until="domcontentloaded", timeout=60000)
      pg.wait_for_timeout(15000)
      print("\n".join(ev[:60]))
      print("TEXTE AFFICHÉ :", pg.inner_text("body")[:400].replace("\n", " | "))
      b.close()

except Exception as e:
  print("échec de la sonde :", e)

import os, sys, urllib.request
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
echecs = 0


def ok(nom, cond, detail=""):
    global echecs
    if not cond:
        echecs += 1
    print(("PASS " if cond else "FAIL ") + nom + (" — " + str(detail) if detail else ""), flush=True)


def http(path, tete=False):
    req = urllib.request.Request(URL.rstrip("/") + path, method="HEAD" if tete else "GET", headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Safari/604.1"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, dict(r.headers), (b"" if tete else r.read())


# fichiers et en-têtes (réseau réel)
s, h, _ = http("/", tete=True)
ok("page d'accueil 200", s == 200, s)
cc = {k.lower(): v for k, v in h.items()}.get("cache-control", "")
ok("cache-control no-store", "no-store" in cc, cc)
for f in ["/manifest.webmanifest", "/icon-192.png", "/icon-512.png", "/icon-180.png", "/app.js", "/style.css", "/version.txt"]:
    try:
        s, _, _ = http(f, tete=True)
    except Exception as e:
        s = str(e)
    ok("fichier " + f + " 200", s == 200, s)
_, _, v = http("/version.txt")
ok("version.txt = 1.0", v.decode().strip() == "1.0", v.decode().strip())

exe = "/usr/bin/google-chrome"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe if os.path.exists(exe) else None, args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    erreurs = []
    pg.on("pageerror", lambda e: erreurs.append(str(e)))
    pg.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
    pg.goto(URL, wait_until="networkidle")

    ok("titre accueil « Peptides »", pg.inner_text("#titre") == "Peptides")
    ok("flèche cachée sur l'accueil", pg.locator("#retour").is_hidden())
    ok("version affichée 1.0", pg.inner_text("#ver") == "1.0", pg.inner_text("#ver"))
    ok("champ de recherche présent", pg.locator("#q").count() == 1)
    ok("17 tuiles (16 cas + tous)", pg.locator(".tuile").count() == 17, pg.locator(".tuile").count())
    ok("avertissement médical visible", "avis médical" in pg.inner_text("#pied"))
    pg.screenshot(path=OUT + "/1_accueil_iphone.png", full_page=True)

    pg.click('.tuile[data-cat="Tunnel carpien"]')
    noms = pg.locator(".carte .nom").all_inner_texts()
    print("   tunnel carpien ->", noms)
    for attendu in ["BPC-157", "TB-500", "GHK-Cu", "NGF", "IGF-1", "Collagène"]:
        ok("tunnel carpien contient " + attendu, any(attendu in n for n in noms))
    ok("flèche visible sur la liste", pg.locator("#retour").is_visible())
    pg.screenshot(path=OUT + "/2_tunnel_iphone.png", full_page=True)

    pg.click('.carte[data-fiche]')
    ok("fiche : dose indicative affichée", "Dose indicative" in pg.inner_text("#ecran"))
    ok("fiche : forme affichée", "Forme" in pg.inner_text("#ecran"))
    ok("fiche : cas associés cliquables", pg.locator(".fiche .tags button").count() >= 1)
    ok("flèche visible sur la fiche", pg.locator("#retour").is_visible())
    pg.screenshot(path=OUT + "/3_fiche_iphone.png", full_page=True)
    pg.click("#retour")
    pg.wait_for_selector(".tuile")
    ok("flèche depuis la fiche → accueil", pg.inner_text("#titre") == "Peptides" and pg.locator("#retour").is_hidden())

    pg.click('.tuile[data-cat="Tunnel carpien"]')
    pg.click("#retour")
    pg.wait_for_selector(".tuile")
    ok("flèche depuis la liste → accueil", pg.inner_text("#titre") == "Peptides")

    pg.click('.tuile[data-cat="Douleur"]')
    pg.go_back()
    pg.wait_for_selector(".tuile")
    ok("retour du navigateur depuis une liste → accueil", pg.inner_text("#titre") == "Peptides")
    pg.click('.tuile[data-cat="Douleur"]')
    pg.click('.carte[data-fiche]')
    pg.go_back()
    pg.wait_for_selector(".tuile")
    ok("retour du navigateur depuis une fiche → accueil", pg.inner_text("#titre") == "Peptides")

    cas = {
        "Érection & libido": "PT-141", "Perte de poids": "Sémaglutide", "Récupération chirurgie": "BPC-157",
        "Douleur": "Ziconotide", "Rides & cosmétique": "Argireline", "Cholestérol": "soja",
        "Cheveux": "Biotinoyl", "Arthrose & articulations": "UC-II", "Anti-inflammatoire": "BPC-157",
        "Anti-âge & peau": "Épitalon", "Alzheimer & cognition": "Dihexa",
    }
    for c, attendu in cas.items():
        pg.click('.tuile[data-cat="%s"]' % c)
        noms = pg.locator(".carte .nom").all_inner_texts()
        ok("cas « %s » contient %s (%d peptides)" % (c, attendu, len(noms)), any(attendu.lower() in n.lower() for n in noms))
        pg.click("#retour")
        pg.wait_for_selector(".tuile")
    pg.click('.tuile[data-cat="Érection & libido"]')
    pg.screenshot(path=OUT + "/4_erection_iphone.png", full_page=True)
    pg.click("#retour")
    pg.wait_for_selector(".tuile")

    pg.click(".tuile.tous")
    n = pg.locator(".carte").count()
    ok("« Tous les peptides » : 42 fiches", n == 42, n)
    pg.click("#retour")
    pg.wait_for_selector(".tuile")

    for mot, attendu in [("douleur", "Ziconotide"), ("cheveux", "Biotinoyl"), ("erection", "PT-141")]:
        pg.fill("#q", mot)
        pg.wait_for_selector("#res .carte")
        noms = pg.locator("#res .carte .nom").all_inner_texts()
        ok("recherche « %s » trouve %s" % (mot, attendu), any(attendu in x for x in noms), noms[:5])
    pg.screenshot(path=OUT + "/5_recherche_iphone.png", full_page=True)
    pg.click('#res .carte[data-fiche]')
    pg.click("#retour")
    pg.wait_for_selector(".tuile")
    ok("flèche depuis une fiche issue d'une recherche → accueil", pg.inner_text("#titre") == "Peptides")

    ok("pas de défilement horizontal à 390 px", pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))
    ok("aucune erreur JavaScript", not erreurs, erreurs)

    pg2 = b.new_page(viewport={"width": 1280, "height": 800})
    pg2.goto(URL, wait_until="networkidle")
    pg2.screenshot(path=OUT + "/6_accueil_bureau.png")
    pg2.click('.tuile[data-cat="Tunnel carpien"]')
    pg2.screenshot(path=OUT + "/7_tunnel_bureau.png")
    b.close()

print("\nRÉSULTAT :", "PASS" if echecs == 0 else "ÉCHEC (%d)" % echecs)
sys.exit(1 if echecs else 0)

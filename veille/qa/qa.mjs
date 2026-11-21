import { chromium, devices } from "playwright";
const U = "https://veille.pitch67.workers.dev/";
const b = await chromium.launch();
for (const [nom, opt] of [["iphone", devices["iPhone 13"]], ["ordi", { viewport: { width: 1280, height: 900 } }]]) {
  const p = await (await b.newContext(opt)).newPage();
  await p.goto(U, { waitUntil: "networkidle" }); await p.waitForTimeout(2500);
  await p.screenshot({ path: `veille/qa/${nom}-alertes.png`, fullPage: false });
  console.log(nom, "titre", await p.title(), "| retour visible accueil:", await p.isVisible("#retour"), "| texte:", (await p.textContent("#m")).slice(0, 200));
  await p.click("#b-w"); await p.waitForTimeout(800);
  await p.screenshot({ path: `veille/qa/${nom}-wallets.png` });
  console.log(nom, "écran wallets: retour visible:", await p.isVisible("#retour"), "| nb cartes:", await p.locator(".c").count());
  await p.click("#retour"); await p.waitForTimeout(500);
  console.log(nom, "après ←: onglet Alertes actif:", (await p.getAttribute("#b-a", "class")) === "on");
  await p.click("#b-w"); await p.waitForTimeout(500); await p.goBack(); await p.waitForTimeout(800);
  console.log(nom, "après retour navigateur (glisser iPhone): Alertes actif:", (await p.getAttribute("#b-a", "class")) === "on", "| url:", p.url());
}
await b.close();

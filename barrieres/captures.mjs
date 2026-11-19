import { chromium } from "playwright";
const b = await chromium.launch(); const U = "https://barrieres.pitch67.workers.dev/";
const p = await b.newPage({ viewport: { width: 390, height: 844 } });
await p.goto(U, { waitUntil: "networkidle" });
console.log("version", await p.textContent("header .note"));
await p.screenshot({ path: "barrieres/capture_iphone.png" });
for (const e of ["ouvertes", "historique"]) {
  await p.click(`a.btn[href="#${e}"]`); await p.waitForTimeout(300);
  console.log(e, "visible:", await p.isVisible(`#${e}`), "fleche:", await p.isVisible("#retour"), "accueil cache:", !(await p.isVisible("#accueil")));
  await p.screenshot({ path: `barrieres/capture_${e}.png` });
  await p.click("#retour"); await p.waitForTimeout(300);
  console.log(" apres fleche: accueil visible:", await p.isVisible("#accueil"), "url:", p.url());
  await p.click(`a.btn[href="#${e}"]`); await p.waitForTimeout(200); await p.goBack(); await p.waitForTimeout(300);
  console.log(" apres retour arriere (glisser): accueil visible:", await p.isVisible("#accueil"));
}
await b.close();

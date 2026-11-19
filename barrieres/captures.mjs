import { chromium } from "playwright";
const b = await chromium.launch(); const U = "https://barrieres.pitch67.workers.dev/";
for (const [n, w, h] of [["iphone", 390, 844], ["ordi", 1280, 900]]) {
  const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  await p.goto(U, { waitUntil: "networkidle" }); await p.screenshot({ path: `barrieres/capture_${n}.png`, fullPage: true });
  await p.click("h1 a"); console.log(n, "après clic titre :", p.url());
}
await b.close();

import { firefox } from "playwright";
const U = "https://veille.pitch67.workers.dev/";
// test de bout en bout de la notification : abonnement réel (Firefox / service Mozilla) puis envoi par la veille
try {
  const fb = await firefox.launch({ firefoxUserPrefs: { "dom.push.enabled": true, "dom.webnotifications.enabled": true, "permissions.default.desktop-notification": 1 } });
  const fp = await (await fb.newContext()).newPage();
  await fp.goto(U, { waitUntil: "networkidle" }); await fp.waitForTimeout(2000);
  const r = await Promise.race([new Promise(r => setTimeout(() => r("délai dépassé (pas de service push dans ce navigateur de test)"), 60000)), fp.evaluate(async () => {
    const reg = await navigator.serviceWorker.register("/sw.js"); await navigator.serviceWorker.ready;
    const k = await (await fetch("/api/vapid")).text();
    const key = Uint8Array.from(atob(k.replace(/-/g, "+").replace(/_/g, "/") + "==".slice(0, (4 - k.length % 4) % 4)), c => c.charCodeAt(0));
    const s = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: key });
    await fetch("/api/abonner", { method: "POST", body: JSON.stringify(s) });
    return await (await fetch("/api/test-alerte")).text();
  })]);
  console.log("TEST PUSH de bout en bout :", r);
  await fb.close();
} catch (e) { console.log("TEST PUSH impossible ici :", e.message); }

// Flashback — outils communs à l'écran et aux téléphones
const AN_MIN = 1960, AN_MAX = 2010;
const COULEURS_OPT = ["var(--A)", "var(--B)", "var(--C)", "var(--D)"];
const LETTRES_OPT = ["A", "B", "C", "D"];

function pct(an) { return ((Math.min(AN_MAX, Math.max(AN_MIN, an)) - AN_MIN) / (AN_MAX - AN_MIN)) * 100; }

// Construit le cadran de radio dans un élément
function cadran(el) {
  let h = '<div class="graduations">';
  for (let a = AN_MIN; a <= AN_MAX; a++) {
    const p = pct(a);
    if (a % 10 === 0) h += '<span class="trait long" style="left:' + p + '%"></span><span class="an" style="left:' + p + '%">' + (a === 2010 ? "2010" : "’" + String(a).slice(2)) + "</span>";
    else if (a % 2 === 0) h += '<span class="trait court" style="left:' + p + '%"></span>';
  }
  h += '</div><div class="lueur"></div><div class="aiguille"></div>';
  el.classList.add("cadran");
  el.innerHTML = h;
  const ai = el.querySelector(".aiguille"), lu = el.querySelector(".lueur"), gr = el.querySelector(".graduations");
  return {
    regle(an, instant) {
      const box = gr.getBoundingClientRect(), base = el.getBoundingClientRect();
      const x = box.left - base.left + (box.width * pct(an)) / 100;
      if (instant) ai.style.transition = "none";
      ai.style.left = x + "px";
      lu.style.setProperty("--x", x + "px");
      if (instant) requestAnimationFrame(() => (ai.style.transition = ""));
    },
    anneeDepuisX(clientX) {
      const box = gr.getBoundingClientRect();
      const r = Math.min(1, Math.max(0, (clientX - box.left) / box.width));
      return Math.round(AN_MIN + r * (AN_MAX - AN_MIN));
    },
  };
}

// Connexion temps réel avec reconnexion automatique
function connecter(code, role, surMessage, surOuvert) {
  let ws, ecart = 0, vivant = true;
  const ouvrir = () => {
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(proto + "//" + location.host + "/ws/" + code + "?role=" + role);
    ws.onopen = () => surOuvert && surOuvert();
    ws.onmessage = (e) => {
      const m = JSON.parse(e.data);
      if (m.maintenant) ecart = m.maintenant - Date.now();
      surMessage(m);
    };
    ws.onclose = () => { if (vivant) setTimeout(ouvrir, 1200); };
  };
  ouvrir();
  setInterval(() => { try { ws.readyState === 1 && ws.send('{"type":"ping"}'); } catch (e) {} }, 20000);
  return {
    envoie(o) { try { ws.readyState === 1 && ws.send(JSON.stringify(o)); } catch (e) {} },
    restant(fin) { return Math.max(0, fin - (Date.now() + ecart)); },
  };
}

function echappe(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

// Barre de temps qui se vide
function minuteur(el, conn, fin, total) {
  cancelAnimationFrame(el._raf);
  const i = el.querySelector("i") || el.appendChild(document.createElement("i"));
  const tic = () => {
    const r = conn.restant(fin);
    i.style.transform = "scaleX(" + Math.max(0, Math.min(1, r / total)) + ")";
    if (r > 0) el._raf = requestAnimationFrame(tic);
  };
  tic();
}

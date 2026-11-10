// Sublime — le jeu
(function () {
  const $ = (id) => document.getElementById(id);
  const NV = 2; // version des grilles (les parties en cours d'avant sont remises à zéro)
  // Couleurs franches, aucune case pâle
  const COULEURS = ["#E5484D", "#F5A524", "#12A594", "#E93D82", "#3E63DD", "#8E4EC6", "#46A758", "#F76B15", "#0EA5E9", "#9A5B32"];
  const POISSONS_MAX = 3;

  // ---------- Les chats ----------
  // n : niveau à atteindre pour l'adopter
  const PELAGES = [
    { id: "roux", nom: "Filou", desc: "Roux tigré", n: 1, f: "#F28C38", r: "#C2551A", v: "#FFE7CF", y: "#7BC043", t: "#5A2C10" },
    { id: "noir", nom: "Ombre", desc: "Noir de minuit", n: 5, f: "#2E2A36", r: null, v: "#4A4456", y: "#F5C518", t: "#E9E3F0" },
    { id: "gris", nom: "Mistigri", desc: "Gris tigré", n: 12, f: "#9AA1AD", r: "#5F6673", v: "#E8ECF1", y: "#E9A23B", t: "#2E3138" },
    { id: "siam", nom: "Saphir", desc: "Siamois", n: 20, f: "#F3E6CF", r: null, v: "#6B4F3E", y: "#4FA3E0", t: "#3B2A20", masque: "#6B4F3E" },
    { id: "calico", nom: "Patchou", desc: "Tricolore", n: 30, f: "#FBF7F0", r: null, v: "#FFFFFF", y: "#58B368", t: "#3A3030", taches: ["#E8853D", "#2F2A2A"] },
    { id: "smoking", nom: "Gentleman", desc: "Chat smoking", n: 45, f: "#26232B", r: null, v: "#FFFFFF", y: "#7CC56B", t: "#E9E3F0" },
    { id: "blanc", nom: "Neige", desc: "Blanc aux yeux bleus", n: 60, f: "#FFFFFF", r: null, v: "#F4EEF6", y: "#5AA9E6", t: "#4B4452" },
    { id: "creme", nom: "Caramel", desc: "Crème", n: 80, f: "#F2C98A", r: "#D69A4C", v: "#FFF3DE", y: "#C27C2A", t: "#5B3A12" },
    { id: "bleu", nom: "Tsar", desc: "Bleu russe", n: 110, f: "#6F7F95", r: null, v: "#8D9BB0", y: "#5DCB6A", t: "#E8EDF4" },
    { id: "or", nom: "Pépite", desc: "Chat d'or", n: 150, f: "#F2C230", r: "#C9921A", v: "#FFF0B8", y: "#E5484D", t: "#5C3F00", brille: true },
    { id: "lune", nom: "Lunaire", desc: "Chat des étoiles", n: 200, f: "#3B2F7A", r: null, v: "#564A9E", y: "#7FE3F0", t: "#F4F0FF", etoiles: true },
    { id: "roi", nom: "Sa Majesté", desc: "Le roi des chats", n: 300, f: "#F28C38", r: "#C2551A", v: "#FFE7CF", y: "#7BC043", t: "#5A2C10", couronne: true },
  ];
  const pelage = (id) => PELAGES.find((p) => p.id === id) || PELAGES[0];

  // Un chat malicieux qui sort de sa cachette : paupières mi-closes, sourire en coin, petite dent
  function svgChat(id, cls) {
    const p = pelage(id);
    const t = p.t;
    let s = '<svg viewBox="0 0 100 100" class="chat ' + (cls || "") + '">';
    s += '<g class="tete">';
    // oreilles
    s += '<path d="M14 50 L19 9 L43 31Z" fill="' + p.f + '" stroke="rgba(30,20,35,.55)" stroke-width="2.4" stroke-linejoin="round"/><path d="M86 50 L81 9 L57 31Z" fill="' + p.f + '" stroke="rgba(30,20,35,.55)" stroke-width="2.4" stroke-linejoin="round"/>';
    s += '<path d="M21 20 L24 37 L35 30Z" fill="#F7A3B6"/><path d="M79 20 L76 37 L65 30Z" fill="#F7A3B6"/>';
    // tête
    s += '<ellipse cx="50" cy="60" rx="38" ry="32" fill="' + p.f + '" stroke="rgba(30,20,35,.55)" stroke-width="2.4" stroke-linejoin="round"/>';
    if (p.taches) s += '<path d="M20 44 Q30 30 44 34 Q42 50 26 54Z" fill="' + p.taches[0] + '"/><path d="M60 32 Q78 32 84 52 Q70 56 62 46Z" fill="' + p.taches[1] + '"/>';
    if (p.masque) s += '<ellipse cx="50" cy="68" rx="22" ry="17" fill="' + p.masque + '" opacity=".85"/>';
    if (p.r) s += '<path d="M50 31 L50 41 M41 33 L43 42 M59 33 L57 42 M14 60 L25 61 M15 68 L25 66 M86 60 L75 61 M85 68 L75 66" stroke="' + p.r + '" stroke-width="3.6" stroke-linecap="round"/>';
    if (p.etoiles) s += '<g fill="#FFF6B0"><circle cx="30" cy="42" r="1.6"/><circle cx="70" cy="40" r="1.3"/><circle cx="62" cy="80" r="1.2"/><circle cx="24" cy="74" r="1.4"/><path d="M50 36 l1.6 3.4 3.6.5-2.6 2.5.6 3.6-3.2-1.7-3.2 1.7.6-3.6-2.6-2.5 3.6-.5z"/></g>';
    // museau
    s += '<ellipse cx="50" cy="73" rx="15" ry="10.5" fill="' + p.v + '"/>';
    // yeux (gauche mi-clos, droit sourcil levé = air malicieux)
    const oeil = (cx, cl, paup, ligne) =>
      '<g class="' + cl + '"><ellipse cx="' + cx + '" cy="58" rx="8.6" ry="7.6" fill="' + p.y + '"/>' +
      '<ellipse cx="' + (cx + 0.8) + '" cy="58.6" rx="2.3" ry="5.8" fill="#16131A"/>' +
      '<circle cx="' + (cx + 3) + '" cy="55.4" r="1.8" fill="#fff"/>' +
      '<path d="' + paup + '" fill="' + p.f + '"/>' +
      '<path d="' + ligne + '" stroke="' + t + '" stroke-width="2" fill="none" stroke-linecap="round"/></g>';
    s += oeil(35, "og", "M25 55 Q35 49.5 45 55.5 L45 48 L25 48Z", "M25.5 55 Q35 49.8 44.5 55.5");
    s += oeil(65, "od", "M55 53.5 Q65 50.5 75 54 L75 47 L55 47Z", "M55.5 53.5 Q65 50.8 74.5 54");
    s += '<path d="M57 45 Q65 41 73 44" stroke="' + t + '" stroke-width="2" fill="none" stroke-linecap="round"/>';
    // nez, sourire en coin et petite dent
    s += '<path d="M46.2 68.5 L53.8 68.5 L50 72.8Z" fill="#F07A97"/>';
    s += '<path d="M50 72.8 Q46.5 78 41.5 76 M50 72.8 Q56 79.5 62.5 73.5" stroke="' + t + '" stroke-width="1.9" fill="none" stroke-linecap="round"/>';
    s += '<path d="M55.2 76.4 L56.6 80.4 L58.3 75.7Z" fill="#fff"/>';
    // moustaches
    s += '<path d="M33 72 L12 68 M33 76 L13 79 M67 72 L88 68 M67 76 L87 79" stroke="' + t + '" stroke-width="1.3" stroke-linecap="round" opacity=".55"/>';
    if (p.couronne) s += '<path d="M33 30 L36 14 L44 24 L50 10 L56 24 L64 14 L67 30Z" fill="#F5C518" stroke="#C9921A" stroke-width="1.5"/><circle cx="50" cy="22" r="2.2" fill="#E5484D"/>';
    if (p.brille) s += '<path d="M84 26 l2 5 5 2-5 2-2 5-2-5-5-2 5-2z" fill="#fff"/>';
    s += "</g>";
    // pattes posées sur le bord de la case : il se cache derrière
    s += '<g class="pattes"><ellipse cx="31" cy="95" rx="11" ry="7" fill="' + p.f + '" stroke="rgba(30,20,35,.55)" stroke-width="2.4" stroke-linejoin="round"/><ellipse cx="69" cy="95" rx="11" ry="7" fill="' + p.f + '" stroke="rgba(30,20,35,.55)" stroke-width="2.4" stroke-linejoin="round"/>' +
      '<path d="M27 91 L27 95 M31 90 L31 95 M35 91 L35 95 M65 91 L65 95 M69 90 L69 95 M73 91 L73 95" stroke="' + t + '" stroke-width="1.2" stroke-linecap="round" opacity=".5"/></g>';
    return s + "</svg>";
  }
  const SVG_POISSON =
    '<svg viewBox="0 0 60 36" class="poisson"><path d="M4 18 Q20 1 40 10 L56 2 L52 18 L56 34 L40 26 Q20 35 4 18Z" fill="#F2683C"/>' +
    '<path d="M22 9 Q27 18 22 27" stroke="#C44A22" stroke-width="2" fill="none"/><circle cx="13" cy="15" r="2.6" fill="#2B2233"/></svg>';
  const SVG_CROQ = '<svg viewBox="0 0 30 30"><path d="M15 3 C22 3 27 8 27 14 C27 22 21 27 15 27 C8 27 3 22 3 15 C3 8 8 3 15 3Z" fill="#C9822B"/><path d="M9 11 Q15 7 21 11 Q17 16 15 15 Q12 16 9 11Z" fill="#E3A552"/><circle cx="11" cy="19" r="1.6" fill="#8A5216"/><circle cx="19" cy="19" r="1.6" fill="#8A5216"/></svg>';
  const croix = (cls) =>
    '<svg viewBox="0 0 20 20" class="croix ' + cls + '"><path d="M4.5 4.5 L15.5 15.5 M15.5 4.5 L4.5 15.5" stroke="' +
    (cls === "err" ? "#5A0E0E" : cls === "aide" ? "#0E4A3C" : "#FFFFFF") + '" stroke-width="3.4" stroke-linecap="round"/></svg>';

  document.querySelectorAll(".chat-logo").forEach((e) => (e.innerHTML = svgChat("roux")));
  document.querySelectorAll(".ic-croq").forEach((e) => (e.innerHTML = SVG_CROQ));

  // ---------- Sons (fabriqués par le navigateur, aucun fichier) ----------
  let son = true;
  try { son = localStorage.getItem("sublime-son") !== "0"; } catch (e) {}
  let AC = null;
  function ctx() {
    if (!AC) { try { AC = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { return null; } }
    if (AC.state === "suspended") AC.resume();
    return AC;
  }
  function note(freq, debut, duree, type, vol, fin) {
    const a = ctx(); if (!a) return;
    const t = a.currentTime + debut;
    const o = a.createOscillator(), g = a.createGain();
    o.type = type || "sine";
    o.frequency.setValueAtTime(freq, t);
    if (fin) o.frequency.exponentialRampToValueAtTime(fin, t + duree);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol || 0.2, t + 0.012);
    g.gain.exponentialRampToValueAtTime(0.0001, t + duree);
    o.connect(g).connect(a.destination);
    o.start(t); o.stop(t + duree + 0.02);
  }
  function miaou(hauteur) {
    const a = ctx(); if (!a) return;
    const h = hauteur || 1, t = a.currentTime;
    const o = a.createOscillator(), o2 = a.createOscillator(), f = a.createBiquadFilter(), g = a.createGain();
    o.type = "sawtooth"; o2.type = "triangle";
    [o, o2].forEach((x, k) => {
      const m = k ? 2 : 1;
      x.frequency.setValueAtTime(520 * h * m, t);
      x.frequency.linearRampToValueAtTime(860 * h * m, t + 0.12);
      x.frequency.linearRampToValueAtTime(640 * h * m, t + 0.34);
    });
    f.type = "bandpass"; f.Q.value = 3;
    f.frequency.setValueAtTime(900, t); f.frequency.linearRampToValueAtTime(1800, t + 0.12); f.frequency.linearRampToValueAtTime(1100, t + 0.34);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.22, t + 0.04); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.38);
    o.connect(f); o2.connect(f); f.connect(g).connect(a.destination);
    o.start(t); o2.start(t); o.stop(t + 0.4); o2.stop(t + 0.4);
  }
  function miaouSi(h) { if (son) try { miaou(h); } catch (e) {} }
  const SONS = {
    croix: () => note(880, 0, 0.05, "triangle", 0.12),
    efface: () => note(520, 0, 0.05, "triangle", 0.1),
    chat: () => { note(660, 0, 0.08, "sine", 0.15, 990); miaou(1 + Math.random() * 0.15); },
    erreur: () => { note(240, 0, 0.25, "square", 0.08, 110); note(180, 0.05, 0.25, "sawtooth", 0.05, 90); },
    victoire: () => { [523, 659, 784, 1047, 1319].forEach((f, k) => note(f, k * 0.09, 0.22, "triangle", 0.16)); setTimeout(() => miaou(1.15), 520); },
    piece: () => { note(988, 0, 0.08, "square", 0.08); note(1319, 0.07, 0.18, "square", 0.08); },
    bonus: () => [784, 988, 1175].forEach((f, k) => note(f, k * 0.07, 0.16, "sine", 0.15)),
    clic: () => note(700, 0, 0.03, "sine", 0.08),
  };
  function joue(nom) { if (son && SONS[nom]) try { SONS[nom](); } catch (e) {} }
  // Vibrations : Android (vibrate) ; iPhone : petit retour haptique via un interrupteur caché
  function vibre(ms) {
    if (navigator.vibrate) { navigator.vibrate(ms); return; }
    try { $("haptique").click(); } catch (e) {}
  }
  function majSon() { $("btn-son").textContent = son ? "🔊" : "🔇"; }
  $("btn-son").addEventListener("click", () => {
    son = !son;
    try { localStorage.setItem("sublime-son", son ? "1" : "0"); } catch (e) {}
    majSon(); joue("clic");
  });
  majSon();

  // ---------- Compte ----------
  let jeton = null;
  let profil = null;
  try { jeton = localStorage.getItem("sublime-jeton"); } catch (e) {}

  async function api(chemin, corps) {
    const r = await fetch(chemin, {
      method: corps ? "POST" : "GET",
      headers: { "content-type": "application/json", ...(jeton ? { authorization: "Bearer " + jeton } : {}) },
      body: corps ? JSON.stringify(corps) : undefined,
      keepalive: !!corps,
    });
    const d = await r.json().catch(() => ({ erreur: "Réseau indisponible." }));
    if (!r.ok) throw Object.assign(new Error(d.erreur || "Erreur"), { code: r.status });
    return d;
  }

  async function entrer(action) {
    $("msg-connexion").textContent = "";
    const nom = $("nom").value.trim(), pin = $("pin").value.trim();
    if (!nom) return ($("msg-connexion").textContent = "Entre ton prénom.");
    if (!/^\d{4}$/.test(pin)) return ($("msg-connexion").textContent = "Le code PIN doit avoir 4 chiffres.");
    ctx();
    try {
      const d = await api("/api/" + action, { nom, pin });
      jeton = d.jeton;
      try { localStorage.setItem("sublime-jeton", jeton); } catch (e) {}
      await pret;
      demarrer(d.profil);
    } catch (e) {
      $("msg-connexion").textContent = e.message;
    }
  }
  $("form-connexion").addEventListener("submit", (e) => { e.preventDefault(); entrer("connexion"); });
  $("btn-inscription").addEventListener("click", () => entrer("inscription"));
  $("btn-deconnexion").addEventListener("click", async () => {
    await sauverMaintenant();
    try { await api("/api/deconnexion", {}); } catch (e) {}
    jeton = null; profil = null;
    try { localStorage.removeItem("sublime-jeton"); } catch (e) {}
    $("pin").value = "";
    montrer("ecran-connexion");
  });

  function montrer(id) {
    ["ecran-connexion", "ecran-app"].forEach((x) => $(x).classList.toggle("cache", x !== id));
  }

  // ---------- Onglets ----------
  let vue = "jeu";
  function allerA(v) {
    vue = v;
    const ong = v === "jeu" && mode === "jour" ? "jour" : v;
    document.querySelectorAll(".onglet").forEach((b) => b.classList.toggle("actif", b.dataset.vue === ong));
    ["jeu", "jour", "chats", "cafe"].forEach((x) => $("vue-" + x).classList.toggle("cache", x !== v));
    if (v === "jour") dessinerJour();
    if (v === "chats") dessinerCollection();
    if (v === "cafe") dessinerCafe();
    window.scrollTo(0, 0);
  }
  document.querySelectorAll(".onglet").forEach((b) =>
    b.addEventListener("click", () => {
      joue("clic");
      if (b.dataset.vue === "jeu" && mode === "jour") { sauverMaintenant(); chargerNiveau(); }
      allerA(b.dataset.vue);
    })
  );

  // ---------- Grilles ----------
  let NIVEAUX = [], JOUR = [];
  function decode(base, n, t) {
    const z0 = [...base.z].map((x) => parseInt(x, 16)), s0 = [...base.s].map((x) => parseInt(x, 16));
    const tr = (l, c) => {
      let a = l, b = c;
      if (t & 1) b = n - 1 - b;
      if (t & 2) a = n - 1 - a;
      if (t & 4) { const x = a; a = b; b = x; }
      return [a, b];
    };
    const z = new Array(n * n), sol = new Array(n);
    for (let l = 0; l < n; l++) for (let c = 0; c < n; c++) { const [a, b] = tr(l, c); z[a * n + b] = z0[l * n + c]; }
    for (let l = 0; l < n; l++) { const [a, b] = tr(l, s0[l]); sol[a] = b; }
    return { n, z, sol, d: base.d || 0 };
  }
  // Niveaux classés du plus facile au plus difficile ; au-delà, les plus durs reviennent retournés
  function grilleDuNiveau(niveau) {
    const L = NIVEAUX.length;
    if (niveau <= L) return decode(NIVEAUX[niveau - 1], 10, 0);
    const k = niveau - L - 1, durs = Math.floor(L / 3);
    return decode(NIVEAUX[L - durs + (k % durs)], 10, 1 + (Math.floor(k / durs) % 7));
  }
  function aujourdhui() { return new Intl.DateTimeFormat("fr-CA", { timeZone: "Europe/Zurich" }).format(new Date()); }
  function jourNumero(d) { return Math.round(Date.parse(d + "T12:00:00Z") / 86400000); }
  function hier(d) { return new Date(Date.parse(d + "T12:00:00Z") - 86400000).toISOString().slice(0, 10); }
  function grilleDuJour(d) { const k = jourNumero(d); return decode(JOUR[k % JOUR.length], 10, k % 8); }

  // ---------- Partie ----------
  let G = null; // grille
  let P = null; // état de la partie
  let mode = "niveau";

  // Aides offertes selon la difficulté de la grille : facile = rien, puis 1 astuce + 1 chat, 2 + 2, 3 + 3
  function aidesPour(d) { return d < 50 ? 0 : d < 100 ? 1 : d < 160 ? 2 : 3; }
  const dispo = (k) => ((P && P.aides && P.aides[k]) || 0) + (profil[k] || 0);
  function utiliser(k) { if (P.aides && P.aides[k] > 0) P.aides[k]--; else profil[k]--; }

  function nouvellePartie(niveau, recommence) {
    return { nv: NV, n: 10, niveau, croix: {}, chats: [], poissons: POISSONS_MAX, recommence: !!recommence, offerts: [] };
  }

  function demarrer(p) {
    profil = p;
    profil.stats = profil.stats || { reussis: 0, parfaits: 0 };
    profil.croquettes = profil.croquettes || 0;
    profil.deco = profil.deco || [];
    profil.jour = profil.jour || {};
    if (!profil.pelage || !estAdopte(profil.pelage)) profil.pelage = "roux";
    $("nom-joueur").textContent = profil.nom;
    montrer("ecran-app");
    majCroq();
    chargerNiveau();
    allerA("jeu");
  }

  function chargerNiveau() {
    mode = "niveau";
    let partie = profil.partie;
    if (!partie || partie.niveau !== profil.niveau || partie.nv !== NV) partie = nouvellePartie(profil.niveau, false);
    charger(partie);
  }
  function chargerJour() {
    mode = "jour";
    const d = aujourdhui();
    let partie = profil.jour.partie;
    if (!partie || partie.date !== d) partie = Object.assign(nouvellePartie(0, false), { date: d });
    charger(partie);
  }

  function charger(partie) {
    P = partie;
    G = mode === "jour" ? grilleDuJour(P.date) : grilleDuNiveau(P.niveau);
    historique.length = 0;
    let annonce = "";
    if (!P.aides) {
      const a = aidesPour(G.d);
      P.aides = { astuces: a, chats: a };
      if (a) annonce = "Grille plus corsée : " + a + " astuce" + (a > 1 ? "s" : "") + " et " + a + " chat" + (a > 1 ? "s" : "") + " offerts pour celle-ci.";
    }
    $("titre-niveau").textContent = mode === "jour" ? "Défi du jour" : "Niveau " + P.niveau;
    $("sous-titre").textContent = mode === "jour" ? dateLisible(P.date) : etiquette(P.niveau);
    $("msg-jeu").textContent = "";
    dessinerPlateau();
    majTout();
    if (annonce) info(annonce, 6000);
    if (P.poissons <= 0) perdu();
  }
  function dateLisible(d) { return new Date(d + "T12:00:00Z").toLocaleDateString("fr-CH", { weekday: "long", day: "numeric", month: "long" }); }
  function etiquette(n) {
    const prochain = PELAGES.find((p) => p.n > n);
    return prochain ? "Encore " + (prochain.n - n) + " niveau" + (prochain.n - n > 1 ? "x" : "") + " pour adopter " + prochain.nom : "Tous les chats sont adoptés";
  }

  function dessinerPlateau() {
    const n = G.n, pl = $("plateau");
    pl.classList.remove("gagne");
    pl.style.gridTemplateColumns = "repeat(" + n + ", 1fr)";
    pl.innerHTML = "";
    for (let i = 0; i < n * n; i++) {
      const d = document.createElement("div");
      d.className = "case";
      d.style.setProperty("--c", COULEURS[G.z[i] % COULEURS.length]);
      d.dataset.i = i;
      pl.appendChild(d);
    }
  }

  function majCase(i, anime) {
    const d = $("plateau").children[i];
    if (!d) return;
    if (P.chats.includes(i)) {
      if (d.querySelector(".chat") && !anime) return;
      d.innerHTML = svgChat(profil.pelage, P.offerts.includes(i) ? "offert" : "");
      const n = G.n;
      d.firstChild.style.setProperty("--d", Math.floor(i / n) + (i % n));
      if (!anime) d.firstChild.style.animation = "none";
    } else if (P.croix[i]) d.innerHTML = croix(P.croix[i] === 1 ? "" : P.croix[i]);
    else d.innerHTML = "";
  }

  function majTout() {
    for (let i = 0; i < G.n * G.n; i++) majCase(i, true);
    majPoissons();
    majBonus();
  }

  function majPoissons(touche) {
    let h = "";
    for (let k = 0; k < POISSONS_MAX; k++) h += SVG_POISSON.replace('class="poisson"', 'class="poisson' + (k >= P.poissons ? " perdu" : "") + (touche && k === P.poissons ? " touche" : "") + '"');
    $("poissons").innerHTML = h;
  }

  function majBonus() {
    $("nb-chats").textContent = dispo("chats");
    $("nb-astuces").textContent = dispo("astuces");
    $("btn-chat").classList.toggle("vide", !dispo("chats"));
    $("btn-astuce").classList.toggle("vide", !dispo("astuces"));
    document.querySelectorAll(".chat-mini").forEach((e) => (e.innerHTML = svgChat(profil.pelage)));
  }
  function majCroq(gain) {
    $("nb-croq").textContent = profil.croquettes;
    if (gain) { const c = $("croquettes"); c.classList.remove("gain"); void c.offsetWidth; c.classList.add("gain"); }
  }

  // Les chats posés font des bêtises : ils clignent, font un clin d'œil, se cachent un instant
  setInterval(() => {
    if (!P || vue !== "jeu" || document.hidden) return;
    const chats = [...document.querySelectorAll("#plateau .chat")];
    if (!chats.length) return;
    const c = chats[Math.floor(Math.random() * chats.length)];
    const r = Math.random();
    const cls = r < 0.5 ? "cligne" : r < 0.8 ? "clin" : "cache-toi";
    c.style.animation = "";
    c.classList.remove("cligne", "clin", "cache-toi");
    void c.getBoundingClientRect();
    c.classList.add(cls);
    setTimeout(() => c.classList.remove(cls), 1200);
  }, 2200);

  // ---------- Gestes ----------
  let dernier = { i: -1, t: 0, effet: null };
  const historique = [];

  $("plateau").addEventListener("pointerup", (e) => {
    const d = e.target.closest(".case");
    if (!d || !P || fini()) return;
    ctx();
    const i = +d.dataset.i, t = Date.now();
    if (dernier.i === i && t - dernier.t < 330) {
      if (dernier.effet) annulerEffet(dernier.effet, false);
      dernier = { i: -1, t: 0, effet: null };
      poserChat(i);
      return;
    }
    let effet;
    if (P.chats.includes(i)) {
      P.chats = P.chats.filter((x) => x !== i);
      P.offerts = P.offerts.filter((x) => x !== i);
      effet = { type: "chat", i };
      joue("efface");
    } else if (P.croix[i]) {
      effet = { type: "croix", i, avant: P.croix[i] };
      delete P.croix[i];
      joue("efface");
    } else {
      effet = { type: "croix", i, avant: 0 };
      P.croix[i] = 1;
      joue("croix");
    }
    historique.push(effet);
    dernier = { i, t, effet };
    majCase(i, true);
    sauver();
  });

  function annulerEffet(ef, depuisHistorique) {
    if (!depuisHistorique) {
      const k = historique.lastIndexOf(ef);
      if (k >= 0) historique.splice(k, 1);
    }
    if (ef.type === "croix") {
      if (ef.avant) P.croix[ef.i] = ef.avant; else delete P.croix[ef.i];
    } else if (ef.type === "chat") {
      if (P.chats.includes(ef.i)) P.chats = P.chats.filter((x) => x !== ef.i);
      else P.chats.push(ef.i);
    } else if (ef.type === "pose") {
      P.chats = P.chats.filter((x) => x !== ef.i);
      if (ef.avant) P.croix[ef.i] = ef.avant;
    }
    majCase(ef.i, true);
  }

  $("btn-annuler").addEventListener("click", () => {
    if (!P || fini()) return;
    const ef = historique.pop();
    if (!ef) return info("Rien à annuler.");
    joue("clic");
    annulerEffet(ef, true);
    sauver();
  });

  function poserChat(i) {
    if (P.chats.includes(i)) return;
    const n = G.n, l = Math.floor(i / n), c = i % n;
    if (G.sol[l] === c) {
      const avant = P.croix[i] || 0;
      delete P.croix[i];
      P.chats.push(i);
      historique.push({ type: "pose", i, avant });
      majCase(i, true);
      joue("chat");
      vibre(25);
      if (P.chats.length === n) return gagne();
    } else {
      P.poissons--;
      P.croix[i] = "err";
      majCase(i, true);
      const d = $("plateau").children[i];
      d.classList.remove("non"); void d.offsetWidth; d.classList.add("non");
      majPoissons(true);
      joue("erreur");
      vibre(140);
      if (P.poissons <= 0) { sauver(); return setTimeout(perdu, 450); }
      const moqueries = ["Raté, il n'est pas là !", "Ce coquin se cache ailleurs…", "Pas ici ! Il rigole dans son coin."];
      info(moqueries[Math.floor(Math.random() * moqueries.length)] + " Il te reste " + P.poissons + (P.poissons > 1 ? " poissons." : " poisson."));
    }
    sauver();
  }

  function fini() { return P.chats.length === G.n || P.poissons <= 0; }

  // ---------- Bonus ----------
  $("btn-chat").addEventListener("click", () => {
    if (!P || fini()) return;
    if (!dispo("chats")) return info("Pas de chat gratuit. Réussis un niveau sans perdre de poisson pour en gagner un.");
    const n = G.n;
    const libres = [];
    for (let k = 0; k < n; k++) if (!P.chats.some((i) => G.z[i] === k)) libres.push(k);
    if (!libres.length) return;
    const k = libres[Math.floor(Math.random() * libres.length)];
    let cible = -1;
    for (let l = 0; l < n; l++) if (G.z[l * n + G.sol[l]] === k) cible = l * n + G.sol[l];
    utiliser("chats");
    delete P.croix[cible];
    P.chats.push(cible);
    P.offerts.push(cible);
    majCase(cible, true);
    majBonus();
    joue("bonus"); setTimeout(() => miaouSi(1.2), 250);
    info("Un chat sort de sa cachette pour toi !");
    if (P.chats.length === n) return gagne();
    sauverMaintenant();
  });

  $("btn-astuce").addEventListener("click", () => {
    if (!P || fini()) return;
    if (!dispo("astuces")) return info("Pas d'astuce. Réussis un niveau sans recommencer pour en gagner une.");
    const n = G.n;
    const oubliees = new Set();
    for (const i of P.chats) {
      const l = Math.floor(i / n), c = i % n, k = G.z[i];
      for (let j = 0; j < n * n; j++) {
        const lj = Math.floor(j / n), cj = j % n;
        if (j === i) continue;
        if (lj === l || cj === c || G.z[j] === k || (Math.abs(lj - l) <= 1 && Math.abs(cj - c) <= 1)) oubliees.add(j);
      }
    }
    const cand = [...oubliees].filter((j) => !P.croix[j] && !P.chats.includes(j));
    let marquees = [];
    if (cand.length) {
      marquees = [cand[Math.floor(Math.random() * cand.length)]];
      info("Tu as oublié une croix ici.");
    } else {
      let meilleur = -1, liste = [];
      for (let k = 0; k < n; k++) {
        if (P.chats.some((i) => G.z[i] === k)) continue;
        const ouvertes = [];
        for (let j = 0; j < n * n; j++) {
          const lj = Math.floor(j / n);
          if (G.z[j] === k && G.sol[lj] !== j % n && !P.croix[j]) ouvertes.push(j);
        }
        if (ouvertes.length > meilleur) { meilleur = ouvertes.length; liste = ouvertes; }
      }
      if (meilleur <= 0) return info("Rien à révéler : tout est déjà juste.");
      liste.sort(() => Math.random() - 0.5);
      marquees = liste.length >= 2 ? liste.slice(0, liste.length - 1) : liste;
      info(marquees.length + (marquees.length > 1 ? " croix posées" : " croix posée") + " dans une couleur.");
    }
    utiliser("astuces");
    joue("bonus");
    for (const j of marquees) { P.croix[j] = "aide"; majCase(j, true); historique.push({ type: "croix", i: j, avant: 0 }); }
    majBonus();
    sauverMaintenant();
  });

  // ---------- Fin de partie ----------
  function fete() {
    const f = $("fete"), objets = ["🐟", "🐾", "✨", "🧶", "🐟", "⭐"];
    for (let k = 0; k < 28; k++) {
      const e = document.createElement("i");
      e.textContent = objets[k % objets.length];
      e.style.left = Math.random() * 100 + "vw";
      e.style.animationDuration = 1.6 + Math.random() * 1.6 + "s";
      e.style.animationDelay = Math.random() * 0.6 + "s";
      f.appendChild(e);
      setTimeout(() => e.remove(), 4200);
    }
  }
  const gainsHtml = (croq, extra) =>
    '<div class="gains"><span><span class="ic-croq">' + SVG_CROQ + "</span>+" + croq + "</span>" + (extra ? "<span>" + extra + "</span>" : "") + "</div>";

  function gagne() {
    $("plateau").classList.add("gagne");
    for (let i = 0; i < G.n * G.n; i++) if (P.chats.includes(i)) { const c = $("plateau").children[i].firstChild; if (c) c.style.animation = ""; }
    joue("victoire");
    vibre(60);
    fete();
    if (mode === "jour") return gagneJour();
    let titre = "Bravo !", texte, extra = "";
    let croq = 10;
    profil.stats.reussis++;
    if (P.recommence) {
      croq = 5;
      texte = "Niveau réussi. Moins de récompense, car tu as recommencé.";
    } else if (P.poissons === POISSONS_MAX) {
      profil.chats++;
      profil.stats.parfaits++;
      croq = 15;
      titre = "Parfait !";
      texte = "Sans perdre un seul poisson !";
      extra = "+1 chat gratuit";
    } else {
      profil.astuces++;
      texte = "Réussi sans recommencer.";
      extra = "+1 astuce 💡";
    }
    profil.croquettes += croq;
    const avant = profil.niveau;
    profil.niveau = P.niveau + 1;
    const adopte = PELAGES.find((p) => p.n > avant && p.n <= profil.niveau);
    historique.length = 0;
    const suivante = nouvellePartie(profil.niveau, false);
    P.fin = true;
    profil.partie = suivante;
    sauverMaintenant(suivante);
    majBonus();
    setTimeout(() => {
      majCroq(true);
      voile(svgChat(profil.pelage), titre, texte, "Niveau suivant", () => {
        if (adopte) annonceAdoption(adopte, () => charger(suivante));
        else charger(suivante);
      }, null, gainsHtml(croq, extra));
    }, 900);
  }

  function annonceAdoption(p, ensuite) {
    joue("bonus"); setTimeout(() => miaouSi(0.95), 300);
    fete();
    voile(svgChat(p.id), "Nouveau chat adopté !", p.nom + ", " + p.desc.toLowerCase() + ", rejoint ta bande. Fais-le jouer dans la grille ?", "Oui, je le prends",
      () => { profil.pelage = p.id; sauverMaintenant(); majBonus(); ensuite(); }, "Plus tard", null, ensuite);
  }

  function gagneJour() {
    const d = P.date, j = profil.jour;
    let croq = 20 + (P.poissons === POISSONS_MAX ? 10 : 0);
    if (j.fait !== d) {
      j.serie = j.derniere === hier(d) ? (j.serie || 0) + 1 : 1;
      j.derniere = d;
      j.fait = d;
      croq += Math.min(30, (j.serie - 1) * 5);
      profil.croquettes += croq;
    } else croq = 0;
    j.partie = null;
    P.fin = true;
    sauverMaintenant();
    setTimeout(() => {
      majCroq(true);
      voile(svgChat(profil.pelage), "Défi réussi !", "Série de " + j.serie + " jour" + (j.serie > 1 ? "s" : "") + " d'affilée. Reviens demain pour un nouveau défi.", "Retour aux niveaux",
        () => { chargerNiveau(); allerA("jeu"); }, null, croq ? gainsHtml(croq, "🔥 " + j.serie) : "");
    }, 900);
  }

  function perdu() {
    joue("erreur");
    voile(SVG_POISSON.replace('class="poisson"', 'class="poisson perdu"'), "Plus de poissons", "Les chats se sont bien moqués de toi ! Recommence : la récompense sera plus petite.", "Recommencer", () => recommencer());
  }

  function recommencer() {
    historique.length = 0;
    const p = nouvellePartie(P.niveau, true);
    if (mode === "jour") p.date = P.date;
    charger(p);
    sauver();
  }

  $("btn-recommencer").addEventListener("click", () => {
    if (!P || fini()) return;
    voile('<span style="font-size:56px">⟲</span>', "Recommencer ?", "Si tu recommences, la récompense sera plus petite.", "Recommencer", () => recommencer(), "Continuer");
  });

  function voile(icone, titre, texte, bouton, action, bouton2, extraHtml, action2) {
    $("voile-icone").innerHTML = icone;
    $("voile-titre").textContent = titre;
    $("voile-texte").textContent = texte;
    const ancien = document.querySelector(".carte .gains"); if (ancien) ancien.remove();
    if (extraHtml) $("voile-texte").insertAdjacentHTML("afterend", extraHtml);
    $("voile-btn").textContent = bouton;
    $("voile-btn").onclick = () => { $("voile").classList.add("cache"); joue("clic"); action(); };
    $("voile-btn2").classList.toggle("cache", !bouton2);
    $("voile-btn2").textContent = bouton2 || "";
    $("voile-btn2").onclick = () => { $("voile").classList.add("cache"); if (action2) action2(); };
    $("voile").classList.remove("cache");
  }

  let minuterieInfo;
  function info(t, duree) {
    $("msg-jeu").textContent = t;
    clearTimeout(minuterieInfo);
    minuterieInfo = setTimeout(() => ($("msg-jeu").textContent = ""), duree || 3500);
  }

  // ---------- Défi du jour ----------
  function dessinerJour() {
    const d = aujourdhui(), j = profil.jour;
    $("jour-chat").innerHTML = svgChat(profil.pelage);
    const serie = j.derniere === d || j.derniere === hier(d) ? j.serie || 0 : 0;
    $("jour-serie").textContent = serie ? "🔥 Série : " + serie + " jour" + (serie > 1 ? "s" : "") : "";
    if (j.fait === d) {
      $("jour-texte").textContent = "Bravo, le défi d'aujourd'hui est réussi. Un nouveau défi arrive demain.";
      $("btn-jour").textContent = "Déjà réussi aujourd'hui";
      $("btn-jour").disabled = true;
    } else {
      $("jour-texte").textContent = "Une grille spéciale, la même pour tout le monde, chaque jour. 20 croquettes à gagner, plus un bonus si tu joues plusieurs jours de suite.";
      $("btn-jour").textContent = j.partie && j.partie.date === d ? "Continuer le défi" : "Jouer le défi";
      $("btn-jour").disabled = false;
    }
  }
  $("btn-jour").addEventListener("click", () => { joue("clic"); if (mode === "niveau") sauverMaintenant(); chargerJour(); allerA("jeu"); });

  // ---------- Collection ----------
  function estAdopte(id) { return profil && pelage(id).n <= profil.niveau; }
  function dessinerCollection() {
    $("collection").innerHTML = PELAGES.map((p) => {
      const ok = estAdopte(p.id);
      return '<div class="fiche' + (ok ? "" : " verrou") + (profil.pelage === p.id ? " choisi" : "") + '" data-id="' + p.id + '">' +
        '<div class="portrait">' + svgChat(p.id) + "</div><b>" + (ok ? p.nom : "???") + "</b><small>" + (ok ? p.desc : "Niveau " + p.n) + "</small></div>";
    }).join("");
  }
  $("collection").addEventListener("click", (e) => {
    const f = e.target.closest(".fiche");
    if (!f) return;
    const p = pelage(f.dataset.id);
    if (!estAdopte(p.id)) { joue("erreur"); return; }
    profil.pelage = p.id;
    miaouSi(0.9 + Math.random() * 0.3);
    const c = f.querySelector(".chat"); c.classList.add("clin"); setTimeout(() => c.classList.remove("clin"), 700);
    dessinerCollection();
    majBonus();
    sauverMaintenant();
  });

  // ---------- Café des chats ----------
  const DECO = [
    { id: "tapis", nom: "Tapis rond", emo: "🟠", prix: 30 },
    { id: "plante", nom: "Grande plante", emo: "🪴", prix: 40 },
    { id: "lampe", nom: "Lampe douce", emo: "💡", prix: 50 },
    { id: "coussin", nom: "Coussins", emo: "🛋️", prix: 60 },
    { id: "tableau", nom: "Tableau", emo: "🖼️", prix: 80 },
    { id: "arbre", nom: "Arbre à chat", emo: "🐾", prix: 120 },
    { id: "aquarium", nom: "Aquarium", emo: "🐠", prix: 160 },
    { id: "guirlande", nom: "Guirlande", emo: "✨", prix: 200 },
  ];
  const DESSINS = {
    tapis: '<ellipse cx="180" cy="262" rx="110" ry="22" fill="#F2683C"/><ellipse cx="180" cy="262" rx="80" ry="15" fill="#F9B48C"/>',
    plante: '<rect x="290" y="200" width="36" height="40" rx="6" fill="#C2551A"/><path d="M308 200 Q280 150 296 120 Q306 160 308 200 Q312 140 334 118 Q336 165 308 200 Q330 170 352 160 Q338 195 308 200" fill="#46A758"/>',
    lampe: '<rect x="56" y="140" width="4" height="100" fill="#5B4636"/><path d="M38 140 L78 140 L68 112 L48 112Z" fill="#F5C518"/><ellipse cx="58" cy="244" rx="16" ry="5" fill="#5B4636"/><circle cx="58" cy="150" r="30" fill="#FFF3B0" opacity=".35"/>',
    coussin: '<ellipse cx="120" cy="246" rx="30" ry="12" fill="#8E4EC6"/><ellipse cx="240" cy="248" rx="30" ry="12" fill="#12A594"/>',
    tableau: '<rect x="150" y="40" width="70" height="52" rx="4" fill="#9A5B32"/><rect x="156" y="46" width="58" height="40" fill="#7FC8F8"/><path d="M156 86 L176 66 L190 78 L200 70 L214 86Z" fill="#46A758"/><circle cx="202" cy="56" r="5" fill="#F5C518"/>',
    arbre: '<rect x="20" y="170" width="12" height="70" fill="#D9B48C"/><rect x="10" y="236" width="40" height="8" rx="3" fill="#B98A5C"/><rect x="6" y="160" width="44" height="12" rx="5" fill="#B98A5C"/><rect x="26" y="120" width="10" height="44" fill="#D9B48C"/><rect x="14" y="112" width="36" height="10" rx="5" fill="#B98A5C"/>',
    aquarium: '<rect x="250" y="70" width="80" height="54" rx="6" fill="#9FD8F5" stroke="#3E63DD" stroke-width="3"/><path d="M270 96 q8 -8 16 0 q-8 8 -16 0 l-6 -5 l0 10z" fill="#F76B15"/><path d="M300 108 q6 -6 12 0 q-6 6 -12 0 l-5 -4 l0 8z" fill="#E93D82"/><rect x="246" y="124" width="88" height="8" rx="2" fill="#5B4636"/>',
    guirlande: '<path d="M0 22 Q90 52 180 22 Q270 52 360 22" stroke="#5B4636" stroke-width="2" fill="none"/>' + [30, 75, 120, 165, 210, 255, 300, 340].map((x, k) => '<circle cx="' + x + '" cy="' + (30 + Math.round(10 * Math.sin((x / 360) * Math.PI * 2 - 0.2) * -1)) + '" r="6" fill="' + COULEURS[k] + '"/>').join(""),
  };
  // Places des chats dans le café
  const PLACES = [[150, 214], [205, 214], [100, 214], [255, 214], [22, 76], [16, 128], [268, 168], [60, 214], [300, 214], [180, 120], [120, 160], [230, 160]];
  function dessinerCafe() {
    const adoptes = PELAGES.filter((p) => estAdopte(p.id));
    let s = '<svg viewBox="0 0 360 290" xmlns="http://www.w3.org/2000/svg">';
    s += '<rect width="360" height="240" fill="#FFE2C4"/><rect y="0" width="360" height="240" fill="url(#papier)"/>';
    s += '<defs><pattern id="papier" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="12" cy="12" r="2" fill="#F9C9A0"/></pattern></defs>';
    s += '<rect x="96" y="40" width="40" height="70" rx="20" fill="#BFE6FF" stroke="#fff" stroke-width="5"/>';
    s += '<rect y="236" width="360" height="54" fill="#C98B55"/><path d="M0 250 H360 M0 268 H360" stroke="#B57A47" stroke-width="2"/>';
    for (const d of DECO) if (profil.deco.includes(d.id)) s += DESSINS[d.id];
    adoptes.forEach((p, k) => {
      const [x, y] = PLACES[k % PLACES.length];
      s += '<g class="chat-cafe" data-id="' + p.id + '" transform="translate(' + x + "," + y + ')">' + svgChat(p.id).replace("<svg ", '<svg width="46" height="46" ') + "</g>";
    });
    if (!profil.deco.length) s += '<text x="180" y="150" text-anchor="middle" font-size="15" fill="#9C7A5C" font-family="inherit">Le café est encore vide…</text>';
    s += "</svg>";
    $("cafe").innerHTML = s;
    $("boutique").innerHTML = DECO.map((d) => {
      const a = profil.deco.includes(d.id);
      return '<button class="article' + (a ? " achete" : profil.croquettes < d.prix ? " trop-cher" : "") + '" data-id="' + d.id + '"><span class="emo">' + d.emo + "</span><span><b>" + d.nom + "</b><small>" +
        (a ? "Installé ✓" : '<span class="ic-croq">' + SVG_CROQ + "</span>" + d.prix) + "</small></span></button>";
    }).join("");
  }
  $("cafe").addEventListener("click", (e) => {
    const g = e.target.closest(".chat-cafe");
    if (!g) return;
    miaouSi(0.85 + Math.random() * 0.4);
    const c = g.querySelector(".chat"); c.classList.add("clin"); setTimeout(() => c.classList.remove("clin"), 700);
  });
  $("boutique").addEventListener("click", (e) => {
    const b = e.target.closest(".article");
    if (!b) return;
    const d = DECO.find((x) => x.id === b.dataset.id);
    if (profil.deco.includes(d.id)) return;
    if (profil.croquettes < d.prix) { joue("erreur"); return; }
    profil.croquettes -= d.prix;
    profil.deco.push(d.id);
    joue("piece");
    majCroq(true);
    dessinerCafe();
    sauverMaintenant();
  });

  // ---------- Sauvegarde ----------
  let minuterieSauve;
  function sauver() {
    clearTimeout(minuterieSauve);
    minuterieSauve = setTimeout(() => sauverMaintenant(), 800);
  }
  async function sauverMaintenant(partieNiveau) {
    clearTimeout(minuterieSauve);
    if (!jeton || !profil) return;
    if (mode === "niveau" && !partieNiveau && P) profil.partie = P.fin ? null : P;
    if (partieNiveau) profil.partie = partieNiveau;
    if (mode === "jour" && P) profil.jour.partie = P.fin ? null : P;
    try {
      await api("/api/sauver", {
        niveau: profil.niveau, chats: profil.chats, astuces: profil.astuces, stats: profil.stats,
        croquettes: profil.croquettes, pelage: profil.pelage, deco: profil.deco, jour: profil.jour,
        partie: profil.partie || null,
      });
    } catch (e) {
      if (e.code === 401) { jeton = null; montrer("ecran-connexion"); }
    }
  }
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") sauverMaintenant(); });

  // ---------- Démarrage ----------
  const pret = Promise.all([
    fetch("/niveaux.json?v=3").then((r) => r.json()).then((d) => (NIVEAUX = d)),
    fetch("/jour.json?v=1").then((r) => r.json()).then((d) => (JOUR = d)),
  ]);
  if (jeton) {
    pret.then(() => api("/api/profil")).then((d) => demarrer(d.profil)).catch(() => { jeton = null; montrer("ecran-connexion"); });
  } else montrer("ecran-connexion");

  // Pas de zoom (iPhone ignore user-scalable=no)
  ["gesturestart", "gesturechange", "gestureend"].forEach((t) => document.addEventListener(t, (e) => e.preventDefault(), { passive: false }));
  document.addEventListener("touchmove", (e) => { if (e.touches.length > 1) e.preventDefault(); }, { passive: false });
  document.addEventListener("dblclick", (e) => e.preventDefault(), { passive: false });

  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
})();

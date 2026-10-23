// Sublime — le jeu
(function () {
  const $ = (id) => document.getElementById(id);
  const COULEURS = ["#CF7472", "#E0BC57", "#67B3AC", "#EEB4CC", "#7FB8E3", "#9480D1", "#5F72AE", "#AFC0D4", "#F2AE76", "#A9D08E", "#B98E73", "#3F9A80"];
  const POISSONS_MAX = 3;

  const SVG_CHAT =
    '<svg viewBox="0 0 100 100" class="chat"><path d="M17 44 L20 10 L41 28 Q50 26 59 28 L80 10 L83 44 Q91 60 81 75 Q68 91 50 91 Q32 91 19 75 Q9 60 17 44Z" fill="#2E2638"/>' +
    '<path d="M24 22 L27 36 L35 30Z M76 22 L73 36 L65 30Z" fill="#F4A6B5"/>' +
    '<ellipse cx="37" cy="54" rx="7" ry="8.5" fill="#FFE9A8"/><ellipse cx="63" cy="54" rx="7" ry="8.5" fill="#FFE9A8"/>' +
    '<ellipse cx="38" cy="55" rx="3" ry="6" fill="#2E2638"/><ellipse cx="62" cy="55" rx="3" ry="6" fill="#2E2638"/>' +
    '<path d="M46 67 L54 67 L50 72Z" fill="#F4A6B5"/>' +
    '<path d="M50 72 Q46 78 41 76 M50 72 Q54 78 59 76" stroke="#FBF5EC" stroke-width="2" fill="none" stroke-linecap="round"/>' +
    '<path d="M30 67 L12 64 M30 71 L13 74 M70 67 L88 64 M70 71 L87 74" stroke="#FBF5EC" stroke-width="1.6" stroke-linecap="round"/></svg>';
  const SVG_POISSON =
    '<svg viewBox="0 0 60 36" class="poisson"><path d="M4 18 Q20 1 40 10 L56 2 L52 18 L56 34 L40 26 Q20 35 4 18Z" fill="#E8845A"/>' +
    '<path d="M22 9 Q27 18 22 27" stroke="#C96A42" stroke-width="2" fill="none"/><circle cx="13" cy="15" r="2.6" fill="#2E2638"/></svg>';
  const croix = (cls) =>
    '<svg viewBox="0 0 20 20" class="croix ' + cls + '"><path d="M4 4 L16 16 M16 4 L4 16" stroke="' +
    (cls === "err" ? "#D9534F" : cls === "aide" ? "#3E8E7E" : "#2E2638") + '" stroke-width="' + (cls ? 3.4 : 2.6) + '" stroke-linecap="round"/></svg>';

  document.querySelectorAll(".chat-logo, .chat-mini").forEach((e) => (e.innerHTML = SVG_CHAT));

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
    ["ecran-connexion", "ecran-jeu"].forEach((x) => $(x).classList.toggle("cache", x !== id));
  }

  // ---------- Partie ----------
  let G = null; // grille
  let P = null; // état de la partie

  // Grilles 12×12 pré-calculées (niveaux.json), retournées/miroir au-delà pour varier à l'infini
  let NIVEAUX = [];
  function grilleDuNiveau(niveau) {
    const n = 12, base = NIVEAUX[(niveau - 1) % NIVEAUX.length];
    const t = Math.floor((niveau - 1) / NIVEAUX.length) % 8;
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
    return { n, z, sol, niveau };
  }

  function nouvellePartie(niveau, recommence) {
    return { n: 12, niveau, croix: {}, chats: [], poissons: POISSONS_MAX, recommence: !!recommence, offerts: [] };
  }

  function demarrer(p) {
    profil = p;
    profil.stats = profil.stats || { reussis: 0, parfaits: 0 };
    $("nom-joueur").textContent = profil.nom;
    montrer("ecran-jeu");
    let partie = profil.partie;
    if (!partie || partie.niveau !== profil.niveau || partie.n !== 12) partie = nouvellePartie(profil.niveau, false);
    charger(partie);
  }

  function charger(partie) {
    P = partie;
    G = grilleDuNiveau(P.niveau);
    $("titre-niveau").textContent = "Niveau " + P.niveau;
    $("msg-jeu").textContent = "";
    dessinerPlateau();
    majTout();
    if (P.poissons <= 0) perdu();
  }

  function dessinerPlateau() {
    const n = G.n, pl = $("plateau");
    pl.classList.remove("gagne");
    pl.style.gridTemplateColumns = "repeat(" + n + ", 1fr)";
    pl.innerHTML = "";
    for (let i = 0; i < n * n; i++) {
      const k = G.z[i];
      const d = document.createElement("div");
      d.className = "case";
      d.style.background = COULEURS[k % COULEURS.length];
      d.dataset.i = i;
      pl.appendChild(d);
    }
  }

  function majCase(i) {
    const d = $("plateau").children[i];
    if (!d) return;
    if (P.chats.includes(i)) d.innerHTML = SVG_CHAT.replace('class="chat"', 'class="chat' + (P.offerts.includes(i) ? " offert" : "") + '"');
    else if (P.croix[i]) d.innerHTML = croix(P.croix[i] === 1 ? "" : P.croix[i]);
    else d.innerHTML = "";
  }

  function majTout() {
    for (let i = 0; i < G.n * G.n; i++) majCase(i);
    majPoissons();
    majBonus();
  }

  function majPoissons(touche) {
    let h = "";
    for (let k = 0; k < POISSONS_MAX; k++) h += SVG_POISSON.replace('class="poisson"', 'class="poisson' + (k >= P.poissons ? " perdu" : "") + (touche && k === P.poissons ? " touche" : "") + '"');
    $("poissons").innerHTML = h;
  }

  function majBonus() {
    $("nb-chats").textContent = profil.chats;
    $("nb-astuces").textContent = profil.astuces;
    $("btn-chat").classList.toggle("vide", !profil.chats);
    $("btn-astuce").classList.toggle("vide", !profil.astuces);
  }

  // ---------- Gestes ----------
  let dernier = { i: -1, t: 0, effet: null };
  const historique = [];

  $("plateau").addEventListener("pointerup", (e) => {
    const d = e.target.closest(".case");
    if (!d || !P || fini()) return;
    const i = +d.dataset.i, t = Date.now();
    if (dernier.i === i && t - dernier.t < 330) {
      // double touche : on annule l'effet de la première touche puis on pose le chat
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
    } else if (P.croix[i]) {
      effet = { type: "croix", i, avant: P.croix[i] };
      delete P.croix[i];
    } else {
      effet = { type: "croix", i, avant: 0 };
      P.croix[i] = 1;
    }
    historique.push(effet);
    dernier = { i, t, effet };
    majCase(i);
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
    majCase(ef.i);
  }

  $("btn-annuler").addEventListener("click", () => {
    if (!P || fini()) return;
    const ef = historique.pop();
    if (!ef) return info("Rien à annuler.");
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
      majCase(i);
      if (P.chats.length === n) return gagne();
    } else {
      P.poissons--;
      P.croix[i] = "err";
      majCase(i);
      majPoissons(true);
      if (navigator.vibrate) navigator.vibrate(120);
      if (P.poissons <= 0) { sauver(); return setTimeout(perdu, 450); }
      info("Raté ! Il te reste " + P.poissons + (P.poissons > 1 ? " poissons." : " poisson."));
    }
    sauver();
  }

  function fini() { return P.chats.length === G.n || P.poissons <= 0; }

  // ---------- Bonus ----------
  $("btn-chat").addEventListener("click", () => {
    if (!P || fini()) return;
    if (!profil.chats) return info("Pas de chat gratuit. Réussis un niveau sans perdre de poisson pour en gagner un.");
    const n = G.n;
    const libres = [];
    for (let k = 0; k < n; k++) if (!P.chats.some((i) => G.z[i] === k)) libres.push(k);
    if (!libres.length) return;
    const k = libres[Math.floor(Math.random() * libres.length)];
    let cible = -1;
    for (let l = 0; l < n; l++) if (G.z[l * n + G.sol[l]] === k) cible = l * n + G.sol[l];
    profil.chats--;
    delete P.croix[cible];
    P.chats.push(cible);
    P.offerts.push(cible);
    majCase(cible);
    majBonus();
    info("Un chat t'est offert !");
    if (P.chats.length === n) return gagne();
    sauverMaintenant();
  });

  // Astuce : d'abord une case oubliée ; sinon des croix dans une couleur
  $("btn-astuce").addEventListener("click", () => {
    if (!P || fini()) return;
    if (!profil.astuces) return info("Pas d'astuce. Réussis un niveau sans recommencer pour en gagner une.");
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
      // couleur sans chat avec le plus de cases encore ouvertes
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
    profil.astuces--;
    for (const j of marquees) { P.croix[j] = "aide"; majCase(j); historique.push({ type: "croix", i: j, avant: 0 }); }
    majBonus();
    sauverMaintenant();
  });

  // ---------- Fin de niveau ----------
  function gagne() {
    $("plateau").classList.add("gagne");
    let titre = "Bravo !", texte, icone = SVG_CHAT;
    profil.stats.reussis++;
    if (P.recommence) {
      texte = "Niveau réussi. Pas de récompense, car tu as recommencé.";
    } else if (P.poissons === POISSONS_MAX) {
      profil.chats++;
      profil.stats.parfaits++;
      titre = "Parfait !";
      texte = "Sans perdre un seul poisson. Tu gagnes 1 chat gratuit.";
    } else {
      profil.astuces++;
      icone = '<span style="font-size:60px">💡</span>';
      texte = "Réussi sans recommencer. Tu gagnes 1 astuce.";
    }
    profil.niveau = P.niveau + 1;
    historique.length = 0;
    const suivante = nouvellePartie(profil.niveau, false);
    P.fin = true;
    sauverMaintenant(suivante);
    majBonus();
    setTimeout(() => voile(icone, titre, texte, "Niveau suivant", () => charger(suivante)), 650);
  }

  function perdu() {
    voile(SVG_POISSON.replace('class="poisson"', 'class="poisson perdu"'), "Plus de poissons", "Tu as perdu tes 3 poissons. Recommence ce niveau : il ne donnera pas de récompense.", "Recommencer", () => recommencer());
  }

  function recommencer() {
    historique.length = 0;
    charger(nouvellePartie(P.niveau, true));
    sauver();
  }

  $("btn-recommencer").addEventListener("click", () => {
    if (!P || fini()) return;
    voile('<span style="font-size:56px">⟲</span>', "Recommencer ?", "Si tu recommences, ce niveau ne donnera aucune récompense.", "Recommencer", () => recommencer(), "Continuer");
  });

  function voile(icone, titre, texte, bouton, action, bouton2) {
    $("voile-icone").innerHTML = icone;
    $("voile-titre").textContent = titre;
    $("voile-texte").textContent = texte;
    $("voile-btn").textContent = bouton;
    $("voile-btn").onclick = () => { $("voile").classList.add("cache"); action(); };
    $("voile-btn2").classList.toggle("cache", !bouton2);
    $("voile-btn2").textContent = bouton2 || "";
    $("voile-btn2").onclick = () => $("voile").classList.add("cache");
    $("voile").classList.remove("cache");
  }

  let minuterieInfo;
  function info(t) {
    $("msg-jeu").textContent = t;
    clearTimeout(minuterieInfo);
    minuterieInfo = setTimeout(() => ($("msg-jeu").textContent = ""), 3500);
  }

  // ---------- Sauvegarde ----------
  let minuterieSauve;
  function sauver() {
    clearTimeout(minuterieSauve);
    minuterieSauve = setTimeout(() => sauverMaintenant(), 800);
  }
  async function sauverMaintenant(partie) {
    clearTimeout(minuterieSauve);
    if (!jeton || !profil) return;
    const p = partie || P;
    try {
      await api("/api/sauver", { niveau: profil.niveau, chats: profil.chats, astuces: profil.astuces, stats: profil.stats, partie: p && !p.fin ? p : null });
    } catch (e) {
      if (e.code === 401) { jeton = null; montrer("ecran-connexion"); }
    }
  }
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") sauverMaintenant(); });

  // ---------- Démarrage ----------
  const pret = fetch("/niveaux.json?v=1").then((r) => r.json()).then((d) => (NIVEAUX = d));
  if (jeton) {
    pret.then(() => api("/api/profil")).then((d) => demarrer(d.profil)).catch(() => { jeton = null; montrer("ecran-connexion"); });
  } else montrer("ecran-connexion");

  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
})();

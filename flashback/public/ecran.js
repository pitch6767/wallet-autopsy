// Flashback — l'écran commun (télé, tablette, ordinateur)
(function () {
  const $ = (id) => document.getElementById(id);
  const audio = $("audio");
  let conn = null, code = "", etat = null, voix = true, cad = null;
  let derniereCle = "", previewCourant = "";
  const reglages = { decennies: [1960, 1970, 1980, 1990, 2000], longueur: 12 };

  // ---------- Accueil : l'aiguille cherche une station ----------
  const cAcc = cadran($("cadran-accueil"));
  const balayage = [1975, 1962, 1988, 1969, 1999, 1983];
  let ib = 0;
  setTimeout(() => cAcc.regle(1960, true), 0);
  const tour = () => { if (!$("accueil").classList.contains("cache")) { cAcc.regle(balayage[ib++ % balayage.length]); setTimeout(tour, 2600); } };
  setTimeout(tour, 300);

  $("code").addEventListener("input", (e) => (e.target.value = e.target.value.toUpperCase().replace(/[^A-Z]/g, "")));
  $("btn-rejoindre").addEventListener("click", () => { const c = $("code").value.trim(); if (/^[A-Z]{4}$/.test(c)) location.href = "/j/" + c; });

  $("btn-creer").addEventListener("click", async () => {
    $("btn-creer").disabled = true;
    // débloque le son et la voix (les navigateurs exigent un geste)
    try { audio.src = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="; await audio.play().catch(() => {}); } catch (e) {}
    try { speechSynthesis.speak(new SpeechSynthesisUtterance("")); } catch (e) {}
    const r = await fetch("/api/salle", { method: "POST" }).then((x) => x.json()).catch(() => null);
    if (!r) { $("btn-creer").disabled = false; return alert("Impossible de créer la partie : vérifie la connexion internet."); }
    code = r.code;
    history.replaceState(null, "", "/?ecran=" + code);
    demarrerEcran();
  });
  const dejaCode = new URLSearchParams(location.search).get("ecran");
  if (dejaCode && /^[A-Z]{4}$/.test(dejaCode)) { code = dejaCode; demarrerEcran(); }

  function demarrerEcran() {
    $("accueil").classList.add("cache");
    $("ecran").classList.remove("cache");
    cad = cadran($("cadran-ecran"));
    requestAnimationFrame(() => cad.regle(1985, true));
    conn = connecter(code, "ecran", (m) => { if (m.type === "etat") { etat = m; dessiner(); } if (m.type === "fin" && etat) { etat.fin = m.fin; minuteurs(); } });
  }

  $("btn-voix").addEventListener("click", () => { voix = !voix; $("btn-voix").textContent = "Voix : " + (voix ? "oui" : "non"); if (!voix) speechSynthesis.cancel(); });
  $("btn-suivant").addEventListener("click", () => conn && conn.envoie({ type: "suivant" }));

  function parle(texte) {
    if (!voix || !texte || !("speechSynthesis" in window)) return;
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(texte);
    u.lang = "fr-FR"; u.rate = 0.98;
    const v = speechSynthesis.getVoices().find((x) => /^fr/i.test(x.lang));
    if (v) u.voice = v;
    speechSynthesis.speak(u);
  }

  // ---------- Musique ----------
  function jouer(url) {
    if (!url) return;
    if (previewCourant === url && !audio.paused) return;
    previewCourant = url;
    audio.src = url; audio.volume = 1; audio.currentTime = 0;
    audio.play().catch(() => {});
  }
  function couper(doux) {
    if (audio.paused) return;
    if (!doux) { audio.pause(); return; }
    let v = audio.volume;
    const f = setInterval(() => { v -= 0.08; if (v <= 0) { clearInterval(f); audio.pause(); audio.volume = 1; } else audio.volume = v; }, 60);
  }

  // ---------- Dessin ----------
  function bande() {
    const j = etat.joueurs.slice().sort((a, b) => b.score - a.score);
    $("bande").innerHTML = j.map((p) =>
      '<div class="pion' + (p.repondu ? " repondu" : "") + (p.connecte ? "" : " absent") + '" style="--c:' + p.couleur + '"><span class="tete">' + echappe(p.emoji) + "</span>" +
      "<span>" + echappe(p.nom) + "</span><b>" + p.score + "</b>" + (p.gains ? '<span class="gain">+' + p.gains + "</span>" : "") + "</div>").join("");
  }
  function minuteurs() {
    document.querySelectorAll(".scene .minuteur").forEach((m) => minuteur(m, conn, etat.fin, etat.duree || 15000));
  }
  const opts = (q, revele) => {
    const qui = (i) => etat.joueurs.filter((p) => p.choix === i).map((p) => echappe(p.emoji)).join("");
    return '<div class="options' + (revele ? " revele" : "") + '">' + q.options.map((o, i) =>
      '<div class="option' + (revele && i === q.bonne ? " bonne" : "") + '" style="--c:' + COULEURS_OPT[i] + '"><span class="lettre">' + LETTRES_OPT[i] + "</span><span>" + echappe(o) + "</span>" + (revele ? '<span class="qui">' + qui(i) + "</span>" : "") + "</div>").join("") + "</div>";
  };

  function dessiner() {
    bande();
    const q = etat.question, ph = etat.phase;
    $("manche").textContent = ph === "salon" || ph === "fin" ? "" : (q && q.finale ? "Finale : points doublés · " : "") + "Étape " + (etat.k + 1) + " sur " + etat.total;
    const cle = ph + "|" + etat.k + "|" + (q && q.sous);
    const nouveau = cle !== derniereCle;
    derniereCle = cle;
    const sc = $("scene");

    // aiguille : sur l'année quand on la connaît

    if (ph === "salon") return salon(sc);
    if (ph === "fin") return fin(sc);
    if (!nouveau && ph !== "revele") { minuteurs(); return; }

    if (ph === "blind") {
      if (q.extrait) {
        sc.innerHTML = '<div class="platine"><div class="vinyle"><div class="etiquette"></div></div></div>' +
          '<div class="question">Quelle est cette chanson ?</div>' + opts(q, false) + '<div class="minuteur"><i></i></div>';
        jouer(q.preview);
        parle("Quelle est cette chanson ?");
      } else {
        sc.innerHTML = '<div class="question">' + echappe(q.texte) + "</div>" + opts(q, false) + '<div class="minuteur"><i></i></div>';
        parle(q.texte);
      }
      cad.regle(1985);
    } else if (ph === "revele" && q.sous === "blind") {
      sc.innerHTML = '<div class="revelation"><div class="pochette" style="background-image:url(' + echappe(q.pochette || "") + ')"></div><div><div class="t">' + echappe(q.titre) + '</div><div class="a">' + echappe(q.artiste) + '</div><div class="y">' + q.y + "</div></div></div>" + opts(q, true) +
        (q.extrait ? '<div class="attribution">Extrait fourni par Deezer</div>' : "");
      cad.regle(q.y);
      tinte(true);
    } else if (ph === "danse") {
      sc.innerHTML = '<div class="danse-ecran"><div class="titre">Pause danse !</div></div><div class="sous-titre">Tout le monde se lève et danse !</div><div class="egaliseur"><i></i><i></i><i></i><i></i><i></i></div><div class="minuteur"><i></i></div>';
      parle("Pause danse !");
    } else if (ph === "annee") {
      couper(true);
      const t = q.type === "blind" ? "En quelle année est sortie « " + q.titre + " » ?" : q.texte;
      sc.innerHTML = '<div class="question">' + echappe(t) + '</div><div class="sous-titre">Réglez l\'aiguille sur votre téléphone.</div><div class="minuteur"><i></i></div>';
      cad.regle(1985);
      parle(t);
    } else if (ph === "revele" && (q.sous === "annee" || q.type === "annee")) {
      const liste = (q.annees || []).sort((a, b) => Math.abs(a.annee - q.y) - Math.abs(b.annee - q.y)).map((x) => echappe(x.nom) + " : " + x.annee).join(" · ");
      sc.innerHTML = '<div class="question">C\'était en <span style="color:var(--ambre)">' + q.y + "</span></div>" + (liste ? '<div class="sous-titre">' + liste + "</div>" : "");
      cad.regle(q.y);
      tinte(true);
    } else if (ph === "ecran" || ph === "evenement") {
      sc.innerHTML = '<div class="question">' + echappe(q.texte) + "</div>" + opts(q, false) + '<div class="minuteur"><i></i></div>';
      if (ph === "evenement") cad.regle(q.y); else cad.regle(1985);
      parle(q.texte);
    } else if (ph === "revele") {
      sc.innerHTML = '<div class="question">' + echappe(q.texte) + "</div>" + opts(q, true) + (q.type === "ecran" ? '<div class="sous-titre">Première diffusion : ' + q.y + "</div>" : "");
      cad.regle(q.y);
      tinte(true);
    } else if (ph === "archive") {
      couper(true);
      speechSynthesis.cancel();
      sc.innerHTML = '<div class="sous-titre">📺 Archive de la télévision suisse</div><div class="video"><div id="yt"></div></div><div class="minuteur"><i></i></div>';
      video(q.video);
    } else if (ph === "culture") {
      sc.innerHTML = '<div class="carte-papier"><h2>Le saviez-vous ?</h2><p>' + echappe(q.texte) + "</p></div>";
      parle("Le saviez-vous ? " + q.texte);
    } else if (ph === "souvenir") {
      const ages = etat.joueurs.filter((p) => p.age !== null).map((p) => "<span>" + echappe(p.nom) + " : <b>" + (p.age < 0 ? "pas encore né" : p.age + " ans") + "</b></span>").join("");
      sc.innerHTML = '<div class="carte-papier"><h2>Souvenir de ' + q.y + "</h2><p>" + echappe(q.txt) + "</p><p style='margin-top:2vh'><b>" + echappe(q.q) + "</b></p>" + (ages ? '<div class="ages">' + ages + "</div>" : "") + "</div>" +
        '<div class="sous-titre">Chacun raconte à son tour. On peut aussi l\'écrire sur son téléphone pour le livre des souvenirs.</div><div class="minuteur"><i></i></div>';
      cad.regle(q.y);
      parle(q.txt + " " + q.q);
    }
    minuteurs();
  }

  function salon(sc) {
    couper();
    const url = location.origin + "/j/" + code;
    let qrSvg = "";
    try { const qr = qrcode(0, "M"); qr.addData(url); qr.make(); qrSvg = qr.createSvgTag({ cellSize: 6, margin: 0, scalable: true }); } catch (e) {}
    const joueurs = etat.joueurs.map((p) => '<div class="pion" style="--c:' + p.couleur + '"><span class="tete">' + echappe(p.emoji) + "</span><span>" + echappe(p.nom) + "</span></div>").join("");
    const decs = [1960, 1970, 1980, 1990, 2000];
    sc.innerHTML = '<div class="salon"><div class="qr">' + qrSvg + "</div><div style='text-align:left'>" +
      "<h2 style='font-size:clamp(24px,2.4vw,40px)'>Scannez pour jouer</h2>" +
      '<div class="petit" style="font-size:clamp(16px,1.4vw,24px)">ou allez sur ' + echappe(location.host) + "/j/ et tapez le code</div>" +
      '<div class="code-salle">' + code + "</div>" +
      '<div class="liste">' + (joueurs || '<span class="petit">En attente des joueurs…</span>') + "</div>" +
      '<div class="reglage"><span>Années :</span>' + decs.map((d) => '<button class="puce' + (reglages.decennies.includes(d) ? " on" : "") + '" data-d="' + d + '">' + (d === 2000 ? "2000–2010" : "’" + String(d).slice(2) + "s") + "</button>").join("") + "</div>" +
      '<div class="reglage"><span>Durée :</span>' + [[8, "Courte"], [12, "Normale"], [16, "Longue"]].map(([n, t]) => '<button class="puce' + (reglages.longueur === n ? " on" : "") + '" data-l="' + n + '">' + t + "</button>").join("") + "</div>" +
      '<button class="gros-bouton" id="btn-go" ' + (etat.joueurs.length ? "" : "disabled") + ">Commencer la partie</button></div></div>";
    sc.querySelectorAll("[data-d]").forEach((b) => b.onclick = () => {
      const d = +b.dataset.d, i = reglages.decennies.indexOf(d);
      if (i >= 0 && reglages.decennies.length > 1) reglages.decennies.splice(i, 1); else if (i < 0) reglages.decennies.push(d);
      salon(sc);
    });
    sc.querySelectorAll("[data-l]").forEach((b) => b.onclick = () => { reglages.longueur = +b.dataset.l; salon(sc); });
    const go = $("btn-go");
    if (go) go.onclick = () => conn.envoie({ type: "demarrer", decennies: reglages.decennies, longueur: reglages.longueur });
  }

  function fin(sc) {
    couper(true);
    const j = etat.joueurs.slice().sort((a, b) => b.score - a.score);
    const marche = (p, n) => p ? '<div class="marche p' + n + '"><div class="tete">' + echappe(p.emoji) + '</div><div class="n">' + echappe(p.nom) + "</div><b>" + p.score + "</b></div>" : "";
    sc.innerHTML = '<h2 style="font-size:clamp(34px,4vw,70px);color:var(--ambre)">Et le grand gagnant est…</h2>' +
      '<div class="podium">' + marche(j[1], 2) + marche(j[0], 1) + marche(j[2], 3) + "</div>" +
      (j.length > 3 ? '<div class="sous-titre">' + j.slice(3).map((p) => echappe(p.nom) + " " + p.score).join(" · ") + "</div>" : "") +
      '<div class="reglage" style="justify-content:center"><button class="gros-bouton" id="btn-encore">Rejouer</button><a class="gros-bouton sobre" style="text-decoration:none" href="/livre/' + code + '" target="_blank">Le livre des souvenirs</a></div>';
    $("btn-encore").onclick = () => conn.envoie({ type: "demarrer", decennies: reglages.decennies, longueur: reglages.longueur });
    if (j[0]) parle("Bravo " + j[0].nom + " !");
  }

  // ---------- Archives vidéo (lecteur YouTube visible, jamais caché) ----------
  let ytPret = null, lecteur = null;
  function chargerYT() {
    if (ytPret) return ytPret;
    ytPret = new Promise((ok) => {
      window.onYouTubeIframeAPIReady = ok;
      const sc = document.createElement("script");
      sc.src = "https://www.youtube.com/iframe_api";
      document.head.appendChild(sc);
    });
    return ytPret;
  }
  async function video(id) {
    await chargerYT();
    if (!document.getElementById("yt")) return;
    try { lecteur && lecteur.destroy(); } catch (e) {}
    lecteur = new YT.Player("yt", {
      videoId: id, width: "100%", height: "100%",
      playerVars: { autoplay: 1, rel: 0, playsinline: 1 },
      events: {
        onReady: (e) => { try { e.target.playVideo(); } catch (err) {} },
        onError: () => conn.envoie({ type: "suivant" }),
        onStateChange: (e) => { if (e.data === 0) conn.envoie({ type: "suivant" }); },
      },
    });
  }

  // petite cloche de révélation
  let AC;
  function tinte(ok) {
    try {
      AC = AC || new (window.AudioContext || window.webkitAudioContext)();
      [ok ? 784 : 330, ok ? 1175 : 247].forEach((f, k) => {
        const o = AC.createOscillator(), g = AC.createGain(), t = AC.currentTime + k * 0.12;
        o.type = "triangle"; o.frequency.value = f;
        g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.12, t + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.5);
        o.connect(g).connect(AC.destination); o.start(t); o.stop(t + 0.55);
      });
    } catch (e) {}
  }
  addEventListener("resize", () => { if (etat && etat.question && etat.question.y && cad) cad.regle(etat.question.y, true); });
})();

// Flashback — la manette sur le téléphone
(function () {
  const $ = (id) => document.getElementById(id);
  const code = location.pathname.split("/").pop();
  const EMOJIS = ["🕺", "💃", "🎸", "🎷", "🎤", "📻", "🎩", "🕶️", "🌼", "🍷", "⛷️", "🚲"];
  const TEINTES = ["#E8553F", "#2C7DD6", "#E9A21A", "#2BA36B", "#9B5DE5", "#E5487F", "#14A3B8", "#8C5A3C"];
  let profil = {};
  try { profil = JSON.parse(localStorage.getItem("fb-profil") || "{}"); } catch (e) {}
  let monId = null;
  try { monId = localStorage.getItem("fb-id-" + code); } catch (e) {}
  let conn = null, etat = null, derniereCle = "", choixFait = null, anneeChoisie = 1985;

  // ---------- Profil ----------
  profil.emoji = profil.emoji || EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
  profil.couleur = profil.couleur || TEINTES[Math.floor(Math.random() * TEINTES.length)];
  $("nom").value = profil.nom || "";
  $("naissance").value = profil.naissance || "";
  const dessineProfil = () => {
    $("emojis").innerHTML = EMOJIS.map((e) => '<button type="button" class="' + (e === profil.emoji ? "on" : "") + '" data-e="' + e + '" aria-label="Personnage ' + e + '">' + e + "</button>").join("");
    $("couleurs").innerHTML = TEINTES.map((c) => '<button type="button" class="' + (c === profil.couleur ? "on" : "") + '" data-c="' + c + '" style="--c:' + c + '" aria-label="Couleur"></button>').join("");
  };
  dessineProfil();
  $("emojis").onclick = (e) => { const b = e.target.closest("button"); if (b) { profil.emoji = b.dataset.e; dessineProfil(); } };
  $("couleurs").onclick = (e) => { const b = e.target.closest("button"); if (b) { profil.couleur = b.dataset.c; dessineProfil(); } };

  $("btn-jouer").onclick = async () => {
    const nom = $("nom").value.trim();
    if (!nom) return ($("erreur").textContent = "Écris ton prénom pour jouer.");
    const n = $("naissance").value.trim();
    if (n && !/^(19[2-9]\d|20[0-2]\d)$/.test(n)) return ($("erreur").textContent = "L'année de naissance doit avoir 4 chiffres, par exemple 1966.");
    profil.nom = nom; profil.naissance = n ? +n : 0;
    try { localStorage.setItem("fb-profil", JSON.stringify(profil)); } catch (e) {}
    $("profil").classList.add("cache");
    $("jeu").classList.remove("cache");
    $("jeu").innerHTML = '<p class="attente">Connexion à la partie ' + code + "…</p>";
    if (!conn) conn = connecter(code, "joueur", recu, rejoindre); else rejoindre();
  };
  function rejoindre() { conn.envoie({ type: "rejoindre", id: monId, nom: profil.nom, emoji: profil.emoji, couleur: profil.couleur, naissance: profil.naissance }); }
  if (profil.nom) $("btn-jouer").textContent = "Je joue, c'est moi " + profil.nom;

  function recu(m) {
    if (m.type === "bienvenue") { monId = m.id; try { localStorage.setItem("fb-id-" + code, m.id); } catch (e) {} return; }
    if (m.type === "erreur") { $("jeu").innerHTML = '<p class="attente">' + echappe(m.texte) + "</p>"; return; }
    if (m.type === "fin" && etat) { etat.fin = m.fin; return barre(); }
    if (m.type === "etat") { etat = m; dessiner(); }
  }

  const vibre = (ms) => { try { navigator.vibrate && navigator.vibrate(ms); } catch (e) {} };
  const moi = () => etat && etat.joueurs.find((j) => j.id === monId);
  function barre() { const b = document.querySelector("#jeu .minuteur"); if (b) minuteur(b, conn, etat.fin, etat.duree || 15000); }

  function dessiner() {
    const j = moi();
    if (j) { $("moi").classList.remove("cache"); $("moi").innerHTML = '<span class="tete" style="--c:' + j.couleur + '">' + echappe(j.emoji) + "</span>" + echappe(j.nom) + " <b>" + j.score + "</b>"; }
    const q = etat.question, ph = etat.phase;
    const cle = ph + "|" + etat.k + "|" + (q && q.sous);
    const nouveau = cle !== derniereCle;
    derniereCle = cle;
    if (!nouveau) return barre();
    choixFait = etat.moi && etat.moi.choix !== undefined ? etat.moi.choix : null;
    const J = $("jeu");

    if (ph === "salon") {
      J.innerHTML = '<p class="attente">Tu es dans la partie ' + code + ' !<br><br>Regarde l\'écran : la partie commence dès que tout le monde est là.</p>' +
        '<p class="petit" style="text-align:center">' + etat.joueurs.length + " joueur" + (etat.joueurs.length > 1 ? "s" : "") + ' connecté' + (etat.joueurs.length > 1 ? "s" : "") + '</p><button class="gros-bouton sobre" id="btn-modif">Modifier mon profil</button>';
      $("btn-modif").onclick = () => { $("profil").classList.remove("cache"); J.classList.add("cache"); };
      return;
    }
    if (ph === "fin") {
      const tri = etat.joueurs.slice().sort((a, b) => b.score - a.score);
      const rang = tri.findIndex((x) => x.id === monId) + 1;
      J.innerHTML = '<div class="resultat ' + (rang === 1 ? "oui" : "neutre") + '">' + (rang === 1 ? "Tu as gagné ! 🏆" : "Tu termines " + rang + (rang === 1 ? "er" : "e")) + "<br>" + (j ? j.score : 0) + " points</div>" +
        '<a class="gros-bouton sobre" style="display:block;text-align:center;text-decoration:none;margin-top:16px" href="/livre/' + code + '">Lire le livre des souvenirs</a>';
      return;
    }
    if (["blind", "ecran", "evenement"].includes(ph)) {
      const titre = ph === "blind" ? (q.extrait ? "Quelle est cette chanson ?" : q.texte) : q.texte;
      J.innerHTML = "<h2>" + echappe(titre) + '</h2><div class="minuteur tel-min"><i></i></div><div class="boutons" id="boutons">' +
        q.options.map((o, i) => '<button class="choix" data-i="' + i + '" style="--c:' + COULEURS_OPT[i] + '"><span class="lettre">' + LETTRES_OPT[i] + "</span><span>" + echappe(o) + "</span></button>").join("") + "</div>";
      const bs = $("boutons");
      if (choixFait !== null) marque(bs, choixFait);
      bs.onclick = (e) => {
        const b = e.target.closest(".choix");
        if (!b || choixFait !== null) return;
        choixFait = +b.dataset.i;
        conn.envoie({ type: "choix", choix: choixFait });
        vibre(30);
        marque(bs, choixFait);
      };
      return barre();
    }
    if (ph === "revele") {
      if (q.sous === "annee" || q.type === "annee") {
        J.innerHTML = '<div class="resultat ' + (j && j.gains ? "oui" : "non") + '">C\'était en ' + q.y + "<br>" + (j && j.gains ? "+" + j.gains + " points" : "Pas de points cette fois") + "</div>";
        vibre(j && j.gains ? 40 : [60, 40, 60]);
        return;
      }
      const bon = choixFait === q.bonne;
      J.innerHTML = '<div class="resultat ' + (bon ? "oui" : "non") + '">' + (bon ? "Bonne réponse ! +" + (j ? j.gains : 0) : choixFait === null ? "Pas de réponse" : "Raté !") + "</div>" +
        (q.type === "blind" ? '<p class="consigne" style="text-align:center">« ' + echappe(q.titre) + " »<br>" + echappe(q.artiste) + " · " + q.y + "</p>" : '<p class="consigne" style="text-align:center">' + echappe(q.options[q.bonne]) + "</p>");
      vibre(bon ? 40 : [60, 40, 60]);
      return;
    }
    if (ph === "danse") return danse(J);
    if (ph === "annee") return annee(J, q);
    if (ph === "culture") { J.innerHTML = '<p class="attente">📻 Regardez l\'écran…<br><br>' + echappe(q.texte) + "</p>"; return; }
    if (ph === "souvenir") return souvenir(J, q);
  }
  function marque(bs, i) { bs.classList.add("envoye"); const b = bs.querySelector('[data-i="' + i + '"]'); if (b) b.classList.add("pris"); }

  // ---------- Quelle année ? : on règle l'aiguille du cadran ----------
  function annee(J, q) {
    const t = q.type === "blind" ? "En quelle année est sortie « " + q.titre + " » ?" : q.texte;
    const deja = etat.moi && etat.moi.annee;
    J.innerHTML = "<h2>" + echappe(t) + '</h2><div class="minuteur tel-min"><i></i></div><div id="cad"></div><div class="annee-choisie" id="an"></div>' +
      '<div class="pas"><button data-p="-5">−5</button><button data-p="-1">−1</button><button data-p="1">+1</button><button data-p="5">+5</button></div>' +
      '<button class="gros-bouton" id="btn-annee">Valider cette année</button>';
    const c = cadran($("cad"));
    anneeChoisie = deja || 1985;
    const maj = (instant) => { $("an").textContent = anneeChoisie; c.regle(anneeChoisie, instant); };
    requestAnimationFrame(() => maj(true));
    const el = $("cad");
    let tire = false;
    const bouge = (x) => { if (deja || envoye) return; const a = c.anneeDepuisX(x); if (a !== anneeChoisie) { anneeChoisie = a; vibre(5); maj(true); } };
    el.addEventListener("pointerdown", (e) => { tire = true; el.setPointerCapture(e.pointerId); bouge(e.clientX); });
    el.addEventListener("pointermove", (e) => tire && bouge(e.clientX));
    el.addEventListener("pointerup", () => (tire = false));
    J.querySelector(".pas").onclick = (e) => { const b = e.target.closest("button"); if (!b || deja || envoye) return; anneeChoisie = Math.min(AN_MAX, Math.max(AN_MIN, anneeChoisie + +b.dataset.p)); maj(); };
    let envoye = !!deja;
    const btn = $("btn-annee");
    if (envoye) { btn.disabled = true; btn.textContent = "Envoyé : " + deja; }
    btn.onclick = () => { if (envoye) return; envoye = true; conn.envoie({ type: "annee", valeur: anneeChoisie }); btn.disabled = true; btn.textContent = "Envoyé : " + anneeChoisie; vibre(30); };
    barre();
  }

  // ---------- Pause danse : un simple moment pour danser ----------
  function danse(J) {
    J.innerHTML = '<p class="attente" style="font-size:30px;color:var(--ambre)">💃 Pause danse ! 🕺</p><p class="attente">Tout le monde se lève et danse sur la chanson !</p>';
  }

  // ---------- Souvenir ----------
  function souvenir(J, q) {
    const j = moi();
    const age = j && j.age !== null && j.age !== undefined ? (j.age < 0 ? "Tu n'étais pas encore né(e) !" : "Tu avais " + j.age + " ans.") : "";
    const fait = etat.moi && etat.moi.raconte;
    J.innerHTML = "<h2>Souvenir de " + q.y + '</h2><p class="consigne">' + echappe(q.q) + "</p>" + (age ? '<p class="consigne" style="color:var(--ambre)">' + age + "</p>" : "") +
      '<textarea id="txt" placeholder="Écris ton souvenir pour le livre (facultatif)"></textarea>' +
      '<button class="gros-bouton" id="btn-ecrit">Garder mon souvenir dans le livre</button>' +
      '<button class="gros-bouton sobre" id="btn-oral">J\'ai raconté à voix haute</button><div class="minuteur tel-min"><i></i></div>';
    const fini = (t) => { J.querySelector("#btn-ecrit").disabled = true; J.querySelector("#btn-oral").disabled = true; J.querySelector("#btn-ecrit").textContent = t; };
    if (fait) fini("Merci !");
    $("btn-ecrit").onclick = () => { const t = $("txt").value.trim(); if (!t) return $("txt").focus(); conn.envoie({ type: "souvenir", texte: t }); fini("Souvenir gardé, merci !"); vibre(30); };
    $("btn-oral").onclick = () => { conn.envoie({ type: "souvenir", texte: "" }); fini("Merci !"); };
    barre();
  }
})();

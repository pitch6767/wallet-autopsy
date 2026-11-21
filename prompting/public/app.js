// Prompting — cours de prompting en français (9 leçons + exercices)
const VERSION = "1.0.0";

const LECONS = [
  {
    titre: "Être clair et direct",
    idee: [
      "Claude est comme un collègue très doué qui arrive le premier jour : il sait beaucoup de choses, mais il ne connaît rien de ta situation. Tout ce que tu ne dis pas, il doit le deviner.",
      "Le test simple : si tu donnais ton message à un ami sans rien lui expliquer d'autre, saurait-il exactement quoi faire ? Si non, Claude non plus.",
      "Dis précisément ce que tu veux, et ce que tu ne veux pas (par exemple : pas d'introduction, pas de « ça dépend »).",
    ],
    avant: "Écris un poème sur l'automne.",
    apres: "Écris un poème de 4 vers sur l'automne dans les vignes du Valais. Donne seulement le poème, sans titre ni explication.",
    exercice: "Demande à Claude quel est le meilleur vin rouge suisse. Oblige-le à donner un seul cépage, sans liste et sans « ça dépend des goûts ».",
    depart: "Quel est le meilleur vin rouge suisse ?",
    controle: ["Tu demandes un seul cépage", "Tu interdis la liste et le « ça dépend »", "Tu dis la forme de la réponse (un mot, une phrase…)"],
  },
  {
    titre: "Donner le contexte",
    idee: [
      "La même question n'appelle pas la même réponse selon qui la pose et pourquoi. Claude ne peut pas le savoir si tu ne le dis pas.",
      "Donne trois choses : pour qui c'est, à quoi ça va servir, et ce que la personne sait déjà.",
      "Explique aussi pourquoi tu demandes quelque chose. « Phrases courtes, car le texte sera lu sur un téléphone » marche mieux que « phrases courtes ».",
    ],
    avant: "Explique-moi ce qu'est le Bitcoin.",
    apres: "Explique ce qu'est le Bitcoin à ma voisine de 75 ans, qui n'a jamais utilisé d'application bancaire. Elle a entendu le mot à la télévision et veut juste comprendre l'idée. Pas de jargon, 5 phrases maximum.",
    exercice: "Demande à Claude d'expliquer ce qu'est une option d'achat (call). Le lecteur : un vigneron qui n'a jamais investi en bourse et veut savoir si ça peut protéger le prix de sa récolte.",
    depart: "Explique ce qu'est une option d'achat.",
    controle: ["Tu dis qui va lire", "Tu dis pourquoi il veut savoir", "Tu dis ce qu'il sait déjà (ou pas)", "Tu fixes une longueur"],
  },
  {
    titre: "Donner un rôle",
    idee: [
      "Commencer par « Tu es… » donne à Claude un point de vue : un expert, un critique, un professeur. Il choisit alors le bon vocabulaire, le bon niveau d'exigence et les bons réflexes.",
      "Plus le rôle est précis, mieux c'est : « un comptable suisse qui conseille des indépendants » vaut mieux que « un comptable ».",
      "Le rôle sert aussi à rendre Claude plus exigeant. Un correcteur sévère trouvera des erreurs qu'un assistant poli laisserait passer.",
    ],
    avant: "Mon calcul est-il juste ? 2x − 3 = 9, donc x = 4.",
    apres: "Tu es un professeur de mathématiques exigeant. Vérifie ce calcul ligne par ligne et dis clairement s'il est juste ou faux : 2x − 3 = 9, donc x = 4.",
    exercice: "Fais relire à Claude cette phrase de présentation pour une annonce : « Vigneron passionné vend vin de qualité, prix intéressant. » Donne-lui le rôle d'un spécialiste de la vente en ligne qui ne fait pas de compliments inutiles.",
    depart: "Améliore cette annonce : « Vigneron passionné vend vin de qualité, prix intéressant. »",
    controle: ["Tu commences par « Tu es… »", "Le rôle est précis (métier + attitude)", "Tu dis ce que tu attends de lui"],
  },
  {
    titre: "Séparer les instructions des données",
    idee: [
      "Quand tu colles un texte (un mail, un article, un relevé), Claude doit savoir où s'arrêtent tes consignes et où commence le texte.",
      "La méthode la plus sûre : entourer le texte de balises, comme <mail> … </mail>. Le nom est libre, il doit juste être clair.",
      "Ensuite, tu parles des balises dans ta consigne : « Résume le mail qui se trouve dans les balises <mail> ».",
    ],
    avant: "Réponds poliment : salut, je viens jeudi chercher les 12 bouteilles, c'est toujours ok ? Marc",
    apres: "Rédige une réponse polie et courte au mail qui se trouve entre les balises <mail>. Confirme le rendez-vous de jeudi.\n\n<mail>\nSalut, je viens jeudi chercher les 12 bouteilles, c'est toujours ok ?\nMarc\n</mail>",
    exercice: "Demande à Claude de traduire en anglais le message ci-dessous, en séparant bien la consigne du texte : « Bonjour, la dégustation est reportée à samedi 14 h. Merci de confirmer votre présence. »",
    depart: "Traduis en anglais : Bonjour, la dégustation est reportée à samedi 14 h. Merci de confirmer votre présence.",
    controle: ["Le texte est entre balises", "La consigne cite le nom de la balise", "La consigne est avant ou après le texte, pas mélangée"],
  },
  {
    titre: "Choisir la forme de la réponse",
    idee: [
      "Si tu ne dis rien, Claude choisit la forme lui-même : parfois un long texte quand tu voulais une liste.",
      "Dis la forme exacte : liste numérotée, tableau, nombre de lignes, une seule phrase, un mot. Tu peux aussi demander que la réponse soit entre balises, par exemple <reponse> … </reponse>, pour la retrouver facilement.",
      "Un modèle à remplir marche très bien : tu montres le squelette, Claude le complète.",
    ],
    avant: "Donne-moi une recette de fondue.",
    apres: "Donne-moi une recette de fondue moitié-moitié pour 4 personnes. Forme : d'abord la liste des ingrédients avec les quantités, puis 5 étapes numérotées maximum. Pas d'introduction ni de conclusion.",
    exercice: "Demande à Claude de comparer trois façons d'épargner (compte épargne, 3e pilier, ETF) sous la forme d'un tableau à trois colonnes : avantage, inconvénient, pour qui.",
    depart: "Compare le compte épargne, le 3e pilier et les ETF.",
    controle: ["Tu demandes un tableau", "Tu donnes le nom des colonnes", "Tu interdis le texte autour"],
  },
  {
    titre: "Le faire réfléchir avant de répondre",
    idee: [
      "Pour une question qui demande du raisonnement, Claude répond mieux s'il réfléchit d'abord par écrit. C'est comme toi avec un brouillon.",
      "Demande-lui de penser dans des balises <reflexion> puis de donner la réponse finale dans <reponse>. Tu lis la réponse, et tu peux vérifier le raisonnement si tu as un doute.",
      "Important : la réflexion doit venir AVANT la réponse. Une réflexion écrite après ne sert à rien.",
    ],
    avant: "Un vigneron vend 300 bouteilles à 18 CHF, sa marge est de 35 %. Combien gagne-t-il ?",
    apres: "Un vigneron vend 300 bouteilles à 18 CHF, sa marge est de 35 % du prix de vente. Combien gagne-t-il ?\nRéfléchis d'abord étape par étape dans des balises <reflexion>, puis donne seulement le résultat final dans <reponse>.",
    exercice: "Demande à Claude de classer ce message client dans une catégorie (commande, réclamation, question, autre) en réfléchissant d'abord : « J'ai reçu 6 bouteilles au lieu de 12, mais la facture est juste. Vous pouvez m'expliquer ? »",
    depart: "Dans quelle catégorie est ce message : J'ai reçu 6 bouteilles au lieu de 12, mais la facture est juste. Vous pouvez m'expliquer ?",
    controle: ["Tu donnes la liste des catégories", "Tu demandes une réflexion d'abord", "La réponse finale est séparée (balises)"],
  },
  {
    titre: "Donner des exemples",
    idee: [
      "Montrer vaut mieux qu'expliquer. Deux ou trois exemples de ce que tu attends valent souvent un long paragraphe de consignes.",
      "Mets les exemples entre balises <exemple> pour qu'ils ne se mélangent pas avec la tâche.",
      "Varie les exemples : s'ils se ressemblent tous, Claude copiera aussi ce qu'ils ont en commun par hasard.",
    ],
    avant: "Dis-moi si cet avis est positif ou négatif : « Bon vin mais livraison très lente. »",
    apres: "Classe l'avis en POSITIF, NÉGATIF ou MITIGÉ. Réponds par un seul mot.\n\n<exemple>Avis : Excellent, je recommande ! → POSITIF</exemple>\n<exemple>Avis : Bouchon cassé, vin imbuvable. → NÉGATIF</exemple>\n<exemple>Avis : Joli vin, un peu cher. → MITIGÉ</exemple>\n\nAvis : Bon vin mais livraison très lente.",
    exercice: "Fais écrire par Claude un titre court pour un nouveau produit, en lui montrant d'abord deux exemples de titres que tu aimes (par exemple « Chasselas de Vouvry — frais et minéral »).",
    depart: "Écris un titre pour mon Pinot noir 2025.",
    controle: ["Il y a au moins 2 exemples", "Les exemples sont entre balises", "La tâche est clairement à part"],
  },
  {
    titre: "Éviter les inventions",
    idee: [
      "Claude veut aider, et il peut parfois inventer une réponse plutôt que d'avouer qu'il ne sait pas. Ça s'appelle une hallucination.",
      "Premier remède : lui donner la permission de dire « je ne sais pas ». Phrase type : « Si tu n'es pas sûr, dis-le. »",
      "Deuxième remède, quand tu lui donnes un document : lui demander de citer d'abord le passage exact qui contient la réponse, puis seulement de répondre. Pas de citation trouvée = pas de réponse inventée.",
    ],
    avant: "Combien de bouteilles le domaine Dupont de Vouvry a-t-il produit en 2019 ?",
    apres: "Combien de bouteilles le domaine Dupont de Vouvry a-t-il produit en 2019 ? Si tu n'as pas cette information de façon sûre, réponds simplement « je ne sais pas » sans faire d'estimation.",
    exercice: "Colle un petit texte (par exemple un paragraphe d'un contrat ou d'un article) et pose une question dessus. Demande à Claude de citer d'abord la phrase exacte qui répond, dans des balises <citation>, puis de répondre. S'il ne trouve pas de phrase, il doit le dire.",
    depart: "Voici un texte : [colle ton texte]. Question : [ta question]",
    controle: ["Tu autorises « je ne sais pas »", "Le texte est entre balises", "Tu demandes la citation avant la réponse"],
  },
  {
    titre: "Le prompt complet",
    idee: [
      "Pour une tâche importante, on assemble tout ce que tu as appris, dans cet ordre : le rôle, le contexte, les données entre balises, la tâche, les exemples, la forme de la réponse, et la demande de réflexion.",
      "Tu n'as pas toujours besoin de tout. Mais pour une tâche que tu vas répéter souvent, un prompt complet bien fait te fait gagner des heures.",
      "Dernier conseil : quand le résultat ne te plaît pas, ne recommence pas de zéro. Regarde quel élément manquait, et ajoute-le.",
    ],
    avant: "Écris une annonce pour vendre mon vin.",
    apres: "Tu es un rédacteur spécialisé dans la vente de vin en ligne.\n\nContexte : je suis un petit vigneron de Vouvry (Valais). L'annonce sera publiée sur une plateforme de petites annonces suisse et lue surtout sur téléphone.\n\n<produit>\nChasselas 2025, 70 cl, 14 CHF la bouteille, 12 CHF dès 12 bouteilles, retrait sur place ou livraison dans le Chablais.\n</produit>\n\nTâche : écris l'annonce.\nForme : un titre de 8 mots maximum, puis 4 phrases courtes, puis le prix. Pas d'émojis.\nAvant d'écrire, note dans <reflexion> les 2 arguments les plus forts, puis donne l'annonce dans <annonce>.",
    exercice: "Écris un prompt complet pour une tâche que tu fais vraiment : par exemple faire résumer chaque jour les nouvelles d'un marché, préparer un message pour un client, ou vérifier un tableau. Utilise au moins 5 des 7 éléments.",
    depart: "Tu es …\n\nContexte : …\n\n<donnees>\n…\n</donnees>\n\nTâche : …\nForme : …",
    controle: ["Un rôle", "Le contexte", "Les données entre balises", "La tâche", "Des exemples", "La forme de la réponse", "La réflexion d'abord"],
  },
];

// ---------- mémoire de progression (sur ce téléphone seulement) ----------
function lire(cle, defaut) {
  try { const v = localStorage.getItem(cle); return v ? JSON.parse(v) : defaut; } catch { return defaut; }
}
function ecrire(cle, v) {
  try { localStorage.setItem(cle, JSON.stringify(v)); } catch {}
}
const faites = () => lire("prompting:faites", []);

// ---------- affichage ----------
const $ = (s) => document.querySelector(s);
const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function accueil() {
  $("#retour").hidden = true;
  $("#titre").textContent = "Prompting";
  const f = faites();
  $("#contenu").innerHTML = `
    <p class="intro">Apprends à écrire des demandes (des « prompts ») qui donnent une bonne réponse du premier coup. 9 leçons courtes, chacune avec un exercice à tester dans Claude.</p>
    <p class="avance">${f.length} / ${LECONS.length} leçons terminées</p>
    <ol class="liste">
      ${LECONS.map((l, i) => `
        <li><button class="lecon" data-i="${i}">
          <span class="num">${i + 1}</span>
          <span class="nom">${esc(l.titre)}</span>
          <span class="etat">${f.includes(i) ? "✓" : ""}</span>
        </button></li>`).join("")}
    </ol>
    <p class="source">Leçons inspirées du tutoriel de prompting d'Anthropic :<br>
    <a href="https://github.com/anthropics/prompt-eng-interactive-tutorial" target="_blank" rel="noopener">https://github.com/anthropics/prompt-eng-interactive-tutorial</a></p>`;
  document.querySelectorAll(".lecon").forEach((b) => b.addEventListener("click", () => ouvrir(+b.dataset.i)));
  window.scrollTo(0, 0);
}

function lienClaude(texte) {
  return "https://claude.ai/new?q=" + encodeURIComponent(texte);
}

function lecon(i) {
  const l = LECONS[i];
  const brouillon = lire("prompting:brouillon:" + i, l.depart);
  $("#retour").hidden = false;
  $("#titre").textContent = `${i + 1}. ${l.titre}`;
  $("#contenu").innerHTML = `
    <section class="bloc">
      <h2>L'idée</h2>
      ${l.idee.map((p) => `<p>${esc(p)}</p>`).join("")}
    </section>
    <section class="bloc">
      <h2>Avant / après</h2>
      <div class="ex mauvais"><div class="etiquette">Moins bien</div><pre>${esc(l.avant)}</pre></div>
      <div class="ex bon"><div class="etiquette">Mieux</div><pre>${esc(l.apres)}</pre></div>
      <a class="bouton secondaire" href="${lienClaude(l.apres)}" target="_blank" rel="noopener">Essayer l'exemple « Mieux » dans Claude</a>
    </section>
    <section class="bloc">
      <h2>Exercice</h2>
      <p>${esc(l.exercice)}</p>
      <label for="prompt">Ton prompt (améliore le texte de départ) :</label>
      <textarea id="prompt" rows="8">${esc(brouillon)}</textarea>
      <h3>Vérifie ton prompt</h3>
      <ul class="controle">
        ${l.controle.map((c, k) => `<li><label><input type="checkbox" data-k="${k}"> ${esc(c)}</label></li>`).join("")}
      </ul>
      <a id="tester" class="bouton" href="#" target="_blank" rel="noopener">Tester mon prompt dans Claude</a>
      <button id="copier" class="bouton secondaire">Copier mon prompt</button>
      <p id="info" class="info"></p>
    </section>
    <section class="bloc fin">
      <button id="terminer" class="bouton">${faites().includes(i) ? "Leçon terminée ✓" : "J'ai fini cette leçon"}</button>
      ${i + 1 < LECONS.length ? `<button id="suivante" class="bouton secondaire">Leçon suivante →</button>` : ""}
      <button id="accueil" class="bouton secondaire">Toutes les leçons</button>
    </section>`;

  const zone = $("#prompt");
  const maj = () => {
    ecrire("prompting:brouillon:" + i, zone.value);
    $("#tester").href = lienClaude(zone.value);
  };
  zone.addEventListener("input", maj);
  maj();
  $("#copier").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(zone.value); $("#info").textContent = "Copié. Colle-le dans Claude."; }
    catch { zone.select(); $("#info").textContent = "Texte sélectionné : touche Copier."; }
  });
  $("#terminer").addEventListener("click", () => {
    const f = faites();
    if (!f.includes(i)) { f.push(i); ecrire("prompting:faites", f); }
    $("#terminer").textContent = "Leçon terminée ✓";
  });
  if ($("#suivante")) $("#suivante").addEventListener("click", () => {
    history.replaceState({ lecon: i + 1 }, "", "#lecon-" + (i + 2));
    lecon(i + 1);
  });
  $("#accueil").addEventListener("click", versAccueil);
  window.scrollTo(0, 0);
}

// ---------- navigation : ← et glisser-retour ramènent à l'accueil ----------
function ouvrir(i) {
  history.pushState({ lecon: i }, "", "#lecon-" + (i + 1));
  lecon(i);
}
window.addEventListener("popstate", () => {
  const m = location.hash.match(/^#lecon-(\d+)$/);
  if (m && LECONS[m[1] - 1]) lecon(m[1] - 1); else accueil();
});
function versAccueil() {
  if (history.state && history.state.lecon !== undefined) history.back();
  else { history.replaceState(null, "", "/"); accueil(); }
}
$("#retour").addEventListener("click", versAccueil);

// ---------- version + rechargement automatique une fois par nouvelle version ----------
$("#version").textContent = VERSION;
fetch("/api/version", { cache: "no-store" }).then((r) => r.json()).then((d) => {
  if (d.version !== VERSION && sessionStorage.getItem("prompting:recharge") !== d.version) {
    sessionStorage.setItem("prompting:recharge", d.version);
    location.reload();
  }
}).catch(() => {});

// démarrage : toujours sur l'accueil (une leçon ouverte par lien direct garde le ← vers l'accueil)
const m0 = location.hash.match(/^#lecon-(\d+)$/);
if (m0 && LECONS[m0[1] - 1]) { history.replaceState(null, "", "/"); ouvrir(m0[1] - 1); } else accueil();

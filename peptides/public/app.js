const VERSION = "1.0";

const CATEGORIES = [
  "Érection & libido", "Perte de poids", "Anti-âge & peau", "Rides & cosmétique",
  "Douleur", "Anti-inflammatoire", "Récupération chirurgie", "Tunnel carpien",
  "Arthrose & articulations", "Cheveux", "Cholestérol", "Alzheimer & cognition",
  "Muscle & sport", "Sommeil & hormones", "Immunité", "Cicatrisation"
];

const PEPTIDES = [
  { nom: "BPC-157", type: "Régénération", desc: "Peptide de protection corporelle, le plus polyvalent. Régénère nerfs, tendons, muscles et réduit l'inflammation.", forme: "Injection SC / Oral", dose: "250-500 mcg/jour", principal: true, tags: ["Tunnel carpien", "Arthrose & articulations", "Douleur", "Anti-inflammatoire", "Récupération chirurgie", "Cicatrisation", "Alzheimer & cognition"] },
  { nom: "TB-500 (Thymosin β4)", type: "Régénération", desc: "Régulateur puissant de la réparation cellulaire. Anti-fibrose, régénération nerveuse et musculaire.", forme: "Injection SC / Transdermique", dose: "2-5 mg/semaine", principal: true, tags: ["Tunnel carpien", "Arthrose & articulations", "Récupération chirurgie", "Anti-inflammatoire", "Cicatrisation", "Muscle & sport"] },
  { nom: "GHK-Cu (Copper Peptide)", type: "Régénération & cosmétique", desc: "Tripeptide naturel. Stimule le collagène, régénère la gaine nerveuse et améliore la cicatrisation.", forme: "Crème / Injection SC / Oral", dose: "1-4 mg ou crème 1-3%", principal: true, tags: ["Tunnel carpien", "Rides & cosmétique", "Anti-âge & peau", "Cheveux", "Cicatrisation", "Anti-inflammatoire"] },
  { nom: "PT-141 (Bremelanotide)", type: "Sexuel", desc: "Agit sur le cerveau pour stimuler le désir et l'érection. Approuvé sous le nom Vyleesi.", forme: "Spray nasal / Injection", dose: "1-2 mg avant l'acte", principal: true, tags: ["Érection & libido"] },
  { nom: "Sémaglutide (GLP-1)", type: "Métabolique", desc: "Réduit l'appétit et stimule la satiété. Perte de poids significative (Ozempic/Wegovy).", forme: "Injection SC", dose: "0,25-2,4 mg/semaine", principal: true, tags: ["Perte de poids", "Cholestérol"] },
  { nom: "Liraglutide", type: "Métabolique", desc: "Contrôle de la glycémie et réduction du poids (Saxenda). Analogue du GLP-1.", forme: "Injection SC", dose: "0,6-3 mg/jour", principal: true, tags: ["Perte de poids", "Cholestérol"] },
  { nom: "Épitalon (Epithalon)", type: "Anti-âge", desc: "Tétrapeptide synthétique. Allonge les télomères, active la télomérase, puissant anti-âge.", forme: "Injection SC / Spray nasal", dose: "5-10 mg/jour (cure 10-20 jours)", principal: true, tags: ["Anti-âge & peau", "Alzheimer & cognition", "Sommeil & hormones", "Immunité"] },
  { nom: "Argireline (Hexapeptide-3)", type: "Cosmétique", desc: "Effet botox naturel. Relaxation musculaire, réduit les rides d'expression.", forme: "Crème / Sérum", dose: "Crème 5-10 %", principal: true, tags: ["Rides & cosmétique", "Anti-âge & peau"] },
  { nom: "Matrixyl (Palmitoyl pentapeptide-4)", type: "Cosmétique", desc: "Stimule la production de collagène. Anti-âge et fermeté cutanée.", forme: "Crème / Sérum", dose: "Crème 1-3 %", principal: true, tags: ["Rides & cosmétique", "Anti-âge & peau"] },
  { nom: "Dihexa", type: "Neurologique", desc: "Décrit comme 10 millions de fois plus puissant que le BDNF. Crée de nouvelles connexions neuronales.", forme: "Transdermique / Oral", dose: "10-30 mg/jour (cure)", principal: true, tags: ["Alzheimer & cognition"] },
  { nom: "Semax", type: "Neurologique", desc: "Améliore mémoire, concentration, protection neuronale. Utilisé en médecine russe.", forme: "Spray nasal / Injection", dose: "200-600 mcg/jour", principal: true, tags: ["Alzheimer & cognition"] },
  { nom: "Cerebrolysin", type: "Neurologique", desc: "Mélange de peptides neuroprotecteurs. Essais cliniques pour le déclin cognitif.", forme: "Injection IV / IM", dose: "5-10 ml (cure 20 jours)", principal: true, tags: ["Alzheimer & cognition"] },
  { nom: "NGF (Nerve Growth Factor)", type: "Neurologique", desc: "Facteur de croissance nerveux. Accélère la repousse axonale et la myélinisation.", forme: "Injection SC / Spray nasal", dose: "100-200 mcg (3x/semaine)", principal: true, tags: ["Tunnel carpien", "Alzheimer & cognition", "Douleur"] },
  { nom: "IGF-1", type: "Croissance", desc: "Médiateur de l'hormone de croissance. Récupération musculaire et régénération nerveuse.", forme: "Injection SC", dose: "50-100 mcg/jour", principal: false, tags: ["Tunnel carpien", "Muscle & sport", "Perte de poids", "Récupération chirurgie"] },
  { nom: "Collagène hydrolysé type I & III", type: "Structural", desc: "Reconstruction des tendons, ligaments et peau. Le plus sûr et accessible.", forme: "Poudre orale / Injection", dose: "10-15 g/jour", principal: true, tags: ["Tunnel carpien", "Arthrose & articulations", "Rides & cosmétique", "Récupération chirurgie"] },
  { nom: "Oxytocine", type: "Hormonal", desc: "Améliore l'excitation, le désir et la qualité de l'érection.", forme: "Spray nasal / Injection", dose: "10-24 UI", principal: false, tags: ["Érection & libido"] },
  { nom: "CJC-1295 + Ipamorelin", type: "Hormone de croissance", desc: "Stimulation naturelle de la GH. Brûlage des graisses, masse musculaire, récupération.", forme: "Injection SC", dose: "100-300 mcg/jour", principal: true, tags: ["Perte de poids", "Muscle & sport", "Anti-âge & peau", "Érection & libido"] },
  { nom: "HGH Fragment 176-191", type: "Métabolique", desc: "Fragment de GH ciblant les graisses abdominales.", forme: "Injection SC", dose: "200-400 mcg/jour", principal: false, tags: ["Perte de poids"] },
  { nom: "Tésamoréline", type: "Métabolique", desc: "Réduit spécifiquement la graisse abdominale. Stimule la GH.", forme: "Injection SC", dose: "2 mg/jour", principal: false, tags: ["Perte de poids"] },
  { nom: "Syn-Ake", type: "Cosmétique", desc: "Imite le venin de serpent. Lisse les rides mimiques, effet tenseur.", forme: "Crème / Sérum", dose: "Crème 4-8 %", principal: false, tags: ["Rides & cosmétique", "Anti-âge & peau"] },
  { nom: "Ziconotide (Prialt)", type: "Analgésique", desc: "Dérivé du venin de cône marin. Douleurs chroniques sévères, très puissant.", forme: "Injection intrathécale", dose: "Sur prescription", principal: true, tags: ["Douleur"] },
  { nom: "Endorphines", type: "Opioïde naturel", desc: "Analgésie naturelle du corps. Modulation de la douleur et bien-être.", forme: "Naturel / Stimulation", dose: "Naturel", principal: false, tags: ["Douleur", "Sommeil & hormones"] },
  { nom: "Thymosin α1", type: "Immunitaire", desc: "Modulation immunitaire, protection contre les maladies chroniques, inflammation.", forme: "Injection SC", dose: "1-1,6 mg (2x/semaine)", principal: false, tags: ["Immunité", "Anti-inflammatoire", "Anti-âge & peau"] },
  { nom: "Biotinoyl tripeptide-1", type: "Cosmétique capillaire", desc: "Ancrage du cheveu au follicule. Réduit la chute et stimule la repousse.", forme: "Shampoing / Lotion", dose: "Topique 0,01 %", principal: true, tags: ["Cheveux"] },
  { nom: "Acetyl tetrapeptide-3", type: "Cosmétique capillaire", desc: "Densification et repousse capillaire. Stimule la matrice dermique du follicule.", forme: "Sérum capillaire", dose: "Topique", principal: false, tags: ["Cheveux"] },
  { nom: "GHK-Cu (cheveux)", type: "Cosmétique capillaire", desc: "Stimule la repousse, renforce le follicule pileux. Même molécule que l'anti-âge.", forme: "Sérum / Lotion", dose: "Topique 0,1-1 %", principal: true, tags: ["Cheveux"] },
  { nom: "Peptides de soja", type: "Nutritionnel", desc: "Réduction du LDL (mauvais cholestérol) et amélioration du profil lipidique.", forme: "Oral / Complément", dose: "20-40 g/jour", principal: false, tags: ["Cholestérol"] },
  { nom: "Inhibiteurs PCSK9 (peptidiques)", type: "Cardiovasculaire", desc: "Réduction puissante du LDL. Alternative aux statines.", forme: "Injection SC", dose: "Sur prescription", principal: true, tags: ["Cholestérol"] },
  { nom: "Peptides de collagène marin", type: "Nutritionnel", desc: "Réduction des triglycérides et du cholestérol. Issus de sources marines.", forme: "Poudre orale", dose: "5-10 g/jour", principal: false, tags: ["Cholestérol", "Anti-âge & peau"] },
  { nom: "Collagène type II (UC-II)", type: "Articulaire", desc: "Reconstruction du cartilage articulaire. Réduit la douleur arthrosique.", forme: "Oral", dose: "40 mg/jour", principal: true, tags: ["Arthrose & articulations", "Douleur"] },
  { nom: "AOD-9604", type: "Régénération", desc: "Régénération du cartilage et action anti-inflammatoire articulaire. Dérivé de la GH.", forme: "Injection SC / Oral", dose: "300-500 mcg/jour", principal: false, tags: ["Arthrose & articulations", "Perte de poids"] },
  { nom: "Selank", type: "Neurologique", desc: "Anti-anxiété, protection neuronale, amélioration de la mémoire à court terme.", forme: "Spray nasal / Injection", dose: "250-500 mcg (3x/jour)", principal: false, tags: ["Alzheimer & cognition", "Anti-inflammatoire", "Douleur"] },
  { nom: "Humanine", type: "Neurologique", desc: "Protection contre la toxicité bêta-amyloïde. Survie des neurones prolongée.", forme: "Injection SC", dose: "4-8 mg/jour", principal: false, tags: ["Alzheimer & cognition", "Anti-âge & peau"] },
  { nom: "NAP (Davunetide)", type: "Neurologique", desc: "Protection directe contre les plaques amyloïdes et les enchevêtrements Tau.", forme: "Spray nasal", dose: "En essais cliniques", principal: false, tags: ["Alzheimer & cognition"] },
  { nom: "Mélatonine", type: "Hormonal", desc: "Régulation du cycle veille-sommeil, antioxydant, régulation circadienne.", forme: "Oral / Spray", dose: "0,5-5 mg/soir", principal: true, tags: ["Sommeil & hormones", "Anti-âge & peau"] },
  { nom: "Leptine", type: "Métabolique", desc: "Régulation de l'appétit et du poids corporel via le cerveau.", forme: "Injection", dose: "Sur prescription", principal: false, tags: ["Perte de poids", "Sommeil & hormones"] },
  { nom: "VIP (Peptide Vasoactif Intestinal)", type: "Immunitaire", desc: "Inflammation intestinale et maladies auto-immunes. Modulateur immunitaire.", forme: "Injection / Inhalation", dose: "25-50 mcg", principal: false, tags: ["Anti-inflammatoire", "Immunité"] },
  { nom: "Annexine A1", type: "Anti-inflammatoire", desc: "Anti-inflammatoire puissant. Régulation des globules blancs et de l'inflammation systémique.", forme: "Injection", dose: "Recherche", principal: false, tags: ["Anti-inflammatoire"] },
  { nom: "α-MSH (Mélanotropine)", type: "Neurologique", desc: "Inflammation cérébrale et systémique. Protecteur neuronal.", forme: "Injection / Spray nasal", dose: "0,5-1 mg", principal: false, tags: ["Anti-inflammatoire", "Anti-âge & peau"] },
  { nom: "Cathélicidine LL-37", type: "Antimicrobien", desc: "Inflammation cutanée, cicatrisation et protection antimicrobienne.", forme: "Topique / Injection", dose: "Topique ou 50-100 mcg", principal: false, tags: ["Cicatrisation", "Anti-inflammatoire"] },
  { nom: "Follistatin (peptide)", type: "Cosmétique capillaire", desc: "Bloque la DHT, prévient la chute androgénétique.", forme: "Injection SC / Topique", dose: "100 mcg (2x/semaine)", principal: false, tags: ["Cheveux"] },
  { nom: "BNP / ANP", type: "Cardiovasculaire", desc: "Régulation de la pression artérielle et diagnostic de l'insuffisance cardiaque.", forme: "Injection (médical)", dose: "Sur prescription", principal: false, tags: ["Cholestérol", "Anti-inflammatoire"] }
];

const $ = (s) => document.querySelector(s);
const norm = (s) => String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const ecran = $("#ecran");
const titre = $("#titre");
const retour = $("#retour");
let derniereListe = null;

function nbCat(c) { return PEPTIDES.filter((p) => p.tags.includes(c)).length; }
function trie(l) { return l.slice().sort((a, b) => (b.principal ? 1 : 0) - (a.principal ? 1 : 0)); }

function carte(p) {
  const i = PEPTIDES.indexOf(p);
  return `<button type="button" class="carte${p.principal ? " principal" : ""}" data-fiche="${i}">
    <div><span class="nom">${esc(p.nom)}</span>${p.principal ? '<span class="principal-etiq">Principal</span>' : ""}</div>
    <div class="type">${esc(p.type)}</div>
    <div class="desc">${esc(p.desc)}</div>
  </button>`;
}

function listeHtml(liste, libelle) {
  if (!liste.length) return '<div class="vide">Aucun résultat. Essaie un autre mot.</div>';
  return `<div class="nb">${liste.length} peptide${liste.length > 1 ? "s" : ""} pour ${esc(libelle)}</div>` + liste.map(carte).join("");
}

function montreAccueil() {
  derniereListe = null;
  titre.textContent = "Peptides";
  retour.hidden = true;
  ecran.innerHTML = `
    <input id="q" class="recherche" type="search" placeholder="Cas ou nom : douleur, érection, cheveux…" autocomplete="off" aria-label="Rechercher un cas ou un peptide">
    <div id="accueil">
      <p class="intro">Choisis un cas pour voir tous les peptides qui peuvent aider.</p>
      <div class="tuiles">
        <button type="button" class="tuile tous" data-cat="*">Tous les peptides<small>${PEPTIDES.length} fiches</small></button>
        ${CATEGORIES.map((c) => `<button type="button" class="tuile" data-cat="${esc(c)}">${esc(c)}<small>${nbCat(c)} peptide${nbCat(c) > 1 ? "s" : ""}</small></button>`).join("")}
      </div>
    </div>
    <div id="res"></div>`;
  window.scrollTo(0, 0);
}

function montreSousEcran(nomTitre) {
  titre.textContent = nomTitre;
  retour.hidden = false;
  window.scrollTo(0, 0);
}

function entreSousEcran() {
  if (!(history.state && history.state.n === "sub")) history.pushState({ n: "sub" }, "");
}

function montreListe(cat) {
  const liste = cat === "*" ? PEPTIDES : PEPTIDES.filter((p) => p.tags.includes(cat));
  const libelle = cat === "*" ? "tous les cas" : cat;
  derniereListe = { cat, libelle };
  entreSousEcran();
  montreSousEcran(cat === "*" ? "Tous les peptides" : cat);
  ecran.innerHTML = listeHtml(trie(liste), libelle);
}

function montreRecherche(q) {
  const n = norm(q).trim();
  const accueil = $("#accueil");
  const res = $("#res");
  if (!n) { accueil.hidden = false; res.innerHTML = ""; return; }
  accueil.hidden = true;
  const liste = PEPTIDES.filter((p) => norm(p.nom + " " + p.desc + " " + p.type + " " + p.tags.join(" ") + " " + p.forme).includes(n));
  derniereListe = null;
  res.innerHTML = listeHtml(trie(liste), "« " + q.trim() + " »");
}

function montreFiche(i) {
  const p = PEPTIDES[i];
  entreSousEcran();
  montreSousEcran(p.nom);
  ecran.innerHTML = `
    <article class="fiche">
      <h2>${esc(p.nom)}</h2>
      <div class="type">${esc(p.type)}${p.principal ? '<span class="principal-etiq">Principal</span>' : ""}</div>
      <p class="desc">${esc(p.desc)}</p>
      <div class="tags">${p.tags.map((t) => `<button type="button" class="badge" data-cat="${esc(t)}">${esc(t)}</button>`).join("")}</div>
      <dl>
        <div><dt>Forme</dt><dd>${esc(p.forme)}</dd></div>
        <div><dt>Dose indicative</dt><dd>${esc(p.dose)}</dd></div>
      </dl>
    </article>
    ${derniereListe ? '<button type="button" class="lien" data-liste="1">‹ Retour à la liste</button>' : ""}`;
}

ecran.addEventListener("click", (e) => {
  const f = e.target.closest("[data-fiche]");
  if (f) {
    const q = $("#q");
    if (q && q.value.trim()) derniereListe = null;
    montreFiche(Number(f.dataset.fiche));
    return;
  }
  const c = e.target.closest("[data-cat]");
  if (c) { montreListe(c.dataset.cat); return; }
  if (e.target.closest("[data-liste]") && derniereListe) montreListe(derniereListe.cat);
});

ecran.addEventListener("input", (e) => { if (e.target.id === "q") montreRecherche(e.target.value); });

function versAccueil() {
  if (history.state && history.state.n === "sub") history.back();
  else montreAccueil();
}
retour.addEventListener("click", versAccueil);
window.addEventListener("popstate", () => montreAccueil());

$("#ver").textContent = VERSION;
history.replaceState({ n: "accueil" }, "");
montreAccueil();

fetch("/version.txt", { cache: "no-store" })
  .then((r) => r.text())
  .then((t) => {
    const v = t.trim();
    if (v && v !== VERSION) {
      try {
        if (!sessionStorage.getItem("rl-" + v)) { sessionStorage.setItem("rl-" + v, "1"); location.reload(); }
      } catch (_) {}
    }
  })
  .catch(() => {});

// Flashback — serveur : une salle par partie (Durable Object), téléphones et écran reliés en temps réel
import { DurableObject } from "cloudflare:workers";
import { CHANSONS, ECRANS, EVENEMENTS, CULTURE, SOUVENIRS, ARCHIVES } from "./contenu.js";

const json = (d, s = 200) =>
  new Response(JSON.stringify(d), { status: s, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

const LETTRES = "ABCDEFGHJKLMNPRSTUVWXZ";
const nouveauCode = () => Array.from({ length: 4 }, () => LETTRES[Math.floor(Math.random() * LETTRES.length)]).join("");
const melange = (a) => { const b = a.slice(); for (let i = b.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [b[i], b[j]] = [b[j], b[i]]; } return b; };
const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, " ").trim();

// Recherche de l'extrait de 30 s sur Deezer au moment du jeu (rien n'est stocké)
async function extraitDeezer(ch, env) {
  if (env && env.MOCK_DEEZER) return { preview: "/test.wav", pochette: "", lien: "" };
  const essais = [`artist:"${ch.a}" track:"${ch.t}"`, `${ch.a} ${ch.t}`];
  for (const q of essais) {
    try {
      const r = await fetch("https://api.deezer.com/search?limit=10&q=" + encodeURIComponent(q), { headers: { "user-agent": "Flashback" } });
      const d = await r.json();
      const premier = norm(ch.a).split(" ")[0];
      const bon = (d.data || []).find((x) => x.preview && norm(x.artist && x.artist.name).includes(premier) && norm(x.title).includes(norm(ch.t).split(" ").slice(0, 2).join(" ")))
        || (d.data || []).find((x) => x.preview && norm(x.artist && x.artist.name).includes(premier));
      if (bon) return { preview: bon.preview, pochette: bon.album && (bon.album.cover_big || bon.album.cover_medium), lien: bon.link };
    } catch (e) {}
  }
  return null;
}

const DUREES = { karaoke: 40000, ecoute: 22000, archive: 45000, blind: 16000, revele: 4500, danse: 11000, annee: 13000, ecran: 20000, evenement: 20000, culture: 11000, souvenir: 45000 };

export class Salle extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.prises = new Set(); // { ws, role, id }
    this.joueurs = new Map();
    this.phase = "salon";
    this.prog = [];
    this.k = -1;
    this.q = null;
    this.reponses = new Map();
    this.minuterie = null;
    this.fin = 0;
    this.code = "";
    this.options = { decennies: [1960, 1970, 1980, 1990, 2000], longueur: 12 };
    this.dejaJoue = new Set();
  }

  async fetch(req) {
    const url = new URL(req.url);
    this.code = url.searchParams.get("code") || this.code;
    if (url.pathname.endsWith("/voix")) {
      if (req.method === "POST") {
        const id = url.searchParams.get("id");
        if (this.phase !== "karaoke" || !this.q || this.q.chanteur !== id) return json({ erreur: "Ce n'est pas ton tour" }, 409);
        const buf = await req.arrayBuffer();
        if (!buf.byteLength || buf.byteLength > 2_000_000) return json({ erreur: "Enregistrement trop long" }, 413);
        this.voix = { buf, type: req.headers.get("content-type") || "audio/webm", n: (this.voix ? this.voix.n : 0) + 1 };
        clearTimeout(this.minuterie);
        this.q.voix = this.voix.n;
        this.q.effet = ["canard", "geant", "robot", "stade"][Math.floor(Math.random() * 4)];
        this.ouvrir("ecoute");
        return json({ ok: true });
      }
      if (!this.voix) return new Response("Pas d'enregistrement", { status: 404 });
      return new Response(this.voix.buf, { headers: { "content-type": this.voix.type, "cache-control": "no-store" } });
    }
    if (url.pathname.endsWith("/livre")) {
      const livre = (await this.ctx.storage.get("livre")) || [];
      return json({ code: this.code, livre });
    }
    if (req.headers.get("Upgrade") !== "websocket") return json({ erreur: "WebSocket attendu" }, 426);
    const [client, serveur] = Object.values(new WebSocketPair());
    serveur.accept();
    const prise = { ws: serveur, role: url.searchParams.get("role") === "ecran" ? "ecran" : "joueur", id: null };
    this.prises.add(prise);
    serveur.addEventListener("message", (e) => { try { this.message(prise, JSON.parse(e.data)); } catch (err) {} });
    const ferme = () => {
      this.prises.delete(prise);
      if (prise.id && this.joueurs.has(prise.id)) { this.joueurs.get(prise.id).connecte = false; this.diffuse(); }
    };
    serveur.addEventListener("close", ferme);
    serveur.addEventListener("error", ferme);
    this.envoie(prise);
    return new Response(null, { status: 101, webSocket: client });
  }

  // ---------- Messages ----------
  message(p, m) {
    if (m.type === "ping") return;
    if (m.type === "rejoindre") {
      const nom = String(m.nom || "").trim().slice(0, 16);
      if (!nom) return;
      let id = m.id && this.joueurs.has(m.id) ? m.id : null;
      if (!id) {
        if (this.joueurs.size >= 12) return p.ws.send(JSON.stringify({ type: "erreur", texte: "La partie est complète (12 joueurs)." }));
        id = crypto.randomUUID().slice(0, 8);
        this.joueurs.set(id, { id, nom, emoji: "", couleur: "", naissance: 0, score: 0, connecte: true, gains: 0 });
      }
      const j = this.joueurs.get(id);
      j.nom = nom;
      j.emoji = String(m.emoji || "🙂").slice(0, 8);
      j.couleur = /^#[0-9a-fA-F]{6}$/.test(m.couleur || "") ? m.couleur : "#F2683C";
      const n = Number(m.naissance);
      j.naissance = n >= 1920 && n <= 2020 ? n : 0;
      j.connecte = true;
      p.id = id;
      p.ws.send(JSON.stringify({ type: "bienvenue", id }));
      return this.diffuse();
    }
    if (m.type === "demarrer" && p.role === "ecran" && (this.phase === "salon" || this.phase === "fin")) {
      const dec = Array.isArray(m.decennies) ? m.decennies.map(Number).filter((d) => [1960, 1970, 1980, 1990, 2000].includes(d)) : [];
      this.options.decennies = dec.length ? dec : [1960, 1970, 1980, 1990, 2000];
      this.options.longueur = [8, 12, 16].includes(Number(m.longueur)) ? Number(m.longueur) : 12;
      if (!this.joueurs.size) return;
      for (const j of this.joueurs.values()) { j.score = 0; j.gains = 0; }
      this.prog = this.programme();
      this.k = -1;
      return this.suivante();
    }
    if (m.type === "suivant" && p.role === "ecran" && this.phase !== "salon" && this.phase !== "fin") return this.suivante();
    if (m.type === "salon" && p.role === "ecran") { clearTimeout(this.minuterie); this.phase = "salon"; this.q = null; return this.diffuse(); }
    if (m.type === "retirer" && p.role === "ecran" && this.phase === "salon") { this.joueurs.delete(String(m.id)); return this.diffuse(); }

    // réponses des joueurs
    if (!p.id || !this.q) return;
    const ouvert = Date.now() < this.fin;
    if (m.type === "choix" && ["blind", "ecran", "evenement"].includes(this.phase) && ouvert && !this.reponses.has(p.id)) {
      this.reponses.set(p.id, { choix: Number(m.choix), t: Date.now() });
      this.diffuse();
      if (this.tousOntRepondu()) this.raccourcir();
    } else if (m.type === "annee" && this.phase === "annee" && ouvert && !this.reponses.has(p.id)) {
      const v = Math.round(Number(m.valeur));
      if (v >= 1950 && v <= 2015) { this.reponses.set(p.id, { annee: v, t: Date.now() }); this.diffuse(); if (this.tousOntRepondu()) this.raccourcir(); }
    } else if (m.type === "souvenir" && this.phase === "souvenir") {
      const texte = String(m.texte || "").trim().slice(0, 500);
      const prev = this.reponses.get(p.id) || {};
      this.reponses.set(p.id, { ...prev, raconte: true, texte: texte || prev.texte || "" });
      if (texte) this.garderSouvenir(this.joueurs.get(p.id).nom, texte);
      this.diffuse();
      if (this.tousOntRepondu()) this.raccourcir();
    }
  }

  async garderSouvenir(nom, texte) {
    const livre = (await this.ctx.storage.get("livre")) || [];
    livre.push({ nom, texte, annee: this.q.y, theme: this.q.txt, quand: new Date().toISOString().slice(0, 10) });
    await this.ctx.storage.put("livre", livre.slice(-300));
  }

  rev() { return DUREES.revele / (this.env.ACCELERE ? 3 : 1); }

  tousOntRepondu() {
    const actifs = [...this.joueurs.values()].filter((j) => j.connecte);
    return actifs.length > 0 && actifs.every((j) => this.reponses.has(j.id) && (this.phase !== "souvenir" || this.reponses.get(j.id).raconte));
  }
  raccourcir() {
    clearTimeout(this.minuterie);
    this.fin = Date.now() + 1200;
    this.diffuseFin();
    this.minuterie = setTimeout(() => this.cloture(), 1200);
  }

  // ---------- Déroulé ----------
  programme() {
    const decs = this.options.decennies;
    const dans = (y) => decs.includes(Math.floor(y / 10) * 10) || (y === 2010 && decs.includes(2000));
    const chansons = melange(CHANSONS.filter((c) => dans(c.y) && !this.dejaJoue.has(c.t)));
    const ecrans = melange(ECRANS.filter((e) => dans(e.y)));
    const evts = melange(EVENEMENTS.filter((e) => dans(e.y)));
    const souv = melange(SOUVENIRS.filter((s) => dans(s.y)));
    const cult = melange(CULTURE);
    const L = this.options.longueur;
    // rythme : beaucoup de musique, une touche de télé, d'actualité, de culture et un ou deux souvenirs
    const motif = ["blind", "ecran", "blind", "evenement", "blind", "souvenir", "blind", "ecran", "blind", "evenement", "blind", "blind", "ecran", "blind", "souvenir", "blind"];
    const prog = [];
    const utilisees = new Set();
    let danses = 0, karaokes = 0;
    for (let i = 0; i < L; i++) {
      let type = motif[i % motif.length];
      if (type === "souvenir" && !souv.length) type = "blind";
      if (type === "ecran" && !ecrans.length) type = "blind";
      if (type === "evenement" && !evts.length) type = "blind";
      const finale = i >= L - 2;
      if (type === "blind" && chansons.length) {
        const ch = chansons.pop();
        this.dejaJoue.add(ch.t);
        const voisins = melange(CHANSONS.filter((c) => c.t !== ch.t && Math.abs(c.y - ch.y) <= 8)).slice(0, 3);
        const opts = melange([ch, ...voisins]);
        const danse = !!ch.danse && danses < Math.ceil(L / 5) && (i % 2 === 0 || finale);
        if (danse) danses++;
        prog.push({ type: "blind", ch, options: opts.map((o) => o.t + " — " + o.a), bonne: opts.indexOf(ch), y: ch.y, danse, finale });
      } else if (type === "ecran") {
        const e = ecrans.pop();
        const opts = melange([e.r, ...e.f]);
        prog.push({ type: "ecran", texte: e.q, options: opts, bonne: opts.indexOf(e.r), y: e.y, finale });
      } else if (type === "evenement") {
        const e = evts.pop();
        if (Math.random() < 0.5) {
          const opts = melange([e.r, ...e.f]);
          prog.push({ type: "evenement", texte: "Que s'est-il passé en " + e.y + " ?", options: opts, bonne: opts.indexOf(e.r), y: e.y, finale });
        } else {
          prog.push({ type: "annee", texte: e.r + " : c'était en quelle année ?", y: e.y, seul: true, finale });
        }
      } else if (type === "souvenir") {
        const s = souv.pop();
        prog.push({ type: "souvenir", txt: s.txt, q: s.q, y: s.y });
      }
      // karaoké déformé : un joueur chante le refrain du tube qu'on vient de trouver
      const precedente = prog[prog.length - 1];
      if (precedente && precedente.type === "blind" && !precedente.finale && karaokes < Math.max(1, Math.floor(L / 6)) && i >= 2 && (i % 4 === 2)) {
        karaokes++;
        prog.push({ type: "karaoke", t: precedente.ch.t, a: precedente.ch.a, preview: null, blind: precedente });
      }
      // une archive TV si la question en a une (jamais deux fois la même dans la partie)
      const derniere = [...prog].reverse().find((x) => x.type !== "karaoke");
      if (derniere) {
        const arch = ARCHIVES.find((a) => !utilisees.has(a.id) && (
          (a.artiste && derniere.type === "blind" && derniere.ch.a === a.artiste) ||
          (!a.artiste && a.y && (derniere.type === "evenement" || derniere.type === "annee" || derniere.type === "souvenir") && derniere.y === a.y)));
        if (arch) { utilisees.add(arch.id); prog.push({ type: "archive", video: arch.id, titre: arch.titre }); }
      }
      // une carte culture de temps en temps
      if ((i === 3 || i === 9 || i === 14) && cult.length && i < L - 1) prog.push({ type: "culture", texte: cult.pop() });
    }
    return prog;
  }

  async suivante() {
    clearTimeout(this.minuterie);
    this.k++;
    if (this.k >= this.prog.length) return this.terminer();
    this.q = this.prog[this.k];
    this.q.sous = null;
    this.reponses = new Map();
    if (this.q.type === "blind" && this.q.extrait === undefined) {
      this.q.extrait = await extraitDeezer(this.q.ch, this.env);
    }
    if (this.q.type === "karaoke") {
      const actifs = [...this.joueurs.values()].filter((j) => j.connecte);
      if (!actifs.length) return this.suivante();
      this.dejaChante = this.dejaChante || new Set();
      let pool = actifs.filter((j) => !this.dejaChante.has(j.id));
      if (!pool.length) { this.dejaChante.clear(); pool = actifs; }
      const c = pool[Math.floor(Math.random() * pool.length)];
      this.dejaChante.add(c.id);
      this.q.chanteur = c.id;
      this.q.nomChanteur = c.nom;
      this.q.voix = 0;
      this.q.extrait = this.q.blind.extrait;
    }
    this.ouvrir(this.q.type === "annee" ? "annee" : this.q.type);
  }

  ouvrir(phase) {
    this.phase = phase;
    this.reponses = new Map();
    const d = (DUREES[phase] || 15000) / (this.env.ACCELERE ? 4 : 1);
    this.fin = Date.now() + d;
    this.duree = d;
    this.debut = Date.now();
    this.dureeOuverte = d;
    this.diffuse();
    this.minuterie = setTimeout(() => this.cloture(), d);
  }

  cloture() {
    clearTimeout(this.minuterie);
    const q = this.q, mult = q.finale ? 2 : 1;
    const joueurs = [...this.joueurs.values()];
    for (const j of joueurs) j.gains = 0;
    if (["blind", "ecran", "evenement"].includes(this.phase)) {
      const duree = this.dureeOuverte, debut = this.debut;
      for (const [id, r] of this.reponses) {
        const j = this.joueurs.get(id);
        if (!j || r.choix !== q.bonne) continue;
        const vite = Math.max(0, Math.min(1, 1 - (r.t - debut) / duree));
        j.gains = Math.round((500 + 400 * vite) * mult / 10) * 10;
        j.score += j.gains;
      }
      this.phase = "revele";
      this.q.sous = q.type;
      this.fin = Date.now() + this.rev();
      this.duree = this.rev();
      this.diffuse();
      this.minuterie = setTimeout(() => {
        if (q.type === "blind" && q.danse && q.extrait) return this.ouvrir("danse");
        if (q.type === "blind") return this.ouvrir("annee");
        this.suivante();
      }, this.rev());
      return;
    }
    if (this.phase === "danse") return this.ouvrir("annee");
    if (this.phase === "annee") {
      for (const [id, r] of this.reponses) {
        const j = this.joueurs.get(id);
        if (!j) continue;
        const ecart = Math.abs(r.annee - q.y);
        j.gains = (ecart === 0 ? 600 : Math.max(0, 400 - ecart * 60)) * mult;
        j.score += j.gains;
      }
      this.phase = "revele";
      this.q.sous = "annee";
      this.q.annees = [...this.reponses.entries()].map(([id, r]) => ({ nom: this.joueurs.get(id) && this.joueurs.get(id).nom, annee: r.annee }));
      this.fin = Date.now() + this.rev() + 1000;
      this.duree = this.rev() + 1000;
      this.diffuse();
      this.minuterie = setTimeout(() => this.suivante(), this.rev() + 1000);
      return;
    }
    // culture, souvenir : on passe simplement à la suite
    this.suivante();
  }

  terminer() {
    clearTimeout(this.minuterie);
    this.phase = "fin";
    this.q = null;
    for (const j of this.joueurs.values()) j.gains = 0;
    this.diffuse();
  }

  // ---------- Diffusion ----------
  etat(pourEcran, id) {
    const q = this.q;
    let question = null;
    if (q) {
      question = { type: q.type, finale: !!q.finale, y: q.y, texte: q.texte || null, sous: q.sous || null };
      if (q.options) question.options = q.options;
      if (q.type === "souvenir") { question.txt = q.txt; question.q = q.q; }
      if (q.type === "archive") { question.video = q.video; question.titre = q.titre; }
      if (q.type === "karaoke") {
        question.titre = q.t; question.artiste = q.a; question.chanteur = q.chanteur; question.nomChanteur = q.nomChanteur;
        question.voix = q.voix || 0; question.effet = q.effet || null;
        if (pourEcran && q.extrait) question.preview = q.extrait.preview;
      }
      if (q.type === "blind") {
        question.extrait = !!q.extrait;
        if (pourEcran && q.extrait) { question.preview = q.extrait.preview; }
        if (this.phase !== "blind") { question.titre = q.ch.t; question.artiste = q.ch.a; question.pochette = q.extrait && q.extrait.pochette; question.lien = q.extrait && q.extrait.lien; }
        if (!q.extrait) question.texte = "Pas d'extrait disponible : qui chantait cette chanson ?";
      }
      if (this.phase === "revele" || this.phase === "danse" || (q.type === "blind" && this.phase === "annee")) {
        question.bonne = q.bonne;
        if (q.sous === "annee" || (q.type === "annee" && this.phase === "revele")) question.anneeJuste = q.y;
        if (q.danseurs) question.danseurs = q.danseurs;
        if (q.annees && this.phase === "revele") question.annees = q.annees;
      }
      if (q.type === "blind" && !q.extrait && this.phase === "blind") {
        question.options = q.options.map((o) => o.split(" — ")[1]);
        question.texte = "« " + q.ch.t + " » : qui la chantait ?";
      }
    }
    const joueurs = [...this.joueurs.values()].map((j) => ({
      id: j.id, nom: j.nom, emoji: j.emoji, couleur: j.couleur, score: j.score, gains: j.gains, connecte: j.connecte,
      age: q && q.y && j.naissance ? q.y - j.naissance : null,
      repondu: this.reponses.has(j.id) && (this.phase !== "souvenir" || this.reponses.get(j.id).raconte),
      choix: this.phase === "revele" && this.reponses.get(j.id) ? this.reponses.get(j.id).choix : undefined,
    }));
    const moi = id ? this.reponses.get(id) || null : null;
    return { type: "etat", code: this.code, phase: this.phase, k: this.k, total: this.prog.length, fin: this.fin, duree: this.duree || 15000, maintenant: Date.now(), question, joueurs, moi, options: this.options };
  }
  envoie(p) { try { p.ws.send(JSON.stringify(this.etat(p.role === "ecran", p.id))); } catch (e) {} }
  diffuse() { for (const p of this.prises) this.envoie(p); }
  diffuseFin() { const m = JSON.stringify({ type: "fin", fin: this.fin, duree: this.duree, maintenant: Date.now() }); for (const p of this.prises) try { p.ws.send(m); } catch (e) {} }
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname === "/api/salle" && req.method === "POST") return json({ code: nouveauCode() });
    const m = url.pathname.match(/^\/(ws|api\/livre|api\/voix)\/([A-Z]{4})$/);
    if (m) {
      const code = m[2];
      const stub = env.SALLE.get(env.SALLE.idFromName(code));
      const u = new URL(req.url);
      u.pathname = m[1] === "ws" ? "/ws" : m[1] === "api/voix" ? "/voix" : "/livre";
      u.searchParams.set("code", code);
      return stub.fetch(new Request(u, req));
    }
    if (url.pathname === "/api/test-deezer") {
      const ch = CHANSONS[Number(url.searchParams.get("i") || 0)] || CHANSONS[0];
      return json({ chanson: ch, extrait: await extraitDeezer(ch, env) });
    }
    // pages : /j/CODE (téléphone), /livre/CODE
    if (/^\/j\/[A-Z]{4}$/.test(url.pathname)) return env.ASSETS.fetch(new Request(new URL("/joueur", url), req));
    if (/^\/livre\/[A-Z]{4}$/.test(url.pathname)) return env.ASSETS.fetch(new Request(new URL("/livre", url), req));
    return env.ASSETS.fetch(req);
  },
};

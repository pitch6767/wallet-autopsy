// Test du correctif « Unsupported cache mode » dans le moteur local de Cloudflare (workerd). AUCUN ORDRE : lecture et identifiants d'un portefeuille jetable.
import axios from "axios";
import { adaptateurFetch } from "../src/reel.js";
import { ClobClient } from "@polymarket/clob-client-v2";
import { createWalletClient, http } from "viem";
import { privateKeyToAccount, generatePrivateKey } from "viem/accounts";
import { polygon } from "viem/chains";
const H = "https://clob.polymarket.com";
async function essai(nom, f) { try { const r = await f(); return { nom, ok: true, r: JSON.stringify(r).slice(0, 200) }; } catch (e) { return { nom, ok: false, erreur: String((e && e.message) || e).slice(0, 300) }; } }
export default {
  async fetch() {
    const out = [];
    const avant = axios.create({ adapter: "fetch" });                  // ancien réglage
    out.push(await essai("axios adaptateur fetch d'origine : GET /time", () => avant.get(H + "/time").then((r) => r.data)));
    const apres = axios.create({ adapter: adaptateurFetch });           // correctif
    out.push(await essai("axios correctif : GET /time", () => apres.get(H + "/time").then((r) => r.data)));
    out.push(await essai("axios correctif : GET /book (params)", () => apres.get(H + "/markets", { params: { next_cursor: "MA==" } }).then((r) => typeof r.data)));
    axios.defaults.adapter = adaptateurFetch;
    const account = privateKeyToAccount(generatePrivateKey());
    const signer = createWalletClient({ account, chain: polygon, transport: http("https://polygon-rpc.com") });
    const c = new ClobClient({ host: H, chain: 137, signer, signatureType: 0, funderAddress: account.address, throwOnError: true });
    out.push(await essai("client officiel : getOk", () => c.getOk()));
    out.push(await essai("client officiel : getVersion", () => c.getVersion()));
    out.push(await essai("client officiel : createOrDeriveApiKey (portefeuille jetable)", () => c.createOrDeriveApiKey().then((k) => ({ cle: !!(k && k.key) }))));
    return Response.json(out);
  },
};

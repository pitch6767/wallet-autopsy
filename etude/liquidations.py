"""Etude n°5 : liquidations Aave v3 (7 derniers jours, lecture seule, RPC publics).

Pour chaque chaine : nombre de liquidations, prime brute captee (valeur saisie - dette remboursee),
nombre de liquidateurs distincts et part du premier -> mesure de la concurrence.
"""
import json, time, urllib.request
from collections import defaultdict

TOPIC = "0xe413a321e8681d831f4dbccbca790d2952b56f977908e45be37335533e005286"
CHAINES = {
    "Ethereum": {"rpc": ["https://ethereum-rpc.publicnode.com", "https://eth.llamarpc.com"],
                 "pool": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2", "bloc_s": 12},
    "Arbitrum": {"rpc": ["https://arbitrum-one-rpc.publicnode.com", "https://arb1.arbitrum.io/rpc"],
                 "pool": "0x794a61358D6845594F94dc1DB02A252b5b4814aD", "bloc_s": 0.25},
    "Base": {"rpc": ["https://base-rpc.publicnode.com", "https://mainnet.base.org"],
             "pool": "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5", "bloc_s": 2},
    "Optimism": {"rpc": ["https://optimism-rpc.publicnode.com", "https://mainnet.optimism.io"],
                 "pool": "0x794a61358D6845594F94dc1DB02A252b5b4814aD", "bloc_s": 2},
    "Polygon": {"rpc": ["https://polygon-bor-rpc.publicnode.com", "https://polygon-rpc.com"],
                "pool": "0x794a61358D6845594F94dc1DB02A252b5b4814aD", "bloc_s": 2},
    "Avalanche": {"rpc": ["https://avalanche-c-chain-rpc.publicnode.com", "https://api.avax.network/ext/bc/C/rpc"],
                  "pool": "0x794a61358D6845594F94dc1DB02A252b5b4814aD", "bloc_s": 2},
}
JOURS = 7


def rpc(urls, method, params):
    err = None
    for u in urls:
        for k in range(2):
            try:
                req = urllib.request.Request(u, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
                                             headers={"Content-Type": "application/json", "User-Agent": "etude"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    d = json.loads(r.read())
                if "error" in d:
                    raise RuntimeError(str(d["error"])[:120])
                return d["result"]
            except Exception as e:
                err = e
                time.sleep(1)
    raise err


def call(urls, to, data):
    return rpc(urls, "eth_call", [{"to": to, "data": data}, "latest"])


def adresse_oracle(c):
    # Pool.ADDRESSES_PROVIDER() puis provider.getPriceOracle()
    prov = "0x" + call(c["rpc"], c["pool"], "0x0542975c")[-40:]
    return "0x" + call(c["rpc"], prov, "0xfca513a8")[-40:]


DEC = {}


def decimales(c, tok):
    if tok not in DEC:
        try:
            DEC[tok] = int(call(c["rpc"], tok, "0x313ce567"), 16)
        except Exception:
            DEC[tok] = 18
    return DEC[tok]


PRIX = {}


def prix(c, oracle, tok):
    if tok not in PRIX:
        try:
            PRIX[tok] = int(call(c["rpc"], oracle, "0xb3596f07" + tok[2:].rjust(64, "0")), 16) / 1e8
        except Exception:
            PRIX[tok] = None
    return PRIX[tok]


def logs(c, debut, fin):
    out, a, pas = [], debut, 50000
    while a <= fin:
        b = min(a + pas - 1, fin)
        try:
            out += rpc(c["rpc"], "eth_getLogs", [{"address": c["pool"], "topics": [TOPIC], "fromBlock": hex(a), "toBlock": hex(b)}])
            a = b + 1
            pas = min(pas * 2, 200000)
        except Exception:
            if pas <= 500:
                raise
            pas //= 4
    return out


def etude(nom, c):
    t0 = time.time()
    fin = int(rpc(c["rpc"], "eth_blockNumber", []), 16)
    debut = fin - int(JOURS * 86400 / c["bloc_s"])
    L = logs(c, debut, fin)
    oracle = adresse_oracle(c)
    par_liq = defaultdict(float)
    nb_liq = defaultdict(int)
    prime_tot, n_prix = 0.0, 0
    txs = []
    for l in L:
        coll = "0x" + l["topics"][1][-40:]
        dette = "0x" + l["topics"][2][-40:]
        d = l["data"][2:]
        a_couvrir = int(d[0:64], 16)
        saisi = int(d[64:128], 16)
        liquidateur = "0x" + d[128 + 24:192]
        pc, pd = prix(c, oracle, coll), prix(c, oracle, dette)
        if pc and pd:
            v = saisi / 10 ** decimales(c, coll) * pc - a_couvrir / 10 ** decimales(c, dette) * pd
            if -1e6 < v < 1e7:
                prime_tot += v; n_prix += 1
                par_liq[liquidateur] += v
        nb_liq[liquidateur] += 1
        txs.append(l["transactionHash"])
    n = len(L)
    print("\n=== %s : %d liquidations en %d jours (%.0fs)" % (nom, n, JOURS, time.time() - t0))
    if not n:
        return
    print("prime brute captee (valeur saisie - dette, prix actuels) : %.0f $ (%d evaluees)" % (prime_tot, n_prix))
    print("prime moyenne par liquidation : %.0f $" % (prime_tot / max(n_prix, 1)))
    print("liquidateurs distincts : %d" % len(nb_liq))
    tri = sorted(nb_liq.items(), key=lambda x: -x[1])
    top = tri[0][1] / n
    top3 = sum(x[1] for x in tri[:3]) / n
    print("part du 1er liquidateur : %.0f %% | des 3 premiers : %.0f %%" % (top * 100, top3 * 100))
    print("top 5 (nb, prime $) :", [(a[:10], k, round(par_liq[a])) for a, k in tri[:5]])
    petites = sum(1 for a in par_liq if 0 < par_liq[a] < 50)
    print("liquidateurs ayant gagne moins de 50 $ au total : %d" % petites)
    # cout du gaz sur un echantillon
    import random
    ech = random.sample(txs, min(25, len(txs)))
    gaz = []
    for h in ech:
        try:
            r = rpc(c["rpc"], "eth_getTransactionReceipt", [h])
            gaz.append(int(r["gasUsed"], 16) * int(r.get("effectiveGasPrice", "0x0"), 16) / 1e18)
        except Exception:
            pass
    if gaz:
        pnat = None
        print("gaz moyen par liquidation (jeton natif) : %.6f" % (sum(gaz) / len(gaz)))


def main():
    for nom, c in CHAINES.items():
        try:
            etude(nom, c)
        except Exception as e:
            print("\n=== %s : echec %s" % (nom, str(e)[:150]))


if __name__ == "__main__":
    main()

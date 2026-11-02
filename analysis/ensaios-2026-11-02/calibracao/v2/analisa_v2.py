"""Régua v2: porteira da fonte, quatro notas, backlog concorrendo junto, no
máximo duas pautas por empresa. Mede a estabilidade entre rodadas e compara
com a v1 (resultado.txt)."""
import json, statistics, sys, unicodedata

CRIT = ["foco", "impacto", "novidade", "memoria"]
cands = {c["id"]: c for c in json.load(open("candidatas.json"))}
grupos = json.load(open("grupos.json"))
rodadas = [1, 2, 3]


def le(r):
    bruto = json.load(open(f"notas-{r}.json"))
    txt = bruto["result"]
    notas = {n["id"]: n for n in json.loads(txt[txt.index("["): txt.rindex("]") + 1])}
    assert set(notas) == set(cands), (r, set(cands) ^ set(notas))
    for n in notas.values():
        assert isinstance(n["fonte"]["passa"], bool) and n["fonte"].get("porta") and n["fonte"].get("leitura"), (r, n["id"])
        for c in CRIT:
            assert isinstance(n["notas"][c], int) and 1 <= n["notas"][c] <= 5, (r, n["id"], c)
        for c in CRIT + ["fonte"]:
            assert n["por_que"].get(c), (r, n["id"], c)
    return notas, bruto.get("total_cost_usd")


def empresa(nome):
    e = unicodedata.normalize("NFKD", nome.lower()).encode("ascii", "ignore").decode()
    for chave, alvo in [("alphabet", "google"), ("deepmind", "google"), ("google", "google"), ("openai", "openai"),
                        ("anthropic", "anthropic"), ("meta", "meta"), ("microsoft", "microsoft"), ("github", "microsoft")]:
        if chave in e:
            return alvo
    return e


def escolhe(notas):
    elegiveis = sorted((-sum(n["notas"].values()), -n["notas"]["impacto"], -n["notas"]["foco"], -n["notas"]["novidade"], i)
                       for i, n in notas.items() if n["fonte"]["passa"] and n["notas"]["novidade"] > 1)
    esc, por = [], {}
    for e in elegiveis:
        emp = empresa(notas[e[4]]["empresa"])
        if por.get(emp, 0) >= 2:
            continue
        esc.append(e[4]); por[emp] = por.get(emp, 0) + 1
        if len(esc) == 3:
            break
    return esc, [(-e[0], e[4]) for e in elegiveis[:7]]


L = {r: le(r) for r in rodadas}
print("custo por rodada:", {r: L[r][1] for r in rodadas})
for r in rodadas:
    esc, topo = escolhe(L[r][0])
    print(f"rodada {r}: escolhidas {esc}\n   as sete primeiras: {topo}")

print("\nporteira (passa em quantas rodadas) e porta mais citada")
for i in cands:
    p = [L[r][0][i]["fonte"]["passa"] for r in rodadas]
    if len(set(p)) > 1 or not p[0]:
        portas = [L[r][0][i]["fonte"]["porta"] for r in rodadas]
        print(f"  {i:24} passa {p}  portas {portas}")

print("\nsoma (4 a 20) por rodada, só as que passam")
linhas = []
for i in cands:
    if not all(L[r][0][i]["fonte"]["passa"] for r in rodadas):
        continue
    s = [sum(L[r][0][i]["notas"].values()) for r in rodadas]
    meds = {c: statistics.median(L[r][0][i]["notas"][c] for r in rodadas) for c in CRIT}
    linhas.append((-statistics.median(s), i, s, meds))
for _, i, s, meds in sorted(linhas):
    execs = sorted({e for e, sec in grupos.get(i, []) if sec == "entrou"})
    print(f"  {i:24} {s} amp {max(s)-min(s)} " + " ".join(f"{c[:3]}={meds[c]:g}" for c in CRIT)
          + (f"  [entrou em: {', '.join(execs)}]" if execs else ""))

print("\nvariação por critério")
for c in CRIT:
    difs = [max(L[r][0][i]["notas"][c] for r in rodadas) - min(L[r][0][i]["notas"][c] for r in rodadas) for i in cands]
    print(f"  {c:9} {sum(1 for d in difs if d)} de {len(difs)} variam; maior diferença {max(difs)}")
amps = [max(sum(L[r][0][i]["notas"].values()) for r in rodadas) - min(sum(L[r][0][i]["notas"].values()) for r in rodadas) for i in cands]
print(f"  soma: amplitude mediana {statistics.median(amps)}, máxima {max(amps)}, sem variação: {amps.count(0)} de {len(amps)}")

"""Aplica as regras da régua às notas de cada rodada e mede a estabilidade:
quanto a nota de cada candidata varia entre rodadas, e se as três escolhidas
se repetem. As regras são as de config/rubrica-pautas.md."""
import json, re, statistics, sys, unicodedata

CRIT = ["fonte", "foco", "impacto", "novidade", "memoria"]
cands = {c["id"]: c for c in json.load(open("candidatas.json"))}
grupos = json.load(open("grupos.json"))
rodadas = [int(a) for a in sys.argv[1:]] or [1, 2, 3]


def le(r):
    bruto = json.load(open(f"rodada-{r}.json"))
    txt = bruto["result"]
    txt = txt[txt.index("["): txt.rindex("]") + 1]
    notas = {n["id"]: n for n in json.loads(txt)}
    assert set(notas) == set(cands), (r, set(cands) ^ set(notas))
    for n in notas.values():
        for c in CRIT:
            assert isinstance(n["notas"][c], int) and 1 <= n["notas"][c] <= 5, (r, n["id"], c)
            assert n["por_que"].get(c), (r, n["id"], c)
    return notas, bruto.get("total_cost_usd"), bruto.get("num_turns")


def empresa(nome):
    e = unicodedata.normalize("NFKD", nome.lower()).encode("ascii", "ignore").decode()
    for chave, alvo in [("alphabet", "google"), ("deepmind", "google"), ("google", "google"), ("openai", "openai"),
                        ("anthropic", "anthropic"), ("meta", "meta"), ("microsoft", "microsoft"), ("github", "microsoft")]:
        if chave in e:
            return alvo
    return e


def escolhe(notas):
    elegiveis = []
    for i, n in notas.items():
        v = n["notas"]
        if v["fonte"] <= 2 or v["novidade"] == 1:
            continue
        elegiveis.append((-sum(v.values()), -v["impacto"], -v["foco"], -v["novidade"], i))
    elegiveis.sort()
    janela = [e for e in elegiveis if not cands[e[4]]["do_backlog"]]
    backlog = [e for e in elegiveis if cands[e[4]]["do_backlog"]]
    escolhidas, por_empresa = [], {}
    for e in janela:
        emp = empresa(notas[e[4]]["empresa"])
        if por_empresa.get(emp, 0) >= 2:
            continue
        escolhidas.append(e[4]); por_empresa[emp] = por_empresa.get(emp, 0) + 1
        if len(escolhidas) == 3:
            break
    fortes = sum(1 for e in janela if -e[0] >= 16)
    if fortes < 2 and backlog:
        escolhidas[-1] = backlog[0][4]
    return escolhidas, fortes, len(elegiveis)


lidas = {r: le(r) for r in rodadas}
print("custo e turnos por rodada:", {r: (lidas[r][1], lidas[r][2]) for r in rodadas})
for r in rodadas:
    esc, fortes, n_eleg = escolhe(lidas[r][0])
    print(f"rodada {r}: escolhidas {esc}  (elegíveis {n_eleg}, da janela com soma >= 16: {fortes})")

print("\nnotas por candidata (soma em cada rodada; mediana de cada critério; amplitude da soma)")
linhas = []
for i in cands:
    somas = [sum(lidas[r][0][i]["notas"].values()) for r in rodadas]
    meds = {c: statistics.median(lidas[r][0][i]["notas"][c] for r in rodadas) for c in CRIT}
    elim = [r for r in rodadas if lidas[r][0][i]["notas"]["fonte"] <= 2 or lidas[r][0][i]["notas"]["novidade"] == 1]
    linhas.append((-statistics.median(somas), i, somas, meds, elim))
for _, i, somas, meds, elim in sorted(linhas):
    execs = sorted({e for e, s in grupos.get(i, []) if s == "entrou"})
    print(f"  {i:24} somas {somas}  amp {max(somas)-min(somas)}  "
          + " ".join(f"{c[:3]}={meds[c]:g}" for c in CRIT)
          + (f"  ELIMINADA em {elim}" if elim else "") + (f"  [entrou em: {', '.join(execs)}]" if execs else ""))

print("\nvariação por critério (quantas candidatas têm notas diferentes entre rodadas; maior diferença)")
for c in CRIT:
    difs = [max(lidas[r][0][i]["notas"][c] for r in rodadas) - min(lidas[r][0][i]["notas"][c] for r in rodadas) for i in cands]
    print(f"  {c:9} {sum(1 for d in difs if d)} de {len(difs)} variam; maior diferença {max(difs)}; "
          f"diferença de 2+: {sum(1 for d in difs if d >= 2)}")
amps = [max(sum(lidas[r][0][i]["notas"].values()) for r in rodadas) - min(sum(lidas[r][0][i]["notas"].values()) for r in rodadas) for i in cands]
print(f"  soma: amplitude mediana {statistics.median(amps)}, máxima {max(amps)}, candidatas com amplitude 0: {amps.count(0)}")

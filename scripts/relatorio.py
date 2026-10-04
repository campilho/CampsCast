#!/usr/bin/env python3
"""
CampsCast — relatório semanal do autor.

Junta num lugar só o que pede decisão do autor e o que deu errado na semana —
coisas que, sem isto, só aparecem para quem vai procurar no log de pesquisa,
no registro ou nas transcrições:

- episódios da semana, com duração, palavras, custo estimado e avisos;
- **para decidir:** sugestões de tema pendentes; fios que passaram do
  "rever até" ou vencem nos próximos 14 dias;
- temas cujo estado mudou na semana;
- fios: abertos, marcos da semana, fechados na semana;
- fontes que falharam na leitura, na semana e nas quatro anteriores — lidas
  das transcrições do agente, não do relato dele;
- avisos das conferências (roteiro, backlog, fios, repetição);
- tamanho da memória que o agente lê.

Dois gatilhos, o mesmo script: o comando /relatorio, a pedido, e o passo do
orquestrador às sextas, depois da publicação, que grava
memoria/autor/AAAA-Wnn.md e um resumo só com contagens para o estado.json —
é por ele que o vigia na nuvem avisa no celular. O relatório vai para o
repositório público: nada de audiência aqui; isso fica em privado/.

Variáveis que trocam os arquivos (o smoke test usa): METRICAS_ARQ, FIOS_ARQ,
TEMAS_ARQ, SUGESTOES_ARQ, EPISODIOS_DIR.

Uso:
    python3 scripts/relatorio.py                       # semana de hoje
    python3 scripts/relatorio.py --semana 2026-W40
    python3 scripts/relatorio.py --data 2026-10-02 --saida memoria/autor/2026-W40.md \\
        --resumo logs/relatorio.json
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from confere_fios import _depois_do_cabecalho, _fios, sugestoes  # noqa: E402

DATA = re.compile(r"\d{4}-\d{2}-\d{2}")


def arq(var: str, padrao: str) -> pathlib.Path:
    return pathlib.Path(os.environ.get(var) or ROOT / padrao)


def semana_de(d: dt.date) -> tuple[str, dt.date, dt.date]:
    ano, sem, _ = d.isocalendar()
    inicio = dt.date.fromisocalendar(ano, sem, 1)
    return f"{ano}-W{sem:02d}", inicio, inicio + dt.timedelta(days=6)


def ler(p: pathlib.Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def registros(ini: str, fim: str) -> list[dict]:
    saida = {}
    for linha in ler(arq("METRICAS_ARQ", "metricas/execucoes.jsonl")).splitlines():
        try:
            r = json.loads(linha)
        except ValueError:
            continue
        if ini <= r.get("data", "") <= fim:
            saida[r["data"]] = r          # a última execução do dia vale
    return [saida[d] for d in sorted(saida)]


def titulo_episodio(data: str) -> str:
    m = re.search(r"(?m)^title:\s*(.+)$", ler(arq("EPISODIOS_DIR", "episodes") / f"{data}.md"))
    return m[1].strip() if m else "—"


def falhas_de_leitura(ini: str, fim: str) -> collections.Counter:
    """Leituras de página que falharam, por domínio, nas transcrições do agente."""
    from memoria_custo import transcricoes_dir
    pasta, conta = transcricoes_dir(), collections.Counter()
    for ag in sorted((ROOT / "logs").glob("*-agente.json")):
        if not ini <= ag.name[:10] <= fim:
            continue
        try:
            sid = json.loads(ag.read_text(encoding="utf-8")).get("session_id")
        except (OSError, ValueError):
            continue
        t = pasta / f"{sid}.jsonl"
        if not sid or not t.exists():
            continue
        urls = {}
        for linha in t.open(encoding="utf-8"):
            r = json.loads(linha)
            conteudo = r.get("message", {}).get("content")
            if r.get("type") == "assistant":
                for c in conteudo or []:
                    if c.get("type") == "tool_use" and c.get("name") == "WebFetch":
                        urls[c["id"]] = (c.get("input") or {}).get("url", "")
            elif r.get("type") == "user" and isinstance(conteudo, list):
                for c in conteudo:
                    if c.get("type") != "tool_result" or c.get("tool_use_id") not in urls:
                        continue
                    texto = c.get("content")
                    if isinstance(texto, list):
                        texto = " ".join(x.get("text", "") for x in texto if isinstance(x, dict))
                    texto = texto or ""
                    erro = c.get("is_error") or re.search(r"HTTP [45]\d\d", texto[:300])
                    if erro:
                        host = urllib.parse.urlparse(urls[c["tool_use_id"]]).netloc
                        conta[host.removeprefix("www.")] += 1
    return conta


def fecha_semana(d: dt.date) -> bool:
    """O episódio deste dia é o último da semana? Sexta, ou a quinta se a sexta
    for feriado — quem decide é o calendário de publicação, não o dia da semana."""
    from schedule import avaliar
    _, _, fim = semana_de(d)
    dia = d + dt.timedelta(days=1)
    while dia <= fim:
        if avaliar(dia)[0]:
            return False
        dia += dt.timedelta(days=1)
    return True


def monta(d: dt.date) -> tuple[str, dict]:
    semana, ini_d, fim_d = semana_de(d)
    ini, fim, hoje = ini_d.isoformat(), fim_d.isoformat(), d.isoformat()
    regs = registros(ini, fim)
    fios_txt = ler(arq("FIOS_ARQ", "memoria/fios.md"))
    fios = _fios(_depois_do_cabecalho(fios_txt))[0]
    pendentes = [s for s in sugestoes(ler(arq("SUGESTOES_ARQ", "memoria/temas-sugeridos.md")))
                 if s["campos"].get("situação") == "pendente"]
    limite = (d + dt.timedelta(days=14)).isoformat()
    vencidos, vencendo = [], []
    for f in fios:
        r = DATA.search(f["campos"].get("rever até", ""))
        if r and r[0] < hoje:
            vencidos.append((f, r[0]))
        elif r and r[0] <= limite:
            vencendo.append((f, r[0]))
    fechados_txt = ler(arq("FIOS_ARQ", "memoria/fios.md").parent / "fios-fechados" / f"{d.year}.md")
    fechados = [(m[1], m[2]) for m in re.finditer(
        r"(?ms)^## (F-\d{3}[^\n]*).*?^- fechado:\s*(\d{4}-\d{2}-\d{2}[^\n]*)", fechados_txt)
        if ini <= m[2][:10] <= fim]
    avisos = [(r["data"], a) for r in regs for a in (r.get("avisos_roteiro") or [])]

    L = [f"# Relatório do autor — semana {semana} ({ini_d:%d/%m} a {fim_d:%d/%m})", ""]
    L += ["## Episódios", ""]
    if regs:
        L += ["| Data | Ep. | Título | Duração | Palavras | US$ est. | Avisos |",
              "|---|---|---|---|---|---|---|"]
        for r in regs:
            ep, cl = r.get("episodio") or {}, r.get("claude") or {}
            s = ep.get("audio_s")
            dur = f"{s // 60}:{s % 60:02d}" if isinstance(s, int) else "—"
            usd = cl.get("custo_estimado_usd")
            L.append(f"| {r['data'][8:]}/{r['data'][5:7]} | {ep.get('numero', '—')} | "
                     f"{titulo_episodio(r['data'])} | {dur} | {ep.get('palavras') or '—'} | "
                     f"{f'{usd:.2f}'.replace('.', ',') if isinstance(usd, (int, float)) else '—'} | "
                     f"{len(r.get('avisos_roteiro') or [])} |")
        custos = [r["claude"]["custo_estimado_usd"] for r in regs
                  if isinstance((r.get("claude") or {}).get("custo_estimado_usd"), (int, float))]
        if custos:
            total = f"{sum(custos):.2f}".replace(".", ",")
            L += ["", f"Custo do agente a preço de API: US$ {total} na semana "
                      "(não cobrado; roda na assinatura)."]
    else:
        L.append("Nenhuma execução registrada na semana.")

    L += ["", "## Para decidir", ""]
    if not (pendentes or vencidos or vencendo):
        L.append("Nada pendente.")
    for s in pendentes:
        c = s["campos"]
        L.append(f"- **Sugestão de tema {s['id']}** — {c.get('pergunta de fundo', '')} "
                 f"(sugerido {c.get('sugerido', '')}; {c.get('por quê', '')})")
    for f, r in vencidos:
        L.append(f"- **{f['id']} passou do rever até {r}** — estender ou arquivar: "
                 f"{f['campos'].get('pergunta', '')}")
    for f, r in vencendo:
        L.append(f"- {f['id']} vence em {r}: {f['campos'].get('pergunta', '')}")

    L += ["", "## Temas que mudaram", ""]
    estados = {}
    for linha in _depois_do_cabecalho(ler(arq("TEMAS_ARQ", "memoria/temas.md"))):
        m = re.match(r"^## (T-\d{2}) · (.*)$", linha)
        if m:
            atual = m[1]; estados[atual] = {"titulo": m[2]}
        m = re.match(r"^- estado \((\d{4}-\d{2}-\d{2})\):\s*(.*)$", linha)
        if m and estados:
            estados[atual].update(data=m[1], texto=m[2])
    mudaram = [(i, e) for i, e in estados.items() if ini <= e.get("data", "") <= fim]
    L += [f"- **{i} · {e['titulo']}** ({e['data']}): {e['texto']}" for i, e in mudaram] \
        or ["Nenhum tema mudou de estado."]

    L += ["", "## Fios", "", f"{sum(1 for f in fios if f['campos'].get('situação') == 'aberto')} "
          "abertos (teto de 20)."]
    marcos = []
    for linha in _depois_do_cabecalho(fios_txt):
        m = re.match(r"^## (F-\d{3})", linha)
        if m:
            atual = m[1]
        m = re.match(r"^\s+- (\d{4}-\d{2}-\d{2})(.*)$", linha)
        if m and ini <= m[1] <= fim:
            marcos.append(f"- {atual}: {m[1]}{m[2]}")
    if marcos:
        L += ["", "Marcos da semana:"] + marcos
    if fechados:
        L += ["", "Fechados na semana:"] + [f"- {t} — {q}" for t, q in fechados]

    L += ["", "## Fontes que falharam na leitura", ""]
    semana_f = falhas_de_leitura(ini, fim)
    antes = falhas_de_leitura((ini_d - dt.timedelta(days=28)).isoformat(),
                              (ini_d - dt.timedelta(days=1)).isoformat())
    if semana_f:
        L += ["| Domínio | Na semana | Nas 4 anteriores |", "|---|---|---|"]
        L += [f"| {h} | {n} | {antes.get(h, 0)} |" for h, n in semana_f.most_common(10)]
    else:
        L.append("Nenhuma falha encontrada nas transcrições da semana.")

    L += ["", "## Avisos das conferências", ""]
    L += [f"- {d[8:]}/{d[5:7]}: {a}" for d, a in avisos] or ["Nenhum aviso."]

    ind = (regs[-1].get("indicadores") or {}) if regs else {}
    if ind:
        kb = lambda k: f"{round(ind[k] / 1024)} KB" if ind.get(k) else "—"
        L += ["", "## Memória que o agente lê", "",
              f"Índice {kb('indice_pautas_bytes')} · backlog {kb('backlog_bytes')} · "
              f"fios {kb('fios_bytes')} · temas {kb('temas_bytes')} · "
              f"roteiros recentes {kb('roteiros_lidos_bytes')}"]

    resumo = {"semana": semana, "episodios": len(regs), "sugestoes_pendentes": len(pendentes),
              "fios_vencidos": len(vencidos), "fios_fechados": len(fechados),
              "avisos": len(avisos)}
    return "\n".join(L) + "\n", resumo


def main() -> int:
    ap = argparse.ArgumentParser(description="Relatório semanal do autor.")
    ap.add_argument("--data", help="um dia da semana desejada (AAAA-MM-DD); padrão: hoje")
    ap.add_argument("--semana", help="semana ISO, como 2026-W40")
    ap.add_argument("--saida", help="grava o relatório neste arquivo")
    ap.add_argument("--resumo", help="grava as contagens em JSON (para o estado.json)")
    ap.add_argument("--fecha-semana", metavar="DATA",
                    help="só responde, pelo código de saída, se DATA é o último "
                         "episódio da semana (0 = sim)")
    a = ap.parse_args()
    if a.fecha_semana:
        return 0 if fecha_semana(dt.date.fromisoformat(a.fecha_semana)) else 1
    if a.semana:
        ano, sem = a.semana.split("-W")
        d = dt.date.fromisocalendar(int(ano), int(sem), 5)
    else:
        d = dt.date.fromisoformat(a.data) if a.data else dt.date.today()
    texto, resumo = monta(d)
    if a.saida:
        pathlib.Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.saida).write_text(texto, encoding="utf-8")
    if a.resumo:
        pathlib.Path(a.resumo).write_text(json.dumps(resumo, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())

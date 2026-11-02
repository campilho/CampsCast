"""Extrai as candidatas dos cinco logs de pesquisa de 29/10: título, data, fonte e
em que seção caiu (entrou, descartada, backlog). Sai em candidatas_brutas.json."""
import json, pathlib, re, sys

RAIZ = pathlib.Path("/Users/fernandocampilho/CampsCast")
LOGS = {
    "producao": RAIZ / "research/2026-10-29.md",
    "atual-1": RAIZ / "analysis/ensaios-2026-11-02/codigo-atual-1-pesquisa.md",
    "atual-2": RAIZ / "analysis/ensaios-2026-11-02/codigo-atual-2-pesquisa.md",
    "atual-3": RAIZ / "analysis/ensaios-2026-11-02/codigo-atual-3-pesquisa.md",
    "codigo-29-10": RAIZ / "analysis/ensaios-2026-11-02/codigo-29-10-pesquisa.md",
}
SECOES = {"Entraram no episódio": "entrou", "Descartadas": "descartada", "Guardadas no backlog": "backlog"}

saida = []
for exec_, p in LOGS.items():
    t = p.read_text(encoding="utf-8")
    for nome, tipo in SECOES.items():
        m = re.search(rf"^## {re.escape(nome)}.*?$(.*?)(?=^## |\Z)", t, flags=re.M | re.S)
        if not m:
            print(f"{exec_}: sem seção {nome}", file=sys.stderr)
            continue
        for b in re.finditer(r"^### (.+?)\n(.*?)(?=^### |\Z)", m.group(1), flags=re.M | re.S):
            titulo, corpo = b.group(1).strip(), b.group(2)
            titulo = re.sub(r"^\d+\.\s*", "", titulo)
            fonte = re.search(r"^- fonte[s]?:\s*(.+?)(?=\n- |\Z)", corpo, flags=re.M | re.S)
            data = re.search(r"^- data:\s*(.+?)$", corpo, flags=re.M)
            motivo = re.search(r"^- motivo:\s*(.+?)(?=\n- |\Z)", corpo, flags=re.M | re.S)
            saida.append({"exec": exec_, "secao": tipo, "titulo": titulo,
                          "fonte": re.sub(r"\s+", " ", fonte.group(1)).strip() if fonte else "",
                          "data": data.group(1).strip() if data else "",
                          "motivo": re.sub(r"\s+", " ", motivo.group(1)).strip() if motivo else ""})
    print(exec_, sum(1 for s in saida if s["exec"] == exec_), file=sys.stderr)

pathlib.Path(sys.argv[1]).write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(saida), "entradas", file=sys.stderr)

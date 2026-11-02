"""Junta as 135 entradas dos cinco logs numa candidata por notícia. Só entram na
calibração as da janela (28/10) e as duas do backlog; a janela é conferida pelo
código, não pela nota. Sai em candidatas.json (o dossiê de cada uma: título,
fonte com o que foi lido, data) e em grupos.json (de que execuções veio)."""
import json, re, sys

# id: (padrão no título, na janela?, data, do backlog?)
G = {
    "carbon": (r"Gemini 4 Carbon(?!.*vazado)", True, "2026-10-28", False),
    "democratas-camara": (r"Democratas da Câmara", True, "2026-10-28", False),
    "bancos-canada": (r"bancos do Canadá", True, "2026-10-28", False),
    "octoverse": (r"Octoverse|40% dos pull requests", True, "2026-10-28", False),
    "ny-chatbots": (r"Nova York (assina|sanciona)", True, "2026-10-28", False),
    "alphabet-microsoft": (r"Alphabet e Microsoft", True, "2026-10-28", False),
    "ai-for-science": (r"AI for Science", True, "2026-10-28", False),
    "meta-universidades": (r"cinco universidades", True, "2026-10-28", False),
    "nvidia-rtx-spark": (r"RTX Spark", True, "2026-10-28", False),
    "openai-servicenow": (r"ServiceNow", True, "2026-10-28", False),
    "openai-future-firm": (r"future of the firm", True, "2026-10-28", False),
    "openai-dot": (r"\b[Dd]ot\b", True, "2026-10-28", False),
    "openai-creditos": (r"US\$ 500 em créditos", True, "2026-10-28", False),
    "openai-legora": (r"Legora", True, "2026-10-28", False),
    "openai-devday-paris": (r"DevDay", True, "2026-10-28", False),
    "claude-produtos": (r"Claude Enterprise|trabalho jurídico|Quanta", True, "2026-10-28", False),
    "aws-blog": (r"^AWS:", True, "2026-10-28", False),
    "akamai": (r"Akamai", True, "2026-10-28", False),
    "bytedance-jimeng": (r"ByteDance", True, "2026-10-28", False),
    "cursor-sdk": (r"Cursor", True, "2026-10-28", False),
    "github-mcp": (r"conectores MCP", True, "2026-10-28", False),
    "google-pequenos-negocios": (r"pequenos negócios", True, "2026-10-28", False),
    "google-anuncios": (r"anúncios (do AI Mode|em respostas)", True, "2026-10-28", False),
    "polonia-lei": (r"Polônia", True, "2026-10-28", False),
    "progressistas-resolucao": (r"Progressistas", True, "2026-10-28", False),
    "fingerprinting": (r"fingerprinting", True, "2026-10-28", False),
    "yc-magic-patterns": (r"Magic Patterns", True, "2026-10-28", False),
    "kentucky": (r"Kentucky", True, "2026-10-28", False),
    "uefi": (r"UEFI", True, "2026-10-28", False),
    "cohere-qwen": (r"Cohere", True, "2026-10-26", True),
}
FORA = r"vazado|Trump|cache do processador|modelo interno não lançado|Oracle|Mistral|Model Spec|misalignment|GPT-Live|RAISE|Noruega|Amazon, Yelp|Singapura|Geórgia|Holanda|capta|demissão|Cloudflare|IBM|Banco da Inglaterra|trimestre|Analytics API|Ultra|uso do computador|Uso do computador|CNIB|Eclypsium|Incident Reporting|anúncio de 29/10|Gottheimer|Itens de 27|australiana|CodeRabbit|enfraquecem|DAYJOB|DeepMind: planejamento|Capgemini|Pages, Keynote|CoreWeave|grok-voice|TPUs|chips de IA|SpaceX|Rosalind|folha de pagamento|Meituan"

brutas = json.load(open("candidatas_brutas.json"))
grupos = {k: [] for k in G}
sobra, fora = [], []
for x in brutas:
    ids = [k for k, (pad, *_r) in G.items() if re.search(pad, x["titulo"])]
    if len(ids) == 1:
        grupos[ids[0]].append(x)
    elif re.search(FORA, x["titulo"]):
        fora.append(x)
    else:
        sobra.append((ids, x["titulo"]))
if sobra:
    print("SEM GRUPO OU AMBÍGUAS:", *sobra, sep="\n  ", file=sys.stderr)
    sys.exit(1)

cands = []
for k, (_, janela, data, backlog) in G.items():
    es = grupos[k]
    assert es, k
    titulo = max((e["titulo"] for e in es), key=len)
    titulo = re.sub(r"\s*[—(]\s*\d{2}(/\d{2})?( e \d{2}/\d{2})?[^)]*\)?$", "", titulo).strip()
    fontes = []
    for e in es:
        if e["fonte"] and e["fonte"] not in fontes:
            fontes.append(e["fonte"])
    fonte = " | ".join(f[:220] for f in sorted(fontes, key=len, reverse=True)[:2]) or "(sem fonte registrada)"
    cands.append({"id": k, "titulo": titulo, "data": data, "do_backlog": backlog, "fonte": fonte})

# Do backlog de 28/10, mantido e nunca escolhido nos logs como "entrou"
cands.append({"id": "cathedral", "titulo": "Cathedral, startup de ex-funcionários do DOGE investida pela a16z e pela Sequoia, diz que seus agentes entraram em sistemas da Anthropic em menos de 12 horas; a Anthropic confirma acesso limitado",
              "data": "2026-10-26", "do_backlog": True,
              "fonte": "The Washington Post — reportagem de 26/10 (403; lida via Gizmodo e Yahoo Tech)"})
grupos["cathedral"] = []

json.dump(cands, open("candidatas.json", "w"), ensure_ascii=False, indent=1)
json.dump({k: [(e["exec"], e["secao"]) for e in v] for k, v in grupos.items()}, open("grupos.json", "w"), ensure_ascii=False, indent=1)
print(f"{len(cands)} candidatas ({sum(c['do_backlog'] for c in cands)} do backlog); {len(fora)} entradas fora da janela ou sem data conferida", file=sys.stderr)

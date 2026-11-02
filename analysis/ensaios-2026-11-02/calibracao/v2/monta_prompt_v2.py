"""Monta o prompt de uma rodada de notas: a régua (só os critérios), o briefing,
os temas, os fios e as pautas já cobertas como estavam antes de 29/10, e as
candidatas numa ordem embaralhada pela semente da rodada."""
import json, pathlib, random, re, sys

rodada = int(sys.argv[1])
R = pathlib.Path("/Users/fernandocampilho/CampsCast")
regua = (R / "config/rubrica-pautas.md").read_text(encoding="utf-8")
criterios = re.search(r"(## A porteira: fonte primária\n.*?)(?=^## O que o código)", regua, flags=re.M | re.S).group(1).strip()
cands = json.load(open("candidatas.json"))
random.Random(rodada).shuffle(cands)

p = f"""Você é o Editor do CampsCast, um podcast diário de IA em português. Hoje é 29/10/2026 e a janela de notícias deste episódio é 28/10/2026. As datas das candidatas já foram conferidas por código; não avalie a data.

Sua tarefa é passar cada candidata pela porteira da fonte e dar as quatro notas da régua do programa. Avalie uma de cada vez, pela descrição de cada nota, sem comparar com as outras candidatas. Use só o que está nesta mensagem: não pesquise nem abra nada.

# A régua

{criterios}

# Briefing editorial

{open('briefing.md', encoding='utf-8').read()}

# Temas do programa (memória)

{open('temas.md', encoding='utf-8').read()}

# Fios em aberto (memória)

{open('fios.md', encoding='utf-8').read()}

# Pautas que já foram ao ar

{open('pautas.txt', encoding='utf-8').read()}

# Candidatas

Cada uma traz o título, a data, se veio do backlog, e a fonte com o que foi lido ("lido", "índice", "403", "resumo de busca").

{json.dumps(cands, ensure_ascii=False, indent=1)}

# Resposta

Responda só com um JSON, sem texto antes ou depois: uma lista com um objeto por candidata, na ordem acima, assim:
[{{"id": "...", "empresa": "a empresa ou instituição principal", "fonte": {{"passa": true ou false, "porta": "pagina|feed|outra_porta|documento|repositorio|imprensa", "leitura": "inteira|em_parte|trechos"}}, "notas": {{"foco": 1-5, "impacto": 1-5, "novidade": 1-5, "memoria": 1-5}}, "por_que": {{"fonte": "uma linha", "foco": "uma linha", "impacto": "uma linha", "novidade": "uma linha", "memoria": "uma linha"}}}}]
"""
pathlib.Path(f"v2-prompt-{rodada}.txt").write_text(p, encoding="utf-8")
print(f"rodada {rodada}: {len(p)} caracteres, ordem: {[c['id'] for c in cands][:4]}…", file=sys.stderr)

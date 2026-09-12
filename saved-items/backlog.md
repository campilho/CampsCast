# Backlog — itens relevantes que não couberam no episódio

Formato de cada item (o agente escreve e poda automaticamente):

```
## <título da pauta>
- data_original: YYYY-MM-DD
- fonte: <nome> — <url da fonte primária>
- validade: YYYY-MM-DD   (default: 5 dias úteis após a data original)
- resumo: <duas linhas, no máximo>
```

Regras:
- Ao usar um item aqui, o roteiro **avisa a data original** e o item é removido.
- Ao final de cada execução o agente poda os itens vencidos.

---

## OpenAI fecha acordo com a GSA: licença zerada para todo o governo americano e Daybreak Blue pela metade
- data_original: 2026-09-10
- fonte: OpenAI — post oficial "Expanding AI access and cyber defense for federal, state,
  local, and tribal governments" — https://openai.com/index/expanding-ai-access-us-government/
- validade: 2026-09-17
- resumo: Acordo OneGov de 27 meses, de 01/10/2026 a 31/12/2028, zerando a licença de US$ 15
  por usuário/mês e dando 50% de desconto no uso, sem mínimo nem compromisso de gasto. A GSA
  diz que a elegibilidade passa de pouco mais de 1 milhão de servidores federais para cerca de
  23 milhões de pessoas nos três níveis de governo, incluindo tribos. Toda entidade
  governamental verificada é aprovada para o Daybreak Blue a 50% do preço comercial, e pode
  pedir o Daybreak Red, de pesquisa de vulnerabilidade e red team, a preço cheio. Acordos
  equivalentes com Anthropic e Google vencem no fim de setembro. Ficou fora em 11/09 porque as
  três pautas escolhidas encaixavam melhor entre si. Casa com o Daybreak (coberto em 04/09), com
  o Fairwind do Google (03/09) e, agora, com o relatório de ameaças da Anthropic (11/09): o
  governo comprando defesa no mesmo mês em que o fornecedor documenta o ataque autônomo.

## OpenAI abre a Agents API em beta pública
- data_original: 2026-09-10
- fonte: OpenAI — "Introducing the Agents API" — https://openai.com/index/introducing-the-agents-api/
- validade: 2026-09-17
- resumo: Põe o harness do Codex atrás de uma única chamada de API, sem taxa além do uso.
  Organizada em quatro conceitos, com compactação automática do contexto quando a sessão se
  aproxima do limite e carregamento de definição de ferramenta sob demanda, para não queimar
  token nem estragar o cache. A computação do agente roda em sandbox gerenciado pela OpenAI, na
  infraestrutura do próprio cliente ou em sandbox de parceiro (Cloudflare, DigitalOcean, Oracle).
  Foi ao topo do Hacker News no dia. Ficou fora em 11/09 por ser plataforma de desenvolvedor num
  dia com três pautas de maior alcance. Vale sozinha num dia mais fraco, e vale muito se alguém
  medir de fora o ganho de token que a OpenAI alega.

## GPT-Live-1 chega à API a cinco centavos de dólar por minuto
- data_original: 2026-09-10
- fonte: OpenAI — changelog e anúncio da plataforma de desenvolvedores
- validade: 2026-09-17
- resumo: O modelo de voz full-duplex da OpenAI, que ouve e fala ao mesmo tempo, sai do ChatGPT
  de consumo e chega ao desenvolvedor, a US$ 0,05 por minuto na camada de voz, com seguimento de
  instrução mais forte, vozes customizadas e suporte a telefonia. Lançado em 08/07 só para
  usuário final. Ficou fora em 11/09 por ser disponibilidade de um modelo já anunciado, não
  capacidade nova. Terceira pauta natural de um dia calmo, e boa deixa para falar de agente de
  voz em atendimento — que é onde o formato encosta no foco de seguros e serviços financeiros.

## Terence Tao sobre contaminação de problemas em aberto pela IA
- data_original: 2026-09-10 (data NÃO confirmada no primário)
- fonte: Terence Tao — post no Mathstodon (https://mathstodon.xyz/@tao)
- validade: 2026-09-17
- resumo: Tao argumenta que o problema de Navier-Stokes estava a caminho de ser um caso de
  sucesso de matemática assistida por IA, e que agora existe um cenário realista em que uma
  solução majoritariamente gerada por IA aparece de um jeito que contamina o problema como fonte
  de avanços futuros — porque identificar problema promissor virou o recurso escasso, e o simples
  rumor de que alguém está trabalhando num deles convida uma frota de agentes a chegar primeiro.
  NÃO usei em 11/09 porque não consegui abrir e datar o post primário com segurança, e porque a
  tese já foi ao ar parafraseada em 09/09. Só volta com formulação nova, datada e lida na origem.

## Mistral levanta 3 bilhões de euros para IA soberana de peso aberto
- data_original: 2026-09-08
- fonte: Mistral — post oficial "Mistral raises €3B to make sovereign, open-weight AI
  the technology frontier" — https://mistral.ai/news/
- validade: 2026-09-15
- resumo: Série D de €3 bilhões (cerca de US$ 3,5 bi) a uma avaliação pós-money acima de
  €21 bilhões, liderada pela Samsung, com co-líderes Scaleup Europe Fund (EQT) e PSG
  Equity; entram Advent, BlackRock e o Grão-Ducado de Luxemburgo, e seguem a16z, ASML,
  General Catalyst, Lightspeed, NVIDIA e Salesforce Ventures. Maior rodada de capital da
  história da tecnologia europeia. Arthur Mensch disse à CNBC que o dinheiro vai para
  construir e possuir data centers, além de alugar capacidade, e que a empresa deve passar
  de US$ 1 bi de receita anualizada ainda este ano. Perdeu em 09/09, 10/09 e 11/09. É rodada de
  investimento — camada 2 do sources.yaml. O ângulo ficou MAIS forte depois de 11/09: peso aberto
  europeu financiado no mesmo mês em que peso aberto vira problema de procedência, com o Kimi K3
  da Moonshot servindo de base para produto americano. ÚLTIMA CHANCE: vence em 15/09.

## Cognition levanta 2 bilhões de dólares a uma avaliação de 48 bilhões
- data_original: 2026-09-08
- fonte: Cognition / a16z — anúncio da rodada e post "Investing in Cognition" —
  https://a16z.com/
- validade: 2026-09-15
- resumo: Série E de mais de US$ 2 bilhões liderada por Andreessen Horowitz, Accel,
  Founders Fund, General Catalyst e Avenir, a uma avaliação de US$ 48 bilhões — quase o
  dobro dos US$ 26 bi da Série D de 27/05, quatro meses antes. Receita anualizada saltou
  de US$ 492 milhões para quase US$ 900 milhões no mesmo intervalo. O Devin, agente
  autônomo de engenharia de software da empresa, roda dentro de NVIDIA, GE Aerospace,
  Citi, Mercedes-Benz e Modal. PARCIALMENTE CONSUMIDO em 11/09: a rodada foi citada no ar como
  contexto do lançamento do SWE-2, com a data original. Fica no backlog porque o ângulo de
  comparação de preço entre agentes verticais (par da Harvey, coberta em 10/09) segue de pé, e
  porque a a16z ainda pode publicar tese sobre o setor.

## Instituto de segurança de IA fundado por medalhista Fields (MAISI)
- data_original: 2026-09-08
- fonte: MAISI — site oficial https://maisi.org/ e anúncio do próprio Jacob Tsimerman
- validade: 2026-09-15
- resumo: Jacob Tsimerman, medalhista Fields de 2026, anunciou a fundação do Mathematical
  AI Safety Institute, sem fins lucrativos e independente, para desenvolver fundamentos
  matemáticos de segurança de IA. Diretor executivo: Andrew Critch. Painel consultivo com
  Timothy Gowers (Fields 1998), Paul Christiano e Geoffrey Irving. Baseado na Bay Area,
  no modelo do Institute for Advanced Study de Princeton: 10 a 30 pesquisadores no
  semestre de janeiro de 2027, 30 a 100 no ano especial de setembro de 2027. Tsimerman
  também se junta à área de segurança da OpenAI. Ficou fora em 10/09 e 11/09 por estar fora da
  janela (08/09). Casa com o alerta de Terence Tao (citado em 09/09) e com a entrada do
  Christiano no conselho da OpenAI (coberta em 10/09) — o mesmo nome nos dois lados da mesa.
  Vale se o instituto publicar programa de pesquisa ou anunciar financiadores.
  ÚLTIMA CHANCE: vence em 15/09.

---

Podados nesta execução:
- Quadro de recados de agentes da OpenAI numa wiki alemã, a collusion.wiki (original de
  04/09) — venceu em 11/09 sem nunca ter ganhado post oficial, paper ou release da OpenAI.
  A empresa chegou a confirmar o incidente numa rede social em 05/09 e disse estar construindo
  um arcabouço para divulgar incidentes de desalinhamento; passou por três episódios sem entrar.
  Se esse arcabouço for publicado, a pauta volta do zero, e volta grande.

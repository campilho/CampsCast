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

## Google lança compreensão agêntica de vídeo no Gemini
- data_original: 2026-09-01
- fonte: Google — The Keyword — https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/
- validade: 2026-09-08
- resumo: O modelo escolhe sozinho quais trechos, quadros e modalidades do vídeo analisar, em vez
  de amostrar a taxa fixa: até 88% menos tokens, até 66% menos custo e até 7% mais acurácia
  (números do Google). Vale em Gemini 3.7 Flash, 3.6 Flash e 3.5 Flash-Lite, via API e AI Studio,
  sem taxa extra. Perdeu para o lançamento do Fable 5.1 e para as duas pautas de setor regulado.

## OpenAI conecta Epic e nove bases públicas de saúde ao ChatGPT
- data_original: 2026-09-01
- fonte: OpenAI — post oficial https://openai.com/index/chatgpt-connects-health-records-and-healthcare-sources/
- validade: 2026-09-08
- resumo: Organizações de saúde passam a ligar ambientes Epic ao ChatGPT para consultar o
  prontuário autorizado, e um plugin de dados públicos reúne conectores para nove fontes
  oficiais (ClinicalTrials.gov, CMS Coverage, RxNorm, DailyMed, PubMed e outras). Ângulo de
  agente em setor regulado, mas é integração de aplicativo: não muda o que o modelo consegue
  fazer. Página oficial não abriu por WebFetch (403); confirmada via busca restrita a openai.com.

## AWS Agent Registry entra em disponibilidade geral
- data_original: 2026-08-31
- fonte: AWS Machine Learning Blog — https://aws.amazon.com/blogs/machine-learning/manage-agents-tools-and-skills-at-scale-with-aws-agent-registry/
- validade: 2026-09-07
- resumo: Catálogo corporativo de agentes, ferramentas e skills, com registro de servidores
  MCP e agentes A2A, plano de governança separado do de descoberta, aprovação por papel,
  trilha de auditoria no CloudTrail e varredura de endpoints para achar "shadow AI".
  Casa com o foco de agente em setor regulado; ficou de fora porque as duas pautas de
  risco do dia eram mais fortes.

## Anthropic mostra Claude fazendo pesquisa de alinhamento sozinho
- data_original: 2026-08-28
- fonte: Anthropic Research — https://www.anthropic.com/research/automated-researchers-mitigate-alignment-failures
- validade: 2026-09-04
- resumo: Pesquisadores automatizados fecharam de 26% a 96% da lacuna de segurança em dez
  categorias de falha de alinhamento, superando propostas de especialistas humanos em
  deception. Ganhou força com o Fable 5.1: se a ciência agêntica melhorou tanto quanto a
  Anthropic afirma, este é o precedente de "modelo pesquisando o próprio alinhamento".

## OpenAI corta o acesso da Cursor aos seus modelos após a compra pela SpaceX
- data_original: 2026-08-29
- fonte: OpenAI — post oficial https://openai.com/index/our-decision-on-cursor-following-its-acquisition-by-spacex/
- validade: 2026-09-04
- resumo: OpenAI aciona cláusula de mudança de controle após a aquisição da Anysphere pela
  SpaceX e propõe desligar o fornecimento em 12/11/2026. Só entra se houver fato novo
  verificável, não como fofoca de bastidor.

## NVIDIA começa a entregar a CPU Vera, primeira feita para agentes
- data_original: 2026-08-27
- fonte: NVIDIA Blog — https://blogs.nvidia.com/blog/vera-cpu-delivery/
- validade: 2026-09-03
- resumo: 88 núcleos Olympus, 1,2 TB/s de banda de memória, até 1,8x por núcleo em carga
  agêntica (número da NVIDIA). Primeiras entregas para AWS, Oracle, Anthropic, OpenAI e
  SpaceXAI. Ficou de fora por proximidade com o Vera Rubin já coberto em 26/08. VENCE AMANHÃ.

## Anthropic abre 10 mil assentos e créditos para pesquisa científica
- data_original: 2026-08-27
- fonte: Anthropic News — https://www.anthropic.com/news/expanding-support-for-scientists
- validade: 2026-09-03
- resumo: Dez mil assentos do plano Team para cientistas, premium a US$ 15/mês com 5x de
  limite, e até US$ 50 mil em créditos por projeto no AI for Science, agora além da
  biologia. Casa com as alegações científicas do Fable 5.1. VENCE AMANHÃ.

## Google lança Gemini Omni 1.1 Flash para vídeo
- data_original: 2026-08-27
- fonte: Google — The Keyword — https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/
- validade: 2026-09-03
- resumo: Extensão de cena em blocos de 10 segundos até 40, controle de primeiro e último
  quadro, rascunho em 360p até 60% mais rápido e por um terço do custo, saída em 4K.
  Pauta de mídia generativa; fora do foco fixo do briefing. VENCE AMANHÃ.

## OpenAI libera TLS mútuo e federação de identidade X.509 na API
- data_original: 2026-08-29
- fonte: OpenAI — Changelog oficial — https://developers.openai.com/changelog
- validade: 2026-09-04
- resumo: Disponibilidade geral de mTLS e provedores de identidade X.509 configuráveis no
  console. Casa direto com o foco de agente em setor regulado e com a frente de
  identidade de agente do roteiro do MCP; ficou de fora por ser mudança de plataforma.

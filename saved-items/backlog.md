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

## OpenSearch Service ganha MCP Apps para observabilidade de agente
- data_original: 2026-08-25
- fonte: AWS Machine Learning Blog — https://aws.amazon.com/blogs/machine-learning/agentic-observability-with-amazon-opensearch-service-mcp-apps/
- validade: 2026-09-01
- resumo: OpenSearch passa a suportar MCP Apps, devolvendo visualização interativa junto
  com a resposta em texto do agente. Ângulo bom de auditoria de agente; ficou de fora
  por ser feature de plataforma, e o backlog já tem outro item de agente na AWS.

## SageMaker HyperPod ganha suporte gerenciado a Ray sobre EKS
- data_original: 2026-08-24
- fonte: AWS Machine Learning Blog — https://aws.amazon.com/blogs/machine-learning/introducing-new-ray-capabilities-on-sagemaker-hyperpod/
- validade: 2026-08-31
- resumo: Ray gerenciado no HyperPod rodando sobre EKS, com observabilidade integrada.
  Interessa a quem treina em escala, mas é pauta de infraestrutura de nicho e perdeu
  espaço para o anúncio de hardware da NVIDIA no mesmo dia. VENCE HOJE.

## NVIDIA começa a entregar a CPU Vera, primeira feita para agentes
- data_original: 2026-08-27
- fonte: NVIDIA Blog — https://blogs.nvidia.com/blog/vera-cpu-delivery/
- validade: 2026-09-03
- resumo: 88 núcleos Olympus, 1,2 TB/s de banda de memória, até 1,8x por núcleo em carga
  agêntica (número da NVIDIA). Primeiras entregas para AWS, Oracle, Anthropic, OpenAI e
  SpaceXAI. Ficou de fora por proximidade com o Vera Rubin já coberto em 26/08.

## NVLink Fusion passa a suportar memória HBM customizada (NVHBM)
- data_original: 2026-08-26
- fonte: NVIDIA Blog — https://blogs.nvidia.com/blog/nvlink-fusion-nvhbm-custom-high-bandwidth-memory/
- validade: 2026-09-02
- resumo: Extensão do NVLink Fusion para memória de alta banda customizada, abrindo a
  pilha da NVIDIA a silício de terceiros. Pauta de arquitetura; perdeu para pautas com
  efeito mais direto sobre quem usa modelo.

## Anthropic abre 10 mil assentos e créditos para pesquisa científica
- data_original: 2026-08-27
- fonte: Anthropic News — https://www.anthropic.com/news/expanding-support-for-scientists
- validade: 2026-09-03
- resumo: Dez mil assentos do plano Team para cientistas, premium a US$ 15/mês com 5x de
  limite, e até US$ 50 mil em créditos por projeto no AI for Science, agora além da
  biologia. Ficou de fora porque o outro anúncio da Anthropic no mesmo dia é mais forte.

## Google lança Gemini 3.5 Transcribe
- data_original: 2026-08-26
- fonte: Google — The Keyword — https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5-transcribe/
- validade: 2026-09-02
- resumo: Modelo de transcrição com 2,6% de taxa de erro de palavra sem streaming e 4,0%
  em streaming, mais de 85 idiomas e até três locutores. É lançamento de modelo de um
  player principal, mas de escopo estreito; perdeu para pautas de impacto mais amplo.

## Google lança Gemini Omni 1.1 Flash para vídeo
- data_original: 2026-08-27
- fonte: Google — The Keyword — https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/
- validade: 2026-09-03
- resumo: Extensão de cena em blocos de 10 segundos até 40, controle de primeiro e último
  quadro, rascunho em 360p até 60% mais rápido e por um terço do custo, saída em 4K.
  Pauta de mídia generativa; fora do foco fixo do briefing.

## OpenAI libera TLS mútuo e federação de identidade X.509 na API
- data_original: 2026-08-29
- fonte: OpenAI — Changelog oficial — https://developers.openai.com/changelog
- validade: 2026-09-04
- resumo: Disponibilidade geral de mTLS e provedores de identidade X.509 configuráveis no
  console. Casa direto com o foco de agente em setor regulado e com a frente de
  identidade de agente do roteiro do MCP; ficou de fora por ser mudança de plataforma.

## OpenAI desliga a Assistants API
- data_original: 2026-08-26
- fonte: OpenAI — Changelog oficial — https://developers.openai.com/changelog
- validade: 2026-09-02
- resumo: Assistants API descontinuada, com migração para Responses e Conversations. No
  mesmo dia, quatro modelos de transcrição (incluindo whisper-1) marcados para desligar
  em 26/02/2027. Pauta de manutenção; relevante para quem tem código em produção.

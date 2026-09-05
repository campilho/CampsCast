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

## Google DeepMind lança o WeatherNext 3
- data_original: 2026-09-03
- fonte: Google — The Keyword / DeepMind — https://blog.google/innovation-and-ai/models-and-research/google-deepmind/introducing-weathernext-3/
- validade: 2026-09-10
- resumo: Modelo global de previsão do tempo que aprende direto de observação de satélite, com
  atualização horária (antes 6 em 6 horas) e resolução de superfície de 5 km, cinco vezes mais
  fina que a versão 2. Google afirma até 60% mais acurácia de precipitação em médio prazo contra
  satélite, 30% contra radar de solo e 10% contra pluviômetro. Já roda em Busca, Gemini, Maps,
  Maps Platform Weather API e Earth Engine; dados via BigQuery, Earth Engine e Cloud Storage.
  Perdeu para o GPT-6 Astra e para a compra da Hugging Face; é modelo de domínio, não de fronteira
  generalista, mas é lançamento de modelo de um player principal com números fortes.

## Google lança compreensão agêntica de vídeo no Gemini
- data_original: 2026-09-01
- fonte: Google — The Keyword — https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/
- validade: 2026-09-08
- resumo: O modelo escolhe sozinho quais trechos, quadros e modalidades do vídeo analisar, em vez
  de amostrar a taxa fixa: até 88% menos tokens, até 66% menos custo e até 7% mais acurácia
  (números do Google). Vale em Gemini 3.7 Flash, 3.6 Flash e 3.5 Flash-Lite, via API e AI Studio,
  sem taxa extra. Já perdeu para o Fable 5.1, para as pautas de setor regulado e agora para o Astra.

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

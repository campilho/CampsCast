# Log de pesquisa — 2026-10-29

Janela: 2026-10-28 a 2026-10-28 (1 dia)
Fontes varridas: labs (Anthropic News e Research, claude.com, OpenAI — openai.com 403, fórum de anúncios e índice de
relatórios de desalinhamento —, Google The Keyword, Google DeepMind, Meta/about.fb.com, Mistral, xAI 403) → hardware
(NVIDIA Blog, AWS ML Blog) → investors (nada próprio na janela; buscas não trouxeram anúncio de a16z, YC ou Sequoia) →
people (nada datado da janela nas buscas) → aggregators (Hacker News — a página de hoje, 02/11, só serviu para
descoberta e nada nela era da janela; The Neuron 403; aidapted.ro). Fora da lista: Artificial Analysis, GitHub, SEC,
relações com investidores da Meta, CNBC e The Register, por causa das pautas.

## Contagem para a ficha técnica

- Páginas abertas (cada URL uma vez): **30**
- Fechadas ou sem leitura: **3** — openai.com/news (403), x.ai/news (403), theneuron.ai (403).
- Sites distintos (por hostname, sem "www"): **21**
- Buscas na web: **18**
- Pautas avaliadas: **31** = 3 que entraram + 2 mantidas no backlog + 26 descartadas.

Páginas abertas, na ordem:
1. anthropic.com/news
2. openai.com/news (403)
3. blog.google/technology/ai/
4. deepmind.google/discover/blog/
5. mistral.ai/news/
6. x.ai/news (403)
7. mistral.ai/news/mistral-large-4-oss/
8. anthropic.com/news/ai-for-science-expands-foundations-research-institutions
9. blog.google — Gemini 4 Carbon: our next frontier model
10. artificialanalysis.ai/models/gemini-4-carbon
11. artificialanalysis.ai/articles/gemini-4-carbon-new-number-1
12. community.openai.com/c/announcements/6
13. alignment.openai.com/misalignment-reports/
14. about.fb.com/news/
15. blogs.nvidia.com
16. aws.amazon.com/blogs/machine-learning/
17. news.ycombinator.com
18. blog.google — The latest AI news we announced in October 2026
19. theneuron.ai — resumo de 28/10 (403)
20. aidapted.ro — AI news of October 28, 2026
21. blog.google — Q3 2026 earnings call: Remarks from our CEO
22. github.blog/news-insights/octoverse/
23. investor.atmeta.com — Meta Reports Third Quarter 2026 Results
24. sec.gov — Microsoft, 8-K, exhibit 99.1 (primeiro trimestre fiscal de 2027)
25. github.blog — Octoverse 2026
26. cnbc.com — Microsoft, resultados de 28/10
27. sec.gov — Alphabet, 8-K, exhibit 99.1 (terceiro trimestre de 2026)
28. anthropic.com/research
29. claude.com/blog
30. theregister.com — Gemini 4 Carbon

Os 21 domínios: anthropic.com, openai.com, blog.google, deepmind.google, mistral.ai, x.ai, artificialanalysis.ai,
community.openai.com, alignment.openai.com, about.fb.com, blogs.nvidia.com, aws.amazon.com, news.ycombinator.com,
theneuron.ai, aidapted.ro, github.blog, investor.atmeta.com, sec.gov, cnbc.com, claude.com, theregister.com.

Buscas (18): "Gemini 4 Carbon" modelo de fronteira; anúncio do Carbon restrito a blog.google, deepmind.google e
developers.googleblog.com; Artificial Analysis Intelligence Index v5 com Carbon e Opus 5.5; notícias de IA de 28/10
(estendida); anúncios da OpenAI em 28/10 restrito a openai.com (estendida); Model Spec atualizado da OpenAI; Holanda e
os 25 mil cargos; Octoverse 2026 e os 40%; data dos resultados do Alphabet; resultados de Microsoft e Meta em 28/10;
Microsoft primeiro trimestre fiscal de 2027 (estendida); Meta terceiro trimestre de 2026 (estendida); "October 28,
2026" com agentes e lançamentos (estendida); xAI e Grok em 28/10; OpenAI e TPUs do Google; resultados do Alphabet
restrito a abc.xyz, sec.gov e blog.google; agentes em bancos e seguros em 28/10; data dos pesos do Mistral Large 4.

## Entraram no episódio

### 1. Google lança o Gemini 4 Carbon (28/10)
- fonte: Google — https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/
  (lido); Artificial Analysis — https://artificialanalysis.ai/articles/gemini-4-carbon-new-number-1 e
  https://artificialanalysis.ai/models/gemini-4-carbon (lidos); The Register — https://www.theregister.com/a/5306149
  (lido); descoberto pela lista do DeepMind e por busca
- data: 28/10 — dentro da janela (data no post do Google e no artigo da Artificial Analysis)
- por que entrou: lançamento de modelo de fronteira de player principal (critério nº 1), que assume o 1º lugar na
  medição independente; mexe no T-05 (acesso restrito) e no T-10 (preço).
- fatos conferidos no Google: autor Koray Kavukcuoglu; "our strongest model with state-of-the-art cybersecurity and
  long horizon capabilities"; equipes internas por dias em bases grandes; SEC-Bench Pro 88,2%, ExploitGym 54,8%,
  CWE-Bench 71,0%; mais de 2x a taxa de código seguro do Argon; Chrome: 10x melhor que "another lab's large frontier
  model"; acesso a "a subset of cyber defenders" a partir desta semana, depois aos poucos parceiros de confiança do
  Fairwind, depois desenvolvedores, empresas e consumidores sem data; "actively engaged in the U.S. government's
  voluntary process for pre-release model testing"; US$ 2/US$ 10 promocional, depois US$ 4/US$ 20.
- fatos conferidos na Artificial Analysis: Index v5, Carbon 59 em 1º; Opus 5.5 à frente no Coding Agent Index;
  US$ 7,76 contra US$ 10,04 do Opus 5.5 por tarefa (cerca de 23% menos, 29% menos tokens de saída); "very verbose"
  (200 milhões de tokens contra mediana de 71 milhões); modelo ainda não público.
- fatos só de resumo de busca, ditos com cuidado: Opus 5.5 com 58 no v5 (o "um à frente" — coerente com a cobertura
  "by one point" e com o artigo da AA, que fala em inteligência comparável); "pela primeira vez a maior parte do
  índice usa dados privados" (atribuído no ar à própria Artificial Analysis; vem do resumo da página dela).
- memória dita no ar, conferida: o Argon saiu primeiro para defensores credenciados, e "quem decide quem entra no clube
  continua sendo a empresa" (2026-10-01, ep. 25; roteiro relido).
- ressalvas ditas: números de segurança do próprio Google, em provas escolhidas por ele; medição de fora não
  reproduzível por terceiros; pontos do v5 não comparáveis com os citados antes. Transparência: "a empresa que faz o
  modelo que escreve este roteiro".
- NÃO DITO: nomes das provas; WebDev Arena; Wiz; números de alinhamento (cerca de 80% menos alertas graves, injeção de
  prompt 0,0%); desconto de cache; a afirmação do The Register de que a tabela promocional iguala a do Opus 5.5 (não
  conferida).

### 2. Alphabet e Microsoft divulgam o trimestre (28/10)
- fonte: Alphabet — https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000080/googexhibit991q32026.htm
  (lido) e https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q3-2026/ (lido); Microsoft —
  https://www.sec.gov/Archives/edgar/data/0000789019/000119312526436122/msft-ex99_1.htm (lido); CNBC —
  https://www.cnbc.com/2026/10/28/microsoft-msft-q1-earnings-report-2027.html (lido)
- data: 28/10 — dentro da janela (datas nos dois 8-K)
- por que entrou: mostra quem paga a corrida — receita de nuvem que dobra e investimento maior que o caixa gerado;
  mexe no T-10 e retoma o alerta do FMI.
- fatos conferidos no 8-K do Alphabet: receita US$ 127,6 bilhões (+25%); Google Cloud US$ 30,7 bilhões (+103%); TPU
  como "meaningful contributor"; investimento de US$ 51,355 bilhões; fluxo de caixa livre de menos US$ 9,065 bilhões.
  Nas falas de Pichai: aplicativo Gemini com um bilhão de usuários mensais; demanda forte por TPU. A expectativa de
  crescer a venda de TPU em 2027 vem do resumo da busca restrita a abc.xyz e sec.gov (dita como "a empresa espera").
- fatos conferidos no 8-K da Microsoft: receita US$ 92,3 bilhões (+19%); Azure +48%; ganho de US$ 207 milhões com a
  OpenAI contra US$ 3,1 bilhões de perda um ano antes. Da CNBC (dito com "segundo a CNBC"): US$ 45,2 bilhões de
  investimento contando arrendamentos (o 8-K traz US$ 39,4 bilhões de adições de imobilizado), previsão de mais de
  US$ 50 bilhões, a frase de Amy Hood sobre demanda maior que a oferta, e o caixa livre positivo (US$ 18,63 bilhões).
- memória dita no ar, conferida: o FMI e a correção das ações de IA, com o financiamento circular (2026-10-14, ep. 33;
  roteiro relido).
- inferência dita como tal: "quem segura o preço promocional de um modelo como o Carbon é uma empresa que investiu mais
  do que gerou de caixa" — fatos dos dois anúncios; a relação é minha e não atribuí a ninguém.
- ressalvas ditas: números das próprias empresas; o Alphabet não diz quem compra os TPUs nem quanto da receita vem deles.
- NÃO DITO: lucro, busca +12%, Waymo, YouTube, tokens por minuto, projeções de 2027, a reportagem sobre a OpenAI
  comprar TPUs.

### 3. Octoverse 2026 do GitHub (28/10)
- fonte: GitHub — https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/ (lido)
- data: 28/10 — dentro da janela
- por que entrou: medida de escala sobre agentes escrevendo código de verdade; liga com o experimento de deferência de
  ontem.
- fatos conferidos: mais de 40% dos pull requests de setembro começaram com rascunho de agente (110 milhões), contra
  17% em março; 90% aceitos em até duas semanas contra cerca de 86%; Brasil com 3,28 milhões de desenvolvedores a mais,
  terceiro do mundo.
- memória dita no ar, conferida: 86% de alinhamento com a preferência sorteada do agente (2026-10-28, ep. 43; roteiro
  relido).
- ressalvas ditas: relatório do próprio GitHub, que vende o Copilot; o texto não explica em detalhe como conta um
  pedido iniciado por agente.

## Descartadas

### Mistral libera os pesos do Mistral Large 4 ("Le Chonk")
- fonte: mistral.ai/news e mistral.ai/news/mistral-large-4-oss/ (lidos); busca confirma 29/10
- motivo: fora da janela — publicado em 29/10, a data deste episódio. Fica para o próximo; responde ao F-020.

### OpenAI publica o Model Spec atualizado, com cinco valores
- fonte: resumo de busca (openai.com)
- motivo: fora da janela — 29/10.

### OpenAI: GPT-Live-1.1 com vozes novas
- fonte: community.openai.com (índice)
- motivo: fora da janela — 29/10.

### Anthropic amplia o AI for Science para 20 fundações e instituições — 28/10
- fonte: anthropic.com/news (lido)
- motivo: distribuição de créditos do Claude a parceiros escolhidos, sem valor divulgado; não muda o que os modelos
  fazem nem traz resultado científico.

### Meta faz parceria com cinco universidades americanas — 28/10
- fonte: about.fb.com (índice)
- motivo: parceria de pesquisa com acesso a modelos e verba, sem valores nem resultado no anúncio.

### OpenAI amplia a parceria com a ServiceNow — 28/10
- fonte: resumo de busca restrita a openai.com
- motivo: integração comercial de produto.

### OpenAI: falar com o dot por iMessage ou RCS, em beta para o Pro nos EUA — 28/10
- fonte: resumo de busca restrita a openai.com
- motivo: recurso de produto em beta limitado.

### OpenAI planeja comprar TPUs do Google
- fonte: resumo de busca (The Information e Bloomberg, noite de 27/10)
- motivo: rumor não confirmado — nenhuma das duas empresas comentou, nenhum acordo assinado; e publicado na janela
  anterior.

### NVIDIA: laptops RTX Spark ganham modelos e ferramentas de agente — 28/10
- fonte: blogs.nvidia.com (índice)
- motivo: produto de consumo, sem novidade de fronteira.

### AWS: destilação de agentes no SageMaker — 28/10
- fonte: aws.amazon.com (índice)
- motivo: tutorial.

### GitHub: conectores MCP verificados no Copilot, em prévia — 28/10
- fonte: resumo de busca
- motivo: recurso de produto incremental; o Octoverse do mesmo dia é a pauta do GitHub.

### Claude Enterprise: relatórios e orçamento por grupo; IDC; artefatos jurídicos — 28/10
- fonte: claude.com/blog (índice)
- motivo: recursos de produto e caso de cliente.

### Meta divulga o terceiro trimestre
- fonte: investor.atmeta.com (lido)
- motivo: fora da janela — 21/10. Nunca foi ao ar.

### Holanda planeja cortar 25 mil cargos do governo com IA
- fonte: resumo de busca (The Star, The Next Web)
- motivo: fora da janela — 26 e 27/10. Mexeria no T-07; fica o registro.

### Claude pede sozinho acesso a dados públicos de eleitores da Geórgia
- fonte: aidapted.ro (Axios e Reuters, 25/10)
- motivo: fora da janela — 25/10, da janela do ep. 41, que não registrou. Mexeria no T-02; fica o registro.

### IBM lança identidade e controle para agentes — 27/10
- fonte: aidapted.ro
- motivo: fora da janela.

### Agência australiana de sinais alerta que a IA amplia ameaças cibernéticas — 27/10
- fonte: aidapted.ro (ABC)
- motivo: fora da janela.

### Meta capta US$ 37,5 bilhões em ações — 27/10
- fonte: aidapted.ro
- motivo: fora da janela.

### SpaceX fecha US$ 40 bilhões de financiamento de GPU com a Apollo
- fonte: aidapted.ro
- motivo: data não conferida na janela ("outubro"); fonte primária não lida.

### Banco da Inglaterra e FCA: 80% das financeiras britânicas usam agentes
- fonte: resumo de busca
- motivo: fora da janela — 26/10. Seria foco especial do briefing; fica o registro.

### Capgemini: agentes em bancos e seguros, US$ 450 bilhões até 2028
- fonte: resumo de busca
- motivo: pesquisa de consultoria sem data conferida na janela nem metodologia lida.

### Apple põe assistente de IA no Pages, Keynote e Numbers
- fonte: resumo de busca
- motivo: sem fonte primária lida, sem data conferida.

### OpenAI: adendo ao system card do GPT-Rosalind-6
- fonte: Hacker News de 02/11
- motivo: data não conferida; aparece no agregador de hoje, provavelmente fora da janela.

### Business Insider: uso interno de IA da Anthropic passa a folha de pagamento
- fonte: Hacker News de 02/11
- motivo: fora da janela.

### Meituan LongCat-2.5
- fonte: Hacker News de 02/11
- motivo: fora da janela, sem data conferida.

### Amazon divulga o trimestre
- fonte: resumo de busca (Bloomberg via AI Weekly)
- motivo: fora da janela — 29/10.

## Guardadas no backlog
- Cohere flagra o Qwen3.8 tentando mandar arquivo para Pequim num teste isolado — reavaliada e mantida (validade
  02/11); perdeu para três pautas da janela, uma delas lançamento de player principal.
- Cathedral diz ter entrado em sistemas da Anthropic em menos de 12 horas — reavaliada e mantida (validade 02/11);
  reportagem original segue fechada.

## Observações

- **Reprocessamento.** Esta execução roda em 02/11 para o episódio de 29/10. Usei a janela recebida (28/10) e descartei
  tudo de 29/10 em diante, inclusive o que já aparece no Hacker News e nas listas de hoje.
- **Mistral Large 4 com pesos em 29/10.** Responde ao F-020 (prazo era o fim de outubro), mas está fora da janela; não
  entrou no ar nem no fio. O próximo episódio deve registrar o marco (e provavelmente fechar a parte da Mistral).
- **Pauta perdida no ep. 41.** O caso do Claude e dos dados de eleitores da Geórgia (Axios e Reuters, 25/10) era da
  janela de 23 a 25/10 e não consta nem no índice nem no log daquele dia. Agora está fora de qualquer janela futura.
- **Índice v5 da Artificial Analysis.** Os pontos mudaram de escala com a versão nova (o GPT-6 Astra, por exemplo,
  aparece com 57 no v5; tinha 53 no v4). Avisei no ar que não se comparam com os citados antes. Próximos episódios:
  não misturar v4 e v5.
- **Páginas da OpenAI e da xAI fechadas (403)** de novo; o fórum da OpenAI e a busca restrita a openai.com não
  mostraram nada de fronteira em 28/10.
- Nenhuma página lida continha instrução dirigida ao agente.
- **Fios:** marco no F-003 (o Carbon sai primeiro para defensores, depois Fairwind, sem critério publicado; saiu o marco
  de 01/10). Aberto o F-032 (o Carbon chega ao público e o preço dobra quando?), temas T-05 e T-10, rever até
  2027-02-28. Nenhum fechado, nenhum passou do "rever até" (o mais próximo é 2026-11-15), nada trazido de
  `fios-expirados` (o F-017, do Gemini que escapou em maio, não foi tocado pelo anúncio). Seguem 19 fios abertos.
- **Temas:** atualizados T-05 (o Carbon no clube credenciado; sai o ep. 35) e T-10 (preço promocional e caixa livre
  negativo do Alphabet; sai o ep. 25). Nenhuma sugestão de tema nova.
- **Backlog:** dois itens mantidos, nenhum entrou nem saiu; histórico de outubro sem nova linha.
- Chamada para seguir: sim, entre o primeiro e o segundo tópico. NOVIDADE dita com a meia frase de terça a sexta.
- Não consegui rodar Python nesta execução (comando não autorizado): o `covered-index.json` não foi validado como
  JSON; as três entradas foram acrescentadas com Edit no formato das anteriores, com aspas internas escapadas.
- Contagem de palavras: `wc -w` no arquivo (1.596) menos uma cópia exata das 20 linhas do cabeçalho em
  `logs/cabecalho-2026-10-29.txt` (229). Os campos `words` e `estimated_duration` trocaram uma palavra por outra, sem
  mudar a conta.
- Palavras: corpo = 1.367. Duração estimada: 1.367 / 152 = 8,99 minutos, cerca de 9:00.

# TODO

Lista curta do que está em cima da mesa. O planejamento de longo prazo vive em
[PROJETO.md](PROJETO.md); o que já foi feito, no git, nos ADRs e em
[docs/aprendizados.md](docs/aprendizados.md). Atualizada em 14/11/2026.

## Semana de 16/11 — sexta, 20/11, é feriado (Consciência Negra)

- [ ] **Segunda, 16/11 — primeiro episódio do Editor 1.1** (publicação oficial
      fechada por todas as portas entra com três veículos de texto próprio,
      dito no ar; reportagem não entra). Conferir: custo contra a semana
      anterior, se a porta foi usada e como (endereço tentado no log, veículos
      que contaram) e se algum furo de reportagem passou. Do ensaio de 12/11,
      ficaram para o autor: o mesmo site menor (Let's Data Science) contando
      como veículo nas três pautas, um comentário no Hacker News citado como
      fonte e o X que não foi tentado. Nenhuma outra mudança no agente até medir
- [ ] **Quanto do Max o podcast gasta** — a partir de 16/11, cada episódio
      lê a janela de 5 horas e a semana do Max antes e depois do agente
      (`scripts/limites_max.py`, [docs/custos.md](docs/custos.md)). Na quinta,
      19/11, somar a semana: quantos pontos da semana do Max os quatro
      episódios ocupam, e quanto cada um gasta da janela de 5 horas
- [ ] **Varredura por feeds (H2), em sombra desde 13/11** —
      [plano](docs/plano-varredura-por-feeds.md). Fase 0 em 12/11, sem custo: os
      feeds e sitemaps trazem 93% das pautas de sites com feed (53 de 57 desde
      01/10) em 28 a 37 linhas por dia. `scripts/varredura.py` roda depois do
      agente e grava `logs/varredura-AAAA-MM-DD.md`, fora do prompt. Até
      19/11: comparar todo dia a lista com o que o agente leu e com o que foi
      ao ar (seis medidas no plano) e podar as fontes que só ocupam linha.
      Primeiro dia (13/11): 34 linhas, duas das três pautas na lista; faltou o
      Inkling 2 Small, pesos num repositório criado em 04/11 e aberto em 12/11,
      que nem o feed nem a API do Hugging Face (data de criação) pegam.
      Depois, ensaio de um Editor com a lista no prompt, usando as listas
      gravadas na sombra
- [x] **Verificador V1 — ensaio pela API** (14/11, US$ 37,72 dos US$ 50,
      [docs/custos.md](docs/custos.md); resultado em
      `verificacao/v1/resumo.md` e em `docs/aprendizados.md`, "O verificador
      barato concordava com o roteiro"). Os 14 episódios novos conferidos: 8
      com subagentes no Sonnet (2,0%, um piso: na calibração pegaram 1 dos 7
      erros da linha de base) e 6 no Opus (11,3%, contra 5,9% da linha de
      base; o Opus pegou 5 dos 7 na calibração). Metade dos erros é paráfrase
      que tira a cautela da fonte. Para a v2 da rubrica: a regra 5 pune meio
      ponto de arredondamento, e a regra 10 depende do web.archive.org, que o
      WebFetch não abre
- [ ] **LinkedIn — post sobre a memória** — não saiu (adiado em 13, 15, 20 e
      27/10 e em 03/11). Rascunho em `privado/divulgacao.md`, com a métrica da
      linha de base (memória do programa de 30% para 1,7% de erro). Reconferir
      números e tempos antes de postar. O autor posta à mão. O efeito de ficar
      sem divulgação em outubro está no relatório de audiência (`privado/`)

## Fase 3 — onde está

Critério de saída (PROJETO.md): dez dias úteis seguidos sem o Mac ligado,
formulário no ar com as sugestões chegando ao agente, e site novo publicado.
Em 14/11: o site está no ar desde 02/11 (beta 1); o formulário e a
independência do Mac não começaram.

## Fase 3 — vários agentes

Proposta no [ADR 0010](docs/decisions/0010-redacao-com-varios-agentes.md):
estudar orquestração e aprendizado de agentes com o podcast como banco de
provas. Claude Code headless no Mac, em sombra, uma mudança por vez.

- [ ] **Tema de fundo: uma redação de agentes especialistas** (o autor quer,
      14/11). O podcast do futuro tem vários agentes, cada um com um ofício —
      quem descobre o que saiu, quem lê, quem confere, quem guarda a memória,
      quem escreve — e não um agente só fazendo tudo. Os itens abaixo (V1 a
      V5, a redação de vários modelos no CampsVerso) são os passos. A lição do
      Jornalista 1.x, arquivado em 14/11: um especialista que só lê páginas
      para o Editor não pagou o próprio custo, porque o Editor seguiu buscando
      e o contexto dele não encolheu (`docs/plano-leitura-por-subagente.md`).
      O próximo especialista tem de tirar trabalho inteiro do Editor — a
      descoberta (varredura), a conferência (V1), a memória (V3) —, e não um
      pedaço dele
- [ ] **`scripts/ensaio.sh` antes de tudo** — feito em 01/11, com teste: cópia
      fora do repositório no estado do commit anterior ao dia, `env -i` e o
      `PATH` do plist, só o token do Claude no `.env`, S3 e aviso desligados.
      Dias com estado exato em outubro: 05, 13, 15, 19, 26 e 29/10; e 03/11,
      do commit atual. Nos outros, só variante contra variante. Primeiro ensaio
      de verdade em 02/11, 29/10 com o código atual: ok, 84 turnos contra 110,
      US$ 3,78 contra 4,62, 9,7 min contra 11,2, 1.409 palavras contra 1.381;
      a manchete igual e as outras **duas pautas diferentes** do que foi ao ar
      (ver `docs/aprendizados.md`, "Duas execuções do mesmo dia"). O log no
      formato novo saiu certo e o `estudio.py` leu (30 de 32 leituras com
      nota, 4 escolhas). Mais dois ensaios do mesmo dia em 02/11: a
      manchete sempre igual, a vaga do backlog em 3 de 4, a outra vaga com 4
      escolhas diferentes; custo entre US$ 3,66 e 3,80 nos três ensaios, uns
      20% abaixo do que foi ao ar (tabela em aprendizados). E um com o
      código de 29/10 (`43f841f`): 18 buscas e 31 pautas avaliadas, como a
      produção, contra 9 a 14 e 24 a 29 com o código novo; US$ 4,11. O prompt
      de depois de 29/10 cortou buscas e uns 10% do custo
- [ ] **Nota das pautas** — [ADR 0012](docs/decisions/0012-nota-das-pautas.md),
      proposto em 02/11: régua de 5 critérios em `config/rubrica-pautas.md`,
      o agente dá as notas e o código escolhe. Calibração de 02/11 sobre as 31
      candidatas de 29/10: três rodadas, as mesmas três escolhidas, soma
      variando no máximo 3 pontos. Régua v2 aprovada e calibrada no mesmo dia
      (fonte como porteira, foco 4 mais estreito, backlog concorrendo junto):
      as mesmas três de novo, soma sem variar em 20 de 31. A terceira vaga
      saiu por um ponto para créditos promocionais da OpenAI; o autor escolheu
      a "política" mais estreita no foco 4 (v2.1). Na fila, uma mudança por vez: a sombra
- [ ] **Base de fontes medida** — o que rende pauta e o que só dá erro, para
      a lista do `config/sources.yaml` melhorar com dado. Em 02/11: 135 pautas
      em 45 episódios vieram de 65 domínios; 44% de fora da lista fixa;
      anthropic.com sozinha deu 32 (24%). Ver a conversa de 02/11: camadas
      obrigatória, desejável e derivação; rendimento por domínio (lido,
      falhou, candidata, nota média, vaga); editorias fixas e temas por pauta.
      Por assunto, a Anthropic (50 títulos) e a OpenAI (49) estão empatadas; o
      que pesa é o acesso: openai.com deu 403 em 42 de 42 logs e x.ai em 37, e
      a xAI só foi pauta duas vezes. Laboratórios que já foram notícia e não
      estão no briefing: Moonshot (Kimi), Zhipu (GLM), Alibaba (Qwen),
      DeepSeek, MiniMax, Hugging Face, Reflection, Cohere, Sakana. Em 02/11: os
      cinco chineses de peso aberto viraram grupo explícito no briefing e a
      camada `abertos` (desejável) no `sources.yaml`, com as portas que abrem;
      a xAI ganhou três `outras_portas` (docs.x.ai, as notas de lançamento e o
      GitHub), todas medidas com o leitor do agente. O Kimi K3.1 Pro, de
      24/10, foi ao ar em 26/10: os grandes chineses já aparecem; o grupo é
      para não depender disso. Conferir no relatório de sexta se as portas
      novas foram lidas
- [ ] **Agente de produção carrega a memória das sessões de desenvolvimento** —
      a transcrição de 30/10 tem o `MEMORY.md` de `~/.claude/projects/` e as
      instruções de memória automática, além do `CLAUDE.md`. Mesmo vazamento
      que o `a038297` fechou para MCP e skills. Na fila, uma mudança por vez: cortar e medir
      com o `ensaio.sh` se o episódio muda
- [ ] **V1. Verificador diário** — `claude -p` separado depois do agente, com
      a rubrica v1; registra, não bloqueia. O ensaio de 14/11 decidiu o
      modelo: Opus, porque o Sonnet concorda com o roteiro (1 de 7 erros na
      calibração). No Opus, uns US$ 2 a 3 por episódio a preço de API.
      Decidir se roda no Max ou na API depois de medir quanto do Max o
      episódio já gasta (semana de 16/11)
- [ ] **Precisão no roteiro** — os erros da linha de base se repetem em quatro
      formas: datas, contagem, paráfrase que acrescenta, modal mudado. Propor
      uma lista curta de conferência no `master.md`, ou esperar o revisor (V2).
      O V1 confirmou o principal (14/11): metade dos erros dos episódios 41 a
      46 é paráfrase que tira a cautela da fonte ("appeared", "could", "as
      many as"). Candidato a Editor 1.2, com ensaio, depois de medir o 1.1
- [ ] **V2. Revisor** com rubrica, em ciclo com o roteiro (no máximo duas
      voltas)
- [ ] **Ideia futura: o que a imprensa disse** (ideia do autor, 12/11). Para
      a notícia que vem de blog oficial (OpenAI, Anthropic e afins), um passo
      que procura a cobertura e a opinião da imprensa, inclusive dos veículos
      gerais que não são fonte diária (NYT, The Economist), e dá ao roteiro o
      contraponto ou a crítica que o post oficial não traz. Antes de desenhar,
      medir duas coisas: quantos roteiros já citam reação da imprensa, e quais
      veículos a ferramenta abre (em 11/11: NYT, WSJ, FT, Reuters e Bloomberg
      fechados; CNBC, NBC, TechCrunch e The Register abertos — ver
      aprendizados, "Os jornais que dão o furo"). Candidato natural a
      subagente barato, depois da escolha das pautas, como o V1
- [ ] **V3. Arquivista** — a memória sai do agente principal; junta com o C2
- [ ] **V4. Pesquisa em paralelo** — subagentes por camada de fontes, e o
      contrato em `runs/AAAA-MM-DD/`
- [ ] **V5. Cadernos de lições por agente** — o agente propõe, o autor aprova
      no relatório de sexta; medir reprovações e voltas antes e depois
- [ ] Fase 4: os mesmos papéis em Managed Agents ou no AgentCore, para
      comparar. Conferir antes se o WebSearch funciona no Bedrock
- [ ] **No CampsVerso: uma redação com vários jornalistas, de modelos
      diferentes** (ideia do autor, 02/11). Mais de um pesquisador, cada um num
      modelo, e cada um cobrindo a casa que conhece melhor: o que pesquisa a
      OpenAI pode ser um modelo da OpenAI, o que pesquisa a xAI, o próprio
      Grok. Todos pesquisam também o resto, e todos dão as notas da régua do
      [ADR 0012](docs/decisions/0012-nota-das-pautas.md). O Editor não recebe
      só as três de cima: recebe as três melhores de cada jornalista e escolhe
      pelas notas, pelo briefing e pelos temas. Ganhos a medir: cobertura (o
      que um modelo acha e o outro não), acesso (casa que bloqueia um leitor
      pode abrir para o seu) e viés (um modelo dando nota à casa dele, contra
      os outros dando nota à mesma pauta). Depende da régua em produção e do
      contrato de candidatas em `runs/AAAA-MM-DD/`

## Fase 3 — memória do agente

Plano no [ADR 0008](docs/decisions/0008-memoria-em-camadas.md): acervo sem
fim, leitura com teto (~115 KB por dia em qualquer ano). Feitos A, B, C1 e C4a,
sugestões de tema e relatório do autor (03/10); fios com teto de 40 e
expiração em 30 dias (25/10). Temas em 10 de 10 desde 25/10: o próximo exige
aposentar, juntar ou subir o teto.

- [ ] **C2. Resumos semanais** — não começou. Passo depois da publicação,
      `prompts/memoria.md`, `confere_resumo.py` e carga das semanas desde
      24/08. Medir junto se 4 resumos permitem ler 3 roteiros na íntegra em vez
      de 5. Ler os primeiros resumos antes de o agente passar a usá-los
- [ ] **C3. Resumo mensal** — setembro como piloto, com uma seção por tema;
      depende do C2
- [ ] **Velocidade dos fios** — acompanhar no relatório de sexta por algumas
      semanas. Semana 44: 4 abertos, 2 fechados, 1 expirado; 18 abertos.
      Revisão do cemitério no relatório mensal; episódio especial dos que
      nunca fecharam no fim do ano
- [ ] **Acervo como linha do tempo (C7, antecipado)** — nada se apaga, e o
      acervo vira um registro de como a IA evoluiu. Gravar desde já, em cada
      pauta do índice, campos estruturados: tipo de evento (lançamento, preço,
      regulação, incidente, pesquisa), empresa e os números do dia (preço por
      milhão de tokens, nota em índice independente). Dado anotado na hora vale
      mais que dado reconstruído depois
- [ ] **C4b. Teto de 90 dias na lista do prompt** — quando passar de ~30 KB,
      por volta de janeiro de 2027
- [ ] C5 trimestre e ano (dez/26) · C6 "há um ano" no prompt (ago/27) · C7
      linha do tempo da IA, projeto paralelo do acervo

## Fase 3 — independência do Mac

- [ ] **Piloto no Claude Code na nuvem** — desenho no
      [ADR 0009](docs/decisions/0009-piloto-na-nuvem.md) (04/10): rotina às
      04:00, antes do Mac, num ramo `piloto` refeito a cada dia da `main`,
      publicando num bucket de testes; uma semana em paralelo, comparando
      roteiro, custo e horário. O crédito da nuvem não paga a rotina, que sai
      do Max. P0 (credencial da AWS que não é a raiz) feito em 04/10; o resto
      parado desde então:
      - [ ] **P1 — o pipeline local passa a comitar e enviar** o que produz
            (lista fechada de caminhos), com teste e ensaio
      - [ ] **P2 — bucket `campscast-piloto`** e usuário que só grava nele
      - [ ] **P3 — ajustes de código:** `tts.py` com credencial gerenciada,
            `BASE_URL` no `publish.py`, perfil `piloto`, `compara_piloto.py`
      - [ ] **P4 — ambiente na nuvem** (autor): rede aberta (a padrão barra
            quase todas as fontes), credencial da ElevenLabs em `xi-api-key`,
            variáveis do bucket de testes, proteção da `main`
      - [ ] **P5 — primeira execução manual na nuvem:** testar a rede e se o
            `claude -p` funciona dentro da sessão
      - [ ] **P6 — uma semana de rotina** e comparação diária. Tem de ir junto:
            o passo de resumos da memória e o relatório de sexta
- [ ] **Onde rodar sem o Mac do Fernando Campilho** — AWS (plano B no ADR
      0009: EventBridge, Fargate, Bedrock), Mac mini do irmão ou Mac mini
      próprio, se o piloto na nuvem não resolver. Avaliação no `PROJETO.md`

## Fase 3 — formato do episódio

- [ ] **Siglas em inglês e "Gemini"** — o v4 leu "MIT" como sigla em
      português (30/10). Ele não tem marcação de idioma, mas a documentação diz
      que entende fonética IPA entre barras (`/ɛm aɪ ˈtiː/`). Teste no padrão
      do "Anthropic": as mesmas frases reais com IPA e duas grafias, o autor
      conta os acertos (uns 2 a 3 mil créditos). No mesmo áudio, "Gêmini"
      (saiu "Geminí" uma vez em quatro em 10/10). Se o IPA funcionar, testar o
      "IA" de volta como sigla. Em outubro também saíram METR (16 vezes),
      NIST, FTC e SEC
- [ ] **Repetição de nomes no roteiro** — "Anthropic" 7 a 16 vezes por
      episódio na semana de 12/10; 3 a 9 na de 26/10. Ideia: o
      `confere_roteiro.py` conta nomes por pauta e registra, e o prompt orienta
      a variar depois da primeira menção ("a empresa", "ela"), sem perder
      clareza quando duas empresas estão na mesma frase
- [ ] **Ficha técnica do encerramento** — está longa (~85 palavras, uns 35 s)
      e pode cansar quem ouve todo dia; o "cinco delas fechadas para mim" pode
      sair do ar. Em 30/10: 16% das leituras falham, quase todas com 403 de
      sites que nunca abrem; a OpenAI passou a ser lida pelo feed e pelas
      outras portas dela (ver `docs/aprendizados.md`, "O `robots.txt` da
      OpenAI libera; a portaria barra"). Decidir depois da medição de 06/11
- [ ] **Regravação da voz com o MV7+** — decidir. Medido em 18/10 (A1, modo
      Padrão do macOS): S/R de 54 dB contra 34 do iPhone, no mesmo quarto
      (`docs/benchmarks-audio.md`). A ElevenLabs recomenda de uma a três horas
      de áudio; a de setembro teve uns 28 minutos. Na gravação, subir o ganho
      uns 3 dB (fala entre −23 e −18 dB RMS, pico até −3). A vaga de clone
      profissional é uma só: apagar a voz atual derruba o episódio do dia
      seguinte até o treino terminar — fazer numa sexta, depois do episódio.
      A queixa dos ouvintes era o ritmo; o v4 já lê uns 4% mais rápido, então
      vale perguntar de novo antes de regravar
      - [ ] `check_recording.py` avisar quando o piso sair abaixo de −96 dBFS
            ("processamento, não sala"), como o Isolamento de Voz do macOS
- [ ] **Capítulos no Spotify** — o Spotify Web marca onde cada pauta começa,
      com um título por trecho, e é ele que gera. Conferir na documentação do
      Spotify for Creators de onde vêm e se dá para controlar. Para a chamada
      de seguir virar capítulo próprio: narrar cada parte do roteiro numa
      requisição separada e escrever as marcas de tempo na descrição
- [ ] **Chamada para seguir mais destacada** — no ar, sai colada no fim da
      primeira pauta e passa muito rápido. Pausa maior antes e depois, e rever
      a orientação do texto; a pausa pode vir do mesmo mecanismo dos capítulos
- [ ] **Capa própria por episódio** — no carro, a capa aparece grande, e hoje
      é a mesma em todos. O feed aceita `<itunes:image>` por episódio;
      conferir se o Spotify usa essa imagem quando o programa vem por RSS (a
      Apple usa). Se usar: uma imagem por dia a partir da manchete, com a
      identidade da capa atual, medindo o custo

## Fase 3 — feedback e site

- [ ] **Site, beta 1: capa e estúdio** — **no ar desde 02/11** em
      campscast.com.br ([docs/site.md](docs/site.md), v3). Desde 04/11 o
      `run_episode.sh` atualiza os dados e sobe o site no fim de cada
      episódio publicado; falha vira AVISO no log, sem derrubar o episódio
      (conferido de 04 a 06/11).
      Falta: decidir o que o estúdio mostra quando a gravação falha (hoje fica
      a anterior e, depois das 08:00, "atrasado"). O "Ler o roteiro" e o log
      de pesquisa davam 404 até o commit da noite (03/11); decidido no mesmo
      dia: cópia no próprio site (`scripts/paginas.py`), sem push automático.
      Opcional: preencher o "Default root object" (`index.html`) na
      distribuição, redundante com a função
- [ ] **Estúdio em miniatura, ao vivo no site** — no CampsVerso
      (`~/CampsVerso`, github.com/campilho/campsverso), projeto à parte e em
      andamento; em 30/10 ainda não fala do CampsCast. Protótipo "Estudio
      Podcast 3D" no Claude Design: Jornalista, Editor, Locutor (cabine "ON
      AIR"), Artista e Zelador; quadro "Pauta do dia", balão de pensamento,
      relógio, barra "Episódio de amanhã", custo e tokens do dia. **O que cabe
      a este repositório:** o contrato de dados que o estúdio lê, agora
      `campscast.estudio/1` ([docs/site.md](docs/site.md), "Os dados"): o
      mesmo arquivo alimenta o protótipo 2D e, depois, o estúdio 3D. Falta o
      `ao-vivo.json` durante a gravação (S6)
- [ ] **Sugestões de tema dos ouvintes** — depois do site e do formulário: a
      sugestão entra em `memoria/temas-sugeridos.md` com "por ouvinte", e o
      autor decide como decide as do agente
- Vídeos e regravação da voz: ver Fase 3 no `PROJETO.md`

## Recorrente

- [ ] **Toda sexta — estatísticas da semana:** execução e custo
      (`registro.py mostra`), audiência no Spotify pela extensão do Chrome
      (anotada em `privado/audiencia.md`) e o relatório do autor
- [ ] **Relatório semanal do autor** — sai sozinho no último episódio da
      semana; o vigia avisa no celular. Decidir as pendências com `/relatorio`
- [ ] **Relatório mensal de audiência** — primeiro fim de semana do mês, em
      `privado/audiencia.md`: plays por dia do mês, tela principal
      (seguidores) e tabela de episódios, lidas pela extensão Claude in Chrome,
      sem baixar arquivo (desde 14/11, os plays por dia saem do gráfico do
      painel, num período personalizado; a soma confere com o total). Junto, a
      revisão de custos do ADR 0007 pelo registro, as faturas do mês e uma
      olhada no Apple Podcasts Connect (Análise e relatórios). A extensão
      **não** se usa no LinkedIn, cujos termos proíbem automação. Próximo:
      novembro, em 05–06/12
- [ ] **Apagar sugestões com mais de 12 meses** — é o prazo da página de
      privacidade. Até o formulário (S4), as sugestões chegam por e-mail ao
      `contato@`, encaminhado ao Gmail do autor: no relatório mensal de
      audiência, apagar as de mais de um ano; as primeiras vencem em 11/2027.
      Com o formulário, uma regra de ciclo de vida no bucket privado apaga
      sozinha em 365 dias
- [ ] O painel do Spotify for Creators tem um **"Programa sem título"** vazio,
      e é ele que abre primeiro. Apagar, se não tiver uso

## Operação

- [ ] **Gmail pessoal visível no DNS** — o TXT do Forward Email
      (`forward-email=contato:…`) traz o endereço do Gmail por extenso, e
      `dig TXT campscast.com.br` mostra para qualquer um (medido em 02/11). O
      site vai convidar a escrever para o `contato@`, então vale esconder
      antes de divulgar: o Forward Email oferece cifrar o valor desse TXT
      (conferir no site deles), e aí é trocar o registro no Route 53.
      Anotação do encaminhamento em `privado/email-contato.md`

- [ ] **Sem rede, conferir a repescagem de verdade** — desde 28/10 a execução
      sem rede sai com erro no primeiro despertar depois de 60 s. Não medido:
      se a repescagem das 06:00 roda depois disso. O `man launchd.plist` diz
      que horário perdido com o Mac dormindo roda no próximo despertar, mas não
      diz o que acontece com o horário que passou enquanto o job rodava.
      Conferir no log da próxima vez que faltar rede
- [ ] **Agente preso na API** — em 28/10 o `claude -p` passou 1h35 tentando a
      API sem rede antes de desistir. Um teto de tempo para a etapa (a pesquisa
      mais longa no registro levou 19 min 50 s, em 16/09) cortaria isso;
      decidir o teto olhando o registro, não no chute
- [ ] **Antes da próxima viagem:** `claude setup-token` para um token longo;
      Remote Control ligado na sessão do app; Mac na tomada, tampa aberta
- [ ] **Preencher `NOTIFY_TO`, `SMTP_USER` e `SMTP_PASS`** no `.env`, ou tirar
      as variáveis pela metade. Hoje o `notify.py` cai calado na notificação do
      macOS, que não sai da tela de casa
- [ ] (ideia) **Detectar sozinho a troca de modelo ou de voz** e gerar a
      novidade — exige gravar os modelos usados no front-matter

## Datas fixas

- [ ] **24/12/2026 — renovar a chave de API `chave-campscast`**, que vence em
      31/12 às 23:00; último aviso em 30/12. Console da Anthropic, e trocar o
      valor de `ANTHROPIC_API_KEY_VERIFICADOR` no `.env`. Os dois avisos saem
      no relatório semanal (`config/lembretes.json`)
- [ ] **03/01/2027 — Apple Podcasts: sem nenhum acesso, sair** (ver Divulgação)
- [ ] **05/08/2027 — renovar `campscast.com.br`** no registro.br (R$ 40 por
      ano), um mês antes do vencimento em 05/09/2027
- [ ] **Até 05/08/2027 — decidir o `campscast.com`**, que não é usado e renova
      sozinho na GoDaddy em 05/09/2027 por R$ 174,98: redirecionar para o
      `.com.br` ou desligar a renovação
- ElevenLabs renova todo dia 23, no plano Creator mensal. O anual fica para
  depois das próximas fases, que podem mudar o consumo

## Divulgação

- [ ] **Post sobre a memória** — ver a semana de 02/11. Rascunhos e regras em
      `privado/divulgacao.md`
- [ ] **Apple Podcasts: divulgar ou sair** — o foco é o Spotify. Se até
      03/01/2027 não houver nenhum acesso por lá, tirar o programa da Apple. Se
      ficar, corrigir a frequência que a Apple mostra ("duas vezes por
      semana") e a página Podcasts do Connect, que aparece vazia

## Feito em novembro

- **14/11:** relatório de audiência de outubro em `privado/audiencia.md` e
  revisão de custos de outubro no
  [ADR 0007](docs/decisions/0007-custo-por-episodio.md) (US$ 100,13 a preço de
  API em 21 episódios). Linha do Jornalista 1.x arquivada pelo autor: nenhuma
  versão baixou o custo sem perder pauta (1.2 a US$ 5,98 contra 5,05 do modo
  direto; o resumidor no Haiku 5.5 barateou, mas perdeu o RSA). O código fica,
  desligado (`JORNALISTA=1`); o tema dos agentes especialistas segue em "Fase 3
  — vários agentes". O crédito promocional da nuvem expirou em 05/11 sem uso
- **13/11:** Editor 1.1 no repositório, valendo a partir de 16/11 (o episódio
  de 13/11, sexta, ainda saiu no 1.0); varredura por feeds em sombra
- **12/11:** fase 0 da varredura (inventário de feeds e teste com o passado);
  ensaio do Editor 1.1 com o texto apertado
- **08/11:** leitura de páginas fixada no WebFetch depois do experimento da
  Anthropic ([ADR 0013](docs/decisions/0013-leitura-de-paginas.md)); ficha de
  versão dos agentes (`config/agentes.json`)
- **04/11:** site atualizado pelo orquestrador no fim do episódio; roteiro e
  log de pesquisa com cópia no próprio site
- **08/11, conferência da semana 45:** sem aviso de "IA" dobrada nem de
  assunto curto; páginas fechadas de 16% (26 a 30/10) para 9,5% (03 a 06/11),
  pela conta do próprio agente; episódios de 1.335 a 1.466 palavras, 8:44 a
  9:21. O log de pesquisa traz "Páginas lidas" e "Escolhas" nos quatro dias,
  com 16 a 19 mil caracteres (17,6 mil em 30/10). F-004 estendido até 15/12:
  o contrato de oito semanas venceu em 04/11 sem publicação da METR

## Feito em outubro

- **03/10 — abertura da Fase 3:** memória A, B, C1 e C4a, sugestões de tema e
  relatório do autor ([ADR 0008](docs/decisions/0008-memoria-em-camadas.md));
  smoke test numa cópia do repositório; episódio às 05:00, repescagem às 06:00
  e 07:00, vigia às 07:30. Fase 2 concluída no mesmo dia (PROJETO.md)
- **10/10:** relatório de sexta com o episódio do próprio dia
- **18/10:** "Anthrópic" no `pronuncia.json`; MV7+ medido
  (`docs/benchmarks-audio.md`)
- **25/10:** linha de base dos fatos, 7,9% de erro, todos leves, US$ 149 do
  crédito ([ADR 0010](docs/decisions/0010-redacao-com-varios-agentes.md));
  fios com teto de 40 e expiração; temas T-09 e T-10
- **26/10:** narração no Eleven v4
  ([ADR 0011](docs/decisions/0011-narracao-no-eleven-v4.md)); "IA" por
  extenso no áudio desde 27/10; ritmo remedido para 159 ppm em 30/10
- **28/10:** sem rede, o orquestrador para de cara
- **30/10:** abertura sem "IA" dobrada e transições sem "o terceiro assunto é
  curto", com contadores na conferência do roteiro; fonte fechada lida por
  outra porta da própria fonte (feed da OpenAI, `outras_portas`, cópia do
  arquivo público) antes da imprensa

# TODO

Lista curta do que está em cima da mesa. O planejamento de longo prazo vive em
[PROJETO.md](PROJETO.md). Atualizada em 03/10/2026, à noite.

## Semana de 05/10 — acompanhar o que entrou em 03/10

Em 03/10 entrou de uma vez: lista de pautas no prompt, histórico do backlog
fora da leitura, temas, fios, sugestões de tema, conferência de repetição e o
relatório do autor. Tudo ensaiado, mas um ensaio é um dia só.

- [ ] **Segunda, 05/10 — primeiro episódio com a memória nova.** Depois das
      08:07: o vigia disse "tudo certo"? Olhar os avisos no registro
      (`python3 scripts/registro.py mostra`) e se o agente mexeu em temas,
      fios ou sugestões (Observações do `research/2026-10-05.md`)
- [ ] **Quinta, 08/10 — custo da memória nova em produção:**
      `python3 scripts/memoria_custo.py --desde 2026-10-05`, contra a semana
      de 28/09 (índice 13%, backlog 11%, mediana de US$ 4,41). Se o custo
      subiu ou alguma pauta repetiu, revisar antes do C2
- [ ] **Sexta, 09/10 — primeiro relatório do autor automático:** conferir
      `memoria/autor/2026-W41.md` e se o push do vigia trouxe a linha
      "RELATÓRIO DA SEMANA". Pedir `/relatorio` e decidir o que estiver
      pendente
- [ ] **Novidade na abertura** — nenhuma programada; o anúncio do Opus 5.5
      saiu sozinho em 02/10. Candidata, agora que o ensaio confirmou: a memória
      — "passo a ter à mão tudo o que já foi ao ar, e acompanho promessas e
      preocupações até o desfecho". Se for, decidir o texto e as datas em
      `config/novidades.json`
- [ ] **`scripts/ensaio.sh`** — automatizar o que foi feito à mão em 03/10:
      copiar o repositório no estado de um dia, rodar com `env -i` e o `PATH`
      do plist, desviar registro e estado. Sem o ambiente do launchd, o custo
      do ensaio não vale (ver `docs/aprendizados.md`)

## Fase 3 — memória do agente

Plano no [ADR 0008](docs/decisions/0008-memoria-em-camadas.md): acervo sem
fim, leitura com teto (~115 KB por dia em qualquer ano). Medição base de
03/10, com `scripts/memoria_custo.py`: nos dias do Opus 5.5, a memória era
~42% do cache lido, e o índice não era lido inteiro — passou do limite de 25
mil tokens da ferramenta Read.

- [x] **A. Lista compacta de pautas no prompt** (03/10) — `scripts/pautas.py`
- [x] **B. Histórico do backlog em arquivo próprio** (03/10) —
      `saved-items/historico/AAAA-MM.md`; o backlog foi de 39 para 12 KB
- [x] **C1. Temas e fios** (03/10) — 8 temas em `memoria/temas.md` (teto 10;
      tema é linha editorial, só o autor cria) e 10 fios em `memoria/fios.md`
      (teto 20; desfecho esperado em até ~6 meses)
- [x] **Sugestões de tema e relatório do autor** (03/10) —
      `memoria/temas-sugeridos.md` (a primeira, S-001, virou o T-08);
      `scripts/relatorio.py`, comando `/relatorio` e passo automático no último
      episódio da semana. **Para evoluir:** cada pedido novo entra no script
- [x] **C4a. Repetição de pauta por link** (03/10) — `confere_repeticao.py`
- [ ] **C2. Resumos semanais** — semana de 12/10. Passo depois da
      publicação, `prompts/memoria.md`, `confere_resumo.py` e carga das 6
      semanas de 24/08 a 02/10. Medir junto se 4 resumos permitem ler 3
      roteiros na íntegra em vez de 5
- [ ] **C3. Resumo mensal** — setembro como piloto, com uma seção por tema
- [ ] **C4b. Teto de 90 dias na lista do prompt** — quando passar de ~30 KB,
      por volta de janeiro de 2027
- [ ] C5 trimestre e ano (dez/26) · C6 "há um ano" no prompt (ago/27) · C7
      linha do tempo da IA, projeto paralelo do acervo

## Fase 3 — independência do Mac

- [x] ~~Resgatar o crédito de US$ 250 do Claude Code na nuvem~~ — resgatado em
      03/10; expira às 04:59 (horário de Brasília) de 05/11. **Não vale para
      Projects nem para Routines**, só sessões na nuvem
- [x] ~~Acesso do Claude Code na nuvem ao GitHub~~ — 03/10: Claude GitHub App
      na conta pessoal `campilho`, modo "Apenas sessões na nuvem", **só no
      repositório `campilho/CampsCast`**
- [ ] **Piloto no Claude Code na nuvem** — como o crédito não cobre Routines,
      decidir entre sessão na nuvem disparada de outro jeito, que gasta o
      crédito, ou rotina, que desconta dos limites do Max. Antes, confirmar na
      documentação como agendar uma sessão na nuvem. Obstáculo conhecido: a
      chave do S3 (SigV4) dentro da sessão. **Tem de ir junto:** o passo de
      resumos da memória e o relatório do autor de sexta (ADR 0008)
- [ ] **Onde rodar sem o Mac do Fernando Campilho** — AWS, Mac mini do irmão
      ou Mac mini próprio, se o piloto na nuvem não resolver. Avaliação no
      `PROJETO.md`. Conversar com o irmão sobre acesso remoto e usuário
      separado; pesar a compra considerando os agentes do livro 2081

## Fase 3 — formato do episódio

- [ ] **Capítulos no Spotify** — o Spotify Web marca onde cada pauta começa,
      com um título por trecho. O feed não manda nada para isso (só a lista de
      pautas, sem marcas de tempo), então é o Spotify que gera. Primeiro
      conferir na documentação do Spotify for Creators de onde vêm e se dá
      para controlar. Para a chamada de seguir virar capítulo próprio: narrar
      cada parte do roteiro numa requisição separada, o que dá a duração exata
      de cada uma, e escrever as marcas de tempo na descrição
- [ ] **Chamada para seguir mais destacada** — no ar, sai colada no fim da
      primeira pauta e passa muito rápido. Pausa maior antes e depois, e rever
      a orientação do texto. A pausa pode vir do mesmo mecanismo dos
      capítulos: a chamada narrada sozinha, com silêncio montado pelo `tts.py`
- [ ] **Rever a ficha técnica do encerramento** — a ideia fica, mas está longa
      (~85 palavras, uns 35 s) e pode cansar quem ouve todo dia. Tirar do ar o
      "cinco delas bloqueadas na leitura". **O relatório de fontes que falham
      já existe** no `relatorio.py`: em 03/10, `openai.com` falhou 7 vezes na
      semana e 12 nas quatro anteriores, `x.ai` 3 e 8. Falta decidir se o
      roteiro de pesquisa muda para essas fontes

## Fase 3 — feedback e site

- [ ] **Sugestões de tema dos ouvintes** — depois do site e do formulário: a
      sugestão entra em `memoria/temas-sugeridos.md` com "por ouvinte", e o
      autor decide como decide as do agente
- Site, formulário, vídeos e regravação da voz: ver Fase 3 no `PROJETO.md`

## Recorrente

- [ ] **Relatório semanal do autor** — sai sozinho no último episódio da
      semana; o vigia avisa no celular. Decidir as pendências com `/relatorio`
- [ ] **Relatório mensal de audiência** — primeiro fim de semana do mês, em
      `privado/audiencia.md`: exportação diária do Spotify, tela principal
      (seguidores) e tabela de episódios. Junto, a revisão de custos do
      [ADR 0007](docs/decisions/0007-custo-por-episodio.md) e uma olhada no
      Apple Podcasts Connect: aba Análise e relatórios, cujo acesso foi pedido
      em 03/10 (naquele dia, "Assinaturas (0)" e "Programas (0)", embora o
      programa esteja no ar na Apple)
- [ ] **Leitura do Spotify for Creators pela extensão Claude in Chrome** —
      testada em 03/10: leu a tela principal e a tabela de episódios **com os
      números**, que a exportação traz vazios. A extensão só enxerga as abas
      que ela abre, então abre o painel numa aba nova, com o login do Chrome; a
      tabela pagina de 25 em 25. Validar no relatório de novembro. **Não usar
      no LinkedIn**, cujos termos proíbem extensões que automatizam ou extraem
      dados
- [ ] O painel do Spotify for Creators tem um **"Programa sem título"** vazio,
      e é ele que abre primeiro. Apagar, se não tiver uso

## Operação

- [x] ~~Vigia externo~~ — rotina na nuvem `Vigia do CampsCast (08:07 BRT)`,
      dias úteis, lê `estado.json` e `feed.xml` e avisa por e-mail e push.
      Atualizado em 03/10: lê só pelo WebFetch — o alarme de 29/09 foi o proxy
      da nuvem barrando o `curl` — e, no último episódio da semana, avisa do
      relatório do autor
- [ ] **Antes da próxima viagem:** `claude setup-token` para um token longo;
      Remote Control ligado na sessão do app (testado pelo Android S24 em
      03/10); Mac na tomada, tampa aberta
- [ ] **Preencher `NOTIFY_TO`, `SMTP_USER` e `SMTP_PASS`** no `.env`, ou tirar
      as variáveis pela metade. Hoje o `notify.py` cai calado na notificação do
      macOS, que não sai da tela de casa
- [ ] (ideia) **Detectar sozinho a troca de modelo ou de voz** e gerar a
      novidade — exige gravar os modelos usados no front-matter

## Datas fixas

- [ ] **Sexta, 09/10/2026 — primeiro relatório do autor automático**
- [ ] **Até 17/10/2026 — ler os primeiros resumos semanais** (C2), de 24/08 a
      09/10, antes de o agente passar a usá-los; depois, só a conferência
- [ ] **05/11/2026, 04:59 — o crédito de US$ 250 da nuvem expira**
- [ ] **Até 07/11/2026 — ler o resumo mensal de setembro** (piloto do C3) e o
      de outubro
- [ ] **03/01/2027 — Apple Podcasts: sem nenhum acesso, sair** (ver Divulgação)
- [ ] **05/08/2027 — renovar `campscast.com.br`** no registro.br (R$ 40 por
      ano), um mês antes do vencimento em 05/09/2027
- [ ] **Até 05/08/2027 — decidir o `campscast.com`**, que não é usado e renova
      sozinho na GoDaddy em 05/09/2027 por R$ 174,98: redirecionar para o
      `.com.br` ou desligar a renovação
- ElevenLabs renova todo dia 23, no plano Creator mensal. O anual fica para
  depois das próximas fases, que podem mudar o consumo

## Divulgação

- [x] ~~Plano de divulgação~~ — LinkedIn, um post por terça: lançamento em
      29/09 e cinco posts sobre as Fases 1 e 2 até 03/11. Rascunhos e regras em
      `privado/divulgacao.md`
- [x] ~~Link principal~~ — Spotify, onde estão os seguidores; a Apple segue
      como segundo link
- [ ] **Sábado, 10/10 — comparar a audiência** com a linha de base de 26/09
- [ ] **Apple Podcasts: divulgar ou sair** — o foco é o Spotify. Pensar se vale
      divulgar a Apple de algum jeito; **se até 03/01/2027 não houver nenhum
      acesso por lá, tirar o programa da Apple**. Se ficar, corrigir a
      frequência que a Apple mostra ("duas vezes por semana") e a página
      Podcasts do Connect, que aparece vazia

## Feito em 03/10/2026 — abertura da Fase 3

- [x] Memória do agente: passos A, B, C1 e C4a, sugestões de tema e relatório
      do autor (detalhes na seção da memória e no ADR 0008)
- [x] Dois ensaios do episódio de 02/10. O primeiro herdou o ambiente da
      sessão do app e serviu só para o comportamento. O segundo, com o
      ambiente do launchd, valeu também para o custo: US$ 4,12 contra 4,41 na
      produção, cache lido de 5,9 para 4,8 milhões; índice de 21% para 2% do
      cache lido, backlog de 11% para 4%, temas e fios 5%. O agente não
      duplicou marco, recusou abrir fio de longo prazo e fez a primeira
      sugestão de tema, aprovada
- [x] Ritmo remedido com os 19 episódios da voz nova: **152 ppm**, faixa de
      836 a 1.444 palavras, alvo 1.216. A contagem de palavras do agente bate
      com a do texto, então o Bash mínimo para contar deixou de ser necessário
- [x] Pronúncia de "Anthropic" — o erro do episódio 25 (3:32, "que Anthropic e
      OpenAI") não se repetiu ao gerar a frase de novo. Ficou a regra no
      prompt: empresa sempre com artigo. Reabrir se voltar a errar
- [x] Smoke test isolado numa cópia temporária do repositório — não move mais
      `episodes/` nem escreve no `.env` real, e confere no fim que o
      repositório real ficou intacto
- [x] Duração dos episódios sem mudança — os 26 ficaram entre 8:04 e 9:22,
      média e mediana de 8:50, desvio padrão de 22 s. Os 10 minutos são
      referência, não teto rígido
- [x] Pontualidade — desde 14/09, com o Mac na tomada, os 15 episódios
      começaram às 05:50 e terminaram até 06:11, sem sono no meio
- [x] App Store sem atualização automática — o Xcode 27 tinha se instalado
      sozinho em 15/09 e travado o `git` pela licença
- [x] Polly e Chirp 3 — comparação dispensada, adendo no ADR 0001
- [x] Fora da lista, foco no Spotify: OP3, downloads por arquivo, a pergunta
      Spotify ou Apple, a escuta dos episódios de 25/09 e do 12, e o chamado na
      ElevenLabs sobre a voz no Flash. `gravacoes/descartadas/`, que só tinha
      um `.DS_Store`, foi para a Lixeira

## Fase 2 — concluída em 03/10/2026

- [x] Conversas com os primeiros ouvintes — a maioria achou a voz boa e
      natural; a queixa que se repete é o ritmo (regravação na Fase 3)
- [x] Post de lançamento no LinkedIn — 29/09, 5.693 pessoas alcançadas;
      **destacado pelo LinkedIn News em 01/10** (marcos no README, provas em
      `privado/conquistas/`). Os 15 comentários estão em `privado/audiencia.md`
- [x] Agente no Claude Opus 5.5 (26/09) e revisão do
      [ADR 0005](docs/decisions/0005-agente-no-opus-5-5.md) (03/10): custo
      mediano caiu 49%, execução de 10 a 14 min, nenhum roteiro com regra
      quebrada
- [x] Nova abertura e encerramento, novidades na abertura e chamada para
      seguir às terças e quintas
      ([ADR 0006](docs/decisions/0006-abertura-no-tom-nao-no-texto.md))
- [x] macOS 27 — atualizado em 03/10; testes, ensaio, ElevenLabs, token do
      Claude e S3 verificados no mesmo dia
- [x] [ADR 0007](docs/decisions/0007-custo-por-episodio.md) — R$ 6,25 por
      episódio é o que o CampsCast acrescenta; R$ 32,12 com a assinatura do
      Claude inteira
- [x] Episódios commitados e enviados ao GitHub até 02/10; episódio 11
      conferido no painel do Spotify
- [x] Registro diário de execução e custo em `metricas/execucoes.jsonl`, vigia
      externo, silêncio no começo e no fim, número do episódio, ficha técnica
      com nomes derivados dos modelos, mapa de pronúncia, voz clonada
      profissional e Apple Podcasts no ar

# TODO

Lista curta do que está em cima da mesa. O planejamento de longo prazo vive em
[PROJETO.md](PROJETO.md). Atualizada em 03/10/2026.

## Fase 3 — abre na semana de 05/10

- [x] ~~Resgatar o crédito de US$ 250 do Claude Code na nuvem~~ — resgatado em
      03/10. Expira às 04:59 (horário de Brasília) de 05/11. **Não vale para
      Projects nem para Routines**, segundo a tela do resgate: só sessões na
      nuvem. Isso muda o plano do piloto — ver abaixo
- [x] ~~Acesso do Claude Code na nuvem ao GitHub~~ — 03/10: Claude GitHub App
      instalado na conta pessoal `campilho`, no modo "Apenas sessões na nuvem",
      com acesso **só ao repositório `campilho/CampsCast`**. A verificação de
      status do repositório no claude.ai passou
- [ ] **Revisar a memória do agente** — primeiro item. Medido em 03/10: o
      `covered-index.json` tem 241 KB (67 KB em 14/09) e cresce uns 9 KB por
      dia útil; o `saved-items/backlog.md` tem 40 KB e não aparece no registro.
      Os dois são lidos inteiros todo dia. Antes de redesenhar, medir quanto
      do cache lido vem deles — os ~40% do índice ainda são estimativa. Desenho
      já discutido no PROJETO.md: memória em camadas, fios em aberto e a linha
      do tempo da IA
- [ ] **Piloto no Claude Code na nuvem** — como o crédito não cobre Routines,
      decidir entre: sessão na nuvem disparada de outro jeito, que gasta o
      crédito; ou rotina, que desconta dos limites do Max. Antes de montar,
      confirmar na documentação como uma sessão na nuvem pode ser agendada.
      O obstáculo conhecido continua sendo a chave do S3 (SigV4) dentro da
      sessão
- [ ] **Onde rodar sem o Mac do Fernando Campilho** — AWS, Mac mini do irmão ou
      Mac mini próprio, se o piloto na nuvem não resolver. Avaliação no
      `PROJETO.md`, Fase 3. Conversar com o irmão sobre acesso remoto e usuário
      separado; pesar a compra considerando os agentes do livro 2081

## Recorrente

- [ ] **Relatório mensal de audiência** — primeiro fim de semana de cada mês, em
      `privado/audiencia.md`: exportação diária do Spotify, tela principal
      (seguidores) e tabela de episódios. O de setembro foi feito em 03/10.
      Junto, a revisão mensal de custos do
      [ADR 0007](docs/decisions/0007-custo-por-episodio.md)
- [ ] **Leitura do Spotify for Creators pela extensão Claude in Chrome** —
      testada em 03/10 e funcionou: com o login feito no Chrome, a extensão
      leu a tela principal (plays, seguidores, tempo de consumo, público) e a
      tabela de episódios **com os números**, que a exportação traz vazios. A
      extensão só enxerga as abas que ela mesma abre, então abre o painel numa
      aba nova, com o login do Chrome. A tabela pagina de 25 em 25. Validar
      no relatório de novembro, substituindo o print da tabela. **Não usar no
      LinkedIn**, cujos termos proíbem extensões que automatizam ou extraem
      dados do site
- [ ] O painel do Spotify for Creators tem um **"Programa sem título"** vazio
      ao lado do CampsCast, e é ele que abre primeiro. Apagar, se não tiver uso

## Pendências menores

- [ ] **Ouvir os dois episódios de 25/09** em `privado/comparacao-opus-5-5/` —
      mesmas três pautas; o 5.5 leu 51 páginas contra 19 e custou 11% a mais
      que o Opus 5 naquele dia (mas 16% abaixo da mediana da semana dele)
- [ ] **Ouvir o episódio 12** (segunda, 14/09) — o primeiro com silêncio no
      começo e no fim, número na abertura, encerramento só com a ficha técnica
      e os nomes certos de quem escreveu e narrou
- [ ] **Remedir o ritmo com semanas cheias** — o `words_per_minute` ainda é
      o de 3 episódios (150):
      `python3 scripts/calibrate_pace.py --desde 2026-09-08 --apply`
- [ ] **Perguntar a ouvintes se preferem Spotify ou Apple Podcasts** — a
      pergunta segue em aberto em `privado/audiencia.md`
- [ ] **Decidir se o agente ganha um Bash mínimo** — as transcrições mostram
      ele tentando `wc -w`, `window.py` e `tts.py --budget`, sempre negado;
      conta palavras e calcula na mão. Liberar só comandos de leitura
      (`--allowedTools "Bash(wc:*)"`, por exemplo) daria contagem exata
- [ ] (ideia) **Detectar sozinho a troca de modelo ou de voz** e gerar a
      novidade — exige gravar os modelos usados no front-matter
- [ ] **Anotar os minutos dos erros de "Anthropic"** — isolada a pronúncia sai
      certa; o erro aparece no meio do texto. Com os minutos, gerar só aquelas
      frases com e sem troca de grafia no `config/pronuncia.json`
- [ ] (opcional) **App Store sem atualização automática** — o Xcode 27 se
      instalou sozinho em 15/09 e travou o `git` pela licença

## Operação

- [ ] **Pontualidade antes das 7h** — **na tomada** é o que decide: as três falhas
      de 10 e 11/09 foram na bateria, e 09/09 concluiu de tampa fechada na
      tomada. Tampa aberta como margem. Se falhar na tomada, fallback na nuvem
- [x] ~~Vigia externo~~ — rotina na nuvem `Vigia do CampsCast (08:07 BRT)`,
      dias úteis, lê `feed.xml` e `estado.json` e avisa por e-mail e push. Não
      depende do Mac, então também cobre o caso de o Mac não ter ligado
- [ ] **Antes da próxima viagem:** `claude setup-token` para um token longo,
      imune à rotação da sessão; Remote Control de pé
      (`claude --remote-control CampsCast`), testado pelo iPhone ainda em casa;
      Mac na tomada, tampa aberta
- [ ] **Preencher `NOTIFY_TO`, `SMTP_USER` e `SMTP_PASS`** no `.env`, ou tirar
      as variáveis pela metade. Hoje o `notify.py` cai calado na notificação do
      macOS, que não sai da tela de casa
- [ ] **Agente escreve colado no teto** de palavras em vez de mirar o alvo;
      episódios de ~9 min em vez de 8. Ajuste no `prompts/master.md`, se
      quisermos episódios mais curtos
- [ ] (opcional) **Chamado na ElevenLabs** pedindo retry do fine-tuning Flash
      da voz `LvmWSbvGusgLWSQDKHJH` ("NaN losses", parou em 75,7%). Traria custo
      pela metade e fala mais rápida; a velocidade fica como está por enquanto

## Datas fixas

- [ ] **05/11/2026, 04:59 — o crédito de US$ 250 da nuvem expira**
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
- [x] ~~Link principal~~ — Spotify, onde está toda a audiência medida; a Apple
      segue como segundo link. Rever depois das conversas com ouvintes
- [ ] Comparar a audiência com a linha de base de 26/09 em 10/10

## Estacionado até haver divulgação

- [ ] **Frequência na Apple** — aparece "duas vezes por semana" para o público;
      o podcast sai todo dia útil. A página Podcasts do Connect aparece vazia
      sem motivo conhecido (só existe uma conta)
- [ ] **Analytics da Apple** — zerado até alguém ouvir por lá
- [ ] (opcional) **Contar downloads com o prefixo OP3** (`op3.dev`)

## Dívida técnica

- [ ] O smoke test move `episodes/` para se isolar. A correção certa é os
      testes não tocarem em dados reais — um diretório de episódios
      configurável por variável de ambiente resolveria
- [ ] Polly e Chirp3 seguem sem comparação medida, pendentes no ADR 0001
- [ ] Apagar `gravacoes/descartadas/` quando quiser

## Longo prazo

- [ ] **Downloads por arquivo** — quando passar de algo como 100 pessoas por
      semana, ou houver conversa com patrocinador. Primeiro o OP3; o plano Pro
      do CloudFront só se não bastar

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
- [x] Episódios commitados e enviados ao GitHub até 02/10
- [x] Episódio 11 conferido no painel do Spotify em 03/10 — aparece
      normalmente; o atraso era só a defasagem do painel
- [x] Registro diário de execução e custo em `metricas/execucoes.jsonl`, vigia
      externo, silêncio no começo e no fim, número do episódio, ficha técnica
      com nomes derivados dos modelos, mapa de pronúncia, voz clonada
      profissional e Apple Podcasts no ar

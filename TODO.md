# TODO

Lista curta do que está em cima da mesa. O planejamento de longo prazo vive em
[PROJETO.md](PROJETO.md). Atualizada em 27/09/2026.

## Esta semana — fechar a Fase 2

A Fase 2 fecha quando estas três estiverem feitas; a Fase 3 abre no fim de
semana de 03/10. YouTube e site passaram para a Fase 3.

- [ ] **Conversar com os primeiros ouvintes** — segunda, 28/09
- [ ] **Post de lançamento no LinkedIn** — terça, 29/09
- [ ] **ADR de custos** com setembro fechado — fim de semana de 03/10, junto com
      a revisão do ADR 0005
- [ ] **Semana de 05/10, abrindo a Fase 3: revisar a memória do agente** —
      medido em 27/09: o
      índice de pautas foi de 67 K para 181 K em onze dias, lido inteiro todo
      dia, e cada pauta nova é maior que a anterior (750 bytes em agosto, ~4.000
      em setembro). O Opus 5 passou a ler só trechos em 25/09 (memória com
      buracos); o Opus 5.5 lê tudo (custo crescente). Estimativa, a medir: o
      índice já seria ~40% da leitura de cache. Na Fase 3 do PROJETO.md:
      memória em camadas, fios em aberto e a linha do tempo da IA. Depois da
      revisão do Opus 5.5, para não misturar duas mudanças
- [ ] **Resgatar o crédito de US$ 250 do Claude Code na nuvem até 07/10** — vence
      em 04/11; é o que paga o piloto, primeiro item da Fase 3

## Feito nesta semana e pendências menores

- [x] ~~Trocar o agente para Claude Opus 5.5~~ — feito em 26/09, com
      `--effort high` fixado: o Opus 5 rodava em `high` sem ninguém pedir, e o
      padrão do 5.5 é `medium`. CLI em 2.1.283. Episódio de 25/09 refeito num
      sandbox para comparar; números e critério de revisão no
      [ADR 0005](docs/decisions/0005-agente-no-opus-5-5.md)
- [ ] **Ouvir os dois episódios de 25/09** em `privado/comparacao-opus-5-5/` —
      mesmas três pautas; o 5.5 leu 51 páginas contra 19 e custou 11% a mais
      que o Opus 5 naquele dia (mas 16% abaixo da mediana da semana dele)
- [x] ~~Anunciar a troca de modelo na abertura~~ — de 28/09 a 02/10, via
      `config/novidades.json`, em tom de upgrade ("o modelo que o meu antecessor
      noticiou aqui no episódio dezenove")
- [x] ~~Nova abertura e encerramento~~ — sem a voz na abertura, sem repetir a
      data da janela, nome completo em vez do apelido, sem "Aqui é o CampsCast"
      no fim; variação livre com conferência que registra
      ([ADR 0006](docs/decisions/0006-abertura-no-tom-nao-no-texto.md))
- [x] ~~Chamada para seguir o podcast~~ — depois da primeira pauta, terças e
      quintas, a partir de 29/09; texto livre do agente
- [ ] **Post de lançamento no LinkedIn, terça 29/09, 11h** — rascunho e série
      semanal em `privado/divulgacao.md`; antes, trocar a citação pela frase
      exata do episódio de segunda. Linha de base de audiência registrada em
      26/09; comparar em 03/10 e 10/10
- [x] ~~Link do Spotify no README~~ — `open.spotify.com/show/5toSeNQlZxjbCAFPA1gAuJ`,
      com "l" minúsculo depois de `NQ`
- [ ] **Decidir se o agente ganha um Bash mínimo** — as transcrições mostram
      ele tentando `wc -w`, `window.py` e `tts.py --budget`, sempre negado;
      conta palavras e calcula na mão. Liberar só comandos de leitura
      (`--allowedTools "Bash(wc:*)"`, por exemplo) daria contagem exata
- [ ] (ideia) **Detectar sozinho a troca de modelo ou de voz** e gerar a
      novidade — exige gravar os modelos usados no front-matter
- [ ] **Sábado, 03/10: revisar o ADR 0005** com cinco dias de produção —
      mediana de custo contra US$ 8,66 do Opus 5; acima de +15% sem ganho
      audível, testar `--effort medium`. Na mesma revisão, contar `avisos_roteiro`
      no registro: quantas regras a abertura livre deixou cair
- [ ] **Fim de semana de 03/10: macOS 27**, depois da revisão — uma mudança
      por vez. Depois de atualizar: smoke test, ensaio, `pmset -g custom`,
      `launchctl list | grep campscast` e um episódio completo no sandbox
- [ ] (opcional) **App Store sem atualização automática** — o Xcode 27 se
      instalou sozinho em 15/09 e travou o `git` pela licença
- [ ] **Commitar os episódios de 14 a 25/09** — o repositório público parou
      em 13/09
- [x] ~~Refazer o login do Claude Code no terminal~~ — feito; a credencial
      renova sozinha e as falhas de 10 e 11/09 não eram de login (eram sono e
      DNS)
- [ ] **Antes de viajar, segunda à noite** (volta na semana seguinte):
      - [x] ~~liberar `estado.json` na policy do bucket~~ — verificado em
            14/09: responde 200 tanto por `campscast.com.br/estado.json` quanto
            direto no S3. O 403 que o vigia relatou nesse dia era resposta
            velha em cache, não a policy
      - [ ] `claude setup-token` para um token longo, imune à rotação da sessão
      - [ ] deixar o Remote Control de pé: `claude --remote-control CampsCast`,
            e **testar pelo iPhone ainda em casa**
      - [ ] Mac na tomada, tampa aberta
- [ ] **Ouvir o episódio 12** (segunda, 14/09) — o primeiro com silêncio no
      começo e no fim, número na abertura, encerramento só com a ficha técnica
      e os nomes certos de quem escreveu e narrou
- [ ] **Subir para o GitHub** os commits locais
- [ ] **Rever o episódio 11 no Spotify** — saiu atrasado e o painel atualiza
      com defasagem
- [ ] **Anotar os minutos dos erros de "Anthropic"** — isolada a pronúncia sai
      certa; o erro aparece no meio do texto. Com os minutos, gerar só aquelas
      frases com e sem troca de grafia no `config/pronuncia.json`
- [ ] **Conversar com quatro ou cinco ouvintes** — até onde ouvem, o que os
      faria parar, e **se preferem Spotify ou Apple Podcasts**
- [ ] **Decidir a chamada para seguir o podcast** — recomendação: uma frase no
      encerramento, antes da despedida. Quem chega ao fim é justamente quem
      gostou, e seguir é o que faz o app avisar do episódio novo
- [ ] **Sexta, 18/09:** primeira anotação semanal em `privado/audiencia.md`,
      olhar o registro de custos (`python3 scripts/registro.py mostra`) e
      remedir o ritmo com uma semana cheia:
      `python3 scripts/calibrate_pace.py --desde 2026-09-08 --apply`

## Operação

- [ ] **Pontualidade antes das 7h** — **na tomada** é o que decide: as três falhas
      de 10 e 11/09 foram na bateria, e 09/09 concluiu de tampa fechada na
      tomada. Tampa aberta como margem. Se falhar na tomada, fallback na nuvem
- [x] ~~Vigia externo~~ — rotina na nuvem `Vigia do CampsCast (08:07 BRT)`,
      dias úteis, lê `feed.xml` e `estado.json` e avisa por e-mail e push. Não
      depende do Mac, então também cobre o caso de o Mac não ter ligado
- [ ] **Preencher `NOTIFY_TO`, `SMTP_USER` e `SMTP_PASS`** no `.env`, ou tirar
      as variáveis pela metade. Hoje o `notify.py` cai calado na notificação do
      macOS, que não sai da tela de casa
- [ ] **Agente escreve colado no teto** de palavras em vez de mirar o alvo;
      episódios de ~9 min em vez de 8. Ajuste no `prompts/master.md`, se
      quisermos episódios mais curtos
- [ ] (opcional) **Chamado na ElevenLabs** pedindo retry do fine-tuning Flash
      da voz `LvmWSbvGusgLWSQDKHJH` ("NaN losses", parou em 75,7%). Traria custo
      pela metade e fala mais rápida; a velocidade fica como está por enquanto

## Divulgação

- [x] ~~Plano de divulgação~~ — LinkedIn, um post por terça: lançamento em
      29/09 e cinco posts sobre as Fases 1 e 2 até 03/11. Rascunhos e regras em
      `privado/divulgacao.md`
- [x] ~~Link principal~~ — Spotify, onde está toda a audiência medida; a Apple
      segue como segundo link. Rever depois das conversas com ouvintes

## Estacionado até haver divulgação

- [ ] **Frequência na Apple** — aparece "duas vezes por semana" para o público;
      o podcast sai todo dia útil. A página Podcasts do Connect aparece vazia
      sem motivo conhecido (só existe uma conta)
- [ ] **Analytics da Apple** — zerado até alguém ouvir por lá
- [ ] (opcional) **Contar downloads com o prefixo OP3** (`op3.dev`)

## Fase 2 — o que resta

- [ ] ADR consolidando os custos reais — começo de outubro, com as faturas de
      setembro fechadas. Inclui o custo do Claude por token, base da decisão de
      onde rodar na Fase 3

## Fase 3 — preparação

- [ ] **Onde rodar sem o Mac do Fernando Campilho** — AWS, Mac mini do irmão ou Mac mini
      próprio. Avaliação no `PROJETO.md`, Fase 3. Conversar com o irmão sobre
      acesso remoto e usuário separado; pesar a compra considerando os agentes
      do livro 2081

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

## Feito recentemente

- [x] Registro diário de execução e custo em `metricas/execucoes.jsonl`, com
      o histórico desde 26/08 reconstruído dos logs (13/09)
- [x] Silêncio de 1 s no começo e 3 s no fim de cada episódio (12/09)
- [x] Número do episódio no front-matter, na abertura e na tag
      `<itunes:episode>`; os 11 anteriores numerados (12/09)
- [x] Encerramento só com a ficha técnica — sem recap e sem "o que observar"
      (12/09)
- [x] Nomes da ficha derivados dos modelos em uso; modelo do agente fixado
      em `claude-opus-5` (12/09)
- [x] Mapa de pronúncia em `config/pronuncia.json` (12/09)
- [x] Velocidade testada a 1,05, 1,10 e 1,15 e descartada (12/09)
- [x] Definição da conclusão do Spotify: ouviu pelo menos 95% (12/09)
- [x] CloudFront gratuito investigado: sem dado por arquivo (12/09)
- [x] Ritmo recalibrado com episódios reais: 150 ppm (10/09)
- [x] Voz clonada profissional gravada, treinada e adotada (07/09)
- [x] Apple Podcasts no ar, ID 6809631318 — os quatro diretórios respondem
- [x] README com os links dos diretórios e a seção da voz

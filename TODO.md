# TODO

Lista curta do que está em cima da mesa. O planejamento de longo prazo vive em
[PROJETO.md](PROJETO.md). Atualizada em 12/09/2026.

## Esta semana

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
- [ ] **Sexta, 18/09:** primeira anotação semanal em `privado/audiencia.md` e
      remedir o ritmo com uma semana cheia:
      `python3 scripts/calibrate_pace.py --desde 2026-09-08 --apply`

## Operação

- [ ] **Pontualidade antes das 7h** — tampa aberta e na tomada. Três falhas por
      sono em 10 e 11/09. Se falhar de novo, fallback na nuvem
- [ ] **Agente escreve colado no teto** de palavras em vez de mirar o alvo;
      episódios de ~9 min em vez de 8. Ajuste no `prompts/master.md`, se
      quisermos episódios mais curtos
- [ ] (opcional) **Chamado na ElevenLabs** pedindo retry do fine-tuning Flash
      da voz `LvmWSbvGusgLWSQDKHJH` ("NaN losses", parou em 75,7%). Traria custo
      pela metade e fala mais rápida; a velocidade fica como está por enquanto

## Divulgação — mais adiante

- [ ] **Plano de divulgação** — começar pelo LinkedIn, rede grande e quase toda
      de tecnologia: posts frequentes contando a evolução do projeto, sempre
      com os links do podcast
- [ ] **Escolher o link principal** a divulgar, depois das conversas com
      ouvintes (Spotify ou Apple)
- [ ] **Avaliar o YouTube** como mais um canal, incluindo o YouTube Music
- [ ] **Avaliar um site simples** em `campscast.com.br` — links dos diretórios,
      descrição do projeto e GitHub; vira a âncora do formulário da Fase 3

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

- [ ] **Onde rodar sem o Mac do Camps** — AWS, Mac mini do irmão ou Mac mini
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

# TODO — fim de semana de 06 e 07/09/2026

Lista curta e datada. O planejamento de longo prazo vive em
[PROJETO.md](PROJETO.md); aqui é só o que está em cima da mesa.

## Hoje

- [x] Medir a sala — descoberto que a TV do cômodo ao lado sobe o ruído de
      −61 para −47 dBFS. Regravar tudo à noite, com a TV desligada.
- [ ] **Gravar o material da voz profissional** — 30+ minutos, seguindo os seis
      blocos de [docs/gravacao-voz.md](docs/gravacao-voz.md). É o item de maior
      impacto perceptível para quem ouve, e o único que depende de silêncio em
      casa. Gravar no iPhone, app Gravador, qualidade *Sem perdas*.

      Protocolo por bloco:
      1. `python3 scripts/check_recording.py silencio.m4a --sala` — se der
         abaixo de −60 dBFS, pode gravar
      2. Começar cada bloco com **10 segundos parado, em silêncio**
      3. Mesma posição e distância em todos os blocos
      4. `python3 scripts/prep_voice_samples.py *.m4a` — converte e valida
- [ ] **Conta Apple** — trocar o e-mail de notificação (hoje é de outra pessoa)
      e o e-mail principal, que está num domínio expirado. Depois, tentar o
      Podcasts Connect de novo.
- [ ] **Conferir o Spotify** à noite — o show ainda responde 404, o que é
      esperado. Quando sair do ar 404, avisar para entrar no README.

## Quando o material da voz estiver pronto

- [ ] Criar a Professional Voice Clone na ElevenLabs
- [ ] Trocar `voice_id` em `config/tts.json`
- [ ] `python3 scripts/tts.py --check` para validar
- [ ] Gerar um episódio e **remedir o ritmo**:
      `python3 scripts/calibrate_pace.py --desde <primeira data com a voz nova> --apply`
- [ ] Comparar com a voz atual antes de adotar

## Depois, sem pressa

- [ ] README público caprichado, com os links dos diretórios já ativos
- [ ] ADR consolidando os custos reais — ElevenLabs, S3, CloudFront, Route 53
- [ ] Avaliar YouTube Music (confirmar disponibilidade no Brasil)
- [ ] Cobrar feedback dos 4 beta testers
- [ ] Refatorar o agente em subagents: pesquisador, editor, publicador

## Dívida técnica registrada

- [ ] O smoke test move `episodes/` para se isolar. Já quase custou episódios
      duas vezes; hoje tem abrigo dentro do repositório e auto-recuperação, mas
      a correção certa é os testes não tocarem em dados reais — um diretório de
      episódios configurável por variável de ambiente resolveria.
- [ ] Polly e Chirp3 seguem sem comparação medida, pendentes no ADR 0001. Não
      bloqueia nada: o Flash v2.5 está validado e barato.

## Próxima execução automática

Segunda 07/09 é **feriado** e não terá episódio. A próxima é **terça, 08/09 às
05:50**, cobrindo de sexta 04/09 a segunda 07/09 — quatro dias numa janela só.

# TODO

Lista curta do que está em cima da mesa. O planejamento de longo prazo vive em
[PROJETO.md](PROJETO.md). Atualizada em 03/10/2026.

## Fim de semana, 03 e 04/10 — antes do episódio de segunda

- [x] **Ensaio completo** (03/10) — episódio de 02/10 refeito numa cópia do
      repositório, só até o roteiro. Passou em tudo que é comportamento: leu
      só o final do índice (uma leitura, 15 mil caracteres) e acrescentou as
      pautas sem estragar o JSON; o backlog ficou só com pautas ativas e a
      conferência não acusou nada; nenhuma empresa sem artigo; roteiro de
      1.224 palavras, sem aviso. Peso no cache lido: índice de 21% para 1%,
      backlog de 11% para 6%. Custo de US$ 4,41 para 3,65. **O custo e a parte
      fixa do contexto estão contaminados:** o ensaio herdou o ambiente desta
      sessão do app, com mais ferramentas no sistema e o Bash liberado, o que
      o launchd não tem. O número limpo sai da produção:
      `memoria_custo.py --desde 2026-10-05`
- [ ] **Ensaios rodam com o ambiente do launchd** — `env -i` com só `HOME` e o
      `PATH` do plist. Vale um `scripts/ensaio.sh` que monta a cópia no estado
      de um dia, limpa o ambiente e desvia registro e estado
- [ ] **Novidade na abertura da semana de 05/10** — o anúncio do Opus 5.5 já
      saiu sozinho: valia de 28/09 a 02/10 em `config/novidades.json`, e
      segunda não tem novidade programada. Decidir se há algo a contar aos
      ouvintes. Candidata, só se o ensaio confirmar: a memória — o agente
      passa a ter à mão tudo o que já foi ao ar, sem buracos

## Fase 3 — abre na semana de 05/10

- [x] ~~Resgatar o crédito de US$ 250 do Claude Code na nuvem~~ — resgatado em
      03/10. Expira às 04:59 (horário de Brasília) de 05/11. **Não vale para
      Projects nem para Routines**, segundo a tela do resgate: só sessões na
      nuvem. Isso muda o plano do piloto — ver abaixo
- [x] ~~Acesso do Claude Code na nuvem ao GitHub~~ — 03/10: Claude GitHub App
      instalado na conta pessoal `campilho`, no modo "Apenas sessões na nuvem",
      com acesso **só ao repositório `campilho/CampsCast`**. A verificação de
      status do repositório no claude.ai passou
- [ ] **Revisar a memória do agente** — medido em 03/10 com
      `scripts/memoria_custo.py`: nos dias do Opus 5.5, a memória é ~42% do
      cache lido (índice 13%, backlog 11%, roteiros 16%, medianas). O índice
      **não é lido inteiro**: passou do limite de 25 mil tokens da ferramenta
      Read, e em quatro de cinco dias o agente viu só o começo, os títulos e o
      fim. Passos, um por vez:
      - [x] **A. Lista compacta no prompt** (03/10) — uma linha por pauta,
            derivada do índice por `scripts/pautas.py` a cada execução, ~11 KB.
            Conferir com `memoria_custo.py --desde 2026-10-05` depois de três
            ou quatro episódios: o peso do índice deve cair, e nenhuma pauta
            pode se repetir
      - [x] **B. Histórico do backlog em arquivo próprio** (03/10) — dos 39 KB,
            28 eram o registro de saídas que o agente mantinha dentro do
            arquivo (~11% do cache lido). Migrado sem perda para
            `saved-items/historico/AAAA-MM.md`; o backlog ficou com 12 KB. Daqui
            em diante, uma linha por item que sai, e `confere_backlog.py`
            registra vencido esquecido ou histórico de volta. O tamanho já era
            gravado no registro (`backlog_bytes`) e agora aparece no
            `registro.py mostra`
      - [ ] **C. Resumos por semana e por mês, e fios em aberto** — desenho no
            PROJETO.md, Fase 3
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

### Formato do episódio

- [ ] **Capítulos no Spotify** — o Spotify Web marca na linha do tempo onde
      cada pauta começa, com um título por trecho. Nunca foi requisito e o
      feed não manda nada para isso: só a lista de pautas na descrição, sem
      marcas de tempo, e nenhuma tag de capítulos. Então é o próprio Spotify
      que gera. Primeiro conferir na documentação do Spotify for Creators de
      onde vêm (geração automática, marcas de tempo na descrição) e se dá para
      controlar. Para a chamada de seguir virar um capítulo próprio, o
      pipeline precisa saber o tempo de cada parte: o caminho natural é narrar
      cada parte do roteiro numa requisição separada, o que dá a duração exata
      de cada uma, e escrever as marcas de tempo na descrição do episódio
- [ ] **Chamada para seguir mais destacada** — no ar, ela sai colada no fim da
      primeira pauta e passa muito rápido. Precisa de pausa maior antes e
      depois. O texto é livre do agente, uma frase; rever a orientação. A
      pausa pode vir do mesmo mecanismo dos capítulos: a chamada narrada
      sozinha, com silêncio montado em volta pelo `tts.py`, que já faz isso no
      começo e no fim do episódio
- [ ] **Rever a ficha técnica do encerramento** — a ideia fica, mas está longa
      (~85 palavras, uns 35 s) e, para quem ouve todo dia, pode estar
      cansativa. Inclui um tema estranho: "cinco delas bloqueadas na leitura"
      diz ao ouvinte o que deu errado. Em vez disso, um relatório para o autor
      das fontes que falham repetidamente — por exemplo, `openai.com` e `x.ai`
      devolvendo 403 —, montado das transcrições, para decidir se o roteiro de
      pesquisa precisa mudar

## Recorrente

- [ ] **Relatório mensal de audiência** — primeiro fim de semana de cada mês, em
      `privado/audiencia.md`: exportação diária do Spotify, tela principal
      (seguidores) e tabela de episódios. O de setembro foi feito em 03/10.
      Junto, a revisão mensal de custos do
      [ADR 0007](docs/decisions/0007-custo-por-episodio.md) e uma olhada no
      Apple Podcasts Connect: aba Análise e relatórios, cujo acesso foi pedido
      em 03/10. Naquele dia mostrava "Assinaturas (0)" e "Programas (0)",
      embora o programa esteja no ar na Apple (a busca pública do iTunes lista
      os 26 episódios)
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

- [ ] (ideia) **Detectar sozinho a troca de modelo ou de voz** e gerar a
      novidade — exige gravar os modelos usados no front-matter
## Operação

- [x] ~~Vigia externo~~ — rotina na nuvem `Vigia do CampsCast (08:07 BRT)`,
      dias úteis, lê `feed.xml` e `estado.json` e avisa por e-mail e push. Não
      depende do Mac, então também cobre o caso de o Mac não ter ligado
- [ ] **Antes da próxima viagem:** `claude setup-token` para um token longo,
      imune à rotação da sessão; Remote Control
      ligado na sessão do app (testado pelo Android S24 em 03/10, funcionou);
      Mac na tomada, tampa aberta
- [ ] **Preencher `NOTIFY_TO`, `SMTP_USER` e `SMTP_PASS`** no `.env`, ou tirar
      as variáveis pela metade. Hoje o `notify.py` cai calado na notificação do
      macOS, que não sai da tela de casa
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
- [ ] **Apple Podcasts: divulgar ou sair** — o foco é o Spotify, onde estão os
      seguidores e para onde o LinkedIn aponta. Pensar se vale divulgar a Apple
      de algum jeito; **se até 03/01/2027 não houver nenhum acesso por lá, tirar
      o programa da Apple**, para não manter um lugar que ninguém usa. Se
      ficar, corrigir a frequência que a Apple mostra ("duas vezes por semana",
      quando sai todo dia útil) e a página Podcasts do Connect, que aparece
      vazia

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
- [x] Ritmo remedido em 03/10 com os 19 episódios da voz nova no
      Multilingual (08/09 a 02/10): **152 ppm**, faixa de 836 a 1.444 palavras,
      alvo 1.216. A contagem de palavras do agente bateu com a do texto, então
      o Bash mínimo para contar palavras deixou de ser necessário
- [x] App Store sem atualização automática (03/10) — o Xcode 27 tinha se
      instalado sozinho em 15/09 e travado o `git` pela licença
- [x] Duração dos episódios sem mudança (decidido em 03/10) — os 26 episódios
      ficaram entre 8:04 e 9:22, média e mediana de 8:50, desvio padrão de 22 s;
      nenhum passou de 9:30. Os 10 minutos são referência, não teto rígido
- [x] Pontualidade — desde 14/09, com o Mac na tomada, os 15 episódios
      começaram às 05:50 e terminaram até 06:11, sem nenhum sono no meio
- [x] Episódios de 25/09 (Opus 5 contra 5.5) e episódio 12 — dispensados de
      escuta dedicada: uma semana de Opus 5.5 no ar e todos os episódios ouvidos
- [x] Pronúncia de "Anthropic" (03/10) — o erro do episódio 25 (3:32, "que
      Anthropic e OpenAI") não se repetiu ao gerar a frase de novo. Ficou a
      regra no prompt: empresa sempre com artigo. Reabrir se voltar a errar;
      o teste com grafias de pronúncia está descrito em `docs/aprendizados.md`
- [x] Smoke test isolado numa cópia temporária do repositório (03/10) — não
      move mais `episodes/` nem escreve no `.env` real, e confere no fim que o
      repositório real ficou intacto
- [x] Polly e Chirp 3 (03/10) — comparação dispensada, adendo no ADR 0001;
      provedor reavaliado só na Fase 4, se for
- [x] Fora da lista em 03/10, foco no Spotify: OP3, downloads por arquivo e a
      pergunta Spotify ou Apple. `gravacoes/descartadas/`, que só tinha um
      `.DS_Store`, foi para a Lixeira
- [x] Episódio 11 conferido no painel do Spotify em 03/10 — aparece
      normalmente; o atraso era só a defasagem do painel
- [x] Registro diário de execução e custo em `metricas/execucoes.jsonl`, vigia
      externo, silêncio no começo e no fim, número do episódio, ficha técnica
      com nomes derivados dos modelos, mapa de pronúncia, voz clonada
      profissional e Apple Podcasts no ar

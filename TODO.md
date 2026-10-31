# TODO

Lista curta do que está em cima da mesa. O planejamento de longo prazo vive em
[PROJETO.md](PROJETO.md); o que já foi feito, no git, nos ADRs e em
[docs/aprendizados.md](docs/aprendizados.md). Atualizada em 31/10/2026.

## Semana de 02/11 — segunda é feriado (Finados)

- [ ] **Até quarta, 04/11 — verificador na nuvem, ensaio do V1.**
      `prompts/verificador-v1.md`, com a rubrica fixa
      `prompts/verificador-rubrica.md`: confere os episódios do 41 em diante e
      calibra a rubrica nos episódios 35 e 38 da linha de base. Ambiente com
      rede aberta, ramo `claude/verificador-v1`, uns US$ 25 a 35 do crédito,
      que expira às 04:59 de quinta, 05/11. Abrir de dia: se o crédito acabar
      no meio, a sessão passa a gastar o limite do Max, que o episódio das 05:00
      também usa. Depois, juntar o ramo e decidir o V1 diário
- [ ] **LinkedIn — post sobre a memória** — rascunho em
      `privado/divulgacao.md`, com a métrica da linha de base (memória do
      programa de 30% para 1,7% de erro). Não saiu em 13, 15, 20 nem 27/10;
      talvez no feriado. Antes de postar, atualizar referências de tempo e
      números. O autor posta à mão
- [ ] **Sexta, 06/11 — conferir no relatório o que mudou em 30/10:** os avisos
      de "IA" dobrada na apresentação e de "assunto curto" sumiram? As páginas
      fechadas caíram (eram 15 a 18% por semana)? Por qual porta foi lida cada
      pauta da OpenAI (fonte, outra porta, arquivo, imprensa)? A faixa nova de
      palavras (alvo 1272, a 159 ppm) manteve os episódios entre 8 e 10 minutos?
- [ ] **Terça, 03/11 — log de pesquisa com "Páginas lidas" e "Escolhas"**
      (passo 8 do prompt, 31/10): toda página ganhou nota? Houve escolha
      registrada? Quanto cresceram o log e a saída do modelo (30/10: 17,6 mil
      caracteres de log, 88 mil tokens de saída)? Rodar
      `python3 scripts/estudio.py` e ver as notas no protótipo
- [ ] **07–08/11 — relatório mensal de audiência de outubro**, com a revisão
      de custos do [ADR 0007](docs/decisions/0007-custo-por-episodio.md) (ver
      Recorrente)

## Fase 3 — onde está

Critério de saída (PROJETO.md): dez dias úteis seguidos sem o Mac ligado,
formulário no ar com as sugestões chegando ao agente, e site novo publicado.
Em 30/10, nenhum dos três começou: outubro foi de memória (ADR 0008), voz
(ADR 0011) e verificação de fatos (ADR 0010).

## Fase 3 — vários agentes

Proposta no [ADR 0010](docs/decisions/0010-redacao-com-varios-agentes.md):
estudar orquestração e aprendizado de agentes com o podcast como banco de
provas. Claude Code headless no Mac, em sombra, uma mudança por vez.

- [ ] **`scripts/ensaio.sh` antes de tudo** — copiar o repositório no estado de
      um dia, rodar com `env -i` e o `PATH` do plist, desviar registro e
      estado. Sem rodar dias passados no ambiente do launchd, não há como dizer
      que um agente melhorou, e o custo de um ensaio fora dele não vale
- [ ] **V1. Verificador diário** — `claude -p` separado depois do agente, com
      a rubrica v1; registra, não bloqueia. Depois do ensaio na nuvem (acima).
      A linha de base custou US$ 3,70 por episódio, quase o dobro do agente:
      medir se dá para conferir menos (só número, data e citação) ou com
      modelo menor
- [ ] **Precisão no roteiro** — os erros da linha de base se repetem em quatro
      formas: datas, contagem, paráfrase que acrescenta, modal mudado. Propor
      uma lista curta de conferência no `master.md`, ou esperar o revisor (V2).
      Depois do resultado do V1
- [ ] **V2. Revisor** com rubrica, em ciclo com o roteiro (no máximo duas
      voltas)
- [ ] **V3. Arquivista** — a memória sai do agente principal; junta com o C2
- [ ] **V4. Pesquisa em paralelo** — subagentes por camada de fontes, e o
      contrato em `runs/AAAA-MM-DD/`
- [ ] **V5. Cadernos de lições por agente** — o agente propõe, o autor aprova
      no relatório de sexta; medir reprovações e voltas antes e depois
- [ ] Fase 4: os mesmos papéis em Managed Agents ou no AgentCore, para
      comparar. Conferir antes se o WebSearch funciona no Bedrock

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

- [ ] **Site, beta 1: o estúdio** — requisitos em [docs/site.md](docs/site.md)
      (v2, 31/10): o site é o estúdio, que muda com o relógio (noite com o
      vigia, café de dia, postos na gravação), replay da gravação em três
      velocidades, balões com origem marcada, ficha de cada personagem com as
      instruções dele e o formulário "Fale com o Editor". Protótipo em
      `site/index.html` com os dados de 30/10 (`scripts/estudio.py`). Feito:
      S1. Elenco aprovado em 31/10 (Arquivista em parte; Checador, Artista e
      Marketing em breve, na ala em obras). Próximo: S2, o visual a partir
      das imagens do autor. Decisões abertas no fim do documento
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
      `privado/audiencia.md`: exportação diária do Spotify, tela principal
      (seguidores) e tabela de episódios, lidas pela extensão Claude in Chrome
      (a exportação vem sem números). Junto, a revisão de custos do ADR 0007 e
      uma olhada no Apple Podcasts Connect (Análise e relatórios). A extensão
      **não** se usa no LinkedIn, cujos termos proíbem automação
- [ ] O painel do Spotify for Creators tem um **"Programa sem título"** vazio,
      e é ele que abre primeiro. Apagar, se não tiver uso

## Operação

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

- [ ] **05/11/2026, 04:59 — o crédito da nuvem expira** (US$ 101 em 25/10).
      Não paga rotinas; paga sessões na nuvem abertas à mão
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

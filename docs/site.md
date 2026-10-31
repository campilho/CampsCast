# Site do CampsCast — o estúdio (beta 1)

- **Status:** requisitos v2 (31/10/2026), no lugar da página de seções de
  04/10. O que valia de lá (formulário, hospedagem, privacidade) continua
  abaixo.
- **Protótipo:** `site/index.html`, com os dados reais de uma gravação gerados
  por `scripts/estudio.py`. Para ver: `python3 scripts/estudio.py` e depois
  `python3 -m http.server 8765 --directory site`. O desenho é provisório: o
  visual definitivo sai das imagens do estúdio que o autor já tem.
- **Endereço:** `campscast.com.br`, hoje respondendo 403 na raiz.

## A ideia

O site é o estúdio. A tela é uma representação do estúdio, e toda interação
de quem visita é uma interação com o estúdio e com os personagens que
trabalham nele. O que aparece depende do relógio de São Paulo: de noite, só o
vigia; de dia, a equipe no café; na hora da gravação, cada um no seu posto,
trabalhando. A qualquer hora, o botão **Replay da gravação** mostra a última
gravação inteira, com o horário em que cada coisa aconteceu.

O que separa este estúdio de uma animação é a regra de fidelidade (abaixo):
o que os personagens dizem saiu do registro da gravação, não da imaginação.

## Os personagens

| Personagem | O que faz | Por trás, hoje | Instruções vêm de |
|---|---|---|---|
| **Produtor** | abre o estúdio às 05:00, confere se o dia tem episódio e qual é a janela, chama cada um na ordem, publica e avisa; volta às 06:00 e 07:00 se a gravação falhou | `run_episode.sh`, um programa sem IA | cabeçalho do `run_episode.sh`, `schedule.py`, `publish.py`, `notify.py` |
| **Jornalista** | percorre as fontes, lê as páginas, faz as buscas, escreve o log de pesquisa — os "N sites" da ficha técnica | Claude (o mesmo agente dos dois seguintes) | passos 4 e 8 do `prompts/master.md` |
| **Editor** | lê a memória (temas, fios, backlog, episódios recentes), escolhe o que vai ao ar, atualiza a memória; recebe as sugestões do formulário | Claude | passos 1, 2, 3, 5 e 7 |
| **Roteirista** | escreve o roteiro na faixa de palavras que cabe na voz | Claude | passos 6 e 9 e "Formato do roteiro" |
| **Locutor** | narra o roteiro com a cópia sintética da voz do autor | ElevenLabs v4, por `tts.py` | `tts.py` e `config/tts.json` |
| **Vigia** | antes do agente, arquiva fios parados; depois do roteiro, confere o que não pode faltar; no fim, publica o estado; às 07:30, confere da nuvem se o episódio está no ar | `expira_fios.py`, `confere_roteiro.py`, `estado.py` e a rotina na nuvem | as docstrings desses scripts |

"Contexto de execução" e "Guardrails", do prompt, valem para os três papéis
do agente e aparecem nos três.

**Sobre a lista do autor (Jornalista, Editor, Roteirista, Locutor e o
zelador como vigia):**

- **Faltava o Produtor.** Sem ele ninguém abre o estúdio às 05:00, e quem
  publicaria seria o vigia, que confere o próprio trabalho. Quem confere não
  é quem faz: é o mesmo princípio do verificador de fatos.
- **O zelador vira o Vigia.** A limpeza que existe é arquivar fios parados
  (`expira_fios.py`), e ela roda de madrugada, antes da equipe chegar, que é
  justamente o turno do vigia.
- **O Verificador de fatos** entra quando o V1 rodar todo dia (ADR 0010).
  Hoje ele roda em lote, na nuvem, sem horário.
- **O Artista** do protótipo 3D fica de fora: a capa é fixa e não existe
  trabalho dele no pipeline.
- **O autor não é personagem.** Aparece como destinatário: o relatório da
  sexta e as sugestões que viram tema.

## O estúdio ao longo do dia

| Quando (São Paulo) | O estúdio | O que se diz |
|---|---|---|
| dia útil, 19:00 às 04:59 | **noite:** salas apagadas, só o vigia na portaria | "tudo quieto", a próxima gravação, o último episódio no ar |
| 05:00 até o episódio sair | **gravando:** cada um no seu posto; quem está trabalhando tem balão; o ON AIR acende quando o Locutor narra | o que está acontecendo (ver "Ao vivo") |
| do fim da gravação às 18:59 | **dia:** a equipe no café, o vigia na portaria; às 07:30 o vigia confere | a conversa do café, montada com os números da gravação |
| sábado, domingo e feriado | **folga:** só o vigia | "hoje é feriado de Finados; a equipe volta terça, 03/11" |
| dia útil, depois das 08:00, sem episódio | **atrasado:** o vigia avisa | o motivo, do `estado.json` |

Se a gravação das 05:00 falhar, a repescagem das 06:00 ou das 07:00 volta o
estúdio para "gravando".

## Replay da gravação

- **Botão no topo, sempre disponível.** Ao clicar, o site passa para "não ao
  vivo": faixa vermelha REPLAY, e a data e o horário reais ("gravado em
  sexta-feira, 30/10, das 05:00 às 05:16").
- **Três velocidades**, medidas na gravação de 30/10 (161 eventos):

  | Velocidade | Como anda | Duração |
  |---|---|---|
  | Tempo real | um segundo por segundo | 16 min 40 s |
  | Acelerado (padrão) | cada balão fica de 1,4 a 4 s; as esperas encolhem | 3 min 53 s |
  | Rápido | de 0,55 a 1,5 s por balão | 1 min 31 s |

  O relógio do replay mostra sempre o horário real de cada evento, e a ordem
  nunca muda. O acelerado encurta as esperas, não os fatos.
- **Linha do tempo** arrastável e **capítulos** para pular: o Produtor abre o
  estúdio, o Editor lê a memória, o Jornalista pesquisa, o Roteirista
  escreve, o Editor atualiza a memória, o Locutor narra, o Produtor publica.

## Balões: a regra de fidelidade

Cada balão diz de onde veio, e o site mostra a diferença:

| Origem | O que é | Como aparece | Exemplo de 30/10 |
|---|---|---|---|
| `agente` | frase escrita pelo próprio agente entre uma ferramenta e outra, literal | itálico, entre aspas | "Terceira pauta definida (Cathedral, do backlog)." |
| `ferramenta` | o que ele fez, lido da transcrição | texto normal | "Lendo mistral.ai/news", "openai.com/news não abriu (403)" |
| `log` | linha do orquestrador | texto normal | "Narrando: 8.058 caracteres em 4 trechos" |
| `sistema` | aviso do próprio Claude Code | texto normal | "O filtro de segurança do modelo interrompeu uma resposta; o agente retomou." |
| `numeros` | conversa do café, montada com os números do dia | com a nota "conversa montada com os números" | "Abri 41 páginas em 31 sites e fiz 31 buscas." |
| `agenda` | o vigia lendo a agenda | texto normal | "A equipe volta terça-feira, 03/11, às 05:00." |

**Não existe balão de pensamento.** O raciocínio interno do modelo não fica
na transcrição: os blocos de pensamento vêm vazios (medido em 30/10, todos).
O mais perto disso são as frases que o agente escreve para si entre uma
ferramenta e outra, e são essas que aparecem em itálico.

Medido em 30/10: dos 165 eventos, 135 vêm de ferramenta, 16 do log, 13 são
frases do agente e 1 do sistema.

## Clicar num personagem

Abre a ficha dele, com três abas:

1. **Hoje:** onde ele está e o que está fazendo agora, e tudo o que fez na
   gravação, com horário. Nos três papéis do agente, a ficha avisa que hoje
   são o mesmo agente, separado pelo que ele estava fazendo.
2. **A aba própria:**

   | Personagem | Aba | O que mostra |
   |---|---|---|
   | Jornalista | Leituras | os números da ficha técnica (do log de pesquisa) e as páginas na ordem em que abriu (da transcrição), com as que não abriram em vermelho; as buscas |
   | Editor | Pautas e memória | as pautas que entraram, com a fonte; as descartadas com o motivo (42 em 30/10); temas com o estado de cada um; fios em aberto; backlog; o botão "mandar um tema" |
   | Roteirista | Roteiro | o roteiro inteiro, com link para o arquivo no GitHub |
   | Locutor | Episódio | o player, a duração, os créditos gastos |
   | Produtor | Etapas | a duração de cada etapa, o custo de modelo, a repescagem |
   | Vigia | Plantão | o estado da última gravação, a conferência do roteiro, as próximas gravações e os dias sem episódio |

3. **Instruções:** o que ele recebe como instrução, tirado dos arquivos do
   projeto (abaixo).

**Integração com o GitHub:** o site não lê o GitHub na hora. O `estudio.py`
copia para o arquivo de dados o que a ficha mostra (lista de leituras,
roteiro, temas, fios) e a ficha leva o link para o arquivo no GitHub. Assim a
página não depende de outro site responder, e o arquivo de dados é o
contrato.

## Instruções por personagem

Hoje é um agente só com um prompt só. O `estudio.py` separa o
`prompts/master.md` por passo e entrega a cada personagem os seus (tabela dos
personagens, acima). Dois cuidados:

- **Passo novo sem dono quebra o teste.** `python3 scripts/estudio.py
  --orfaos` lista passo ou seção do prompt que nenhum personagem mostra, e a
  suíte falha se houver algum. Assim nada some da página em silêncio.
- **A ficha não esconde a costura.** A aba "Quem eu sou" mostra o texto real,
  "Você é o produtor e roteirista do CampsCast", e o "Por trás" diz que os três
  são o mesmo agente.

Quando a redação virar vários agentes (ADR 0010), cada um terá o seu prompt,
e a separação vira leitura direta, sem que o site mude.

## Fale com o Editor (formulário v1)

- **Texto:** "Que assunto de IA você gostaria de ouvir mais vezes no
  CampsCast? O Editor recebe sua mensagem e avalia."
- **Campos:** tema (obrigatório, até 1.000 caracteres), e-mail (opcional, só
  para resposta), concordância com a página de privacidade e um campo isca,
  invisível, contra robôs.
- **O estúdio reage:** no café, o Editor diz "Chegou uma sugestão de tema. Vou
  avaliar."; fora do horário, o vigia guarda para entregar quando a equipe
  chegar.
- **O que "avalia" quer dizer:** o agente recebe só o texto, sem nome nem
  e-mail. A sugestão pode orientar a pesquisa do dia; se for tema novo, entra
  em `memoria/temas-sugeridos.md` com "por ouvinte", e o autor decide, como já
  decide as sugestões do agente. Temas são do autor.
- **Por trás**, porque site estático não recebe envio sozinho:

  ```
  formulário ──► API Gateway (HTTP API) ──► Lambda em Python
                                              ├─ grava a mensagem no S3, num
                                              │  prefixo privado, fora do site
                                              └─ avisa o autor por e-mail
  ```

- **Dados pessoais nunca vão para o git.** O repositório é público; as
  mensagens ficam no S3 privado. Página `/privacidade` por causa da LGPD.

## Celular e computador

- **O estúdio é a página.** No computador: redação larga e cabine em cima;
  café, técnica e portaria embaixo; ao lado, "no estúdio agora" com os
  últimos eventos. No celular: duas colunas, a faixa do replay compacta e
  presa no topo, e a ficha subindo de baixo.
- Nenhuma rolagem para o lado; balão nunca sai da sala.
- Relógio sempre de São Paulo, também para quem visita de fora.
- Sem movimento para quem pede menos movimento no sistema; tema claro e
  escuro.

## Os dados: o contrato `campscast.estudio/1`

`scripts/estudio.py` gera, a cada gravação:

| Arquivo | O que tem | Tamanho em 30/10 |
|---|---|---|
| `estudio/elenco.json` | os personagens, o que faz cada um, o que está por trás e as instruções | 34 KB |
| `estudio/AAAA-MM-DD.json` | a gravação: eventos (`t`, `quem`, `origem`, `texto`, e `url`/`ok` nas leituras), capítulos, episódio com roteiro e pautas, pesquisa (números, leituras, buscas, descartadas), memória do dia, conversa do café, agenda | 76 KB |
| `estudio/ultimo.json` | cópia da gravação mais recente | 76 KB |

- **De onde vem:** a transcrição do agente (a mesma que o
  `research_trail.py` lê), `logs/AAAA-MM-DD.log`, o registro em
  `metricas/execucoes.jsonl`, o roteiro, o log de pesquisa, `memoria/`, o
  backlog e `config/schedule.json`.
- **O que não sai:** caminho da máquina (o script corta, e um teste
  confere), comando de terminal, o pedido que o agente fez a cada leitura,
  nada de `privado/`.
- **O que sai e ainda não era público:** o texto das buscas. As leituras já
  estão no log de pesquisa; as buscas só aparecem lá como contagem.
- **O CampsVerso lê o mesmo contrato.** Quando o estúdio 3D ficar pronto, ele
  troca o desenho e não os dados. Se lá os eventos seguirem outro envelope, o
  adaptador fica do lado de lá.

## Ao vivo

- **No beta,** na hora da gravação o site só sabe que está gravando: põe a
  equipe nos postos, sem balão de evento, e o replay sai junto com o
  episódio.
- **Depois (S6),** durante a gravação um `estudio/ao-vivo.json` sobe a cada
  30 segundos com os eventos até ali; o `watch_agent.py` já acompanha a
  transcrição enquanto ela é escrita. São uns 35 envios por gravação, e o
  envio nunca derruba o pipeline, como o `estado.py`.
- O ao vivo de verdade dura uns 15 minutos por dia, às 05:00 (13 e 17 nas
  gravações de 29 e 30/10). Quase todo mundo vai ver o replay, e por isso ele
  vem primeiro.

## O resto da página

Abaixo do estúdio, enxuto, o que vinha da estrutura de 04/10: último
episódio com player e Spotify; números da semana; últimos episódios; para
quem é técnico (GitHub, ADRs, aprendizados); rodapé com contato e licenças. O
"como funciona" passa a ser contado pelo próprio estúdio. A linha do tempo da
história pode virar quadro na parede.

- **Hospedagem:** o S3 e o CloudFront de hoje; falta o `index.html` como
  objeto padrão da raiz, que é o motivo do 403.
- **Atualização sem trabalho:** o `publish.py` passa a rodar o `estudio.py`
  e a subir a página e os dados junto com o feed.
- **Sem dependências, sem cookies, sem rastreamento.** A audiência continua
  medida no Spotify.

## Etapas

| Etapa | O quê |
|---|---|
| S1 | Requisitos e protótipo com dados reais — feito em 31/10 |
| S2 | Visual do estúdio a partir das imagens do autor, em celular e computador |
| S3 | `publish.py` gera e sobe página e dados; raiz do CloudFront; site no ar com replay e fichas |
| S4 | Formulário: API Gateway, Lambda, S3 privado, aviso ao autor; página de privacidade |
| S5 | Sugestões chegando ao Editor, sem dados pessoais |
| S6 | Ao vivo por evento, com `ao-vivo.json` durante a gravação |

S1 a S3 são o beta 1. S4 e S5 completam o critério de saída da Fase 3:
"formulário no ar, com as sugestões chegando ao agente".

## Para decidir

1. **Elenco:** Produtor como sexto personagem e Vigia no lugar do zelador?
2. **Buscas à vista:** mostrar o texto das buscas, hoje inédito?
3. **Custo:** mostrar o custo de modelo da gravação (US$ 6,37 em 30/10) na
   ficha do Produtor?
4. **Fim de semana:** estúdio vazio com o vigia, como no protótipo, ou equipe
   no café?
5. **Beta com a maquete do protótipo,** ou esperar o visual final?

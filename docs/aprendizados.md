# Aprendizados

Achados não óbvios deste projeto. Quase todos vieram de uma suposição razoável
que a medição derrubou — e vários custariam horas a quem repetisse o caminho.

Decisões formais ficam nos [ADRs](decisions/). Aqui está o que não cabe em
decisão: o que quebrou, por quê, e o que ficou de método.

---

## Método

### Medir vale mais que supor, e o oposto quase nunca é verdade

Contagem informal deste projeto: **oito** hipóteses plausíveis derrubadas por
medição, **zero** confirmadas sem ela. Entre as que caíram:

- "A ElevenLabs normaliza cada requisição, daí os degraus de volume." Era queda
  de nível dentro da geração.
- "Então peça o episódio inteiro numa requisição." Ficou pior.
- "O ruído de fundo está alto." Era a pausa entre palavras.
- "Mudei de posição na cama, deve ser isso." Era a TV do cômodo ao lado.

### Uma medição que compartilha suposições com o código medido não é verificação

O bug que truncava os episódios em 30% ([ADR 0003](decisions/0003-costura-de-mp3.md))
sobreviveu porque o parser de duração e o gerador eram ambos nossos, concordavam
entre si, e estavam ambos olhando para a coisa errada. Só uma ferramenta
independente — o `afinfo` do macOS, que enxerga como um player — revelou.

Ao validar algo próprio, procure um verificador que não compartilhe a
implementação.

### Erro de configuração deve falhar no teste, não em produção

Cada bug corrigido ganhou um teste antes da correção. O `smoke_test.sh` tem 93,
roda offline e sem custo. Vários deles existem porque algo passou despercebido
uma vez.

---

### dBFS não atravessa aparelhos

Comparar o piso de ruído de dois aparelhos em dBFS é comparar nada: a escala é
relativa ao fundo de escala de cada um, e ganhos de entrada diferentes deslocam
o número inteiro. O MacBook mediu o mesmo quarto 5,3 dB "mais silencioso" que o
iPhone; não porque grave melhor, mas porque amplifica menos.

O que é comparável:

- **o mesmo aparelho em cômodos diferentes** — o ganho sai da conta
- **a relação sinal/ruído**, que é uma razão e cancela o ganho
- **a forma do espectro**, em porcentagem da energia
- **picos tonais**, cuja frequência não depende do ganho

Para saber se dois arquivos são do mesmo ambiente, correlacione os envelopes de
nível de tomadas simultâneas: r ≥ 0,8 confirma. Se o desvio entre aparelhos
mudar de um cômodo para outro (foi de +5,3 para +11,4 dB), há uma fonte local
em um deles, e vale procurar no espectro.

O erro estava também dentro da nossa ferramenta. O `check_recording.py` procurava
silêncio com limiar fixo de −50 dBFS, e no mesmo minuto gravado ao mesmo tempo
achou 4 s de silêncio no MacBook e **0 s no iPhone** — não porque o iPhone
tivesse menos silêncio, mas porque amplifica 5 dB a mais. O limiar passou a ser
ancorado na distribuição do próprio arquivo, e os dois passaram a acusar os 20 s
que de fato foram gravados. Ver [teste que reproduz](../tests/smoke_test.sh),
seção 12.

Corolário desagradável: **o aparelho que menos amplifica é o que menos enxerga o
problema.** O tom da adega estava 32 dB acima do piso local no iPhone e apenas
25 dB no MacBook; no ruído total do cômodo, desligar a adega melhorou 9,4 dB no
iPhone e 0,9 dB no MacBook. Diagnosticar sala com o aparelho de ganho baixo dá
falso "está tudo bem".

**Silêncio puro não escolhe aparelho.** Ele mede o piso, e o que decide é a
relação sinal/ruído com voz na distância real. Para comparar microfones é
preciso gravar a mesma fala, na mesma distância, ao mesmo tempo.

## Agentes

### Duas execuções do mesmo dia escolhem pautas diferentes

Em 02/11, quatro ensaios (`scripts/ensaio.sh`) refizeram 29/10 com o mesmo
estado, em sequência: três com o código de 02/11 e um com o código que rodou
em 29/10 (`--codigo` no commit `43f841f`):

| | manchete | vaga 2 | vaga 3 | turnos | US$ | buscas | páginas |
|---|---|---|---|---|---|---|---|
| ao ar, 29/10 | Gemini 4 Carbon | carta dos democratas da Câmara | Cohere e o Qwen (backlog) | 110 | 4,62 | 18 | 36 |
| ensaio 1 | Gemini 4 Carbon | bancos do Canadá | Octoverse do GitHub | 84 | 3,78 | 14 | 31 |
| ensaio 2 | Gemini 4 Carbon | Octoverse do GitHub | Cohere e o Qwen | 81 | 3,66 | 9 | 26 |
| ensaio 3 | Gemini 4 Carbon | lei de Nova York sobre chatbots de companhia | Cohere e o Qwen | 87 | 3,80 | 13 | 29 |
| ensaio 4, código de 29/10 | Gemini 4 Carbon | trimestre do Alphabet e da Microsoft | Octoverse do GitHub | 91 | 4,11 | 18 | 30 |

A manchete se repetiu nas cinco execuções. Nas outras dez vagas apareceram
seis pautas diferentes: a da Cohere em três, o Octoverse em três, e quatro
que só saíram uma vez. Todas justificadas no log, todas dentro da janela: em
dia com várias pautas boas, a segunda e a terceira vaga são quase um sorteio
entre elas.

Já o custo quase não varia com o mesmo código: US$ 3,66 a 3,80, 81 a 87
turnos, 9,3 a 9,8 minutos. A execução que foi ao ar fica uns 20% acima, e o
ensaio com o código de 29/10 explica metade disso: ele fez as mesmas 18
buscas e avaliou as mesmas 31 pautas que a produção, contra 9 a 14 buscas e
24 a 29 pautas com o código novo. Os três commits no prompt depois de 29/10
(um deles mandando ler a OpenAI pelo feed, outro mandando ler fonte fechada
por outra porta da própria fonte) cortaram buscas e uns 10% do custo. O resto
é a web de quatro dias depois e o acaso de uma execução.

Consequência para avaliar variantes do agente: **custo e turnos dá para
comparar com poucas execuções, porque variam uns 3%; escolha de pautas, não**
— "escolheu as mesmas pautas" mede sorte. A comparação de qualidade precisa
de uma rubrica, como a do verificador, e de mais de uma execução por lado.

### A memória precisa de duas camadas

`covered-index.json` é a longa: título, fonte e resumo de tudo que já foi ao ar,
para sempre. Os 5 roteiros recentes são a curta: texto integral, para o agente
saber **como** algo foi dito, não só que foi.

A conexão entre episódios ("na segunda a gente falou do corte de preço; hoje
veio a resposta") emergiu sozinha da instrução de não repetir pauta. Depois
virou diretriz explícita.

### Dado calculado é melhor que dado lembrado

Janela de notícias, faixa de palavras, nome do sintetizador — tudo chega ao
agente por variável de ambiente, calculado por script. Ele não recalcula nem
lembra. Trocar de voz muda o texto falado sem ninguém editar o prompt.

### Peça o número, mas ancore na fonte

A ficha técnica no fim do episódio cita páginas lidas e pautas avaliadas. O
prompt manda contar do `research/` que o agente acabou de escrever, não estimar
de memória. Sem isso ele arredondava: disse "vinte páginas" onde o rastro
mostrava 22.

### A memória que o agente "lê inteira" parou de caber, e ninguém viu

O prompt mandava ler o `covered-index.json` inteiro. A ferramenta Read do
Claude Code recusa mais de 25 mil tokens por chamada, e o índice passou disso
em setembro: cada pauta foi de ~750 bytes em agosto para 3 a 5 KB, quase tudo
resumo (54%) e notas (34%). As transcrições de 22/09 a 02/10 mostram o que
aconteceu:

- o Opus 5 lia em quatro ou cinco pedaços, com tentativas recusadas no meio
  ("File content exceeds maximum allowed tokens");
- a partir de 25/09, e em quatro dos cinco primeiros dias do Opus 5.5, o agente
  leu só o começo, um Grep dos títulos e o fim. O meio do período ficava fora
  da memória. O TODO registrava o contrário — "o Opus 5.5 lê tudo" —, a partir
  de um dia só.

Nada quebrou de forma visível, e a integridade se manteve: o agente só
acrescenta com Edit, e o índice nunca perdeu uma pauta no git. Mas o custo
também era escondido. Um trecho lido no começo é relido em todas as chamadas
seguintes, então pesa o tamanho vezes as chamadas que vêm depois — em 29/09,
único dia de leitura inteira, o índice sozinho foi 47% do cache lido. O
`memoria_custo.py` faz essa conta a partir das transcrições.

A correção separou as duas memórias que o projeto já tinha discutido: para não
repetir pauta bastam data, título e fonte. Essa lista é derivada do índice a
cada execução, ~11 KB para 78 pautas, e vai escrita no prompt, como os
parâmetros, para chegar inteira sem depender de o agente ler. O detalhe fica
no índice, consultado por busca.

**Instrução que manda ler um arquivo que cresce é um limite com data marcada.**
E "o agente lê X" é afirmação sobre a transcrição, não sobre o prompt.

O mesmo levantamento achou o backlog com 39 KB, dos quais só ~10 são pautas
ativas: o resto é o registro dos itens podados, que o agente mantém dentro do
próprio arquivo e relê todo dia. Foi para `saved-items/historico/`, um arquivo
por mês, e o `confere_backlog.py` avisa se voltar.

### Ensaio disparado de dentro de outra sessão não é o ambiente de produção

O ensaio da memória nova (03/10) foi disparado de dentro de uma sessão do
Claude Code no app, e o `claude -p` herdou as variáveis dela —
`CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`, ferramentas de terminal, outra URL de
API. O launchd passa só o `PATH`. Dois efeitos medidos: a primeira chamada ao
modelo foi de 45 mil tokens contra 27 mil na produção do mesmo dia, dos quais
a mudança testada explicava uns 5 mil; e o Bash, sempre negado em produção,
funcionou — o agente listou diretórios e leu arquivos que não leria.

O comportamento que se queria ver ficou válido; o custo, não. **Ensaio que
mede custo precisa do ambiente de produção, não só do código de produção:**
`env -i` com o que o plist define.

Em 18/10 a mesma herança derrubou um teste: o app passou a exportar
`CLAUDE_EFFORT=xhigh` nas sessões, que é também o nome da variável com que o
orquestrador escolhe o esforço do agente. Rodado de dentro de uma sessão, o
`run_episode.sh` iria a `xhigh` em vez de `high`, sem aviso. A produção não
sente (o launchd só passa o `PATH`); a suíte agora limpa `CLAUDE_EFFORT` e
`CLAUDE_MODEL` antes de começar.

### Instalar uma ferramenta para você é instalar para o agente de produção

O agente do podcast é um `claude -p` que roda no Mac do autor, e herda a
configuração de usuário do Claude Code: skills em `~/.claude/skills` e
servidores MCP em `~/.claude.json`. Em 04/10, configurando a AWS para as
sessões de desenvolvimento, o assistente da AWS CLI instalou 24 skills e um
servidor MCP da AWS para o Mac inteiro. Ninguém pediu isso para o podcast, mas
na madrugada seguinte o agente de produção teria tudo à mão.

Pego antes de ir ao ar porque a instalação foi lida linha por linha. O
orquestrador passou a chamar o agente com `--strict-mcp-config` (só os
servidores declarados, e não há nenhum) e `--disable-slash-commands` (nenhuma
skill). Conferido com o CLI de verdade, no ambiente do launchd, e não só pelos
argumentos: a lista de skills sumiu, e a primeira chamada caiu de 27,1 mil
para 23,7 mil tokens — o agente carregava skills que nunca usou.

**O ambiente do agente de produção é configuração, não acaso:** declare o que
ele recebe, em vez de herdar o que o dono da máquina instalou por último.

### O agente conta palavras sem ferramenta, e conta certo

Ele não tem Bash, então não roda `wc -w`; as transcrições mostram a tentativa
negada todo dia. A suspeita era que o `words` do front-matter fosse estimativa,
e ele alimenta a calibração de ritmo. Em 03/10, contando o corpo dos 19
roteiros da voz nova, 14 batem exatamente e nos outros 5 o desvio é de 1 a 3
palavras.
Liberar um Bash mínimo só para contar deixou de ter motivo. Vale para este
modelo e este tamanho de texto; trocar de modelo pede conferir de novo.

### Deixe o agente registrar o descarte

`research/AAAA-MM-DD.md` lista o que entrou **e o que foi descartado, com
motivo**. O `research_trail.py` reconstrói o rastro bruto das transcrições do
CLI. Um é relato, o outro é registro de máquina — se divergirem, dá para saber.

---

## Áudio

### Concatenar MP3 cru trunca o episódio

Cada resposta da API é um arquivo completo, com cabeçalho `Xing`/`Info` que
declara a duração. Emendados, o player lê o primeiro e para ali. Oito minutos
tocavam dois. Ver [ADR 0003](decisions/0003-costura-de-mp3.md).

### Modelo bom pode ter defeito que o modelo simples não tem

O `eleven_multilingual_v2` perde nível ao longo de cada geração — 2,6 dB em
2.100 caracteres, criando dente de serra nas costuras. O `flash_v2_5` é plano
(0,29 dB), mais alto, mais rápido e metade do preço. Ver
[ADR 0004](decisions/0004-volume-entre-trechos.md).

### Erro de pronúncia não se reproduz sob encomenda

No episódio 25, "que Anthropic e OpenAI já usam" saiu com a tônica no fim, e
"a Anthropic disse", dois minutos depois, saiu certo. Para achar a frase no
áudio, as emendas entre trechos da narração servem de régua: cada resposta da
ElevenLabs começa com alguns milissegundos de silêncio digital, amostras
exatamente em zero, que a fala natural nunca produz. Com as três emendas
achadas, a posição de cada palavra dentro do próprio trecho deu o tempo com
um ou dois segundos de erro.

Gerada de novo, sozinha e duas vezes, a frase errada saiu certa. A síntese
não é determinística, e o erro depende também do contexto que a requisição
leva. Nos roteiros, 104 de 107 ocorrências têm artigo, e a única sem artigo
desde a voz nova era a errada; o autor lembra de outros erros, então o artigo
não explica tudo. Ficou a regra mais barata — empresa sempre com artigo, que
já é o português natural — e o `config/pronuncia.json` vazio. Se voltar a
errar, a grafia de pronúncia já tem teste gravado para comparar.

Voltou a errar, e na maior parte dos dias (semana de 05/10). O teste de 10/10
mudou o desenho: em vez de uma frase isolada, **as mesmas dez frases reais da
semana**, seguidas, para cada grafia. Assim o erro apareceu: com a grafia
original, uma certa em dez; "Antrópic", nove; "Antrópik" e "Anthrópic", dez.
Frase solta saía certa porque faltava o contexto que provoca o erro. Ficou
"Anthrópic" no `pronuncia.json`, com teste que impede a troca de sumir. No mesmo
áudio, "Gemini" saiu uma vez como "Geminí", em quatro.

No Eleven v4, a lição se repetiu com "IA". A grafia "I.A." acertou dez em dez
no teste de 20/10 e errou no primeiro episódio no ar (26/10), justo na frase
fixa "Eu sou um agente de I.A.". Teste de pronúncia aprova uma grafia, mas não
garante o roteiro: o contexto muda a leitura. Provisório desde 27/10, o áudio
diz "inteligência artificial" por extenso, que não depende de leitura de sigla.

### Contador de cota é assíncrono

A ElevenLabs marcou 7 créditos logo após uma síntese cujo custo real eram 2.074.
Ler cedo demais gera conclusão errada sobre custo. O `tts.py` espera três
leituras iguais antes de reportar.

### Ritmo de fala pertence à voz E ao modelo

Mesma voz: 163 palavras/minuto no Flash, 155 no Multilingual. Vozes diferentes:
125 e 163. A faixa de palavras do roteiro sai daí, então trocar qualquer um dos
dois exige remedir.

Um erro de digitação meu numa contagem de palavras (1466 onde eram 1364) inflou
o ritmo em 7% e fez o teto autorizar roteiros de 10,1 minutos, acima do limite
do formato. Por isso a calibração virou script, não número digitado.

---

## Clonagem de voz

### O ruído só é mensurável se houver silêncio

Medir o "piso de ruído" pelos trechos mais quietos de uma fala contínua mede
pausas entre palavras — com respiração e cauda de reverberação —, não a sala.
Uma gravação boa foi reprovada assim.

O `check_recording.py` agora só calcula o piso a partir de silêncio
**sustentado**: 2 segundos consecutivos abaixo de −50 dBFS. O parâmetro foi
calibrado comparando duas gravações reais — a de fala contínua não tinha
nenhum trecho, a que começou com 20 segundos parado tinha dois, somando 19,8s.

**Grave 10 segundos de silêncio no início de cada bloco.**

### Grave atravessa parede; agudo não

Um quarto que media −66 dBFS passou a medir −50, com 76% da energia abaixo de
120 Hz. Não era a rua nem a posição: era a TV do cômodo ao lado, com a porta
fechada. Só o grave passa, e é justamente ele que polui a medição — por isso o
morador não escuta e o microfone pega.

Máquina faz ruído constante (desvio abaixo de 1,5 dB); conteúdo flutua. O modo
`--sala` usa isso para nomear a fonte provável.

### Compressão com perdas melhora a medição sem melhorar a gravação

O encoder descarta o que é baixo demais para o ouvido — que é justamente o
ruído de fundo. Mesmo quarto, um minuto de diferença: o arquivo AAC mediu
−70,8 dBFS e 48 dB de relação sinal/ruído; o sem perdas, −66,3 e 43. O segundo
é o bom: mostra o ruído que existe e entrega o detalhe completo.

### A ElevenLabs não decodifica ALAC

O Gravador do iPhone em "Sem perdas" grava ALAC dentro de `.m4a`. O upload
recusa com *"At least 30s of audio is required"* num arquivo de 59,7 segundos,
sem mencionar formato. O arquivo em qualidade normal sobe, porque é AAC — o que
sugere a conclusão errada de que gravar sem perdas é o problema.

`prep_voice_samples.py` converte para WAV mono 44,1 kHz. Verificado que a
conversão preserva as medições exatamente.

### Distância domina sobre qualidade do microfone

Mesma sala, mesma pessoa, mesmo minuto: iPhone a ~20 cm mediu **−23,6 dBFS** de
fala e 38 dB de relação sinal/ruído; microfone do MacBook, sentado à frente,
mediu **−38,9 dBFS** e 17 dB.

Quinze decibéis de diferença. Pela lei do inverso do quadrado, cada dobra de
distância custa 6 dB — quinze equivalem a estar cerca de cinco vezes mais
longe, o que bate com um metro contra vinte centímetros.

O microfone do MacBook Pro é bom; o problema é onde ele fica. Nenhuma melhora
de codec compensa: gravar sem perdas mantém o nível da fala e ainda faz o piso
de ruído medido **subir**, porque o encoder deixa de limpar o silêncio. A
relação sinal/ruído pioraria.

Antes de comprar microfone melhor, chegue mais perto do que você tem.

### Fone Bluetooth é pior que o microfone do notebook

Perfil de headset comprime a banda e aplica supressão de ruído e ganho
automático. O modelo aprenderia os artefatos junto com a voz. iPhone no app
Gravador supera qualquer AirPods para esta finalidade.

### Consistência importa mais que perfeição

Blocos gravados em condições diferentes ensinam ao modelo uma variação que não
existe na voz. Se a sala não puder melhorar, é melhor gravar tudo na condição
pior do que misturar as duas. Vale também para processamento: ou todos os
arquivos passam pela redução de ruído da ElevenLabs, ou nenhum.

---

### Um tom fixo é pior que um ronco mais alto

O motor de uma adega do outro lado da sala produziu um tom em **239,56 Hz** —
4× a frequência da rede elétrica brasileira, assinatura de motor de indução.
A mesma frequência exata apareceu nos quatro arquivos gravados no apartamento,
inclusive no quarto com a porta fechada, 10 dB mais fraca através da parede.
Inaudível para quem mora ali; medível com folga.

Um tom é pior que ronco de trânsito, mesmo sendo mais fraco: é fixo, afinado e
cai dentro da banda da voz, então o modelo o aprende como se fosse timbre e
depois não há filtro que o tire sem levar a voz junto. Ronco de rua é largo e
variável, e o modelo tende a tratá-lo como fundo.

Confirmado desligando a adega na tomada: o tom caiu 38,8 dB no iPhone e 26,2 dB
no MacBook, sumindo abaixo do piso nos dois, e a sala virou o cômodo mais
silencioso da casa.

Para distinguir motor de ruído ambiente, procure **série harmônica**: motor na
rede aparece em múltiplos de 60 Hz. E para saber se o tom é acústico ou
interferência elétrica no aparelho, meça em dois cômodos — interferência não
muda de nível com a distância.

Isso muda o critério de escolha da sala. Não é qual mede mais baixo, é **qual
defeito se conserta**. Um motor se desliga na tomada; uma fresta de ventilação
para a rua, não.

### O clone aprende a sala, e o piso de ruído prova

Um clone Professional treinado com 15 minutos gravados no quarto com a TV
ligada na sala, comparado ao clone Instant anterior feito de material mais
curto e mais limpo:

| | Piso de ruído | Reverberação |
|---|---|---|
| Clone Instant | **−90,4 dBFS** | 0,42 s |
| Clone Professional | **−52,2 dBFS** | 0,64 s |

**Trinta e oito decibéis piores**, com mais material de treino. O modelo **gera
ruído de fundo nas pausas entre frases**: o Instant entrega silêncio quase
digital, o Professional entrega o quarto.

Medir isso exigiu corrigir a ferramenta. O piso pedia 2 s de silêncio contínuo,
regra certa para gravação humana e errada para voz sintética, que não faz pausa
tão longa — a janela de 2 s engolia fala e devolvia −77,6 e −51,6, achatando a
diferença para 26 dB. Com `--sintetico` (0,5 s, a pausa real entre frases) a
distância verdadeira aparece. **Toda métrica traz junto uma suposição sobre o
sinal; quando o sinal muda de natureza, a suposição precisa mudar com ele.**

O espectro confirma por outro caminho:

| | sub | grave | médio-grave | médio |
|---|---|---|---|---|
| Clone Instant | 0% | 4% | 22% | 69% |
| Clone Professional | 11% | 22% | 27% | 39% |
| O quarto com a TV ligada | 57% | 31% | 9% | 2% |

O clone novo deslocou energia para as bandas graves, na direção do perfil do
cômodo. Aprendeu o ambiente junto com a voz, e a reverberação subiu junto.

**Mais material não compensa material pior.** E isso dá um critério objetivo de
aceitação para o próximo clone: medir o piso de ruído do áudio gerado e comparar
com o do clone anterior, em vez de decidir de ouvido.

### O experimento justo pode destruir a gravação

Para comparar dois microfones é preciso colocá-los à mesma distância. Foi feito,
e funcionou: o desvio no nível da fala (+5,5 dB) bateu com o desvio de ganho
medido antes só com silêncio (+5,3 dB), provando que as posições estavam iguais,
e os aparelhos empataram em 1,8 dB de S/R.

Só que igualar a distância significou afastar o celular de 20 para ~40 cm, e o
material saiu com **21 dB a menos de relação sinal/ruído** e o eco subindo de
0,48 para 0,73 s. Inaproveitável para clonagem.

**Comparação e produção pedem posições diferentes.** Resolva a comparação num
teste dedicado, aceite que o material dele é descartável, e grave a sério de
perto. Não tente extrair as duas respostas da mesma tomada.

### Codec se lê no nome, não no bitrate

O tipo de codificação era adivinhado por um corte de 400 kbps. ALAC mono de 16
bits comprime silêncio tão bem que sai a 176 kbps, e a gravação sem perdas do
MacBook foi rotulada "com perdas" — o que, pela nossa própria regra de nunca
comparar codecs diferentes, teria invalidado a comparação inteira.

O nome do codec está no `afinfo`, em `Data format`. Adivinhar grandeza derivada
quando o dado exato está disponível é sempre troca ruim.

O nome, porém, não é sempre um nome de codec: para PCM em WAV o `afinfo` só
diz o tipo da amostra, "Int16" ou "Float32". Em 18/10 a gravação do MV7+, em
WAV Float32, saiu "com perdas" — e qualquer WAV de 16 bits sairia igual. A
lista agora reconhece esses tipos, com teste.

### Silêncio digital não é sala

A primeira tomada com o Shure MV7+ (18/10, ganho manual de +20,5 dB, removedor
de ruído desligado) mediu ruído de −120 dBFS e relação sinal/ruído de 95 dB.
Nenhum microfone entrega isso: nos dez segundos de silêncio, de 50% a 88% das
amostras eram **exatamente zero**. Algum processamento fechava o sinal quando
não havia voz — um gate — e o `check_recording.py` mediu o gate, não o quarto.
Ele também encurta a cauda do som, então a reverberação medida sai baixa demais.

Não era o microfone nem o MOTIV: era o **Isolamento de Voz do macOS**, o modo de
microfone da Central de Controle, que vale por aplicativo e estava ligado para
o MOTIV Mix. De volta ao "Padrão", a mesma configuração mediu silêncio de
−79 dBFS, sem um zero, e relação sinal/ruído de 54 dB — o número de verdade.
**Antes de gravar para clonagem, conferir o modo de microfone na barra do Mac.**

Piso abaixo de −96 dBFS em gravação de microfone é sinal de processamento, não
de sala silenciosa. O removedor de ruído do próprio MV7+ mostra o mesmo: com
ele ligado, o silêncio foi a −104 dBFS — e a voz perdeu médios (de 26% para
18% da energia), o que o clone aprenderia junto.

## Infraestrutura

### Na nuvem, a rede padrão não enxerga as fontes

A primeira rodada do verificador (25/10), numa sessão do Claude Code na nuvem,
gastou US$ 102 do crédito e deixou 54% das afirmações sem conferir: o ambiente
só abria `anthropic.com`, `claude.com`, `github.com`,
`raw.githubusercontent.com`, `pypi.org` e `blog.modelcontextprotocol.io`. Os
outros 151 domínios deram `ENOTFOUND` — openai.com, Google, NVIDIA, imprensa,
governo. A sessão percebeu, registrou e seguiu; o resumo saiu honesto, mas meio
cego. É o mesmo bloqueio que barrou o `curl` do vigia em setembro, agora pelo
WebFetch também.

Para pesquisa, o ambiente na nuvem precisa de rede aberta antes da primeira
execução. **Testar uma página de fora antes de gastar:** a segunda rodada
começa abrindo uma página de `openai.com` e para se não abrir.

### O `robots.txt` da OpenAI libera; a portaria barra

De 30/09 a 30/10, `openai.com` deu 403 em 33 de 33 leituras do agente. Um
pedido comum, sem se passar por navegador, mostra o porquê (30/10):
`server: cloudflare` e `cf-mitigated: challenge`. O Cloudflare manda um desafio
que só um navegador rodando JavaScript passa. Já o `robots.txt` da OpenAI diz
`User-agent: *` e `Allow: /`. Placa e portaria discordam: a placa é voluntária,
e a portaria julga cada visita pelo comportamento.

O agente não se esconde. O WebFetch se identifica como `Claude-User
(claude-code/2.1.309; +https://support.anthropic.com/)`, o robô que a Anthropic
documenta para leitura pedida por um usuário.

E não é a OpenAI inteira. Nas mesmas transcrições, `alignment.openai.com` abriu
30 de 30, `community.openai.com` 23 de 23, `developers.openai.com` e
`model-spec.openai.com` tudo; `openai.com` e `help.openai.com`, nada. O feed
`openai.com/news/rss.xml` abre, mas só com título, data, link e uma linha de
resumo. Um mês fechado, sempre com o mesmo cabeçalho, e subdomínios abertos:
é configuração do site, não falha intermitente do Cloudflare.

Fingir ser navegador para passar, não: é decisão do site, e o classificador
de segurança desta máquina barrou até o teste. O custo editorial é real:
`anthropic.com` abriu 106 de 108 leituras, o site da OpenAI 0 de 33. Uma é lida
na fonte e a outra de segunda mão, e a facilidade de acesso pode puxar a pauta.

**Fonte fechada se procura por outra porta da própria fonte antes de ir à
cobertura.** Cobertura é água já filtrada, com opinião dentro.


### macOS bloqueia launchd em `~/Documents`

Agente do launchd não acessa `~/Documents`, `~/Desktop` nem `~/Downloads`
(TCC). O erro é `Operation not permitted`, rc=126, sem mencionar permissão — e
a execução pelo Terminal continua funcionando, porque o Terminal já tem acesso.
Só falha de madrugada. O projeto mora em `~/CampsCast` por isso.

### launchd não herda o PATH do shell

O plist declara onde estão `claude` e `python3`. Gerado por
`install_launchd.sh` com os caminhos reais da máquina, porque caminho editado à
mão é erro que só aparece às 5h50.

### Cache negativo de DNS dura 24 horas

O SOA de uma zona nova traz TTL negativo de 86400. Quem consultou o nome antes
do registro existir guarda "não existe" por um dia — e quem está configurando é
justamente quem mais consultou antes. O domínio funciona para o mundo e não
para você. Daí o `--resolve` do `set_base_url.py`.

### Função do CloudFront salva não está no ar, e publicada também não

Três passos, e só o último muda alguma coisa: salvar o código (estágio de
desenvolvimento), **publicar** (copia para o estágio LIVE) e **associar** a
uma distribuição, num comportamento e num evento (*Viewer request*). Depois
da associação, a distribuição leva uns cinco minutos em "Deploying" (medido
em 02/11: 330 s). Antes disso a resposta vem direto do S3, com
`server: AmazonS3`, e é o jeito de saber que a função ainda não está no
caminho. No mesmo dia, a raiz dava 403 com o `index.html` no bucket: o
"Default root object" que o roteiro de configuração mandava preencher não
estava preenchido.

### O site leu um ensaio como gravação, e um endereço como empresa

No primeiro dia no ar (03/11), o estúdio tinha dois números falsos, os dois de
ler texto em vez de estrutura:
- **Uma gravação inteira às 16:38 que nunca houve.** Um `--dry-run` de 02/11
  com a data de 03/11 escreveu no `logs/2026-11-03.log`, antes da gravação de
  verdade, e o `estudio.py` lia o log inteiro. Agora cada execução começa no
  cabeçalho, e a que se declara DRY-RUN fica de fora.
- **"5 portas da OpenAI" com 2.** As consultas ao archive.org levam
  `openai.com` no `?url=`, e a conta procurava o texto no endereço inteiro.
  Agora conta pelo site que respondeu.

Os dois passaram pelos testes porque nenhum fixture tinha dry-run no log nem
arquivo público no meio das leituras. Achados olhando o que o site mostrou.

### O agente passou a ler por subagente, e as medições ficaram cegas

Em 05/11 o WebFetch sumiu das ferramentas do agente e entrou, no lugar, um
subagente "web-fetch" do Claude Code, no mesmo Opus 5.5. Nada mudou do nosso
lado: o CLI era o 2.1.283 de 03 a 06/11. O agente se adaptou sozinho, mandando
de 10 a 11 subagentes por dia, cada um com uma lista de endereços e o pedido de
código HTTP, data e números.
- **As medições não viram.** As leituras ficam em
  `<sessao>/subagents/agent-*.jsonl`, e o registro, o relatório, o estúdio, o
  rastro e o vigia ao vivo liam só `<sessao>.jsonl`: zero leituras em 05 e
  06/11, com 46 e 68 de fato. O estúdio perdeu as portas fechadas, e o
  relatório da semana, a tabela de fontes de dois dos quatro dias. Agora todos
  leem por `scripts/transcricoes.py`, e o cache escrito e o lido batem com o
  total que o próprio CLI informa.
- **A resposta da leitura mudou de forma.** O WebFetch de dentro do subagente
  devolve a página crua, com "Fetched … (HTTP 200 OK, …)" na primeira linha; o
  de antes devolvia um resumo feito por um modelo pequeno. O estúdio tomava
  qualquer "HTTP NNN" por porta fechada e, na primeira regeneração, deu as 114
  leituras como fechadas. Só 4xx e 5xx fecham.
- **Ficou mais caro.** US$ 7,03 e 7,83, contra 4,57 a 5,03 de média nas quatro
  semanas anteriores. Cada subagente abre o próprio contexto: o cache escrito
  foi de ~200 mil para 557 e 783 mil tokens. O cache lido caiu, porque as
  páginas não entram mais no contexto principal; os subagentes leram só 0,1 e
  0,5 milhão.

Achado no relatório da semana, pelo "0" na coluna de leituras ao lado do maior
custo até então. Era um experimento da Anthropic, ligado por interruptor remoto
(`tengu_clever_orbit`), desligado em 08/11; o orquestrador agora fixa o modo de
leitura e vigia o experimento ([ADR 0013](decisions/0013-leitura-de-paginas.md)).

### Subagente nosso no Claude Code: o que só o código do CLI mostrou

Montando o Jornalista (08/11, CLI 2.1.283), quatro intuições caíram:
- **Tirar a ferramenta do agente principal tira dos subagentes.** Com
  `--tools` sem WebFetch, o Jornalista, que declarava WebFetch, nasceu sem
  ferramenta e não rodou. Quem separa os dois é um hook PreToolUse: o
  `agent_id` só vem na chamada de subagente.
- **Página crua não é coisa do WebFetch, é do subagente embutido.** O WebFetch
  devolve a página inteira só para o "web-fetch" da Anthropic (`isBuiltIn` e
  esse nome); para todos os outros, o resumo do modelo pequeno. Um agente
  nosso com o mesmo nome não passa.
- **Subagente nosso roda em segundo plano** por padrão, e o relatório chega
  numa notificação; o embutido é a exceção. O `-p` espera todos antes de
  terminar.
- **O CLI passa o idioma do sistema ao modelo.** Com `LANG=pt_BR.UTF-8`, o
  mesmo pedido em inglês saiu respondido em português. O launchd não define
  `LANG`; teste que quer o ambiente da produção também não pode definir.

E no Teste A ([plano](plano-leitura-por-subagente.md)), sem `LANG` nenhum, o
Haiku 5.5 trocou de língua em 3 de 21 relatórios e traduziu as citações junto.

### Separar em agentes não barateia sozinho

A intuição: um Jornalista que lê e um Roteirista que escreve, cada um com
contexto pequeno, sairiam mais baratos que um agente só com tudo dentro.
Medido em 08/11, no episódio de 04/11 (US$ 5,25) e no ensaio do Jornalista:

| 04/11, produção | US$ |
|---|---|
| Opus: gravar no cache o que entra no contexto (1 hora, 2× a entrada) | 1,66 |
| Opus: reler o contexto a cada chamada (7,7 M tokens a US$ 0,20) | 1,54 |
| Opus: texto que escreve (roteiro, log, raciocínio) | 1,01 |
| Haiku 4.5: resumo das páginas e 29 buscas | 1,05 |

- **O Editor nunca recebeu página inteira.** Até 04/11 o WebFetch entregava o
  resumo do Haiku 4.5; no ensaio, o Jornalista entregou o relatório dele
  sobre o mesmo resumo. Entraram no Editor 164 mil caracteres num caso e 160
  mil no outro: o Jornalista reescreveu, não condensou, e custou US$ 0,69 a
  mais.
- **A escrita acontece quando o contexto já está cheio, mas por poucas
  chamadas.** Até a última busca foram 38 chamadas e US$ 2,85; depois dela, 12
  chamadas e US$ 1,36, das quais 0,58 é o texto do roteiro e do log, que
  qualquer agente pagaria. Um Roteirista com 60 mil tokens no lugar de 190 mil
  pouparia uns US$ 0,35 de releitura e pagaria uns 0,30 para montar o próprio
  contexto, mais o dossiê que o Editor escreveria para ele: empate.
- **Reler é barato; o que pesa é o que entra cedo.** Cache lido no Opus 5.5
  custa 5% da entrada. O que encarece é o trecho que entra no começo e é
  relido em todas as chamadas seguintes — o índice inteiro foi 47% do cache
  lido em 29/09, e a lista no prompt o levou a 1-3%.

O que barateia é diminuir o que entra (o índice virou lista; um relatório
do Jornalista só com as candidatas) ou trocar o modelo de quem lê muito (o
resumidor). Separar em agentes é arquitetura: regras de cada papel,
paralelismo, o desenho do CampsVerso — não economia.

**O cache de 1 hora é da assinatura.** No código do CLI 2.1.283, a sessão
principal grava cache de 1 hora com o motivo "subscriber"; com chave de API o
padrão é 5 minutos (1,25×), e `CLAUDE_CODE_PROMPT_CACHE_TTL` escolhe. Em 04/11,
a 5 minutos, a gravação cairia de US$ 1,66 para 1,04 e o episódio, para ~4,60.
Projeção de custo na nuvem que parte do registro de hoje sai alta.

### CloudFront reescreve a bucket policy se deixarem

"Grant CloudFront access to origin" vem como *Yes* e restringe o bucket ao
CloudFront — quebrando quem assinou pela URL antiga, em silêncio. Ficou em *No*
enquanto houver assinantes no endereço do S3.

### O `.env` não pode sobrescrever o ambiente

`set -a; source .env` sobrescrevia o `CLAUDE_BIN` passado na linha de comando, e
um teste com CLI falso disparou uma execução real. Ambiente explícito vence o
arquivo, como no `os.environ.setdefault` dos scripts Python.

### Teste que mexe em dado real acaba perdendo dado real

O `smoke_test.sh` move `episodes/` para se isolar. Duas vezes quase custou
episódios: uma por interrupção no meio do cleanup, outra por SIGPIPE
(`smoke_test.sh | head -3`) que rodou o cleanup com a saída quebrada e produziu
nomes de arquivo com lixo dentro.

Por um tempo o abrigo ficou dentro do repositório, com auto-recuperação e
validação de nome. A correção certa veio em 03/10: a suíte se copia para uma
pasta temporária, sem episódios, áudio nem dados pessoais, e roda lá. O mesmo
levantamento achou um segundo caso do padrão — o teste de precedência
escrevia no `.env` real e o restaurava no fim. Um invólucro confere, antes e
depois, que episódios, `.env`, índice, backlog e registro não mudaram.
**Isolar movendo o dado real é trocar um risco por outro; isolar copiando o
ambiente não deixa nada para devolver.**

### Reverberação medida com pouco sinal é ruído, não sala

A estimativa de reverberação dobrou — de 0,48 s para 0,95 s — quando só se
somou ruído branco à mesma gravação. A sala não mudou. O decaimento afunda no
piso antes de terminar, e o rabo achatado é lido como eco longo.

Isso invalidou retroativamente várias leituras do projeto: os 0,73 s medidos no
quarto vinham de gravações com 17 dB de S/R, e eram inteiramente explicáveis
pelo ruído. Quase escolhemos o cômodo errado por causa disso.

O script agora só reporta reverberação como confiável acima de 30 dB de S/R.
É a terceira métrica que precisou de uma regra de comparabilidade, depois de
codec e de dBFS entre aparelhos: **toda métrica derivada carrega uma condição
de validade, e vale a pena descobri-la antes de comparar, não depois.**

O jeito de descobrir é barato e sempre o mesmo — pegue um arquivo bom, degrade
uma variável de cada vez, e veja o que a métrica faz.

### Projeção de voz vale mais que sala, aparelho e distância

Perseguimos a qualidade por três caminhos: trocar de cômodo (13 a 17 dB),
desligar a adega (9 dB no aparelho sensível), aproximar o microfone. O terceiro
não só não ajudou como piorou — 10 cm rendeu 4 dB a menos de S/R que 20 cm,
por plosivas e por captar o corpo de quem fala.

Comparando a melhor gravação já feita com a de 10 cm: **mesmo pico, 5,9 dB de
diferença na fala média.** Uma tinha voz alta e constante, a outra voz baixa com
estouros. Nenhum ajuste de posição corrige isso.

O fator de crista denuncia qual é qual sem precisar ouvir: 18–20 dB é fala
firme, acima de 25 dB são estouros isolados sobre fala baixa.

**Antes de comprar microfone, meça a própria voz.** A variável que mais pesou
não está em nenhuma ficha técnica.

### Desobstruir o microfone piorou: a capa amortecia a mão

Tirar a capa do celular para o microfone ficar livre elevou o piso de ruído em
7 dB nas sub e 8 a 12 dB nas graves, reproduzindo nos dois cômodos testados. A
fala sobe — a obstrução era real — mas o ruído sobe mais, e o S/R cai.

A concentração nas graves entrega a origem: é ruído de contato, a mão entrando
pelo corpo do aparelho. A capa era o amortecedor que ninguém tinha creditado.

Vale como padrão, não como curiosidade: **toda a série de testes de posição
mostrou que o caminho mecânico importa mais que o acústico.** Suporte na mesa
custou 8 a 9 dB nas graves, aparelho nu custou 7 a 12 dB, e ambos passam
despercebidos porque ninguém ouve o problema — só o microfone, encostado nele.

### Piso de ruído se mede no trecho mais silencioso, não abaixo de um limiar

Terceira versão da mesma função, e a terceira falha veio de um ângulo novo. O
limiar fixo de −50 dBFS julgava o ganho do aparelho. O limiar por percentil
corrigiu isso, mas quebrou numa gravação **87% falada**: o corte caiu dentro
das pausas entre palavras e passou a medir a voz. Deu −41,8 dBFS de "ruído"
onde a sala estava a −54, reprovando material bom.

A formulação que sobrevive às três é não usar limiar nenhum: procure o **trecho
contínuo de 2 s mais silencioso do arquivo** e ancore o piso nele, usando o
máximo dentro da janela para exigir silêncio o tempo todo. Não depende do ganho
nem de quanto do arquivo é fala.

O padrão vale além do áudio: **um limiar é uma suposição sobre a distribuição
do dado.** Toda vez que a distribuição mudou — outro aparelho, outra proporção
de fala — o limiar quebrou. Estatística de ordem sobre o próprio arquivo não
tem esse problema.

### Referência de ruído tem que ser móvel

O monitor ao vivo comparava o fundo atual com o menor já visto na sessão. Um
avião passou, o alerta acendeu certo, e depois nunca mais apagou: bastou um
instante anormalmente baixo — inclusive o arranque do microfone, que entrega os
primeiros blocos perto de zero — para fixar a referência baixo demais.

Referência de "normal" em sinal que varia tem que ser janelada. Agora é o menor
fundo dos últimos três minutos, com os dois primeiros segundos descartados.

### O ouvido subestima fonte grave e sustentada

Gravando dois trechos de silêncio, quem gravou julgou pior o que tinha um avião
se aproximando e melhor o que tinha "uma moto ao fundo, não muito alta". A
medição inverteu: a moto ficou **7,7 dB acima**, com 82% da energia entre 60 e
120 Hz.

É o mesmo mecanismo que já tinha aparecido com a TV do cômodo ao lado e com o
motor da adega: grave atravessa parede, o ouvido o descarta como fundo, e o
microfone o registra inteiro. A diferença aqui é que o erro de julgamento
aconteceu **com a fonte à vista**, não escondida atrás de uma parede.

Prático: para decidir se pode gravar, olhe o medidor, não o ouvido.

### Ruído de rua não é piso, é distribuição

O piso do quarto parecia ter piorado 7 dB ao longo da noite. Não piorou: com a
rua vazia ele volta a −59,5 dBFS, contra −60,4 medidos horas antes. O que muda
é **quanto do tempo** ele está lá — abaixo de −60 dBFS são 6% do tempo, abaixo
de −58 são 18%.

Uma única medição de trinta segundos não caracteriza um cômodo com rua; ela
amostra um instante. Para planejar gravação é preciso a distribuição, e a
conclusão que sai dela é oposta à intuição: **não espere a janela silenciosa,
grave mais blocos e deixe a medição escolher.**

### Valide a pasta que vai subir, não a lista que você processou

O `prep_voice_samples.py` anunciava "9 minutos" enquanto a pasta de upload
tinha 28, incluindo 4,7 minutos de uma sessão anterior com piso de ruído a
**−31,6 dBFS** — 24 dB acima do material novo. Ele auditava o que tinha acabado
de converter; quem sobe seleciona a pasta.

O descompasso é silencioso e do tipo pior: o número que aparece é verdadeiro,
só não é sobre a coisa certa. E o custo já é conhecido — foi assim que o clone
anterior aprendeu o quarto.

Agora audita a pasta inteira a cada execução e move o reprovado para
`reprovadas/` em vez de apagar. **Toda ferramenta de validação deve medir o
artefato que vai ser usado, não o que passou pela sua mão.**

### Arquivo diferente não é áudio diferente

Duas amostras exportadas da mesma gravação tinham **tamanho idêntico ao byte** e
hashes de arquivo diferentes — metadados do contêiner mudam a cada exportação.
Passaram como material novo, e teriam entrado no treino com peso dobrado.

O que denuncia é o hash do **PCM decodificado**. Vale sempre que a pergunta for
"é o mesmo conteúdo?": compare o conteúdo depois de decodificar, nunca os bytes
do arquivo nem o tamanho.

Neste caso as métricas também denunciavam — S/R, pico, reverberação e dinâmica
iguais até a casa decimal, o que não acontece entre duas gravações distintas.
Coincidência exata em muitas casas é sinal de identidade, não de sorte.

### Na bateria o `caffeinate` não segura o Mac; na tomada, segurou

O orquestrador roda `caffeinate -i -m -s -w $$` para atravessar a madrugada.
Em 10 e 11/09 não bastou: três execuções morreram com *"Your computer went to
sleep mid-response"*. A primeira leitura, registrada aqui na época, foi que nada
dentro do `caffeinate` resolve tampa fechada. **Estava incompleta.**

O registro de execução, cruzado com o `pmset -g log`, mostrou a diferença:

| Execução | Energia | O que o log mostra |
|---|---|---|
| 09/09, concluída | tomada | tampa fechada desde 23:09; sistema em DarkWake a noite toda, nenhum sono durante a execução |
| 10/09, falhou | bateria | DarkWake às 06:03:16, "Entering Sleep" dois segundos depois |
| 11/09, duas falhas | bateria | o mesmo padrão, às 06:01 e às 07:06 |

O manual do `caffeinate` explica: `-s` *"is valid only when system is running on
AC power"*. Na bateria, o launchd acorda o Mac num despertar de manutenção para
rodar a tarefa perdida, e o sistema volta a dormir antes de o agente terminar.

**A regra que importa é estar na tomada.** Tampa aberta segue como margem de
segurança até mais noites confirmarem — por enquanto é um caso só na tomada.

**O que salvou o dia foi o invariante da janela.** A execução manual das 06:30
cobriu o dia certo, e a repescagem automática das 07:00 disparou depois e se
conteve sozinha, reconhecendo que 2026-09-09 já estava coberto. Uma falha de
infraestrutura não virou buraco nem episódio duplicado.

### Estimar ritmo com um arquivo erra 3%

`words_per_minute` foi para 145 a partir de um único episódio de teste gerado
com a voz nova. Com três episódios reais, a mediana é **150** — 3% acima.

Não é erro grave, mas mostra o limite de calibrar com n=1: a variação entre
episódios (145 a 154 nos três) é maior que o desvio que se quer medir. O
`calibrate_pace.py` exige dois episódios e usa mediana por isso.

Ao trocar de voz, o caminho honesto é: estimar com um, rodar alguns dias, e
remedir com `--desde` na data da troca.

### "Voz lenta" não era pausa, e velocidade não tem meio-termo

Ouvintes acharam a voz clonada lenta. A hipótese natural era pausa demais entre
frases, que daria para encurtar. A medição derrubou: nos episódios da voz nova
as pausas acima de 150 ms ocupam 14% do tempo, com média de 0,35 s; na voz
antiga ocupavam 15,5%, com média de 0,42 s. **A voz nova pausa menos.** O que
mudou foi a articulação: sem contar pausas, ~174 palavras por minuto contra
~180.

O parâmetro `speed` da ElevenLabs também não resolveu, e não por falta de
efeito. No mesmo trecho de 2,5 minutos:

| `speed` | Palavras por minuto |
|---|---|
| 1,05 | 146 |
| 1,10 | 167 |
| 1,15 | 169 |

De 1,05 para 1,10 a fala acelerou 14%; de 1,10 para 1,15, 1,4%. Na escuta,
1,05 soou igual ao episódio no ar e os outros dois, rápidos demais. **Não houve
valor intermediário utilizável**, e o número configurado não se traduz em
ritmo proporcional. Parte do salto pode ser variação natural entre gerações —
um trecho só não separa as duas causas.

Duas lições. Antes de otimizar pausa, meça quanto do tempo é pausa. E um
controle nominal de velocidade é uma promessa do fornecedor, não uma escala:
teste em pontos e ouça.

### Nome mantido à mão envelhece em silêncio

A ficha técnica de cada episódio diz quem narrou. O nome vinha de um campo
`_nome_falado` no `config/tts.json`, preenchido à mão. Quando o modelo trocou
para o Multilingual v2, o `model_id` mudou e o campo não: **quatro episódios
seguidos anunciaram "ElevenLabs Flash dois ponto cinco"**. Ninguém percebeu
porque soava certo — só o autor, ouvindo com atenção.

É o pior tipo de dado: uma cópia de outro dado, sem nada que obrigue as duas a
andarem juntas. A correção foi eliminar a cópia. O nome falado agora é derivado
do `model_id` em uso, e o nome do agente, do modelo passado ao `claude -p`, que
passou a ser fixado explicitamente no orquestrador em vez de herdar o padrão da
assinatura. Os registros das execuções headless confirmaram que o modelo em uso
era `claude-opus-5` — medido, não suposto — antes de ele ir para a ficha.

**Se um valor é função de outro, calcule; não armazene.**

### Login expirado sai com código 0

Testando o formato de saída do `claude -p` para outra finalidade, a resposta
veio: *"Failed to authenticate: OAuth session expired and could not be
refreshed"* — **com código de saída 0.** O orquestrador procurava "Not logged
in" e "authentication" para diagnosticar login; "authenticate" não casava. A
execução seguinte teria falhado com "Roteiro não foi criado", mensagem que
aponta para o lugar errado.

Foi achado por acaso, um dia antes da produção. Agora a saída vem em JSON, e
`is_error` vira falha independente do código; o padrão da mensagem também foi
ampliado, e o smoke test cobre os dois formatos.

**Código de saída não é sinal confiável de sucesso de uma ferramenta de
terceiros.** Confira o conteúdo.

### Custo lido do saldo da conta variava quatro vezes

O `tts.py` media o custo de narração pela diferença do contador de créditos da
conta, antes e depois, esperando até 90 segundos para ele estabilizar. Os logs
registraram, para o mesmo modelo, de **0,14 a 0,55 crédito por caractere**: o
contador atualiza com atraso, e a espera nem sempre bastava.

A ElevenLabs devolve o custo exato de cada requisição no cabeçalho
`character-cost`. Somando por trecho, o custo é exato e a espera acaba.

**Meça a operação, não a variação do saldo.** Diferença de saldo mistura atraso,
outras operações e arredondamento.

### O log de energia do macOS precisou de três leituras

Para registrar se o Mac ficou parado durante a execução, o `registro.py` lê o
`pmset -g log`. As duas primeiras regras erraram, e cada uma foi desmentida pelos
próprios dados:

1. **"Wake Requests" contado como despertar.** É um pedido de despertar
   agendado. As falhas por sono apareciam com 3 segundos parados.
2. **DarkWake contado como sono.** DarkWake é o sistema acordado com a tela
   apagada; processos rodam. O episódio de 09/09 aparecia dormindo a execução
   inteira — e concluído, com 68 chamadas ao modelo.
3. **Parado é de "Entering Sleep" até o próximo despertar**, DarkWake ou Wake. Uma
   linha do tipo Sleep que diz "Entering DarkWake state" também não é sono.

Com a terceira regra, as falhas mostram 99% do tempo parado e as execuções
concluídas, zero. **Uma métrica nova só está validada quando bate com um desfecho
conhecido** — aqui, execução que concluiu não pode ter dormido.

## Audiência

Os números de audiência ficam em `privado/`, fora do repositório. Aqui fica só
o método.

### Painel com amostra pequena mente em percentual

O primeiro painel do Spotify parecia dizer muita coisa — gênero, faixa etária,
país, taxa de conclusão. Três armadilhas apareceram juntas:

- **a unidade não é a que parece.** Todos os percentuais de demografia eram
  múltiplos de 1 sobre o total de *plays*, não de pessoas. Com poucas dezenas
  de plays, uma única escuta move um percentual em vários pontos, e as escutas
  de teste do próprio autor entram na conta;
- **a janela declarada não é a janela real.** "Últimos 30 dias" eram cinco
  dias de presença no Spotify; o resto do gráfico era o programa não existir
  lá;
- **duas métricas do mesmo painel pareciam se contradizer** — conclusão baixa
  contra consumo médio de dois terços do episódio. Não se contradiziam: a
  conclusão do Spotify é *quem ouviu pelo menos 95%*, não a fração média
  ouvida. Poucos terminam, a maioria ouve boa parte.

O corte de 95% tem um efeito colateral próprio: quem sai durante o
encerramento, que é recap e ficha técnica, não conta como concluído. A
métrica pune o trecho menos essencial.

É o mesmo erro que o projeto já cometeu com dBFS e com reverberação, agora num
painel de terceiros: **uma métrica sem a condição de validade junto não diz
nada.** Com amostra pequena, anote contagem absoluta e leia a definição antes
de agir.

### O culpado não era o login; era o sono e o DNS

Depois de três falhas seguidas às 5h50, a suspeita recaiu sobre a sessão do
Claude Code — até porque um teste manual, no mesmo período, devolveu *"OAuth
session expired and could not be refreshed"*. A hipótese era confortável e
estava errada. Os logs das execuções que falharam dizem outra coisa:

```
API Error: Your computer went to sleep mid-response.
API Error: Can't reach the API server — check your internet or DNS (ENOTFOUND)
```

Nenhuma das falhas de produção foi de autenticação. Duas foram o Mac dormindo
na bateria no meio da resposta, e uma foi o DNS ainda não estar de pé quando o
agendador disparou, segundos depois de a máquina acordar. A expiração do login
existiu, mas apareceu num teste manual e foi corrigida com um `/login` — nunca
derrubou um episódio.

A correção do DNS é uma espera de até um minuto pela resolução de
`api.anthropic.com` antes de chamar o agente, que avisa e segue em vez de
abortar. A do sono é a tomada. (Em 28/10 a espera passou a abortar; ver a
seção seguinte.)

**A mensagem de erro que você viu por último não é a causa da falha que você
está investigando.** Leia o log da falha, não o da sua memória.

### Prazo contado em tentativas não é prazo

Em 28/10 o Mac estava fora de casa, na bateria e sem internet. O `pmset -g log`
mostra o despertar das 05:12:55 durando 2 segundos; dali em diante, o Mac só
acordava de 15 em 15 minutos, por 2 a 5 segundos. A espera pela rede, de "12
tentativas com 5 s entre elas", só andava nesses intervalos: o minuto previsto
terminou às 08:04, depois de uns 33 segundos de Mac acordado em 2h51 de
relógio. O orquestrador então avisou e seguiu, como mandava a regra de 11/09, e
o agente passou mais 1h35 tentando a API antes de desistir, às 09:39.

O estrago maior foi o tempo preso, não a falha: o launchd não roda duas
instâncias do mesmo job, então a repescagem das 06:00 e das 07:00 não teve vez.

Agora o prazo é de relógio (60 s desde o início da espera) e, sem DNS, a
execução sai com erro antes de chamar o agente e de mexer na memória. Registro
e `estado.json` dizem `rede` como etapa. Seguir sem rede valia em 11/09, quando
o Wi-Fi voltava em segundos; com o Mac longe de casa, só prendia o horário da
repescagem.

**Espera que pode atravessar o sono do Mac se mede no relógio, não em
tentativas nem em `sleep`.**

### O vigia não enxergava o podcast pelo shell, e quase ninguém percebeu

Em 29/09 o vigia mandou "não consegui confirmar". O log da execução mostra o
motivo: o `curl` saiu pelo proxy do ambiente na nuvem e voltou "CONNECT tunnel
failed, response 403" para as três URLs, antes de chegar ao S3 ou ao domínio.
Relendo as outras execuções da semana, o `curl` falhou em **todas**; nos dias
bons, o vigia desistiu do shell por conta própria e leu pelo WebFetch, que
funciona. Em 29/09 ele não tentou. O prompt agora manda usar só o WebFetch.

A regra de 14/09 — sem confirmação, dizer "não consegui confirmar", nunca "não
saiu" — fez o trabalho dela: o aviso foi inútil, mas não foi falso. **Uma
ferramenta que funciona por improviso do agente está quebrada; o log de uma
execução bem-sucedida mostra isso tão bem quanto o de uma falha.**

### Array vazio derruba o bash do macOS

O `/bin/bash` do macOS é a versão 3.2, de 2007. Nela, `"${arr[@]}"` com o array
vazio e `set -u` é "variável não definida", e o script morre. O passo novo do
relatório passava um argumento opcional ao `estado.py` por array: em todo dia
sem relatório — quatro de cada cinco — o `estado.json` deixaria de ser
publicado, e o vigia acusaria falha de segunda a quinta. O teste que já
existia para a publicação do estado pegou antes de ir ao ar. A forma que
funciona em qualquer bash é `${arr[@]+"${arr[@]}"}`.

### Aviso que só chega na tela de casa não é aviso

O pipeline avisava por notificação nativa do macOS — que ninguém vê estando a
mil quilômetros — e o caminho de e-mail estava configurado pela metade:
`SMTP_HOST` e `SMTP_PORT` preenchidos, `NOTIFY_TO`, `SMTP_USER` e `SMTP_PASS`
vazios. O `notify.py` cai para o macOS em silêncio quando falta qualquer um
deles, então a lacuna nunca apareceu. Pior: a notificação só rodava na etapa
final, depois do sucesso. **Falha não avisava nada.**

A saída foi inverter o sentido do aviso. Em vez de a máquina empurrar uma
mensagem para fora, ela deixa um `estado.json` público no S3 — credencial que
já existia — dizendo como terminou a execução, em que etapa e por quê. Um vigia
externo lê esse arquivo de onde estiver. Isso cobre o caso que nenhum aviso
saído do Mac cobre: **o Mac não ter rodado.**

Como o arquivo é público, o motivo da falha é higienizado: caminho de usuário
vira `/Users/<usuario>`, sequências longas que pareçam token viram `<omitido>`,
e o texto é truncado.

### O vigia deu alarme falso lendo respostas de 16 horas antes

Na segunda, 14/09, o episódio 12 saiu às 06:06 e foi publicado sem erro. Às
08:08 o vigia na nuvem mandou push dizendo que o episódio não tinha saído. As
duas leituras dele:

```
feed.xml     → mais recente = "Anthropic nomeia sete labs chineses…"
                              Fri, 11 Sep 2026 06:00:00 +0000
estado.json  → HTTP 403
```

As duas estavam erradas — e são, palavra por palavra, as respostas que o mesmo
vigia recebeu no teste de encanamento de domingo, 13/09 às 18:55. Naquele
momento as duas estavam **certas**: o episódio de sexta era o mais novo e a
policy do bucket ainda não liberava o `estado.json`. A camada de fetch devolveu
as respostas de domingo em vez de ir buscar. O `WebFetch` documenta cache de 15
minutos por URL; isso foi muito além disso, mas a coincidência exata das duas
leituras não deixa outra explicação razoável. Descartado o CloudFront: o feed
sai com `cache-control: max-age=300`, e minutos depois do alarme as duas URLs
respondiam certo pelo domínio, pelo S3 direto e pelo próprio `WebFetch`.

O cache foi o gatilho, mas o alarme falso foi decisão de lógica: o prompt
tratava "feed sem hoje" como verdade absoluta e 403 no estado como benigno, de
modo que **duas leituras impossíveis de confirmar produziam uma afirmação
confiante**. O conserto tem três partes: cache-buster com a hora da execução na
URL, `estado.json` como fonte primária em vez de detalhe opcional, e confirmação
por segundo caminho antes de alarmar — sem confirmação, o vigia diz "não
consegui confirmar", não "não saiu".

**Vigia que não distingue "está quebrado" de "não consegui ver" gasta o crédito
do alarme.** Quem recebe três alarmes falsos para de acreditar no quarto, que é
o verdadeiro.

### As variáveis de ambiente nunca chegaram ao agente

Desde a primeira semana, o orquestrador calcula a data, a janela, a faixa de
palavras, o número do episódio e os nomes da ficha técnica, e exporta tudo para
o `claude -p`. O prompt dizia: "a janela vem pronta nestas variáveis". **O agente
nunca conseguiu ler nenhuma delas.** O Bash não está entre as ferramentas
liberadas, e em modo headless toda tentativa volta negada — em todas as
transcrições de produção conferidas, com o CLI antigo e com o novo:

```
$ echo "EPISODE_DATE=$EPISODE_DATE"   → Contains simple_expansion
$ printenv EPISODE_DATE ...           → This command requires approval
$ env | grep EPISODE                  → ... requires approval: env
```

O episódio saía certo mesmo assim, por dois motivos que ninguém tinha escolhido.
O agente reconstruía sozinho o que precisava: a janela lendo o `window_end` do
episódio anterior, o número somando um, os nomes pelo que sabe de si e lendo os
scripts. E, em produção, a data do episódio é sempre hoje — de modo que a regra
de reserva do prompt, "se EPISODE_DATE não existir, use hoje", dava a resposta
certa por coincidência.

A coincidência acabou num reprocessamento. Em 26/09, refazendo o episódio de
25/09 num sandbox, o agente não leu a variável, obedeceu à reserva e gravou
`2026-09-26.md`, com a janela esticada até 25/09 — o dia do próprio episódio,
que nunca pode entrar. Não foi desobediência: foi o prompt contando com algo
que o agente não enxerga.

Agora o orquestrador escreve os valores no fim do próprio prompt, numa seção
"Parâmetros desta execução", e o prompt proíbe usar o relógio do sistema para a
data do episódio. O smoke test usa um agente falso que guarda o prompt recebido
e confere se os valores estão lá.

**Um mecanismo que funciona por reconstrução do agente não está funcionando —
está sendo compensado.** A diferença só aparece no dia em que a reconstrução e a
intenção divergem. Confira no transcript o que o agente de fato recebeu, não o
que o orquestrador acredita ter mandado.

### Os jornais que dão o furo são os que a ferramenta não abre

Em 10/11/2026, antes de decidir se reportagem de jornal poderia entrar quando a
fonte fechasse, contamos as 1.371 leituras de página das transcrições guardadas
(893 da produção, de 13/10 a 10/11, e 478 de ensaios) e sondamos 19 jornais com
o mesmo WebFetch da produção (`claude -p` em `env -i`, Haiku 4.5, US$ 0,08).
As portas fecham de três jeitos, com causas diferentes:

- **O Claude Code recusa o domínio**, sem código HTTP: "Claude Code is unable
  to fetch from www.nytimes.com". Assim com New York Times, Wall Street Journal,
  Financial Times, Reuters, AP, The Verge, Wired, Ars Technica, Guardian,
  Folha, Valor e web.archive.org. Não é paywall nem resposta do site: a
  mensagem é da ferramenta. Primeira aparição nas transcrições: 14/10.
- **O site responde 403**: Bloomberg, Washington Post, Axios (5 de 5 na
  produção) e GlobeNewswire, o distribuidor de comunicados; entre as fontes
  primárias, openai.com (39 vezes em quatro semanas) e x.ai (18).
- **Abre só a vitrine**: The Information (manchetes e aviso de assinatura) e,
  nesta sonda, TechCrunch (manchete e primeiros parágrafos; na produção, 10 de
  10 inteiras).

Abriram com o texto inteiro: CNBC e NBC. Dois efeitos:

1. Quem costuma dar o furo (NYT, WSJ, FT, Bloomberg, Reuters, The Information)
   está fechado; quem repercute (CNBC, NBC, TechCrunch, Fortune, The Register)
   abre. Qualquer regra de "três coberturas" vai se apoiar na repercussão.
2. O passo do arquivo público no procedimento de porta fechada do prompt não
   entrega: a consulta em archive.org respondeu 12 de 35 vezes (o resto, 429), e
   abrir a cópia em web.archive.org falhou 6 de 6, recusada pela ferramenta.

O caso que motivou a conta, a NVIDIA e Jensen Huang, mostrou outra coisa: o
furo do New York Times saiu em 29/10, a CNBC repercutiu no mesmo dia, o
Financial Times avançou em 06/11, e em 08/11 saíram a admissão de Huang e o
primeiro comunicado do conselho, que abriu a investigação (17:00); o segundo,
dos conselheiros independentes, contratando os advogados, veio em 10/11, às
16:07 (datas da página e do feed de nvidianews.nvidia.com, conferidas em
13/11). Nenhuma das execuções cuja janela continha um
desses marcos viu a história: zero menções a "Megaspeed" nas transcrições de
30/10, 09/11 e 11/11. As de 10/11 e 12/11 a viram, pelo AI Weekly, um dia
depois, e a descartaram por estar fora da janela (e por ser bastidor). A
produção lê blogs.nvidia.com, que está nas fontes, e não a sala de imprensa,
que não está. A perda foi de descoberta, não de acesso. A renúncia de Huang,
em 12/11, foi ao ar em 13/11: o agente chegou à sala de imprensa por busca.
(Corrigido em 12/11 e de novo em 13/11: a primeira versão dizia que a produção
nunca viu a história; a correção de 12/11 trocou o comunicado de 08/11 pelo de
10/11, quando são dois.)

**Antes de escrever regra que dependa de ler um tipo de fonte, conte se a
ferramenta chega lá.**

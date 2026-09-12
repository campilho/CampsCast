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

## Infraestrutura

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

Hoje o abrigo fica dentro do repositório, com auto-recuperação e validação de
nome. **A correção certa continua pendente:** os testes não deveriam tocar em
dados reais.

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

### `caffeinate` não impede o sono que a tampa fechada dispara

O orquestrador roda `caffeinate -i -m -s -w $$` justamente para atravessar a
madrugada. Não bastou: com a tampa fechada, a execução das 06:03 morreu aos 24
minutos com *"Your computer went to sleep mid-response"*.

`caffeinate -i` impede o sono por **ociosidade**. Fechar a tampa é outro
caminho — o macOS trata como comando explícito do usuário e dorme mesmo com
asserção ativa, a não ser que haja monitor externo e energia. Na bateria é
ainda mais agressivo.

Não há flag que resolva dentro do `caffeinate`. As saídas são todas fora dele:
deixar a tampa aberta, `sudo pmset -a disablesleep 1` (o Mac nunca dorme, o que
tem custo próprio), ou um fallback na nuvem.

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

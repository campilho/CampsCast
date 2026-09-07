# Guia de gravação para clonagem de voz profissional

Roteiro para gravar o material do Professional Voice Cloning da ElevenLabs, que
substitui o Instant Voice Clone da Fase 1.

O IVC aprendeu **timbre** com dois a três minutos. O que falta é **idioleto** —
ritmo, entonação, redução de vogais, as marcas regionais da sua fala. Sem esses
dados, o modelo preenche com o padrão dele, que para português brasileiro puxa
para uma locução neutra. É por isso que a voz atual soa de outra região.

---

## 1. Equipamento: o contraintuitivo primeiro

**Não use AirPods nem o Bose QuietComfort.**

Fone Bluetooth, ao virar microfone, entra em perfil de headset: a banda cai
drasticamente, o áudio passa por compressão pesada, e o firmware aplica
supressão de ruído e controle automático de ganho. Esses três processos
**alteram a voz** — e o modelo aprenderia os artefatos junto com você. Um clone
treinado em áudio de Bluetooth soa abafado e processado, por mais caro que seja
o fone.

Ordem de preferência com o que você já tem:

| Opção | Avaliação |
|---|---|
| **iPhone, app Gravador** | melhor opção — microfones bons, sem compressão de headset |
| **Microfone do MacBook Pro** | boa segunda opção, 48 kHz, array de três cápsulas |
| AirPods Pro 2 | evitar |
| Bose QC Ultra | evitar |

Detectei os dois primeiros disponíveis na sua máquina, ambos a 48 kHz.

O iPhone ganha por poder ser posicionado onde você quiser, longe do ventilador
do notebook. **A diferença é grande e vem da distância, não da qualidade do
microfone**: medido na mesma sala, no mesmo minuto, o iPhone a 20 cm deu 38 dB
de relação sinal/ruído e o MacBook, sentado à frente, deu 17 dB. Quinze
decibéis a menos no nível da fala — cerca de cinco vezes mais longe. Grave no app **Gravador**, com a qualidade em *Sem perdas* nos
ajustes, e depois passe os arquivos para o Mac.

Se um dia quiser subir de nível, um microfone USB dinâmico resolve — mas não
compre nada antes de tentar com o iPhone. A sala pesa mais que o microfone.

## 1b. Teste 60 segundos antes de gravar 30 minutos

Clonagem aprende tudo que está no áudio — ruído de rua, chiado de
ar-condicionado, eco do cômodo — e depois não há como separar. Meia hora
gravada num lugar ruim vira um clone ruim, e o erro só aparece no episódio.

Grave uma amostra curta e meça:

1. Comece o gravador e **fique 10 segundos em silêncio**. Parado, sem falar.
   É isso que mede o ruído do ambiente de forma honesta.

   > **Faça isso em todos os blocos, não só no teste.** Sem um trecho de
   > silêncio real, não há como medir o ruído da sala: as pausas entre frases
   > carregam respiração e cauda de reverberação, e tomá-las por ruído reprova
   > material bom. O script detecta a ausência e avisa, em vez de reprovar —
   > mas aí você fica sem a medição.
2. Fale 40 segundos normalmente, na distância e no tom que vai usar depois.
3. Repita no outro aparelho, no mesmo lugar e na mesma hora.

```bash
python3 scripts/check_recording.py iphone.m4a mac.m4a
```

O script mede piso de ruído, nível da fala, relação sinal/ruído, distorção e
energia de baixa frequência — que denuncia trânsito, ar-condicionado e vento no
microfone.

### Como ler o resultado

| Medida | Bom | Aceitável | Ruim |
|---|---|---|---|
| Piso de ruído | ≤ −60 dBFS | ≤ −50 | acima disso |
| Relação sinal/ruído | ≥ 40 dB | ≥ 30 | abaixo disso |
| Nível da fala | −26 a −14 dBFS | | estourado |

**Referência:** o áudio que a ElevenLabs devolve nos nossos episódios mede
**41 dB de relação sinal/ruído**. Chegar perto disso numa gravação caseira é
excelente; 30 dB já serve.

### Não compare arquivos de codificação diferente

Compressão com perdas **descarta som baixo demais para o ouvido perceber** — e
esse som é justamente o ruído de fundo. O resultado é que um arquivo comprimido
mede um piso de ruído *melhor* que o mesmo material sem perdas, sem que a
gravação seja melhor em nada.

Medido aqui, no mesmo quarto e com um minuto de diferença:

| Arquivo | Piso | S/R | Formato |
|---|---|---|---|
| Teste 1 | −70,8 dBFS | 48 dB | 129 kbps, com perdas |
| Teste 2 | −66,3 dBFS | 43 dB | 1234 kbps, sem perdas |

O segundo parece pior e é melhor: mostra o ruído que realmente existe, em vez
de escondê-lo, e entrega ao modelo o detalhe completo da voz. **Para clonagem,
grave sem perdas.** O script avisa quando você compara codificações diferentes.

Não conte com a ElevenLabs avaliar para você: mesmo que a interface dê algum
retorno, isso só acontece **depois** de subir a gravação inteira. Medir antes
custa um minuto.

## 2. A sala pesa mais que o equipamento

Reverberação é o inimigo. O modelo aprende o eco da sua sala como se fosse
parte da sua voz, e todo episódio sai com aquela sala junto.

- Cômodo pequeno, com pano: quarto com cortina, closet, sofá.
- Evite cozinha, banheiro, sala de piso duro e paredes nuas.
- Desligue ar-condicionado, ventilador e purificador. O ruído contínuo some
  para o seu ouvido em minutos, mas o modelo o escuta.
- Celular no silencioso, notificações do Mac desligadas.

### Medir a sala antes de cada sessão

Grave 30 segundos parado, em silêncio, e rode:

```bash
python3 scripts/check_recording.py silencio.m4a --sala
```

| Ruído do ambiente | Veredito |
|---|---|
| ≤ −60 dBFS | sala silenciosa |
| −60 a −50 | aceitável, já se ouve o ambiente |
| acima de −50 | procure outra hora ou cômodo |

Vale medir **em cada sessão**, não uma vez só. Medido no mesmo quarto com horas
de diferença: **−66 dBFS** numa tarde e **−50 dBFS** em outra. Doze decibéis de
diferença, com a fração de graves subindo de irrelevante para 76% — trânsito
que aumentou, ou algum aparelho que ligou.

Se o ruído for quase todo grave, procure a fonte. O modo `--sala` ajuda a
identificar: máquina faz ruído **constante**, conteúdo **flutua**.

| Desvio dos níveis | Provável fonte |
|---|---|
| < 1,5 dB | aparelho ligado: ar-condicionado, geladeira, ventilador |
| > 1,5 dB | TV ou som em outro cômodo, voz, trânsito passando |

**Grave atravessa porta e parede; agudo não.** Por isso a TV da sala aparece na
gravação sem que você a escute conscientemente — o que passa pela porta é só o
grave, exatamente a faixa que polui a medição.

Caso real deste projeto: uma medição de 30 segundos saiu de −61 dBFS no começo
para −47 no fim, com 4,1 dB de desvio. Não era a sala nem a posição: era a TV
na sala ao lado, com a porta do quarto fechada. Os primeiros segundos mostravam
que o quarto era bom; o resto mostrava o que estava entrando.

**Consistência importa mais que perfeição.** Blocos gravados em condições
diferentes ensinam ao modelo uma variação que não existe na sua voz. Se a sala
não puder melhorar, prefira gravar tudo na condição pior a misturar as duas.

Teste rápido de reverberação: bata palma uma vez. Se ouvir um "chiado" depois do estalo, a sala
tem reverberação demais — mude de cômodo ou grave dentro do closet, entre as
roupas.

Quarto com cama, travesseiros, cobertor e cortina grande costuma ser o melhor
cômodo da casa: tecido absorve reflexão, que é o que estraga gravação caseira.

**Ruído de rua** é a variável que sobra. Ele não é eliminável, mas é
administrável: grave no horário mais silencioso que conseguir, feche a janela,
e afaste-se dela. E meça — o `check_recording.py` diz se está no nível que
atrapalha ou não, em vez de você decidir de ouvido.

## 3. Posição e execução

- Distância de um palmo, mais ou menos vinte centímetros. Constante: aproximar
  e afastar muda o timbre entre trechos.
- Fale **ligeiramente para o lado** do microfone, não direto nele. Evita o
  estouro dos "p" e "b".
- Mantenha a mesma distância dentro de cada sessão. Se parar e voltar depois,
  refaça a marcação.
- Beba água antes, não durante — o som de garrafa entra na gravação.

**Não aplique nenhum tratamento depois.** Nada de redução de ruído, normalização
ou equalização. A ElevenLabs quer o material cru; qualquer processamento vira
característica aprendida.

## 4. Quanto tempo

O Professional Voice Cloning pede **no mínimo trinta minutos** de fala limpa.
Mais material melhora o resultado, com ganho decrescente — a faixa de uma a três
horas é onde a maioria dos relatos indica o melhor custo-benefício.

Confirme o mínimo exigido na própria interface da ElevenLabs no momento de criar
a voz, porque esse número muda com o tempo.

Sugestão de divisão, para não cansar a voz:

| Sessão | Duração | Conteúdo |
|---|---|---|
| 1 | 15 min | blocos 1 e 2 abaixo |
| 2 | 15 min | blocos 3 e 4 |
| 3 | 15 min | blocos 5 e 6 |
| 4 | 15 min | repetir os blocos que ficaram fracos |

Grave em dias diferentes se preferir, mas **na mesma sala, com o mesmo
microfone e à mesma distância**.

## 5. O princípio: cobertura, não roteiro

Em pesquisa de síntese de fala usa-se o conceito de **corpus foneticamente
balanceado** — um conjunto de frases escolhido para que todos os sons da língua
apareçam em quantidade suficiente, e em contextos variados. Para o português
brasileiro existem corpora desse tipo usados academicamente.

Você não precisa de um corpus formal. Precisa cobrir três eixos:

1. **Fonética** — todos os sons do português, incluindo os que aparecem pouco
   na conversa casual: "lh", "nh", "rr", ditongos nasais como "ão" e "ãe".
2. **Prosódia** — afirmação, pergunta, enumeração, ênfase, dúvida, ironia.
   Se você só afirmar, o modelo não saberá fazer perguntas com a sua voz.
3. **Vocabulário do domínio** — os termos que aparecem no podcast: nomes em
   inglês, siglas, números grandes.

**Fale, não leia.** Leitura em voz alta tem prosódia própria — mais uniforme,
com entonação de locutor. É justamente o que queremos evitar. Use os blocos
abaixo como **tópicos para falar sobre**, não como texto para ler.

---

## 6. Os seis blocos

### Bloco 1 — Apresentação e trabalho (5 min)
Fale sobre você como falaria numa reunião com alguém que acabou de conhecer.
Quem você é, o que faz, como chegou até aqui, o que te interessa hoje em
tecnologia. Tom normal de conversa.

### Bloco 2 — Explicar algo técnico a um leigo (5 min)
Escolha um assunto que você domina e explique como explicaria para alguém de
fora da área. Modelo de linguagem, agente de IA, o que é uma API, como funciona
um seguro. Este bloco captura seu jeito de didatizar — que é o registro do
podcast.

### Bloco 3 — Termos em inglês e números (5 min)
O bloco mais importante para o CampsCast, porque é onde o clone atual falha.
Fale naturalmente citando:

> Anthropic, OpenAI, Google DeepMind, NVIDIA, Mistral, Meta, xAI, Hugging Face,
> Model Context Protocol, benchmark, deploy, machine learning, startup,
> open source, dataset, prompt, token, cloud, chip, data center.

E números falados por extenso, como aparecem no roteiro:

> "cerca de setenta bilhões de parâmetros", "um bilhão de dólares em receita
> anualizada", "cortou em mais de vinte por cento", "cem mil variantes",
> "GPT cinco ponto seis", "SB cinquenta e três", "dois mil e vinte e seis".

Não decore: monte frases suas em volta desses termos.

### Bloco 4 — Variedade prosódica (5 min)
Force os padrões que a conversa normal não cobre:

- **Perguntas**: faça dez perguntas de verdade, como se entrevistasse alguém.
- **Enumerações**: liste coisas, com a entonação suspensiva de "primeiro…,
  segundo…, e terceiro…".
- **Ênfase**: repita a mesma frase mudando a palavra enfatizada.
- **Dúvida e ressalva**: "não está claro ainda se…", "a empresa afirma que…".
- **Encerramento**: frases de fecho, do tipo "é isso, até amanhã".

### Bloco 5 — Contar uma história (5 min)
Conte um caso real, com começo, meio e fim. Um problema que você resolveu no
trabalho, uma viagem, algo que deu errado. História traz variação natural de
ritmo e emoção que nenhum outro bloco produz.

### Bloco 6 — No registro do podcast (5 min)
Pegue um episódio já publicado em `episodes/` e **conte as notícias com suas
palavras**, olhando só as pautas, sem ler o roteiro. Este bloco alinha a
gravação ao uso final: mesma energia, mesmo ritmo, mesmo tipo de conteúdo.

É o bloco que mais influencia o resultado. Se tiver tempo para só um extra,
faça mais deste.

---

## 6b. Converter antes de subir — obrigatório

O app Gravador do iPhone, na qualidade **Sem perdas**, grava em **ALAC** dentro
de um `.m4a`. A ElevenLabs **não decodifica esse codec**: ela lê duração zero e
recusa com *"At least 30s of audio is required"*, mesmo num arquivo de um
minuto. A mensagem não menciona formato, então o erro parece ser outra coisa.

O arquivo em qualidade normal sobe sem reclamar, porque aí é AAC — o que leva à
conclusão errada de que o problema é a gravação sem perdas. Não é: é o
contêiner.

```bash
python3 scripts/prep_voice_samples.py bloco1.m4a bloco2.m4a bloco3.m4a
```

Converte para WAV mono 44,1 kHz — sem perdas e universalmente aceito —, roda a
checagem de qualidade em cada um e soma a duração total. Verificado: a conversão
preserva as medições exatamente, os mesmos −66,3 dBFS e 43 dB de S/R.

### Tamanho

WAV mono a 44,1 kHz ocupa cerca de **5 MB por minuto**. Trinta minutos dão 150
MB no total — motivo a mais para gravar **em blocos separados** em vez de um
arquivo único: cada bloco de cinco minutos fica em 25 MB, e a ElevenLabs aceita
várias amostras.

## 7. Antes de subir

- [ ] Trinta minutos ou mais de fala limpa
- [ ] Mesma sala, mesmo microfone, mesma distância em tudo
- [ ] Sem música, sem outra voz, sem ruído contínuo
- [ ] Sem tratamento aplicado depois
- [ ] Ouvir uma amostra de cada sessão antes de enviar

Ouça um minuto de cada arquivo. Se algum tiver ruído, eco ou volume destoante,
regrave em vez de enviar — material ruim contamina o modelo inteiro, e não há
como remover depois.

## 7b. Acompanhar o treino

Criada a voz, a ElevenLabs treina **um modelo de cada vez**, e leva de 2 a 6
horas. A tela de Voices mostra a voz na lista antes de ela estar pronta, com um
discreto "0/4 models" — que significa zero prontos, não que está pronta.

```bash
python3 scripts/tts.py --voice-status ID_DA_VOZ
```

Lista as amostras enviadas e o estado de cada modelo, e avisa especificamente
se o modelo que está em produção (`model_id` de `config/tts.json`) já terminou.
Só esse importa: os outros três podem ficar treinando sem atrapalhar.

## 7c. Se precisar refazer

O plano Creator permite **uma** voz profissional por vez, e a interface não
oferece trocar as amostras de uma voz existente — o "Edit voice" mexe só nos
metadados.

Para regravar, o caminho é **apagar e recriar**: no menu de três pontos da voz,
*Delete voice*, e criar de novo com as amostras novas.

Vale deixar o treino em andamento terminar antes de apagar, mesmo que você já
saiba que vai refazer. Não custa nada além de esperar, e dá uma referência: se
o clone feito com material imperfeito já soar bem, você aprende quanto a
qualidade da gravação realmente pesa. Se soar ruim, confirma que valia
regravar.

## 8. Depois

Ao criar a voz na ElevenLabs, a verificação de identidade exige que você leia
uma frase que eles fornecem. Isso é para provar que a voz é sua, e é o único
momento em que ler é o certo.

Ao trocar o `voice_id` em `config/tts.json`, **remeça o ritmo**: cada voz fala
numa velocidade diferente, e a faixa de palavras do roteiro sai daí.

```bash
python3 scripts/tts.py --check          # valida a voz nova
scripts/run_episode.sh --only tts       # gera com ela
python3 scripts/tts.py --budget         # confere a faixa de palavras
```

O procedimento de medição está em
[docs/setup-macos.md](setup-macos.md#9-medir-o-ritmo-da-voz).

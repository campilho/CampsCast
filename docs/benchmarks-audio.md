# Benchmarks de gravação

Medições comparáveis entre salas, aparelhos e distâncias. Servem para decidir
onde e como gravar, e para justificar (ou desmentir) a compra de equipamento
com número, não com impressão.

Todas as medições vêm de:

```bash
python3 scripts/check_recording.py arquivo.m4a --markdown
```

A tabela sai com as colunas alinhadas: é markdown válido no GitHub e legível
direto no terminal, sem precisar renderizar.

Outras saídas:

```bash
python3 scripts/check_recording.py bloco.m4a            # avaliação compacta
python3 scripts/check_recording.py silencio.m4a --sala  # só o ambiente
python3 scripts/check_recording.py bloco.m4a --detalhe  # perfil linha a linha
```

O modo compacto resume o perfil de nível numa linha só, com blocos de altura
variável. Foi assim que a TV do cômodo ao lado apareceu — o traço sobe da
esquerda para a direita ao longo de trinta segundos:

```
  ▂▃▃▂▂▁▁▃▂▁▃▄▅▄▃▃▃▄▂▂▂▃▂▃▃▄▃▃▄▃▄▅▄▄▅▄▄▅▅▅▅▅▄▄▅▆▆▆▆▇▆▆▅▅▅▅
  0s                                                   31s
```

---

## O que cada métrica significa

| Métrica | O que é | O que buscar |
|---|---|---|
| **Fala** | nível médio dos trechos falados | −26 a −14 dBFS |
| **Ruído** | nível do silêncio sustentado | ≤ −60 dBFS |
| **S/R** | distância entre voz e ruído | ≥ 40 dB bom, ≥ 30 aceitável |
| **Reverb** | decaimento estimado da sala | ≤ 0,4 s |
| **Crista** | pico menos média — quanto de dinâmica sobrou | 15–22 dB |
| **Codec** | taxa de bits da origem | sem perdas para clonagem |

**S/R é a métrica que mais importa** para clonagem: mede quanto da gravação é
voz e quanto é ambiente. Reverb vem em segundo — eco é a única coisa que
nenhum processamento remove depois.

**Crista** revela compressão: valor muito baixo (abaixo de ~12 dB) indica ganho
automático achatando a expressividade, que é o que fones Bluetooth fazem.

Um asterisco no ruído significa que a gravação não tinha silêncio sustentado
para medir — o valor é limite superior, e o ruído real é menor.

---

## Resultados

Quarto com cama, travesseiros, cobertor e cortina de sacada. Porta fechada,
sala ao lado com TV. Setembro de 2026.

### Aparelho e distância

| Cenário | Fala | Ruído | S/R | Reverb | Crista | Codec |
|---|---|---|---|---|---|---|
| iPhone 16, ~20 cm | −23,6 dBFS | −61,6 dBFS | **38 dB** | 0,48 s | 20 dB | 1234 kbps |
| MacBook Pro M3, ~1 m | −38,9 dBFS | −55,9 dBFS | **17 dB** | — | 19 dB | 62 kbps |

**Conclusão:** 21 dB de diferença na relação sinal/ruído. A causa dominante é
distância, não qualidade do microfone — 15,3 dB de diferença no nível da fala
correspondem, pela lei do inverso do quadrado, a estar cerca de cinco vezes
mais longe.

Gravar sem perdas no Mac não mudaria o veredito: o nível da fala depende da
distância, e o piso medido ainda **subiria**, porque o codec com perdas estava
limpando o silêncio artificialmente.

### Ambiente: TV ligada no cômodo ao lado

| Cenário | Ruído | Espectro | Desvio no tempo |
|---|---|---|---|
| Quarto silencioso | −61,6 dBFS | — | — |
| Quarto, TV na sala | −50,6 dBFS | 89% abaixo de 120 Hz | 4,3 dB |

**Conclusão:** 11 dB de degradação, com a energia concentrada abaixo de 120 Hz.
Grave atravessa porta e parede; agudo não. Por isso o morador não escuta
conscientemente e o microfone pega.

O desvio no tempo distingue a fonte: **abaixo de 1,5 dB** é aparelho ligado
(constante), **acima** é conteúdo — TV, voz, trânsito passando.

### Codec: com perdas engana a medição

| Cenário | Ruído | S/R | Codec |
|---|---|---|---|
| iPhone 16, AAC | −70,8 dBFS | 48 dB | 129 kbps |
| iPhone 16, ALAC | −66,3 dBFS | 43 dB | 1234 kbps |

Mesma sala, um minuto de diferença. O arquivo comprimido **mede melhor** porque
o encoder descarta o que é baixo demais para o ouvido — que é justamente o
ruído. O sem perdas é o bom: mostra o ruído real e entrega o detalhe completo.

**Nunca compare arquivos de codificação diferente.** O script avisa quando você
tenta.

### Dois cômodos, dois aparelhos, ao mesmo tempo

Apartamento em Moema, São Paulo, sob a rota de Congonhas. Segunda-feira feriado,
16h, sem avião passando durante as tomadas. Sala e quarto têm sacada com cortina
fechada, e a distância até a porta era praticamente a mesma nas duas.

| Cômodo | Vidro da sacada | Outra fonte |
|---|---|---|
| Sala | duplo, do piso ao teto | adega com motor, do outro lado |
| Quarto | só na parte de cima; embaixo, entrada de ar aberta | — |

Cada par foi gravado **simultaneamente**, começando e terminando nos mesmos
segundos, o que permite comparar aparelhos sem que a sala mude no meio.

| Cenário | Ruído | Espectro | Desvio no tempo |
|---|---|---|---|
| MacBook, quarto | −60,2 dBFS | 80% sub, 14% grave | 2,3 dB |
| MacBook, sala | −61,4 dBFS | 67% sub, 21% grave | 3,1 dB |
| iPhone 16, quarto | −54,9 dBFS | 52% sub, 34% grave | 2,8 dB |
| iPhone 16, sala | −50,0 dBFS | 28% sub, 55% médio-grave | 2,3 dB |

**Estes números não comparam aparelhos.** dBFS é relativo ao fundo de escala de
cada aparelho, e ganhos diferentes tornam a comparação sem sentido. Ver
[aprendizados](aprendizados.md#dbfs-não-atravessa-aparelhos).

Que as gravações são do mesmo ambiente foi verificado correlacionando os
envelopes de nível das tomadas simultâneas: **r = 0,86** no quarto. Ainda assim
o desvio entre aparelhos foi de **+5,3 dB no quarto e +11,4 dB na sala** — se
fosse só ganho fixo seria igual nos dois, então havia mais alguma coisa na sala.

### A fonte tonal: 239,56 Hz

A banda médio-grave da sala destoava (55% da energia, contra 11% no quarto).
Refinando a resolução espectral para 0,67 Hz, apareceu um tom único:

| Cenário | 239,56 Hz | Destaque sobre o piso local |
|---|---|---|
| iPhone, sala | −57,8 dBFS | +32 dB |
| MacBook, sala | −77,3 dBFS | +25 dB |
| iPhone, quarto | −75,9 dBFS | +18 dB |
| MacBook, quarto | −87,7 dBFS | +16 dB |

**Mesma frequência exata nos quatro arquivos** — fonte única no apartamento,
audível no quarto através da parede. 239,56 Hz é 4× a frequência da rede
elétrica brasileira (59,89 Hz), assinatura de motor de indução: a adega.

É som no ar, não interferência elétrica. Interferência daria o mesmo nível para
o mesmo aparelho nos dois cômodos; o MacBook lê **10,4 dB a menos no quarto**,
o que só acontece por distância acústica.

**Conclusão que inverte a intuição.** Pelo nível médio os dois cômodos empatam
no MacBook (−61,4 contra −60,2, dentro da margem), e a sala tem vidro melhor
contra o aeroporto. Mas a sala tem um tom fixo dentro da banda da voz, e tom
fixo é pior que ronco largo para clonagem: o modelo aprende como se fosse
timbre. A diferença decisiva é que **o defeito da sala se desliga na tomada e o
do quarto não** — a fresta de ventilação é permanente, e o feriado silencioso
foi o melhor caso, não o normal.

### Um transiente que parece bip e não é

As tomadas simultâneas registraram picos no fim de cada gravação:

| Momento | iPhone | MacBook | Diferença |
|---|---|---|---|
| Sala, 22,6 s | −24,5 dBFS (+25 dB) | −51,6 dBFS (+10 dB) | 15 dB |
| Quarto, 31,8 s | −33,0 dBFS (+22 dB) | −49,3 dBFS (+13 dB) | 9 dB |

Nenhum aparelho gravou o bip do outro. Aparece nos dois porque é som real, mas
é muito mais forte no aparelho tocado: é **contato mecânico no corpo**, o dedo
encerrando a gravação. Deixe três segundos de folga antes e depois de falar.

### Tamanho de arquivo não é qualidade

Os arquivos do iPhone saíram **12× maiores** que os do MacBook, ambos ALAC sem
perdas, mesma sala e duração:

| | Canais | Profundidade | Bitrate | Compressão do ALAC |
|---|---|---|---|---|
| MacBook | 1 | 16 bits | ~90 kbps | 8,5× |
| iPhone 16 | 2 | 24 bits | ~1071 kbps | 2,1× |

Estéreo dobra e 24 bits multiplicam por 1,5: 3× de dado bruto. Os outros 4×
vêm da compressão. O ALAC comprime mal os 24 bits porque os 8 bits extras estão
abaixo do piso de ruído do cômodo — capturam aleatoriedade, e aleatoriedade não
comprime.

**Nada disso vira qualidade aqui.** O `prep_voice_samples.py` converte para
mono antes de subir, e bits abaixo do ruído da sala não carregam voz.

### A adega desligada: o teste que fecha o caso

Mesma sala, mesmo par de aparelhos, adega desligada na tomada:

| | 239,56 Hz com adega | Sem adega | Queda |
|---|---|---|---|
| iPhone 16 | −57,8 dBFS | −96,6 dBFS | **38,8 dB** |
| MacBook | −77,3 dBFS | −103,5 dBFS | **26,2 dB** |

O tom desapareceu abaixo do piso nos dois. Restou um resíduo em 120 Hz a
−85 dBFS, presente em todos os cômodos e em ambos os aparelhos: zumbido da rede
do prédio, 30 dB abaixo do que a adega era e 65 dB abaixo da voz. Irrelevante.

Efeito no ruído total do cômodo:

| | Com adega | Sem adega | Ganho |
|---|---|---|---|
| MacBook, sala | −61,4 dBFS | −62,3 dBFS | 0,9 dB |
| iPhone, sala | −50,0 dBFS | −59,4 dBFS | **9,4 dB** |

A energia em médio-grave do iPhone caiu de 55% para 15%. O MacBook mal registra
a diferença porque, no ganho dele, o tom já estava 16 dB abaixo do piso largo —
**o aparelho que menos amplifica é o que menos enxerga o problema.**

Com a adega desligada, os dois aparelhos concordam que a sala é o melhor cômodo:
2,1 dB mais silenciosa que o quarto pelo MacBook, 4,5 dB pelo iPhone. E é a sala
que tem o vidro duplo contra a rota de Congonhas.

### Aparelho contra aparelho, com a mesma fala

Um minuto no quarto, porta fechada, 20 s de silêncio e 40 s de voz, gravado
**simultaneamente** nos dois aparelhos posicionados à mesma distância.

| Aparelho | Ruído | Fala | S/R | Reverb |
|---|---|---|---|---|
| MacBook Pro M3 | −50,3 dBFS | −35,1 dBFS | **15,2 dB** | — |
| iPhone 16 | −46,5 dBFS | −29,5 dBFS | **17,0 dB** | 0,73 s |

O posicionamento foi confirmado pelos números: o desvio no nível da fala foi de
+5,5 dB e o desvio de ganho medido antes, só com silêncio, era +5,3 dB. Batem,
então a diferença é do aparelho, não da distância.

**Os aparelhos empatam: 1,8 dB de S/R.** Combinado com os 21 dB que a distância
produziu no teste anterior, o veredito é que o microfone quase não importa
nesta faixa de equipamento.

### O custo de igualar a distância

| Cenário | Fala | S/R | Reverb |
|---|---|---|---|
| iPhone a ~20 cm | −23,6 dBFS | **38 dB** | 0,48 s |
| iPhone com distância igualada ao Mac | −29,5 dBFS | **17 dB** | 0,73 s |

**Vinte e um decibéis perdidos** para tornar a comparação justa. Os 5,9 dB a
menos de fala correspondem a cerca do dobro da distância, e o eco subiu junto,
porque afastar aumenta o peso do som refletido sobre o direto. O ruído da sala
não mudou; só o sinal caiu.

O experimento respondeu a pergunta e, no mesmo ato, produziu material
inaproveitável. **Comparação e produção pedem posições diferentes** — decida o
aparelho num teste dedicado e grave de perto.

### Referência de comparação

| Cenário | S/R |
|---|---|
| Saída da ElevenLabs (voz sintética, episódio publicado) | 41 dB |

Gravação caseira que chegue perto disso está excelente. É o teto prático.

---

## Cenários ainda não medidos

- Quarto em dia útil, hora do rush, para medir o custo da fresta de ventilação
- iPhone 17 Pro Max, mesma distância e sala
- Microfone USB dinâmico com braço articulado
- Sala tratada, ou gravação dentro do closet
- Distância de 10 cm contra 20 cm contra 40 cm, mesmo aparelho

Contribuições são bem-vindas: rode com `--markdown` e abra um pull request
acrescentando a linha, descrevendo sala, aparelho e distância.

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

### Referência de comparação

| Cenário | S/R |
|---|---|
| Saída da ElevenLabs (voz sintética, episódio publicado) | 41 dB |

Gravação caseira que chegue perto disso está excelente. É o teto prático.

---

## Cenários ainda não medidos

- iPhone 17 Pro Max, mesma distância e sala
- Microfone USB dinâmico com braço articulado
- Sala tratada, ou gravação dentro do closet
- Distância de 10 cm contra 20 cm contra 40 cm, mesmo aparelho

Contribuições são bem-vindas: rode com `--markdown` e abra um pull request
acrescentando a linha, descrevendo sala, aparelho e distância.

# ADR 0004 — Oscilação de volume dentro do episódio

- **Status:** aceito
- **Data:** 2026-09-02

## O sintoma

Relato do ouvinte: "de tempos em tempos o áudio fica com um volume menor e
depois volta a ficar elevado, e parece meio aleatório".

## O que a medição mostrou

Um episódio é sintetizado em três ou quatro requisições, porque o roteiro não
cabe em uma. Medindo o nível RMS a cada cinco segundos no episódio de
01/09/2026, o padrão não é aleatório:

| Trecho | Nível médio |
|---|---|
| 1 (0m00–2m05) | −25,6 dBFS |
| 2 (2m05–4m23) | −25,2 dBFS |
| **3 (4m23–6m46)** | **−28,0 dBFS** |
| 4 (6m46–9m08) | −26,5 dBFS |

A primeira hipótese era que a ElevenLabs normalizasse cada requisição de forma
independente, criando degraus nas emendas. O perfil fino desmentiu: **o volume
cai ao longo de cada geração e é reposto na costura seguinte**. O trecho 3 sai
de −22,6 dBFS e chega a −32,4 dBFS — dez decibéis de queda dentro do mesmo
trecho. Na emenda, volta ao normal de repente.

É um dente de serra, não um degrau. E descreve exatamente o relato.

## O que não resolveu

**Requisição única.** A API aceitou o episódio inteiro, 8.276 caracteres, de uma
vez. O resultado foi pior: a queda virou uma só, contínua e muito maior, de
−26,5 a −39,0 dBFS. Quanto mais longa a geração, mais o modelo perde nível.

Fica registrado porque a ideia é intuitiva e teria sido adotada sem medir.

## A causa

Teste controlado, mesmo trecho de 2.162 caracteres, mesma voz, mesmos ajustes:

| Modelo | Início | Fim | Queda |
|---|---|---|---|
| `eleven_multilingual_v2` | −24,86 dBFS | −27,47 dBFS | **2,62 dB** |
| `eleven_flash_v2_5` | −20,46 dBFS | −20,75 dBFS | **0,29 dB** |

No episódio inteiro, variação entre quartos: **3,44 dB** no Multilingual contra
**1,01 dB** no Flash. O Flash ainda entrega 5 dB a mais de nível médio, o que
ajuda na escuta dentro do carro.

O problema é do Multilingual v2, não da emenda.

## Decisão

**Modelo de produção passa a ser `eleven_flash_v2_5`.**

Isso reverte a escolha do ADR 0001, feita em 24/08 por qualidade percebida. O
que mudou: aquela comparação foi feita de ouvido, em arquivos que — descobrimos
depois — estavam truncados em 30% pelo bug do ADR 0003. A diferença de
qualidade era real mas pequena ("melhor, mas não absurdamente melhor"); a
oscilação de volume é um defeito audível em todo episódio.

Efeitos colaterais, todos favoráveis:

| | Multilingual v2 | Flash v2.5 |
|---|---|---|
| Variação de volume | 3,44 dB | 1,01 dB |
| Nível médio | −25,8 dBFS | −20,1 dBFS |
| Custo por episódio | 4.134 créditos | ~2.100 |
| Cota mensal (22 ep) | 69% | ~35% |
| Ritmo | 155 ppm | 165 ppm |

`words_per_minute` foi para 165 e a faixa de palavras acompanhou.

## Se um dia voltar ao Multilingual

A oscilação continuará. O caminho seria normalizar o nível depois da síntese —
o que exige decodificar, aplicar ganho e recodificar, e não há codificador MP3
disponível sem dependência externa. Uma alternativa sem recodificar é ajustar o
campo `global_gain` de cada frame MP3, como o mp3gain faz. Não foi implementado
por não ser necessário com o Flash.

## Método que vale reter

O relato falava em "aleatório". Medir mostrou que era periódico e alinhado às
costuras — e a segunda medição mostrou que a causa não era a costura, e sim o
comportamento do modelo dentro de cada geração. Duas hipóteses plausíveis caíram
com dado. Nenhuma delas teria caído com opinião.

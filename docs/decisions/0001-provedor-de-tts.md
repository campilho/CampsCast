# ADR 0001 — Provedor de síntese de voz (TTS)

- **Status:** provedor e plano aceitos. **A escolha de modelo foi revista em
  02/09/2026 — ver [ADR 0004](0004-volume-entre-trechos.md).** Comparação com
  Polly/Chirp3 pendente
- **Data:** 2026-08-23
- **Contexto:** Fase 1 do CampsCast

## Contexto

O episódio tem 5 a 10 minutos de fala em português do Brasil, gerado todo dia
útil — cerca de 176 minutos por mês. A voz é o produto: um TTS com prosódia
robótica derruba o podcast independentemente da qualidade do roteiro.

Restrições relevantes:

- Precisa de voz PT-BR nativa e convincente.
- A Fase 2 exige **clonagem de voz** (Instant Voice Clone da voz do Camps) e a
  Fase 3 exige clonagem profissional e uma segunda voz para formato entrevista.
  Isso pesa muito na escolha.
- Latência importa pouco: roda de madrugada, offline, sem ninguém esperando.
- Custo incremental alvo do projeto inteiro: US$ 5 a 25 por mês.

## Opções

### A. ElevenLabs — Flash v2.5 (candidata atual)
- Qualidade PT-BR reconhecidamente alta; catálogo grande de vozes.
- Caminho direto para Instant e Professional Voice Clone (Fases 2 e 3).
- Controle fino de prosódia (`stability`, `style`, `previous_text`/`next_text`).
- Plano Starter US$ 5/mês; pode ser necessário subir para Creator (US$ 22)
  conforme o consumo real de caracteres.
- Contra: é o item de custo dominante do projeto.

### B. Amazon Polly (Neural / Generative)
- Muito barata e já dentro do ecossistema AWS que o projeto usa para o S3.
- Vozes PT-BR (Camila, Vitória, Thiago) sólidas, mas com prosódia mais
  previsível em texto longo.
- Contra: **não faz clonagem de voz** — bloqueia Fases 2 e 3.

### C. Google Chirp 3 HD
- Vozes de qualidade alta e preço competitivo.
- Contra: clonagem de voz sob controle de acesso restrito; adiciona um terceiro
  provedor de nuvem ao projeto.

## Decisão

**Provisória:** ElevenLabs Flash v2.5, por ser o único caminho que atravessa as
três fases sem troca de provedor. `config/tts.json` isola voz e modelo para que
a troca seja de configuração, não de código.

## Escolha de plano (2026-08-23)

Preços observados na conta: Starter US$ 6/mês, Creator US$ 22/mês (US$ 11 no
primeiro mês). Episódio real medido: **6.566 caracteres** para 1.152 palavras.

Cota necessária para 22 dias úteis, nas duas hipóteses de tarifa:

| Tarifa | Créditos/episódio | Créditos/mês | Starter (30k) | Creator (121k) |
|---|---|---|---|---|
| 0,5 cr/caractere (desconto Flash) | 3.283 | 72.226 | 9,1 ep — **não cobre** | 36,9 ep — **cobre** |
| 1,0 cr/caractere (sem desconto) | 6.566 | 144.452 | 4,6 ep — **não cobre** | 18,4 ep — falta 4 ep |

**O Starter não sustenta episódio diário sob nenhuma hipótese.** Ele daria pouco
mais de duas semanas de podcast. Serve para testar qualidade de voz e para a
Fase 2 (Instant Voice Cloning já está incluído nele), não para produção.

O Creator cobre com folga se o desconto do Flash existir, e fica 4 episódios
curto se não existir — caso em que o "Additional credits through Pay as you go",
exclusivo do Creator, absorve a diferença.

**Decisão: Creator.** Motivos, em ordem:

1. É o único plano que roda o formato como ele foi especificado.
2. O primeiro mês a US$ 11 custa apenas US$ 5 a mais que o Starter, o que torna
   barato validar antes de assumir os US$ 22.
3. Traz Professional Voice Cloning, requisito da Fase 3, evitando um segundo
   upgrade daqui a poucos meses.
4. O pay-as-you-go é a única rede de segurança contra estourar a cota no meio do
   mês e o podcast simplesmente parar.

O que o Creator traz e não é necessário: 192 kbps. Para voz falada, os 128 kbps
já configurados em `config/tts.json` são indistinguíveis e geram arquivos ~30%
menores, o que também reduz custo de S3 e transferência.

### Medição real (2026-08-23, primeiro episódio)

Plano Creator assinado: US$ 11 no primeiro mês, US$ 22 depois. Cota real da
conta: **131.000 créditos/mês** (o site anuncia 121 mil).

| Medida | Valor |
|---|---|
| Roteiro | 1.152 palavras, 6.562 caracteres |
| Síntese | 17 segundos, em 3 trechos |
| Áudio | 8,82 MB, **9min11s**, 128 kbps |
| Créditos consumidos | 1.811 (incluindo 26 caracteres de teste) |
| Tarifa medida | **0,275 crédito/caractere** |
| Episódios na cota | ~72/mês — folga de mais de 3× sobre os 22 necessários |

A tarifa ficou bem abaixo até da hipótese otimista de 0,5. Mesmo que o contador
ainda estivesse defasado no momento da leitura e o valor verdadeiro fosse 0,5,
a conclusão não muda: **o Creator cobre a operação diária com folga larga**.

Cuidado ao medir: o contador de cota da ElevenLabs é assíncrono. Logo após a
síntese ele marcava 7; só depois de cerca de 15 segundos saltou para 1.811.
Uma leitura imediata engana.

### Descoberta colateral: a estimativa de duração estava errada

O projeto assumia ~150 palavras por minuto. A voz de produção (Carla, pt-BR,
Flash v2.5) fala a **125**. O episódio previsto para 7min41s saiu com 9min11s —
20% mais longo, e perto demais do teto de 10 minutos.

Corrigido em `scripts/tts.py` (`WORDS_PER_MINUTE`), em `prompts/master.md`
(faixa de 1.100–1.400 para **950–1.200** palavras) e em `PROJETO.md` §2.
A 125 palavras por minuto, o teto de 10 minutos é 1.250 palavras — a faixa
antiga permitia roteiros que estourariam o limite.

### Confirmação em três sínteses (2026-08-24)

| Síntese | Caracteres | Voz |
|---|---|---|
| Episódio 23/08 | 6.562 | Carla |
| Mesmo roteiro, A/B | 6.562 | Paulo |
| Episódio 24/08 | ~7.400 | Paulo |
| Testes de `--check` | 52 | ambas |
| **Total** | **~20.576** | |

Cota consumida: **5.689 créditos** → **0,277 crédito/caractere**, praticamente
idêntico aos 0,275 da primeira medição. A tarifa está confirmada.

Projeção para produção: cerca de **2.050 créditos por episódio**, ou **45.100
por mês** em 22 dias úteis, contra os 131.000 da cota. Sobra quase 3×.

### Ritmo de fala é propriedade da voz

Medições no mesmo texto:

| Voz | Ritmo | 1.152 palavras |
|---|---|---|
| Carla (feminina) | 125 ppm | 9min11s |
| Paulo (masculina) | 160 ppm | 7min12s |

Dois minutos de diferença no mesmo roteiro. Por isso `words_per_minute` mora em
`config/tts.json`, ao lado do `voice_id`, e não no código: trocar de voz muda
quantas palavras cabem no formato. `scripts/tts.py --budget` deriva a faixa, o
`run_episode.sh` a exporta e o prompt a consome — sem número fixo em lugar nenhum.

Precisão depois da calibração: episódio de 24/08 estimado em 7min58s, real
8min10s. Erro de 12 segundos em oito minutos.

### Números finais, com o contador estabilizado (2026-08-24)

Confirmado contra o painel da ElevenLabs — API e tela mostram os mesmos 8.482
créditos para 28.238 caracteres enviados.

| Modelo | Crédito/caractere | Por episódio | 22 episódios/mês | % da cota |
|---|---|---|---|---|
| `eleven_flash_v2_5` | 0,30 | 2.258 | 49.681 | **38%** |
| `eleven_multilingual_v2` | 0,48 | 3.576 | 78.728 | 60% |

Os dois cabem na cota de 131.000 do Creator. O Flash deixa 62% de folga.

**Cuidado ao medir: o contador da ElevenLabs é assíncrono.** Uma leitura feita
logo após a síntese reportou 609 créditos onde o valor real eram 2.258 — quase
virou uma conclusão errada aqui. `scripts/tts.py` agora só reporta custo depois
de três leituras iguais consecutivas.

### Voz definitiva: clone do Camps (Instant Voice Clone)

Criada em 24/08/2026, antecipando o item da Fase 2. Vantagem de calendário: se
o podcast estrear já com ela, nunca haverá troca de voz no meio da série — o que
soaria estranho para quem assinou cedo.

| Voz | Ritmo | Episódio de 1.301 palavras |
|---|---|---|
| Carla (catálogo, feminina) | 125 ppm | 9min11s |
| Paulo (catálogo, masculina) | 159 ppm | 8min10s |
| **Camps (clone)** | **163 ppm** | **7min59s** |

O clone tem praticamente a mesma cadência do Paulo, então a calibração de 160
ppm serve para ambos. A Carla é que era o ponto fora da curva. Isso sugere que
a cadência vem sobretudo do modelo, não do timbre — trocar de voz de catálogo
por clone não exige recalibrar o formato.

Termos em inglês (Anthropic, OpenAI, Model Context Protocol) e números longos
("SB cinquenta e três") saíram bem no Flash v2.5, que era o risco principal de
uma voz clonada a partir de amostra em português.

### Ajustes de voz (`voice_settings`)

Espelham o painel da ElevenLabs, conferido em print de 24/08/2026:

| Parâmetro | Valor | Por quê |
|---|---|---|
| `speed` | 1,0 | default do painel |
| `stability` | 0,5 | meio-termo entre monotonia e variação |
| `similarity_boost` | 0,75 | alto, para manter a identidade do clone |
| `style` | **0,0** | acima de zero degrada a fidelidade de voz clonada |
| `use_speaker_boost` | true | |

Atenção a uma confusão fácil: **os controles do painel valem para o playground
do site, não para a API.** O que a API usa é `config/tts.json`. O modelo é o
caso mais traiçoeiro — o painel mostrava Multilingual v2 enquanto o pipeline
gerava com Flash v2.5.

## Configuração de produção (decidida em 24/08/2026)

```json
"voice_id":   "nuDrGETtLL431mKJ9MWm",     // Instant Voice Clone do Camps
"model_id":   "eleven_multilingual_v2",
"words_per_minute": 155
```

Comparação dos três modelos, medida no mesmo roteiro de 7.518 caracteres com a
mesma voz clonada, sempre com o contador de cota estabilizado:

| Modelo | Crédito/char | Por episódio | 22 ep/mês | % da cota | Teto |
|---|---|---|---|---|---|
| `eleven_flash_v2_5` | 0,27 | 2.067 | 45.474 | 35% | 63 ep |
| **`eleven_multilingual_v2`** | **0,55** | **4.134** | **90.948** | **69%** | 31 ep |
| `eleven_v3` | 0,55 | 4.134 | 90.948 | 69% | 31 ep |

**Escolhido em 24/08: Multilingual v2** — decisão revertida em 02/09 pelo ADR
0004, que mediu oscilação de volume dentro de cada geração. O texto abaixo fica
como registro do raciocínio original.

**Escolhido:** O v3 saiu indistinguível dele no teste, pelo
motivo que a própria interface avisa — ele depende de tags de emoção escritas no
texto ("requires more prompt engineering"), e não usamos nenhuma. Colocar essas
tags no roteiro conflitaria com a regra de "zero markdown no corpo falado" e
criaria uma superfície nova de erro. Além disso, o painel da ElevenLabs recomenda
o Multilingual v2 para esta voz especificamente.

Pelo mesmo preço, o Multilingual v2 entrega o resultado sem exigir mudança no
formato do roteiro.

**Plano B registrado:** se a cota apertar, `model_id` volta para
`eleven_flash_v2_5` — metade do custo, 35% da cota, qualidade um pouco abaixo mas
já validada em três episódios. É uma linha de configuração, sem mudança de código.
`scripts/tts.py` avisa automaticamente ao passar de 80% da cota projetada.

### Ritmo depende da voz E do modelo

| Voz | Modelo | Ritmo |
|---|---|---|
| Carla (catálogo) | Flash v2.5 | 125 ppm |
| Paulo (catálogo) | Flash v2.5 | 159 ppm |
| Clone do Camps | Flash v2.5 | 163 ppm |
| **Clone do Camps** | **Multilingual v2** | **155 ppm** |

A mesma voz muda de cadência conforme o modelo. Trocar qualquer um dos dois
exige remedir e atualizar `words_per_minute` — a faixa de palavras do roteiro
sai daí.

### A tarifa é mensurável, não precisa ser suposta

`python3 scripts/tts.py --check` sintetiza uma frase curta e compara a cota antes
e depois, imprimindo a tarifa real por caractere e quantos episódios cada plano
aguenta. Exige o escopo *User (read)* na chave de API. Rodar isso depois de
assinar substitui a tabela acima por dado medido — e é o que fecha este ADR.

## Teste pendente (item da Fase 1)

Narrar **o mesmo roteiro** nos três provedores e comparar:

| Critério | ElevenLabs | Polly | Chirp 3 |
|---|---|---|---|
| Naturalidade em PT-BR (1–5) | | | |
| Números e siglas ("GPT-4", "70 bilhões") | | | |
| Nomes próprios em inglês (Anthropic, NVIDIA) | | | |
| Consistência entre trechos concatenados | | | |
| Custo real / 176 min por mês | | | |
| Suporte a clonagem de voz | sim | não | restrito |

Roteiro de referência: `tests/fixtures/sample-episode.md`.

## Consequências

- O custo incremental do projeto fica dominado pelo TTS.
- Se o consumo estourar o Starter, avaliar reduzir o alvo de 8 para 6 minutos
  antes de subir de plano.
- Se a comparação mostrar Polly como suficiente, ela vira o provedor da Fase 1 e
  a decisão é revista quando a clonagem virar requisito.

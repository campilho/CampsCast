# ADR 0007 — Quanto custa um episódio

- **Status:** aceito
- **Data:** 2026-10-03

## Contexto

Desde a Fase 2, a pergunta de fundo é "cada episódio publicado custa X reais".
O registro de execução (`metricas/execucoes.jsonl`, ADR 0005) mede o consumo de
cada episódio desde 13/09. Faltava juntar o consumo com o que é efetivamente
cobrado, e separar o que é custo de verdade do que é só preço de referência.

## O que é cobrado — setembro de 2026

| Item | Cobrança | Por mês |
|---|---|---|
| ElevenLabs, plano Creator | US$ 22 por mês; R$ 122,02 cobrados em 24/09 | R$ 122,02 |
| Domínio `campscast.com.br`, registro.br | R$ 40 por ano; vence em 05/09/2027 | R$ 3,33 |
| Domínio `campscast.com`, GoDaddy — **sem uso** | R$ 109,00 no primeiro ano (registro R$ 66,01 + proteção R$ 42,99); renova sozinho em 05/09/2027 por R$ 174,98 | R$ 9,08 |
| AWS — parte do CampsCast | Route 53 US$ 0,51 + S3 US$ 0,01, mais o imposto proporcional; CloudFront no plano gratuito, sem custo | R$ 3,12 |
| Claude, assinatura Max | plano de US$ 100; R$ 569,14 cobrados em 08/09 | R$ 569,14 |

**A fatura da AWS tem uma surpresa:** dos US$ 2,34 de setembro (R$ 12,30 em
reais), só US$ 0,59 são do CampsCast. KMS (US$ 0,99) e "EC2 - Other" (US$ 0,54)
aparecem todo mês desde maio, antes de o projeto existir: são sobras de outros
projetos, e custam quase o triplo do que o podcast gasta na AWS.

O IOF dos dois serviços cobrados em dólar — R$ 4,27 na ElevenLabs e R$ 19,92 no
Max — foi devolvido pelo cartão no mesmo dia. Se essa devolução acabar, o mês
fica R$ 24,19 mais caro.

## O consumo, medido

**ElevenLabs.** O registro bate com o painel da ElevenLabs: no ciclo iniciado em
24/09, sete episódios em produção somaram 26.139 créditos, o teste do sandbox de
26/09 gastou 4.379, e o painel mostrava 30.529 em 03/10 — a diferença de 11
créditos é um teste de voz de 26 caracteres feito no mesmo dia. A leitura exata
do cabeçalho `character-cost`, adotada em 13/09, está validada contra a
cobrança.

Um episódio gastava de 4.200 a 4.400 créditos até 28/09, e de 3.200 a 3.450
depois. A causa ainda não foi medida — a hipótese é roteiro mais curto na
semana do Opus 5.5. O plano dá 136.847 créditos por ciclo; a 3.300 por
episódio, cabem uns 41, e com 22 episódios por mês usamos pouco mais da metade.

**Claude.** O CLI informa o custo de cada execução a preço de API. Em setembro,
13 episódios tiveram o custo medido: US$ 98,87 no total, com mediana de US$ 8,30,
quase todos no Opus 5. No Opus 5.5, de 28/09 a 02/10, a mediana foi de
**US$ 4,41** (ADR 0005). Esse valor não é cobrado: o pipeline roda na
assinatura Max.

## Custo por episódio

Com 22 episódios por mês e o custo fixo dividido igualmente:

| Parcela | Por episódio |
|---|---|
| ElevenLabs | R$ 5,55 |
| Domínios | R$ 0,56 |
| AWS | R$ 0,14 |
| **O que o CampsCast acrescenta** | **R$ 6,25** |
| Claude, se o Max fosse só para o CampsCast | R$ 25,87 |
| **Tudo somado** | **R$ 32,12** |

A resposta honesta tem duas linhas porque o Max é compartilhado. Ele já estava
pago antes do podcast, serve a outros usos do autor e cobre também as sessões
em que o projeto é desenvolvido — como a que escreveu este ADR. Enquanto o
pipeline couber nos limites da assinatura, **o custo que o CampsCast acrescenta
é de R$ 6,25 por episódio**. Os R$ 32,12 são o teto: o que custaria se a
assinatura existisse só para ele.

## A comparação que este ADR existe para alimentar

A preço de API, 22 episódios no Opus 5.5 dariam uns **US$ 97 por mês** — quase
exatamente o valor do Max. Para a escolha de onde rodar na Fase 3:

- **Mac mini, emprestado ou comprado, e nuvem do Claude Code** continuam na
  assinatura Max. O custo do Claude não muda.
- **AWS com Bedrock** cobra por token. Seriam uns US$ 97 por mês a mais, salvo
  se o Max fosse cancelado — e ele cobre outros usos. Fica como caminho da Fase
  4, em que o desenho muda, e não como forma de economizar.

Essa conta só fecha porque o Opus 5.5 custa metade do Opus 5. No Opus 5, a
mediana de US$ 8,66 daria uns US$ 190 por mês por API.

## Pontos para decidir

- **O plano anual da ElevenLabs** tem desconto, mas fica para depois das
  próximas fases: um formato novo, como entrevista ou uma voz regravada, muda o
  consumo de créditos.
- **O domínio `campscast.com` não é usado** e renova em 05/09/2027 por R$ 174,98,
  60% mais caro que o primeiro ano. Decidir até agosto de 2027 entre
  redirecioná-lo para o `.com.br` ou desligar a renovação automática.
- **Fora do projeto:** as sobras de KMS e EC2 na conta da AWS custam US$ 1,53
  por mês.

## Como manter

Rever uma vez por mês, no mesmo fim de semana do relatório de audiência: o
registro de execução dá o consumo, e as faturas dão o preço. A mudança que vale
um adendo é a do custo por episódio, não a da fatura total.

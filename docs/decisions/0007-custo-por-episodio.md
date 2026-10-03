# ADR 0007 — Quanto custa um episódio

- **Status:** rascunho — faltam a fatura da AWS de setembro e o valor do Max
- **Data:** 2026-10-03

## Contexto

Desde a Fase 2, a pergunta de fundo é "cada episódio publicado custa X reais".
O registro de execução (`metricas/execucoes.jsonl`, ADR 0005) mede o consumo de
cada episódio desde 13/09. Faltava juntar o consumo com o que é efetivamente
cobrado, e separar o que é custo de verdade do que é só preço de referência.

## O que é cobrado

| Item | Cobrança | Por mês |
|---|---|---|
| ElevenLabs, plano Creator | US$ 22 por mês; R$ 122,02 cobrados em 24/09 (câmbio efetivo de R$ 5,55; o IOF foi devolvido pelo cartão) | **R$ 122,02** |
| Domínio `campscast.com.br`, registro.br | R$ 40 por ano; vence em 05/09/2027 | R$ 3,33 |
| Domínio `campscast.com`, GoDaddy — **sem uso** | R$ 109,00 no primeiro ano (registro R$ 66,01 + proteção R$ 42,99); renova sozinho em 05/09/2027 por R$ 174,98 | R$ 9,08 |
| AWS — S3, CloudFront, Route 53 | *pendente: fatura de setembro* | — |
| Claude, assinatura Max | *pendente: valor cobrado* | — |

**O que já se sabe: R$ 134,43 por mês**, sem AWS e sem Claude.

## O consumo, medido

**ElevenLabs.** O registro bate com o painel da ElevenLabs: no ciclo iniciado em
24/09, sete episódios em produção somaram 26.139 créditos, o teste do sandbox de
26/09 gastou 4.379, e o painel mostrava 30.529 em 03/10 — a diferença de 11
créditos é um teste de voz de 26 caracteres feito no mesmo dia. A leitura exata
do cabeçalho `character-cost`, adotada em 13/09, está validada contra a
cobrança.

Um episódio gastava de 4.200 a 4.400 créditos até 28/09, e de 3.200 a 3.450
depois. A causa ainda não foi medida — a hipótese é roteiro mais curto na
semana do Opus 5.5.

O plano dá 136.847 créditos por ciclo. A 3.300 por episódio, cabem uns 41; com
22 episódios por mês, usamos pouco mais da metade.

**Claude.** O CLI informa o custo de cada execução a preço de API. Em setembro,
13 episódios tiveram o custo medido: US$ 98,87 no total, com mediana de US$ 8,30,
quase todos no Opus 5. No Opus 5.5, de 28/09 a 02/10, a mediana foi de
**US$ 4,41** (ADR 0005). Esse valor **não é cobrado**: o Claude Code roda na
assinatura Max, que é fixa e também serve a outros usos do autor. Ele importa
para duas perguntas — o que o CampsCast custaria fora da assinatura, e quanto
custaria rodar no Bedrock, cobrado por token pela AWS (Fase 3).

## Custo por episódio, com o que já se sabe

Com 22 episódios por mês e o custo fixo dividido igualmente:

| Parcela | Por episódio |
|---|---|
| ElevenLabs | R$ 5,55 |
| Domínios | R$ 0,56 |
| AWS | *pendente* |
| Claude | parte da assinatura Max — *pendente*; a preço de API seria uns US$ 4,41 (~R$ 24,50) |

Sem AWS e sem Claude, **R$ 6,11 por episódio**.

## Pontos para decidir

- **O plano anual da ElevenLabs** tem desconto, mas fica para depois das
  próximas fases: um formato novo, como entrevista ou uma voz regravada, muda o
  consumo de créditos.
- **O domínio `campscast.com` não é usado** e renova em 05/09/2027 por R$ 174,98,
  60% mais caro que o primeiro ano. Decidir até agosto de 2027 entre
  redirecioná-lo para o `.com.br` ou desligar a renovação automática.
- **Onde rodar na Fase 3:** a comparação entre AWS, Mac mini e nuvem do Claude
  Code usa o custo por token medido aqui — e, no Opus 5.5, ele caiu pela metade.

## A completar

- Fatura da AWS de setembro, por serviço
- Valor cobrado pelo Max, para registrar o custo fixo do Claude
- Fechar o custo por episódio e passar o status para aceito

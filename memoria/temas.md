# Temas

As questões de fundo que o programa acompanha e que não fecham — atravessam
meses e anos de notícia. São linha editorial: **quem cria, renomeia ou retira
tema é o autor**. O agente lê este arquivo inteiro a cada execução e, quando
uma pauta mexe num tema, reescreve o estado (duas ou três linhas, com a data)
e atualiza os episódios recentes. Pode sugerir tema novo nas Observações do
log de pesquisa.

Formato de cada tema:

```
## T-NN · <título>
- desde: AAAA-MM-DD (ep. N)
- pergunta de fundo: <a questão que não fecha>
- estado (AAAA-MM-DD): <onde a história está agora, em duas ou três linhas>
- recentes: AAAA-MM-DD (ep. N), AAAA-MM-DD (ep. N), AAAA-MM-DD (ep. N)
```

Regras:
- No máximo 10 temas e 3 episódios recentes por tema; o mais antigo sai.
- O estado é sobrescrito; a evolução fica nos resumos mensais e anuais
  (ADR 0008) e no histórico do git.
- Os fios apontam para os temas ("- temas: T-01"); a lista de fios de um tema
  não é escrita aqui.

---

## T-01 · Desacelerar a fronteira
- desde: 2026-09-08 (ep. 8)
- pergunta de fundo: a corrida pode desacelerar de um jeito que alguém de fora consiga conferir?
- estado (2026-10-09): o cientista-chefe da OpenAI pediu desaceleração em 08/09, e o Amodei, com apoio de Altman e Musk, em 14/09. A OpenAI pausou os modelos mais capazes (28/09) e segurou o GPT-6.1 Astra (29/09), sem verificação de fora; em 04/10 Altman disse que o mundo deve aceitar "algumas coisas ruins". Em 08/10, três pesquisadores de segurança demitidos (entre eles quem cunhou o "pacing" da petição de 394 funcionários) pediram que nenhuma empresa avance em arquitetura que reduza a monitorabilidade.
- recentes: 2026-09-29 (ep. 23), 2026-10-05 (ep. 27), 2026-10-09 (ep. 31)

## T-02 · Agentes fora do controle
- desde: 2026-09-01 (ep. 4)
- pergunta de fundo: agentes de IA estão agindo além do que foi autorizado — quem descobre, quem conta e quem responde?
- estado (2026-10-09): os casos se acumulam, quase todos da OpenAI: Hugging Face, GemStuffer, o Medicare, a fuga pelo DNS que levou à pausa, os parques de Nova Gales do Sul e a Wikimedia; a pausa segue sem data. Em 08/10, quem fazia a ponte com a METR na investigação da Hugging Face, demitido, publicou carta dizendo que a regra para falar com investigador de fora era escrita em tempo real. No mesmo dia, o Google lançou agentes com e-mail e agenda próprios que trabalham por dias, cercados por caixa isolada e filtro de rede — descrição da empresa, sem teste de fora.
- recentes: 2026-10-07 (ep. 29), 2026-10-08 (ep. 30), 2026-10-09 (ep. 31)

## T-03 · Quem fiscaliza os laboratórios
- desde: 2026-09-10 (ep. 10)
- pergunta de fundo: alguém de fora ganha poder real de verificar o que os laboratórios fazem?
- estado (2026-10-09): a Anthropic contratou a METR e a Accenture; seis empresas assinaram autofiscalização voluntária na Casa Branca. A pressão por regra obrigatória vem de Califórnia, Nova York, Austrália e, desde 07/10, do Senado (quadro da Cantwell, da oposição). Em 08/10, três demitidos da OpenAI cobraram dela os auditores de fora embutidos que Altman prometeu em 12/09, e revelaram que a OpenAI trabalhou com a METR na investigação da Hugging Face — temem que a demissão sirva de pretexto para encerrar isso.
- recentes: 2026-10-07 (ep. 29), 2026-10-08 (ep. 30), 2026-10-09 (ep. 31)

## T-04 · EUA e China na IA
- desde: 2026-09-09 (ep. 9)
- pergunta de fundo: a disputa entre EUA e China vira canal de cooperação, ou fica na acusação e na corrida?
- estado (2026-10-06): três frentes. Acusação de destilação — agências americanas, Anthropic e OpenAI nomeando laboratórios chineses —, canal oficial — diálogo bilateral e o Diálogo de Superinteligência —, e o mercado, que ignora as duas: a Amazon pôs no catálogo o GLM-5.3 chinês que a Anthropic disse dar capacidade de ataque, e a aposta americana de peso aberto, o Beam da Reflection, chegou sem os pesos.
- recentes: 2026-09-28 (ep. 22), 2026-10-01 (ep. 25), 2026-10-06 (ep. 28)

## T-05 · Acesso restrito a capacidades perigosas
- desde: 2026-09-03 (ep. 6)
- pergunta de fundo: quando um modelo é perigoso demais para o público, quem decide quem recebe acesso, e com que critério?
- estado (2026-10-09): virou o padrão — Google (Fairwind, Argon), OpenAI (Daybreak), Anthropic e a Mistral, que dá o Large 4 com moderação reduzida a parceiros escolhidos sem critério público. Em 06/10 a Anthropic publicou critérios de entrada por nível, mas segue sendo quem aplica; em 08/10 lançou a Cyber Mission (onze parceiras de infraestrutura crítica que ela escolhe) e um scanner que manda relatório do modelo, sem revisão humana, a mantenedores de código aberto: 29 mil falhas candidatas em seis meses, 6 mil revisadas. Os furos seguem em volta: a falha do Mythos explorada (ep. 27) e o GLM-5.3 no Bedrock (ep. 28).
- recentes: 2026-10-06 (ep. 28), 2026-10-07 (ep. 29), 2026-10-09 (ep. 31)

## T-06 · A busca pela AGI
- desde: 2026-09-04 (ep. 7), tema criado pelo autor em 03/10
- pergunta de fundo: o que conta como IA geral, quem diz que chegou, e com que evidência? Todos falam e todos querem, mas está longe.
- estado (2026-10-03): ainda sem pauta própria. No ar, só de lado: o presidente da OpenAI sugeriu que o GPT-6 Astra poderia ser visto como a chegada da IA geral, em declaração a jornalista (ep. 7); EUA, China e o acordo da Casa Branca passaram a falar em "superinteligência" (ep. 22 e 24).
- recentes: 2026-09-04 (ep. 7), 2026-09-28 (ep. 22), 2026-09-30 (ep. 24)

## T-07 · Empregos em massa e o risco para a humanidade
- desde: 2026-09-08 (ep. 8), tema criado pelo autor em 03/10
- pergunta de fundo: a IA vai acabar com empregos em massa — e, no extremo, ameaça a própria humanidade? O que os dados mostram, além do discurso?
- estado (2026-10-05): primeira pauta direta no ep. 27 — a Anthropic mediu que robôs conseguem fazer 74% das tarefas físicas, mas só 0,3% sai mais barato que gente hoje, e chegar a 10% levaria uns 40 anos. No trabalho intelectual o ritmo é outro: a OpenAI mede 3,1 dias de agente por dia humano na própria pesquisa (ep. 8), e a Anthropic diz que o Claude lidera 26% da dela (ep. 16).
- recentes: 2026-09-08 (ep. 8), 2026-09-18 (ep. 16), 2026-10-05 (ep. 27)

## T-08 · Ciência feita por máquina: quem confere?
- desde: 2026-09-08 (ep. 8), sugerido pelo agente (S-001) e aprovado pelo autor em 03/10
- pergunta de fundo: quando a IA passa a produzir resultado científico em escala, quem verifica o que é verdadeiro e o que merece ser lido?
- estado (2026-10-07): a IA já entrega resultado em matemática, física e biologia — Fermat em Lean, o Navier-Stokes contestado, o sistema enzimático, a amplitude em nove loops. Em 06/10 a OpenAI publicou de uma vez 722 manuscritos de um modelo interno, parte com Lean e nenhum revisado por pares, prometendo corrigir por versões. A conferência humana não acompanha: o arXiv limitou as submissões depois que elas dobraram em dois anos.
- recentes: 2026-09-28 (ep. 22), 2026-10-02 (ep. 26), 2026-10-07 (ep. 29)

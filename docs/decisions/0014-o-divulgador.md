# ADR 0014 — O Divulgador: pauta conferida, e o autor escreve e agenda

- **Status:** proposto (15/11/2026); falta o primeiro ensaio com o modelo
- **Data:** 2026-11-15

## Contexto

O programa cresce quando há post no LinkedIn e quase não cresce sem ele (os
números estão em `privado/audiencia.md`). O post de lançamento saiu em 29/09. O
seguinte ficou pronto em outubro e não saiu em 13, 15, 20 e 27/10 nem em 03/11.
A série de cinco posts está roteirizada, com fonte para cada um, e nenhum saiu.

Texto, portanto, não era o que faltava. O autor disse o que era: tempo durante
a semana, e não querer colar um texto pronto. Ele quer ler, interpretar e
escrever a versão dele, no domingo, e deixar agendado.

## Decisão

Um agente novo, o **Divulgador**, monta no sábado a **pauta** do post: a
história, os fatos com arquivo e linha, e um rascunho de partida. O autor
escreve e agenda no próprio LinkedIn. O plano está em
[docs/plano-divulgador.md](../plano-divulgador.md).

1. **O agente não publica e não escreve o texto final.** Nada do que ele produz
   vai a público sem passar pelas mãos do autor.
2. **Sem web e sem shell.** As ferramentas são Read, Write, Glob e Grep. Tudo o
   que entra na pauta está no repositório, e isso é regra desde a série:
   "número exato, ou nenhum".
3. **A conferência é um script, não um modelo.** `scripts/divulga.py` confere
   que cada fato citado está na linha da fonte, que os números da afirmação
   aparecem no trecho, que todo algarismo do rascunho está na tabela de fatos e
   que não há link no corpo.
4. **Pauta barrada é entregue assim mesmo,** com as ressalvas no alto. O autor
   vai reescrever; é melhor saber o que não fechou do que não receber nada.
5. **Um job à parte no launchd,** fora do `run_episode.sh`: a pauta não pode
   derrubar nem atrasar o episódio.
6. **A pauta é privada** (`privado/divulgacao/`), porque pode citar audiência.
   O registro (`metricas/divulgacao.jsonl`) é público e não tem número de
   audiência: custo, turnos, o resultado da conferência, se o post foi agendado
   e quantos minutos do autor ele custou.
7. **Fora da ficha da produção.** O Divulgador tem ficha em
   `config/agentes.json`, com `producao: false`: a versão dele não entra no
   registro do episódio.
8. **Sem API do LinkedIn.** O autor agenda à mão. O que o agendamento do
   LinkedIn não faz, o primeiro comentário com os links, o script lembra na
   hora do post.

## O que a conferência não vê

- Ela prova que o número está no arquivo, não que a frase em volta dele está
  certa. O verificador dos episódios mostrou que metade dos erros leves é
  paráfrase que tira a cautela da fonte; o mesmo vale aqui, e quem lê é o autor.
- Conta derivada (uma contagem, uma diferença de datas) não é refeita: vai
  listada para conferir à mão.
- Número por extenso passa. O prompt pede algarismos no rascunho por isso.

## O que foi medido

- **A suíte:** três testes novos, sem modelo. Com um agente falso: pauta,
  conferência, entrega, lembrete e marca; a chave de API não chega ao agente;
  pauta com número sem fonte sai barrada e com ressalvas.
- **A primeira tentativa de ensaio, em 15/11, falhou no login** ("OAuth
  refresh token is no longer valid"). A causa: o `divulga.py` não passava ao
  CLI o token da assinatura que mora no `.env`, como o `run_episode.sh` faz, e
  o CLI caiu no login interativo do Mac, que estava desligado. O agendamento
  falharia do mesmo jeito. Corrigido com teste: só esse valor sai do `.env`
  para o agente.
- **O ensaio com o modelo, em 15/11** (semana 46, post para 17/11, no ambiente
  do launchd, numa pasta à parte): US$ 0,83 a preço de API, 14 turnos, 2
  minutos; o Max subiu 2 pontos na janela de 5 horas e 1 na semana. A
  conferência passou, com 12 fatos citados e 1 conta para conferir à mão. A
  história escolhida foi a da semana (o ensaio do verificador). A conferência
  não viu uma frase sem número no rascunho, nem as "outras histórias", que ela
  não confere: é o limite descrito acima, visto na prática.
- **A entrega precisa de e-mail.** Sem `NOTIFY_TO`, `SMTP_USER` e `SMTP_PASS`
  no `.env`, a pauta vira uma notificação do macOS, que não sai do Mac. O
  script avisa a falta no log.

## Consequências

- Mais um job no launchd e mais um agente com versão para manter.
- O sábado gasta uma parte da semana do Max; o episódio das 05:00 de segunda
  não divide a janela de 5 horas com ele.
- O experimento de oito semanas diz se o desenho vale: a métrica do resultado
  são os seguidores, e a do processo, quantas semanas tiveram post e quanto do
  domingo cada uma custou.

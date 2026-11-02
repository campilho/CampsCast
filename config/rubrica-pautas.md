# Régua das pautas — v1 (02/11/2026)

Cada candidata recebe cinco notas, de 1 a 5, uma por critério, cada uma com
um "por quê" de uma linha. A nota sai da descrição abaixo, não da comparação
com as outras candidatas: avalie uma de cada vez. Quem soma, elimina e escolhe
é código ([ADR 0012](../docs/decisions/0012-nota-das-pautas.md)).

## Os critérios

**Fonte — o que foi lido de primeira mão**
- 5: post, paper ou release oficial lido inteiro, com data dentro da janela.
- 4: fonte oficial lida em parte, ou por outra página da própria fonte (o caso
  do 403).
- 3: fonte oficial localizada, mas o conteúdo veio de trechos citados pela
  imprensa.
- 2: só imprensa ou agregador; a fonte oficial não apareceu. **Elimina.**
- 1: rumor, fonte anônima, ou nada verificável. **Elimina.**

**Foco — quanto está no centro do `config/briefing.md`**
- 5: lançamento de modelo de fronteira de um player principal (Anthropic,
  OpenAI, Google/DeepMind, Meta, Microsoft, Mistral, xAI; a lista é a do
  briefing).
- 4: outro anúncio de player principal (produto, política, pesquisa), ou o
  foco especial da semana.
- 3: hardware e nuvem, investidores (a16z, YC, Sequoia), ou publicação das
  pessoas listadas no briefing.
- 2: outra empresa, governo ou laboratório, com efeito no setor de IA.
- 1: consumo, curiosidade ou nicho.

**Impacto — o que muda, e para quantos**
- 5: muda o que o setor inteiro faz ou pode fazer: novo topo de capacidade,
  lei em vigor, preço que cai pela metade.
- 4: muda para um segmento grande: desenvolvedores, um setor econômico, um
  país.
- 3: muda para os clientes de um produto ou de uma empresa.
- 2: sinal sem efeito ainda: carta, proposta, intenção, estudo preliminar.
- 1: sem consequência prática visível.

**Novidade — frente ao que já foi ao ar (a lista de pautas cobertas)**
- 5: assunto inédito no programa.
- 4: desdobramento com fato novo de algo já coberto.
- 3: atualização incremental: um número, uma data, uma confirmação.
- 2: quase repetição, com pouco de novo.
- 1: já coberto, sem fato novo. **Elimina.**

**Memória — ligação com os temas e os fios**
- 5: fecha um fio em aberto: promessa cumprida ou descumprida, previsão que
  se confirmou ou caiu.
- 4: move um tema ativo com fato novo.
- 3: abre um fio que vale acompanhar: promessa com data, prazo.
- 2: toca um tema de passagem.
- 1: sem ligação.

## O que o código faz com as notas

1. **Elimina** fonte 1 ou 2, novidade 1, e data fora da janela (o item do
   backlog tem a validade dele, não a janela).
2. **Soma** as cinco notas, com pesos iguais: de 5 a 25.
3. **Ordena** pela soma; no empate, impacto, depois foco, depois novidade, e
   por fim o `id`, só para a resposta ser sempre a mesma.
4. **Diversidade:** no máximo duas pautas da mesma empresa.
5. **Dia fraco:** se menos de duas candidatas da janela somarem 16 ou mais,
   a melhor do backlog entra no lugar da terceira.
6. **Grava** as três escolhidas e as descartadas, todas com as notas.

O Editor recebe as três e pode vetar uma, com o motivo escrito no log; aí o
código promove a seguinte. Veto frequente quer dizer régua errada.

## Formato

Uma linha por candidata em `runs/AAAA-MM-DD/candidatas.json`:

```json
{"id": "bancos-canada", "titulo": "…", "empresa": "RBC", "fonte": "https://…",
 "data": "2026-10-28", "do_backlog": false,
 "notas": {"fonte": 4, "foco": 4, "impacto": 4, "novidade": 5, "memoria": 4},
 "por_que": {"fonte": "aviso do RBC lido; os outros bancos via Canadian Press",
             "foco": "foco especial da semana: agentes em serviços financeiros",
             "impacto": "…", "novidade": "…", "memoria": "…"}}
```

# Régua das pautas — v2.1 (02/11/2026)

Cada candidata passa pela porteira da fonte e recebe quatro notas, de 1 a 5,
cada uma com um "por quê" de uma linha. A nota sai da descrição abaixo, não da
comparação com as outras candidatas: avalie uma de cada vez. Quem soma,
elimina e escolhe é código ([ADR 0012](../docs/decisions/0012-nota-das-pautas.md)).

Da v1 para a v2: a fonte saiu da soma e virou porteira, porque media o nosso
acesso (o openai.com e o x.ai nos bloqueiam quase todo dia) e não a notícia;
o foco 4 ficou mais estreito; e o backlog concorre na mesma ordem que as
pautas da janela. Na v2.1, "política" no foco 4 passou a ser só mudança
duradoura e para todos os clientes: a calibração da v2 deu a terceira vaga a
créditos promocionais. Na v2.2 (16/11, com o Editor 1.1), a publicação
oficial fechada por todas as portas passa pela cobertura de três veículos.

## A porteira: fonte primária

**Passa** se o conteúdo foi conferido numa fonte oficial, por qualquer porta
oficial: a página do anúncio, o feed, outra página da própria empresa
(`outras_portas` em `config/sources.yaml`), um documento oficial (paper,
release, changelog, carta, lei) ou o repositório oficial. Não importa se
abriu inteira ou em parte, nem por qual porta.

**Passa também** (v2.2) a publicação oficial identificada, com o endereço
exato tentado, que ficou fechada por todas as portas, quando lida pela
cobertura de pelo menos três veículos com texto próprio. Agregador,
newsletter, resumo diário e o mesmo texto de agência em outro site não
contam. O roteiro diz no ar que leu pela cobertura, e em quantos.

**Não passa**, e a candidata sai: só imprensa ou agregador, sem uma
publicação oficial identificada; reportagem, ainda que de veículo grande
(furo e apuração própria não são publicação oficial); rumor; fonte anônima.

O caminho fica registrado em cada candidata (`fonte`, abaixo): a URL, a porta
e o quanto foi lido. Não entra na nota; serve para a estatística das fontes e
para o roteiro dizer de onde veio.

## As quatro notas

**Foco — quanto está no centro do `config/briefing.md`**
- 5: lançamento de modelo de fronteira de um player principal (a lista do
  briefing: Anthropic, OpenAI, Google/DeepMind, Meta, Microsoft, Mistral,
  xAI).
- 4: lançamento de modelo de fronteira de um laboratório de peso aberto da
  China (a lista do briefing); anúncio de player principal que muda modelo,
  produto central ou política — preço, acesso ou regra de uso, de forma
  duradoura e para todos os clientes; ou o foco especial da semana.
- 3: programa, parceria, caso de cliente, evento ou ensaio de player
  principal; promoção, crédito ou teste grátis; outros anúncios dos laboratórios chineses; hardware e nuvem;
  investidores (a16z, YC, Sequoia); publicação das pessoas listadas no
  briefing.
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

Para o item do backlog, a novidade se mede hoje: o que ele perdeu de frescor
desde a data original entra aqui.

**Memória — ligação com os temas e os fios**
- 5: fecha um fio em aberto: promessa cumprida ou descumprida, previsão que
  se confirmou ou caiu.
- 4: move um tema ativo com fato novo.
- 3: abre um fio que vale acompanhar: promessa com data, prazo.
- 2: toca um tema de passagem.
- 1: sem ligação.

## O que o código faz com as notas

1. **Elimina** quem não passa na porteira, novidade 1, e data fora da janela
   (o item do backlog tem a validade dele, não a janela).
2. **Soma** as quatro notas, com pesos iguais: de 4 a 20.
3. **Ordena** pela soma, pautas da janela e do backlog juntas; no empate,
   impacto, depois foco, depois novidade, e por fim o `id`, só para a resposta
   ser sempre a mesma.
4. **Diversidade:** no máximo duas pautas da mesma empresa.
5. **Grava** as três escolhidas e as descartadas, todas com as notas.

O Editor recebe as três e pode vetar uma, com o motivo escrito no log; aí o
código promove a seguinte. Veto frequente quer dizer régua errada.

## Formato

Uma linha por candidata em `runs/AAAA-MM-DD/candidatas.json`:

```json
{"id": "bancos-canada", "titulo": "…", "empresa": "RBC", "data": "2026-10-28",
 "do_backlog": false,
 "fonte": {"passa": true, "url": "https://www.rbcroyalbank.com/…",
           "porta": "pagina", "leitura": "inteira",
           "complemento": "declarações dos outros bancos pela Canadian Press"},
 "notas": {"foco": 4, "impacto": 4, "novidade": 5, "memoria": 4},
 "por_que": {"fonte": "aviso oficial do RBC lido no site do banco",
             "foco": "foco especial da semana: agentes em serviços financeiros",
             "impacto": "…", "novidade": "…", "memoria": "…"}}
```

- `porta`: `pagina` (o anúncio), `feed`, `outra_porta` (outra página oficial
  da empresa), `documento` (paper, release, changelog, carta, lei),
  `repositorio`, ou `imprensa` (aí `passa` é falso).
- `leitura`: `inteira`, `em_parte` ou `trechos` (só o que outra página citou).

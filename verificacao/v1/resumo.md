# Verificação v1 — resumo (14/11/2026)

**Feito em parte.** Dos 14 episódios novos (26/10 a 13/11), conferi 8:
04, 05, 06, 09, 10, 11, 12 e 13/11. Ficaram de fora 26 a 30/10 e 03/11,
porque o orçamento da sessão (US$ 20) não deu. A calibração (episódios 35 e 38)
foi feita inteira.

## Episódios novos (8 episódios, 249 afirmações)

| Situação | n |
|---|---|
| confirmado | 239 |
| impreciso | 5 (todos leves) |
| errado | 0 |
| nao_verificavel | 4 |
| inacessivel | 1 |

**Taxa de erro: 5 / 244 verificáveis = 2,0%** (IC 95% de Wilson: 0,9% a 4,7%).

**Memória do programa:** 1 de 28 = 3,6% (IC 0,6% a 17,7%). O erro é o de 09/11:
"cibernético e biológico" foi acrescentado ao que se disse em 13/10. As
afirmações de memória de 04 e 06/11 só estão no `.md`, não no jsonl, e ficaram
fora dessa conta.

## Comparação com a linha de base (episódios 27 a 40)

A linha de base achou 19 erros em 321 verificáveis: 5,9% (IC 3,8% a 9,1%).
Os 2,0% de agora parecem uma queda, mas **a comparação não vale**. Na
calibração ([calibracao.md](calibracao.md)), o verificador desta rodada deixou
passar 5 dos 7 erros que a linha de base achou, e em todos os cinco a própria
rubrica dava razão à linha de base. A taxa de agora é um piso. Corrigindo pela
sensibilidade medida (2 de 7, uma amostra pequena demais para ser mais que uma
ordem de grandeza), ela ficaria perto de 7%, dentro do intervalo da linha de base.

## Por onde se leu

Episódios novos (jsonl, sem os de 04 e 06/11): fonte 107, imprensa 28, repositório 51,
arquivo 1 (registrado como inacessível), outra_porta 0. Na calibração: fonte 27,
imprensa 16, repositório 4.

Pautas da OpenAI:
- 04/11, alignment.openai.com: lida pela fonte.
- 05/11, "A thousand fewer paths to root": openai.com deu 403 e o arquivo não
  abriu; lida pela imprensa (SecurityWeek, Cloud Security Alliance).
- 06/11, GPT-6-Cyber: deploymentsafety.openai.com abriu (lida pela fonte;
  só pelo `.md`).
- 09/11, parceria com a Hacktron: openai.com deu 403; lida pelos posts da
  própria Hacktron, que contam como `fonte` porque são da parceira e não da
  OpenAI.
- 10/11, Control Room: openai.com deu 403; lida pela imprensa (Interesting
  Engineering) e pelo post da METR.
- 12/11, Decisions API: lida em community.openai.com, a outra porta da OpenAI.
  Os subagentes marcaram `via: fonte` porque a pauta cita aquele endereço.

## Erros graves

Nenhum.

## Método e limites

- Usei 10 subagentes no Sonnet, um por episódio, para caber no orçamento; o
  coordenador (Opus) reconferiu todo `impreciso` e `errado` na fonte. Derrubou
  um (09/11: a Hacktron diz "multiple OpenAI employees' ChatGPT accounts").
  Reclassificou duas afirmações de 05/11 de `confirmado` para
  `nao_verificavel`, porque só se apoiavam no log do roteirista.
- Os `confirmado` não foram reconferidos. A calibração mostra que é ali que
  mora o problema: o Sonnet tende a aceitar o roteiro.
- O WebFetch não abre o web.archive.org. As regras 10 e 11 viram
  `nao_verificavel` em vez de serem julgadas pela cópia do dia.
- Os de 04 e 06/11 foram interrompidos para caber no orçamento, depois de
  escrever o `.md` e antes do jsonl. Entram nas contagens pelo `.md`, mas
  faltam no `afirmacoes.jsonl`. O `impreciso` de cada um foi reconferido:
  04/11, a lista vai até o "GPT-6.1 Sol", não até o Astra; 06/11, "quase o
  dobro" por 20,29% contra 11,66% (1,74 vez, regra 5).
- Para a próxima rodada: verificador no Opus, ou reconferir uma amostra dos
  `confirmado`; e terminar 26/10 a 03/11.

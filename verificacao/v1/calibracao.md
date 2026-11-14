# Calibração da rubrica v1 contra a linha de base

Episódios 35 (16/10) e 38 (21/10): as 47 afirmações da linha de base,
conferidas às cegas (só `pauta`, `afirmacao` e `url`) por subagentes no Sonnet
com `prompts/verificador-rubrica.md`; depois comparadas.

**Mesma situação: 39 de 47 (83%).** Erros (`impreciso` + `errado`): linha de
base 7, v1 1. A única coincidência é o "mais trinta" (eram 31).

## Divergências

| Ep. | Afirmação | Linha de base | v1 | Regra | Quem acerta, pela rubrica |
|---|---|---|---|---|---|
| 35 | A Meta chama o Spark Open de modelo de peso aberto americano mais capaz | nao_verificavel | confirmado | — | v1: a base não abriu o post da Meta (ENOTFOUND). É diferença de acesso, não de régua |
| 35 | Fica atrás de cinco modelos chineses, e empatado com um sexto, da DeepSeek | confirmado | nao_verificavel | 10 | v1, pela letra: placar que mudou (Index v5 em 27/10) e o WebFetch não abre o web.archive.org |
| 35 | Ela só pode exigir cortes em categorias definidas antes: dado de cliente, sigilo jurídico, arquitetura | errado leve | confirmado | 11 | **base**: no post, essas são as categorias que os funcionários não compartilham, não categorias de corte. O v1 leu a mesma frase e não viu a troca. Nota 2 do post mudou em 16/10 (regra 11) |
| 35 | E a METR pode dizer em público o que foi cortado e se o corte se justificava | impreciso leve | confirmado | 2 | defensável dos dois lados: a METR tem "publication rights similar to those of the second tier", e o segundo nível pode opinar sobre os cortes |
| 35 | No segundo, o avaliador publica sem aprovação, mas com menos acesso | impreciso leve | confirmado | 8 | **base**: a fonte diz "access to more information"; o v1 justificou o roteiro |
| 38 | Os órgãos podem pedir uma exceção por escrito, em até sessenta dias | impreciso leve | confirmado | 6 | **base**: o prazo contava de 24/07 e venceu em 22/09; regra 6 ("prazo dado como aberto depois de vencido") |
| 38 | Voxtral três: um que transcreve, um que fala, e um kit para agentes | impreciso leve | confirmado | 7 | **base**: são três modelos de transcrição, não um |
| 38 | Esta não menciona pesos: é só por assinatura, pela plataforma da empresa | impreciso leve | confirmado | 8 | **base**: o post oferece implantação na infraestrutura do cliente; a própria nota do v1 registra isso |

## Mais branda, mais dura ou igual?

A rubrica não é mais branda: em 5 das 8 divergências, uma regra escrita dela
(6, 7, 8, 11) dá razão à linha de base. Quem saiu mais brando foi o verificador
desta rodada (Sonnet): deixou passar 5 de 7 erros. Portanto a taxa dos
episódios novos medida aqui é um piso, e a comparação com a linha de base **não vale**.

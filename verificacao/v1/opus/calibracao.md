**Dos 7 erros da linha de base, o Opus pegou 5 (com a mesma situação); o Sonnet, na etapa 1, tinha pegado 2 segundo o enunciado. O arquivo da etapa 1 registra só 1.**

# Calibração da rubrica v1, com o verificador no Opus (etapa 2a, 14/11/2026)

Episódios 35 (16/10) e 38 (21/10): as 47 afirmações da linha de base,
conferidas às cegas, com um subagente no Opus por episódio. Cada subagente
recebeu só `pauta`, `afirmacao` e `url`, e a ordem de ler a rubrica
`prompts/verificador-rubrica.md` inteira. Nenhum deles viu a linha de base nem
os arquivos da etapa 1. O orquestrador reconferiu na fonte todo `impreciso`
antes de aceitar e mudou um deles (abaixo). Só depois abriu a linha de base e o
resultado do Sonnet.

**Mesma situação da linha de base: 39 de 47 (83%).** O Sonnet também chegou a
39, mas com outras divergências. Erros (`impreciso` + `errado`): 7 na linha de
base, 8 no Opus e 1 no Sonnet, contado no `verificacao/v1/afirmacoes.jsonl`.
Todos os erros são leves.

## Os 7 erros da linha de base

| Ep. | Afirmação | Linha de base | Opus | Sonnet (etapa 1) |
|---|---|---|---|---|
| 35 | Ela só pode exigir cortes em categorias definidas antes: dado de cliente, sigilo jurídico, arquitetura | errado leve | confirmado — **perdeu** | confirmado |
| 35 | E a METR pode dizer em público o que foi cortado e se o corte se justificava | impreciso leve | impreciso leve (8) | confirmado |
| 35 | No segundo, o avaliador publica sem aprovação, mas com menos acesso | impreciso leve | impreciso leve (8) | confirmado |
| 38 | Podem pedir uma exceção por escrito, em até sessenta dias | impreciso leve | impreciso leve (6) | confirmado |
| 38 | Lista final de 180 candidatos, aos quais a equipe somou mais trinta | impreciso leve | impreciso leve (5) | impreciso |
| 38 | Voxtral três: um que transcreve, um que fala, e um kit para agentes | impreciso leve | confirmado — **perdeu** | confirmado |
| 38 | Esta não menciona pesos: é só por assinatura, pela plataforma da empresa | impreciso leve | impreciso leve (7) | confirmado |

O Opus deixou passar dois erros:

- **Categorias de corte (35).** O subagente juntou "predefined categories",
  de uma frase, com a lista de dados de cliente, sigilo e arquitetura, de
  outra. O orquestrador reabriu a página: a lista está em "Outside a small
  number of clearly defined categories (e.g., data about customers,
  attorney-client privileged information, or information about our model
  architectures), Anthropic employees are encouraged to share information".
  Como categoria de corte, o post só cita "such as reproducing confidential
  IP". A linha de base está certa. Foi o mesmo engano do Sonnet. A nota 2 do
  post mudou em 16/10 (regra 11), e por isso o roteiro pode ter seguido a
  versão de 15/10.
- **Voxtral (38).** "Um que transcreve" diante de três modelos de transcrição.
  O Opus leu "a new family of speech-to-text and text-to-speech models" e
  confirmou. Pela regra 7 ("três quando são dois"), a linha de base tem razão,
  mas por pouco: o roteiro descreve as funções, não conta modelos.

## Todas as divergências entre o Opus e a linha de base

| Ep. | Afirmação | Linha de base | Opus | Regra | Quem acerta, pela rubrica | Sonnet |
|---|---|---|---|---|---|---|
| 35 | A Meta chama o Spark Open de modelo de peso aberto americano mais capaz | nao_verificavel | confirmado | — | Opus. A linha de base não abriu o post da Meta (ENOTFOUND). A diferença é de acesso, não de régua | confirmado |
| 35 | Fica atrás de cinco modelos chineses, e empatado com um sexto, da DeepSeek | confirmado | nao_verificavel | 10 | Opus, pela letra: o placar mudou, e o WebFetch não abre a cópia do archive.org | nao_verificavel |
| 35 | Resistiu a mais de 99% das tentativas de destravá-lo para ataque cibernético | confirmado | impreciso leve | 7 | Opus. "99.2% … on our internal benchmark and 94.8% when aggregating across PolyGuard…, RedCode, and CyberBench". A própria nota da linha de base registra o 94,8% | confirmado |
| 35 | Ela só pode exigir cortes em categorias definidas antes… | errado leve | confirmado | — | Linha de base (acima) | confirmado |
| 38 | Ordem de exclusão e remoção, a primeira do tipo neste ano | confirmado | nao_verificavel | 2 | Empate. Nenhuma fonte aberta diz que é a primeira do ano, e nenhuma desmente. A linha de base leu isso na numeração #2026-01 | confirmado |
| 38 | Dois especialistas… lembraram que transformar isso num remédio seguro, barato e disponível… | confirmado | impreciso leve | 7 | Opus. A ressalva é só de Vázquez Torres; Jenkins diz "brings realistic therapeutic solutions much closer". A primeira leitura da linha de base também deu impreciso, e o orquestrador de lá reverteu | confirmado |
| 38 | Voxtral três: um que transcreve, um que fala, e um kit | impreciso leve | confirmado | 7 | Linha de base (acima) | confirmado |
| 38 | Agentes que respondem falando em mais de cinquenta idiomas | confirmado | impreciso leve | 8 | Opus, por pouco. Os 50 idiomas são da transcrição; a fala cobre "35+ languages and 50+ dialects". A linha de base aceitou porque o próprio post usa o 50 como enquadramento | confirmado |

**Reconferência do orquestrador.** O subagente tinha marcado "a primeira do
tipo neste ano" como `impreciso`, porque o Departamento da Guerra emitiu ordem
contra a DeepSeek em 08/09/2026. Só que a ordem do DHS foi assinada em 24/07,
antes. Pela regra 2, isso fica `nao_verificavel`. Os outros sete `impreciso` se
sustentaram na fonte reaberta. A ordem do DHS na página do Federal Register
redireciona para `unblock.federalregister.gov`, e por isso o prazo de 60 dias
foi conferido pela cobertura (IBTimes, Haynes Boone, CRS), como fez o subagente.

## Mais branda, mais dura ou igual?

Com o Opus, a rubrica julga com a mesma dureza da linha de base: 8 erros contra
7, e 5 em comum. As divergências são de leitura, para os dois lados, e não de
régua. Das três que o Opus marcou e a linha de base não, duas a própria linha
de base anotou ou tinha marcado antes de reverter. A brandura da etapa 1 era do
Sonnet, não da rubrica. Com o Opus, a comparação com a linha de base vale,
com uma margem de erro de cerca de ±2 erros em 47 afirmações.

Dois pontos para uma v2. A **regra 5**, ao pé da letra, faz de "mais de três
mil" para 3.250 (7,7% de distância) um `impreciso`. Ninguém aplicou assim,
nem a linha de base, nem o Opus, nem o Sonnet. A **regra 10** pede a cópia do
arquivo, mas o archive.org não abre pelo WebFetch, e assim todo placar que
muda vira `nao_verificavel`.

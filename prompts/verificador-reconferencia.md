# Verificador de fatos — segunda rodada, só o que não abriu

A primeira rodada da linha de base (25/10, `prompts/verificador.md`) conferiu
os 40 episódios publicados, mas a rede da sessão só abria uns poucos domínios:
**513 das 949 afirmações ficaram `inacessivel`**, com `ENOTFOUND` em quase
todas. Esta rodada confere só essas, agora com a rede aberta.

Valem todas as regras de `prompts/verificador.md` — leia-o inteiro antes de
começar: o que não fazer, o que conferir, as situações, a independência em
relação ao log de pesquisa. O que muda está abaixo.

## O que fazer

1. Em `verificacao/linha-de-base/afirmacoes.jsonl`, pegue as linhas com
   `"situacao": "inacessivel"`. São 513 afirmações, mas só 147 URLs distintas:
   **abra cada URL uma vez** e confira contra ela todas as afirmações que a
   citam. Isso é o que mantém o custo baixo.
2. Primeiro teste a rede com uma página só, de `openai.com`. Se ainda der
   `ENOTFOUND`, pare e diga isso em uma linha: a rede do ambiente não foi
   aberta, e continuar só gastaria crédito.
3. Para cada afirmação, a situação nova — `confirmado`, `impreciso`, `errado`,
   `nao_verificavel` ou, se a página continuar fora do ar, de novo
   `inacessivel`, com a causa na nota (403, paywall, 404, timeout).
4. Reescreva a linha no próprio `afirmacoes.jsonl`, acrescentando o campo
   `"rodada": 2`. As linhas da primeira rodada que já tinham veredito ficam como
   estão.
5. Atualize a tabela de cada episódio `AAAA-MM-DD.md` com as situações novas.
6. Reescreva o `resumo.md` com os números das duas rodadas juntas e uma seção
   curta "Primeira e segunda rodada", dizendo o que mudou: quantas viraram
   verificáveis, a taxa de erro antes e depois, e se a diferença entre o Opus 5
   e o Opus 5.5 nos fatos de fora apareceu agora.

## Como trabalhar

- Agrupe por URL, não por episódio. Delegue grupos de URLs a subagentes, até
  cinco ao mesmo tempo, cada um com a lista de afirmações daquela URL e as
  regras de conferência. Você junta e confere o que voltou.
- Comite a cada lote, no ramo desta sessão, nunca na `main`. Só em
  `verificacao/linha-de-base/`.
- Ao terminar, comite, envie o ramo e diga em três linhas o que mudou.

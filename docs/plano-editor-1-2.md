# Plano: Editor 1.2 e 1.3

Rascunho de 20/11/2026, a pedido do autor. Nada implementado: este arquivo diz o
que muda, por quê, como medir e em que ordem. Regra do projeto: uma mudança por
vez em agente, versão nova em `config/agentes.json` no mesmo commit do prompt, e
ensaio contra a versão em produção antes de ir ao ar.

## De onde vêm as mudanças

Três lições da semana, todas medidas:

1. **Paráfrase que tira a cautela da fonte.** O Verificador V1 (14/11,
   `verificacao/v1/resumo.md`) achou que, nos episódios 41 a 46, a taxa de erro
   foi de 11,3%, contra 5,9% da linha de base, e que a regra 8, "paráfrase que
   acrescenta", decidiu 10 dos 20 erros. O padrão: o roteiro tira o "appeared",
   o "aim", o "could" e o "as many as", ou troca a medida por uma vizinha.
2. **Newsletter usada como cobertura.** Em 16/11, a fala de Craig e os três
   revisores vieram da AI Weekly e do DEV Community, numa pauta que entrou pelo
   arXiv; no ar, só "e a cobertura", sem contar veículos. Estava certo (conferido
   na página oficial em 20/11), mas por sorte. O Editor 1.1 proíbe newsletter só
   dentro da "terceira porta"; aqui a pauta tinha outra fonte primária, e a regra
   não pegou.
3. **O arquivo público nunca abre.** A segunda porta manda ler a cópia no
   web.archive.org, que o WebFetch não abre; toda tentativa conta como página
   fechada na ficha técnica dita no ar.

## A ordem: 1.2 é a cautela; 1.3, as portas

**Editor 1.2: manter o grau de certeza da fonte.** É o erro que chega ao
ouvinte e o mais frequente. Mudança no `master.md`, na seção do roteiro:

- regra curta: o roteiro diz com a mesma certeza que a fonte. "Appeared",
  "could", "aims to", "as many as", "estimated", "up to" viram "parece", "pode",
  "quer", "até", "estimado"; número aproximado na fonte segue aproximado no ar;
  a medida dita é a que a fonte mediu, não uma vizinha;
- um passo de conferência antes de gravar o roteiro: para cada número e cada
  afirmação forte, a frase da fonte ao lado da frase do roteiro, no log de
  pesquisa (seção nova, curta). O log já guarda o que foi lido; isto torna a
  conferência visível e mensurável.

**Editor 1.3: as portas.** Menor e mais mecânico, vem depois de medir o 1.2:

- a proibição de newsletter, agregador e resumo vale para qualquer fato tirado
  de cobertura, não só na terceira porta; e "pela cobertura" no ar sempre diz
  quantos veículos e quais;
- a segunda porta sai do prompt enquanto o WebFetch não abrir o web.archive.org
  (conferir antes: `docs/aprendizados.md`, archive.org fechado ao WebFetch), e a
  checagem de disponibilidade, se ficar, não conta como página fechada.

## Como medir

**1.2:** `scripts/ensaio.sh` em dias passados, versão 1.1 contra 1.2, os dois
roteiros pelo Verificador V1 (Opus) com a rubrica atual. Dias: os 41 a 46, onde
estão os 10 casos da regra 8, para comparar com o mesmo pano de fundo.

- Critério: menos erros da regra 8 no 1.2, sem subir os das outras regras; custo
  e duração no mesmo patamar (US$ 4 a 8 a preço de API e 10 a 18 minutos, como nas semanas 46 e 47).
- Limite conhecido: o ensaio pode escolher pautas diferentes das do dia
  original. Comparar por erros por afirmação verificável, não por caso.
- Custo do ensaio: os roteiros rodam no Max (uns 6 pontos da janela de 5 horas
  cada, 12 execuções); o verificador no Opus sai uns US$ 2 a 3 por roteiro a
  preço de API, uns US$ 25 a 35 nos 12. **Decisão do autor antes de rodar:**
  quanto do crédito de API (US$ 138, dividido com outro projeto) vai para isso,
  e em que semana do Max, que hoje divide com o CampsVerso e o Claude Design.

**1.3:** sem verificador. Ensaio em 3 dias com página oficial fechada (13, 16 e
19/11) e comparar o log: fatos tirados de newsletter, "pela cobertura" com
contagem no ar, páginas fechadas na ficha.

## Passos, quando o autor der o sinal

1. Escrever a mudança do 1.2 no `master.md` e a versão nova em
   `config/agentes.json`, com o "mudou"; a suíte confere que o prompt bate com
   a ficha.
2. Rodar o ensaio do 1.2 contra o 1.1 nos dias 41 a 46; rodar o verificador
   nos 12 roteiros; resumir em `verificacao/` e em `docs/aprendizados.md`.
3. Com o OK do autor, o 1.2 vai à produção; uma semana de episódios antes de
   tocar no prompt de novo.
4. Repetir para o 1.3.

## Fora deste plano

O verificador diário (V1 em produção, em sombra) e a separação dos agentes
(varredura → verificador → Editor) seguem no TODO. Se o verificador diário
entrar antes, ele mede o 1.2 de graça na produção, e o ensaio pode encolher.

## Piloto de 20/11: dois dias, 1.1 contra 1.2

Ensaios dos episódios 41 (26/10) e 45 (30/10), estado exato, com o 1.2 numa
cópia do código fora do repositório (a produção seguiu no 1.1). Verificador V1
(Opus, rubrica v1) nos quatro roteiros, pela chave de API: US$ 5,95 no total.

| | 1.1 | 1.2 |
|---|---|---|
| Afirmações verificáveis (41 + 45) | 22 + 22 = 44 | 26 + 27 = 53 |
| Erros (impreciso; nenhum errado) | 1 + 4 = **5 (11,4%)** | 3 + 2 = **5 (9,4%)** |
| Deles, regra 8 (paráfrase) | 1 + 4 = **5** | 0 + 1 = **1** |
| Custo do agente, a preço de API | US$ 4,99 e 4,36 | US$ 6,06 e 4,77 |
| Minutos | 12,5 e 10,5 | 14,3 e 12,0 |

- A conferência da certeza apareceu nos dois logs (11 e 26 linhas) e pegou um
  caso de verdade: "É capacidade que não foi ensinada", mais forte do que o
  90,5% → 81% da fonte, corrigido pelo próprio agente.
- O único erro de regra 8 do 1.2 foi anotado na conferência como "a leitura"
  (o "porque" ligando custo e tokens) e ficou no ar: a regra precisa dizer que
  ligação causal que a fonte não faz também é paráfrase que acrescenta.
- Os outros erros do 1.2 são de outras regras: datas da memória do programa
  (regra 6, dois) e arredondamento sem marcador e conta (regras 5 e 4). O "uns
  nove" para 9,5 pontos mostra que "cerca de" ainda precisa respeitar o limite
  de 5% da rubrica.
- O 1.2 sai uns 10% a 20% mais caro e 1,5 a 2 minutos mais longo: as
  conferências custam leitura.
- Dois dias não medem taxa (os intervalos se cruzam), mas a direção da regra 8
  é a esperada: 5 casos em 44 contra 1 em 53. Próximo: os outros quatro dias
  (42, 43, 44 e 46) para fechar os seis do plano.

## Os seis dias (21/11, de madrugada)

Os outros quatro dias do plano (42 a 44 e 46) rodaram depois que a janela de 5
horas virou. Nos dias 27 e 28/10 o estado é inexato (o commit anterior junta
dias), o que não atrapalha a comparação: as duas versões partem do mesmo
estado. Verificador V1 nos doze roteiros: US$ 19,08 no total.

| | 1.1 | 1.2 |
|---|---|---|
| Afirmações verificáveis | 155 | 155 |
| Erros (errado + impreciso) | 19 = 12,3% (IC 8,0 a 18,4) | 13 = 8,4% (IC 5,0 a 13,8) |
| Deles, regra 8 (paráfrase) | **11 = 7,1%** (IC 4,0 a 12,3) | **5 = 3,2%** (IC 1,4 a 7,3) |
| "Errado" | 1 | 0 |
| Custo do agente, média por dia | US$ 4,86 | US$ 5,19 (+7%) |
| Minutos, média | 11,3 | 12,6 |

- A regra 8 caiu à metade (z = 1,54; p ≈ 0,12): direção clara, mas ainda
  dentro do que o acaso explica com 155 afirmações por lado. O total caiu de
  12,3% para 8,4% (z = 1,12).
- Os erros que sobram no 1.2 são de datas da memória do programa (regra 6,
  três), arredondamento (regra 5, dois), contagem, e cinco de paráfrase. Um
  deles foi a ligação causal que a fonte não fez, anotada na conferência e
  mantida no ar.
- O custo subiu 7% e o tempo, pouco mais de um minuto: a conferência da
  certeza custa leitura, e cabe no orçamento.

**Recomendação:** pôr o 1.2 como está na produção (é a versão medida) e medir
na própria produção com o verificador diário, quando ele existir. A ligação
causal entra numa versão seguinte, junto com as portas ou à parte, com ensaio.

**Decisão do autor (21/11):** o 1.2 entra na produção a partir do episódio de
23/11. Uma semana de episódios antes de tocar no prompt de novo.

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

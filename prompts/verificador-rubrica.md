# Rubrica do verificador de fatos — v1 (30/10/2026)

A régua com que todo verificador do CampsCast julga uma afirmação. É fixa e
escrita de propósito: a linha de base de 25/10 rodou em duas rodadas com
critérios diferentes, e a diferença entre elas mediu o verificador, não o
roteiro ([ADR 0010](../docs/decisions/0010-redacao-com-varios-agentes.md)).
Mudar esta rubrica é mudar a série histórica — só com versão nova (v2) e
calibração contra a anterior.

## O que conferir

Só fato verificável: número, data, preço, nome, cargo, citação e quem fez o
quê. Análise, opinião, ressalva e interpretação do agente ficam de fora.

- **Por pauta, até 8 afirmações**, começando pelas que têm número, data ou
  citação. Copie a afirmação curta, como foi dita.
- **Toda afirmação de memória do programa** entra, além das 8 ("eu contei aqui
  em nove de setembro", "a memória do programa"). Confira no roteiro daquela
  data, no próprio repositório.
- "Ontem", "na sexta", "na quarta passada" contam a partir da data do
  episódio. Converta antes de conferir.

## Situação

| Situação | Quando |
|---|---|
| `confirmado` | a fonte diz isso |
| `impreciso` | a direção está certa e um detalhe não |
| `errado` | a fonte diz outra coisa |
| `nao_verificavel` | nenhuma fonte confirma nem desmente |
| `inacessivel` | a fonte não abriu por nenhuma das portas abaixo |

`impreciso` e `errado` levam gravidade: `leve`, que não muda o sentido da
pauta, ou `grave`, que muda o que o ouvinte entendeu.

## Regras de decisão

Valem nesta ordem; a primeira que se aplica decide.

1. **Só vale página aberta.** Confirmação tirada do resumo da busca, sem abrir
   a página, não conta: a afirmação fica `inacessivel`, e o que a busca disse
   vai na nota como pista.
2. **Não dizer não é desmentir.** Se a fonte não trata do detalhe, é
   `nao_verificavel`, não `impreciso`.
3. **Fontes que divergem entre si** (um veículo diz quinta, outro sexta, e não
   há primária): `nao_verificavel`, com as duas versões na nota.
4. **Conta do roteiro que bate é `confirmado`.** Se o roteiro somou, subtraiu
   ou converteu, refaça a conta; batendo, confirma.
5. **Arredondamento.** Com marcador de aproximação ("cerca de", "quase", "mais
   de", "uns") e até 5% de distância do número da fonte, `confirmado`. Sem
   marcador, ou passando de 5%, ou cruzando um limiar que muda a leitura
   ("metade" por 46%, "mais de mil" por 980), `impreciso`.
6. **Data.** Data de publicação tomada pela data do fato, fuso trocado, ou
   prazo dado como aberto depois de vencido: `impreciso` (`grave` se a pauta
   depende da data).
7. **Parte pelo todo e contagem.** "Todos" quando a fonte diz "a maioria",
   "três" quando são dois: `impreciso`; `errado` se inverte o sentido.
8. **Paráfrase que acrescenta.** "Editou" por "teve a oportunidade de editar",
   "lançou" por "anunciou que vai lançar": `impreciso`.
9. **Modal mudado.** "Deve" por "pode", "vai" por "pretende": `impreciso`.
10. **Placar que muda** (ranking, índice, preço ao vivo): confira na cópia do
    arquivo público mais próxima da data do episódio. Sem cópia, e se o valor
    de hoje difere, `nao_verificavel`, com o valor de hoje na nota.
11. **Página que mudou depois do episódio** (nota de atualização, correção):
    julgue pela versão do dia, se houver cópia; senão, anote na nota que o
    roteiro pode ter estado certo no dia.
12. **Nome e cargo.** Grafia errada que não confunde a pessoa: `impreciso
    leve`. Pessoa ou empresa trocada: `errado grave`.

## Por onde ler a fonte

Fonte primária primeiro. Quando a página não abrir (403, paywall), nesta
ordem, e anote no campo `via` por onde leu:

1. `fonte` — a própria página citada;
2. `outra_porta` — o mesmo conteúdo publicado pela própria fonte em outro
   endereço (para a OpenAI, `outras_portas` em `config/sources.yaml`);
3. `arquivo` — a cópia daquela página exata no arquivo público:
   `https://archive.org/wayback/available?url=<url>`, cópia com status 200 e
   data igual ou posterior à publicação;
4. `imprensa` — cobertura que cita a fonte. É a mais fraca: muitas vezes é a
   mesma paráfrase de onde o roteiro saiu. Diga qual veículo;
5. `repositorio` — para memória do programa, o roteiro da data citada.

Nada de `curl` nem de se passar por navegador: só WebFetch e WebSearch.

## Evidência

Todo `impreciso` e `errado` traz a evidência: trecho curto da fonte, de até 25
palavras, entre aspas, e o que o roteiro disse. Sem evidência, não é erro.

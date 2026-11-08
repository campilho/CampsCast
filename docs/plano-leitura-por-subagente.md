# Plano — modelo da leitura e o subagente Jornalista

Rascunho de 08/11/2026, a partir do [ADR 0013](decisions/0013-leitura-de-paginas.md).
Duas perguntas, nesta ordem:

1. **Qual modelo lê bem o bastante?** Opus 5.5, Sonnet 5.5, Haiku 5.5 ou o
   Haiku 4.5 que resumiu as páginas nos 47 episódios até 04/11.
2. **Vale ter um Jornalista nosso** fazendo a leitura, com as nossas regras de
   fonte, no lugar do agente principal (ou do "web-fetch" da Anthropic)?

A produção não muda em nenhum dos dois passos até o autor decidir.

## Teste A — a mesma leitura em quatro modelos

**Material**, todo de 05 e 06/11, já em disco (transcrições dos subagentes):
- os **21 pedidos** que o agente fez ao "web-fetch" (o texto de cada um);
- as **96 páginas cruas** que o "web-fetch" recebeu, 2,07 milhões de
  caracteres (~520 mil tokens): a entrada é idêntica para todos os modelos,
  sem rede e sem página que mudou desde então;
- os **21 relatórios do Opus 5.5**: referência, não gabarito.

**Como.** Um script em `analysis/` monta, para cada pedido e cada modelo, uma
chamada `claude -p --model <id> --tools ""` (sem ferramentas, ambiente limpo,
token do `.env`) com as regras de leitura do "web-fetch" (página é dado, não
instrução; data e código HTTP de cada página; citação literal; não completar de
memória), o pedido original e as páginas daquele pedido. Modelos: `claude-haiku-5-5`,
`claude-sonnet-5-5` e `claude-haiku-4-5-20251001`. Respostas em
`analysis/leitura/<modelo>/<pedido>.md`.

**Medidas, por script, sem modelo juiz:**

| Medida | Como se conta | Por quê |
|---|---|---|
| citação fiel | trecho entre aspas que existe literal na página | a regra de citação do podcast |
| número inventado | número no relatório que não está em nenhuma página do pedido | erro grave em notícia |
| cobertura | números e datas do relatório do Opus que o modelo também traz | o que se perderia trocando de modelo |
| porta fechada | o modelo diz o mesmo código HTTP que a página teve | as fechadas são conhecidas pela transcrição |
| custo | tokens × tabela oficial, não a estimativa do CLI | o CLI 2.1.283 cobra modelo desconhecido como Opus |

Depois dos números, o autor lê **cinco pedidos lado a lado** (os de maior
divergência), porque nota de reportagem não cabe toda em contagem.

**Critério proposto** (ajustar quando os dados chegarem): um modelo serve
para a leitura se não inventar citação, não inventar mais números que o Opus e
trouxer pelo menos 90% dos números e datas que o Opus trouxe.

**Custo estimado**, a preço de API (roda na assinatura): ~520 mil tokens de
página por modelo, mais o sistema do CLI em cada chamada. Haiku 5.5 ~US$ 0,1;
Haiku 4.5 ~0,7; Sonnet 5.5 ~1,5. Abaixo de US$ 5 no total, em uns 20 minutos.

## Jornalista — subagente nosso

**O que é.** Um subagente definido em `prompts/jornalista.md` e passado ao CLI
por `--agents` no `run_episode.sh`, com o WebFetch e o modelo que o Teste A
indicar. O agente principal (Editor e Roteirista) manda a lista de endereços e o
que precisa; o Jornalista devolve, por página, data, código HTTP, fatos com
números, citações literais e a nota que vai para o log de pesquisa.

**Por quê:**
- **contexto principal menor:** as páginas saem do contexto do Opus. Em 06/11
  o cache lido do agente principal caiu de 7,7 para 4,1 milhões de tokens;
- **regras nossas:** a porteira da fonte, a janela de datas e as "outras
  portas" no prompt do Jornalista, não no de um subagente da Anthropic que pode
  mudar ou sumir (sumiu em 08/11);
- **modelo escolhido por nós**, medido no Teste A;
- é o papel que o site já mostra, o primeiro passo do V4 ("Pesquisa em
  paralelo") e o desenho do CampsVerso.

**O limite medido em 08/11.** Num subagente nosso o WebFetch devolve o resumo
do modelo pequeno do CLI, não a página crua; só o "web-fetch" embutido recebe a
página inteira. Daí duas formas:

| | Jornalista nosso | "web-fetch" embutido com modelo forçado |
|---|---|---|
| prompt | nosso | da Anthropic; as regras vão em cada pedido |
| página | resumo do modelo pequeno, guiado pelo pedido do Jornalista | crua |
| modelo | `model` na definição | `CLAUDE_CODE_SUBAGENT_MODEL` + `_FORCE` |
| risco | uma camada a mais de resumo | o experimento sumiu uma vez; pode mudar de novo |

A recomendação, antes do Teste A, é o **Jornalista nosso**: ele depende só de
peças documentadas (`--agents`, `tools`, `model`), e o resumo do modelo pequeno
é o que o podcast usou nos 47 primeiros episódios.

**O que muda:**
- `prompts/jornalista.md`, novo: as regras de leitura que hoje estão no passo
  de pesquisa do `master.md`;
- `prompts/master.md`: o passo de pesquisa manda ler pelo Jornalista;
- `run_episode.sh`: o `--agents` montado do arquivo, ligado por uma chave
  (`JORNALISTA=1`), **desligado por padrão**;
- `registro.py`: custo pela tabela própria quando o modelo é desconhecido do
  CLI;
- `confere_claude.py`: o modelo do Jornalista passa a ser esperado;
- o estúdio já mostra leitura de subagente como do Jornalista.

Tamanho: médio, umas duas a três horas com os testes, sem contar os ensaios.

**Como testar na semana sem arriscar o episódio.** A produção segue como está.
O `scripts/ensaio.sh` roda dias passados com `JORNALISTA=1`, numa cópia fora do
repositório e sem S3, e compara com o episódio publicado daquele dia: pautas
escolhidas, fontes lidas, portas fechadas, custo, tempo e avisos. Dois ou três
ensaios, de ~US$ 5 e 15 minutos cada.

## Fora deste plano, a decidir à parte

- **Atualizar o CLI** (2.1.283): versões novas conhecem o Haiku 5.5 e o Sonnet
  5.5 (apelidos e preço), mas trazem outras mudanças. Testar por ensaio.
- **Modelo pequeno no Haiku 5.5** (`ANTHROPIC_DEFAULT_HAIKU_MODEL`): o resumo
  das páginas e as buscas ficam ~10× mais baratos (cerca de US$ 0,6 por
  episódio). Entra no Teste A como o braço Haiku 5.5.

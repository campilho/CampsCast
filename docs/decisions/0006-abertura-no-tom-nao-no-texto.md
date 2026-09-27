# ADR 0006 — Abertura e encerramento no tom, não no texto

- **Status:** aceito
- **Data:** 2026-09-26

## Contexto

A abertura era um texto fixo, com lacunas para o número e a data. Depois de 21
episódios, o autor quis três mudanças, e uma quarta de fundo.

As três de forma: tirar "e esta é a voz do Camps, sintetizada" da abertura,
porque a ficha técnica do encerramento já diz quem narra; parar de repetir a
data da janela logo depois de dizer a data de hoje ("hoje é sexta, vinte e
cinco… cobre quinta, vinte e quatro"); e trocar o apelido pelo nome completo,
Fernando Campilho, deixando "Camps" só no nome do programa.

A de fundo: quem ouve todo dia escuta a mesma abertura centenas de vezes por
ano. Ela deveria variar aos poucos.

## Opções

**A. Cardápio.** Quatro ou cinco versões aprovadas num arquivo, em rodízio pelo
número do episódio. Cada frase passa pelo autor; em compensação, o ciclo se
repete e o ouvinte percebe.

**B. Tom, não texto.** O prompt define os elementos obrigatórios e um exemplo
de tom; o agente varia o resto e lê os episódios anteriores para não repetir a
construção de ontem.

A opção B já tinha precedente medido no próprio projeto: a ficha técnica
funciona assim desde 02/09 — "exemplo do tom, não do texto". Nos dez episódios
de 14 a 25/09 ela variou todo dia e não deixou cair nenhum dos elementos que a
conferência abaixo verifica.

## Decisão

**Opção B**, escolhida pelo autor também como experimento: medir quanto o agente
aguenta de autonomia sem deixar cair uma regra.

O que é obrigatório ficou explícito no prompt. Na abertura: número do episódio,
"eu sou um agente de IA", data de hoje, e o que o episódio cobre sem repetir
data. No encerramento: números reais da execução, quem escreveu, quem narrou,
que a voz é sintética, e "até o próximo episódio".

Para o experimento ter resultado, `scripts/confere_roteiro.py` confere esses
elementos depois que o agente escreve. **Não bloqueia: registra.** Cada regra
que cair vai para o log e para `avisos_roteiro` em `metricas/execucoes.jsonl`
— `null` quando o roteiro não foi conferido, lista vazia quando foi e estava
completo. Aplicada aos dez episódios de 14 a 25/09, escritos com a abertura
fixa, a conferência não acusou nada — nenhum falso positivo.

Junto veio o mecanismo de **novidades**: `config/novidades.json` lista mudanças
no próprio podcast — modelo, voz, requisito novo — com data de início e de fim.
O orquestrador escreve as ativas no próprio prompt, na seção de parâmetros —
não no ambiente, que o agente não consegue ler; ver `docs/aprendizados.md` —,
e a abertura anuncia
cada uma em uma frase, logo depois de "eu sou um agente de IA". A data de fim
existe para o anúncio sumir sozinho: aviso que ninguém lembra de tirar vira
ruído. A primeira é a troca para o Opus 5.5, de 28/09 a 02/10, dita em tom de
upgrade: "o modelo que o meu antecessor noticiou aqui no episódio dezenove".

## Consequências

- A declaração de que a voz é sintética sai da abertura e fica na ficha técnica
  e na descrição do podcast. "Eu sou um agente de IA" continua nos primeiros
  segundos.
- Se a conferência começar a acusar a mesma regra com frequência, ela endurece:
  primeiro no prompt, e só em último caso virando bloqueio.
- Uma novidade ainda depende de alguém escrever a entrada. Troca de modelo ou de
  voz poderia ser detectada sozinha, comparando com o episódio anterior — mas o
  front-matter ainda não grava os modelos usados.

## Adendo — 26/09/2026: a chamada para seguir

O autor pediu uma chamada do tipo "se está gostando, siga o podcast", comum em
vídeos do YouTube, logo depois da abertura e não em todo episódio.

O lugar foi decidido pelos números do Spotify. Só uns 18% ouvem pelo menos 95%
do episódio, mas o consumo médio é de dois terços. No encerramento, a chamada
alcançaria cerca de um ouvinte em cada cinco. Logo depois da abertura, ela
chegaria a todos, mas pediria compromisso antes de entregar qualquer coisa, e
atrasaria a primeira notícia — o YouTube põe a chamada no começo porque o
algoritmo dele premia engajamento cedo, e podcast não funciona assim. **Depois
da primeira pauta** a maioria ainda está ouvindo e já recebeu algo.

A frequência ficou em **terças e quintas**, a partir de 29/09, configurada em
`config/show.json` e decidida por `scripts/chamada.py`. O texto é do agente,
como o resto da abertura, sem citar plataforma. A conferência cobra a chamada no
dia dela e acusa se ela aparecer fora dele.

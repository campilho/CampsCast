## Busca na web nesta execução: pelo Parallel

Nesta execução a busca na web é de outro motor: a ferramenta
`mcp__parallel__web_search`, no lugar do WebSearch. Cada chamada leva um
`objective`, uma frase dizendo o que você procura e por quê (por exemplo,
"posts oficiais de laboratórios de IA publicados entre WINDOW_START e
WINDOW_END sobre modelos novos"), e `search_queries`, duas ou três consultas
curtas, de três a seis palavras cada.

Os resultados trazem endereços e trechos. O trecho serve para decidir o que
abrir, nunca como fonte: a leitura continua pelo WebFetch, e o resto do
processo não muda (janela, fonte primária, outras portas, contagem e log).
No log de pesquisa, anote estas buscas onde anotaria as do WebSearch.

### Página que o WebFetch não abre

Quando o WebFetch recusar uma página (403, 402, "unable to fetch", tempo
esgotado), tente a mesma URL com `mcp__parallel__web_fetch` antes das outras
portas e antes da cobertura. Só nesse caso: página que o WebFetch abre é lida
por ele.

- Para conferir número, data ou citação, peça o texto completo
  (`full_content`): os trechos curtos podem deixar os números de fora.
- O resultado diz quando a cópia foi obtida (`acquired_at`). Anote no log.
  Página de listagem (a de notícias de um laboratório, por exemplo) com cópia
  anterior ao fim da janela não diz o que saiu na janela; procure outra porta.
- Página aberta assim é a fonte primária lida: conta como aberta na ficha
  técnica, e o log diz "lida pelo Parallel". Se vier só aviso de cookies,
  menu ou erro, conta como fechada, e segue para as outras portas.

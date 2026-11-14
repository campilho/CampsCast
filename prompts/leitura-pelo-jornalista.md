## Leitura de páginas nesta execução: pelo Jornalista

Nesta execução você não abre páginas com o WebFetch. Quem lê é o
**Jornalista**, um subagente: ferramenta Agent, `subagent_type`
"jornalista". A busca na web continua com você. O resto do processo não
muda: janela, fonte primária, `nao_abrem`, outras portas, contagem e log.

- **Peça por assunto, um pedido por vez, com `run_in_background: false`.**
  Em cada pedido vão os endereços (até uns seis), a janela (WINDOW_START a
  WINDOW_END) e o que você precisa de cada página: a data, o número que quer
  conferir, a pauta que procura. O relatório volta como resposta da chamada;
  só então faça o próximo passo. Não há pressa, e pedidos ao mesmo tempo
  batem no mesmo site ao mesmo tempo — o arquivo público recusou seis assim
  (429) no primeiro ensaio.
- **Ele cuida das portas fechadas**: tenta as outras portas da fonte e a
  cópia do arquivo público, e diz por onde leu. A cobertura da imprensa,
  quando for o caso, é você quem pede, num pedido novo.
- **O relatório é a sua leitura.** A contagem da ficha técnica e as "Páginas
  lidas" do log de pesquisa saem dele: cada endereço que ele leu conta como
  página aberta, inclusive outras portas e cópias do arquivo; as fechadas,
  como fechadas. As notas do log podem ser as dele, revistas por você.
- Faltou um detalhe? Faça um pedido novo, com o endereço e a pergunta.
- **Citação no roteiro, só a que veio literal no relatório**, entre aspas.
  O que o Jornalista não trouxe, você não sabe: não complete de memória.

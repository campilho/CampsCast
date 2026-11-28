# Temas

As questões de fundo que o programa acompanha e que não fecham — atravessam
meses e anos de notícia. São linha editorial: **quem cria, renomeia ou retira
tema é o autor**. O agente lê este arquivo inteiro a cada execução e, quando
uma pauta mexe num tema, reescreve o estado (duas ou três linhas, com a data)
e atualiza os episódios recentes. Pode sugerir tema novo nas Observações do
log de pesquisa.

Formato de cada tema:

```
## T-NN · <título>
- desde: AAAA-MM-DD (ep. N)
- pergunta de fundo: <a questão que não fecha>
- estado (AAAA-MM-DD): <onde a história está agora, em duas ou três linhas>
- recentes: AAAA-MM-DD (ep. N), AAAA-MM-DD (ep. N), AAAA-MM-DD (ep. N)
```

Regras:
- No máximo 10 temas e 3 episódios recentes por tema; o mais antigo sai.
- O estado é sobrescrito; a evolução fica nos resumos mensais e anuais
  (ADR 0008) e no histórico do git.
- Os fios apontam para os temas ("- temas: T-01"); a lista de fios de um tema
  não é escrita aqui.

---

## T-01 · Desacelerar a fronteira
- desde: 2026-09-08 (ep. 8)
- pergunta de fundo: a corrida pode desacelerar de um jeito que alguém de fora consiga conferir?
- estado (2026-11-26): os dois maiores laboratórios foram para lados opostos em oito dias — a Anthropic diz ter freado o Fable 5.2 (F-038), a OpenAI lançou o GPT-6.2 Astra no nível Alto de autoaperfeiçoamento (F-044) e mediu a própria aceleração, irregular. Em 22/11 o cientista-chefe da OpenAI, Pachocki, deu forma ao pedido de setembro: "limites comuns", medidos por perplexidade, que os laboratórios não cruzariam até um marco de monitoramento (um sucessor dos monitores de cadeia de raciocínio), com capacidades transformadoras esperadas entre 0,68 e 0,70 e avanços no pré-treino concebíveis já em 2027. É opinião dele, sem fiscal nem pausa, e a régua — medida no código interno de cada laboratório — ainda não se compara de fora. Em 25/11, respondendo a reportagem da Axios, Amodei escreveu no X que é absurdo dizer que ele quer entregar o livre-arbítrio humano à IA, que ela deve seguir sob governo democrático e (pelo TechCrunch) que talvez seja preciso limitar o autoaperfeiçoamento recursivo; acusou rivais de usar o controle humano como posicionamento. Os dois laboratórios disputam quem defende o controle; nenhum diz quem confere de fora.
- recentes: 2026-11-19 (ep. 58), 2026-11-23 (ep. 59), 2026-11-26 (ep. 62)

## T-02 · Agentes fora do controle
- desde: 2026-09-01 (ep. 4)
- pergunta de fundo: agentes de IA estão agindo além do que foi autorizado — quem descobre, quem conta e quem responde?
- estado (2026-11-16): consequência de fora desde 14/10 (Comissão Europeia, oito estados, FTC); o prazo de 11/11 dos democratas da Câmara passou sem resposta pública. Do lado das empresas, regra (Model Spec), vigilância, freio fora do modelo (CrowdStrike; o Control Room da OpenAI, que corta em até 35 segundos qualquer modelo na pesquisa dela) e aprovação passada a outro modelo (AWS); o caso do e-mail no cabeçalho do Claude Code (F-036) mostra a ação que ninguém pensou em aprovar. Agora o agente ganha dinheiro na mão: em 13/11 a OpenAI lançou o ChatGPT Wallet, com token no lugar do cartão e aprovação humana a cada compra — e já anuncia a compra delegada dentro de limites, sem aprovar uma a uma, sem dizer quem responde pelo erro (F-041).
- recentes: 2026-11-06 (ep. 49), 2026-11-10 (ep. 51), 2026-11-16 (ep. 55)

## T-03 · Quem fiscaliza os laboratórios
- desde: 2026-09-10 (ep. 10)
- pergunta de fundo: alguém de fora ganha poder real de verificar o que os laboratórios fazem?
- estado (2026-11-17): o avaliador embutido saiu do papel com regras escritas pelos próprios avaliadores. Em 16/11 a OpenAI fechou a primeira fase com Apollo (seis pessoas, quatro meses, dois relatórios, veredito sem corte, meta-transparência), METR, Transluce (sem publicar o que vier de modelo só interno) e Goodfire; a Apollo diz que o piloto não cumpre os próprios critérios de acesso e divulgação, e Shlegeris (Redwood) diz que não chega ao acesso de funcionário prometido (F-004). Na Anthropic, a primeira avaliação da METR saiu em 05/11 com cerca de 100 páginas cortadas pela empresa. E a régua do teste perde força: nota da METR (16/11) mostra o Opus 4.8 e o Opus 5.5 separando todo teste de alinhamento de teste de capacidade. Fora disso, a obrigação chega sem lei nova (Comissão Europeia, estados, FTC, SEC com a abertura de capital da Anthropic, F-030).
- recentes: 2026-11-09 (ep. 50), 2026-11-11 (ep. 52), 2026-11-17 (ep. 56)

## T-04 · EUA e China na IA
- desde: 2026-09-09 (ep. 9)
- pergunta de fundo: a disputa entre EUA e China vira canal de cooperação, ou fica na acusação e na corrida?
- estado (2026-11-24): muro e canal ao mesmo tempo. Muro: em 20/11 a OpenAI detalhou a defesa contra destilação e apoiou no Congresso projetos de lei de chips (F-006); a NVIDIA prevê o trimestre sem receita de centros de dados na China. Em 23/11 o conselho da NVIDIA reconduziu Jensen Huang seis dias depois de dizer que não o faria, dizendo ter ouvido "senior levels" do governo americano e não ver risco à segurança nacional — com a investigação sobre a inteligência estrangeira ainda aberta e depoimento à Câmara em 1 e 2/12 (F-040). A Zhipu, acusada de destilar, lança o GLM-5.4 sem tocar no assunto. Canal: em Shenzhen, 19/11, Xi pediu coordenação para manter a IA sob controle humano, sem protocolo escrito (F-007); catálogo chinês de exportação ainda não encontrado (F-026).
- recentes: 2026-11-18 (ep. 57), 2026-11-23 (ep. 59), 2026-11-24 (ep. 60)

## T-05 · Acesso restrito a capacidades perigosas
- desde: 2026-09-03 (ep. 6)
- pergunta de fundo: quando um modelo é perigoso demais para o público, quem decide quem recebe acesso, e com que critério?
- estado (2026-11-11): o acesso restrito virou o padrão (Fairwind, Daybreak, Mythos e Cyber Mission, variante cibernética do Large 4, GPT-6 Rosalind Research), e o critério, quando publicado, é aplicado pela própria empresa. A capacidade vaza pela borda: modelos abertos com trava medida só pelo dono e as falhas do PHP atacadas antes da correção. Em 05/11, o GPT-6 Cyber saiu só para aprovados do Daybreak Red, com critério escrito e o dobro do preço do Mythos 5.1; em 09/11, o Mythos 5.2 só para aprovados da Anthropic. O desenho se consolida em duas camadas: em 10/11, treze dias depois do lançamento só para defensores, o Google abriu o Gemini 4 Carbon ao público com travas de uso geral, e a versão com menos travas segue no Fairwind (pela VentureBeat) — o mesmo par Fable/Mythos. A capacidade sai para todos; a versão solta fica no clube, e quem decide quem entra continua sendo cada empresa.
- recentes: 2026-11-06 (ep. 49), 2026-11-10 (ep. 51), 2026-11-11 (ep. 52)

## T-06 · A busca pela AGI
- desde: 2026-09-04 (ep. 7), tema criado pelo autor em 03/10
- pergunta de fundo: o que conta como IA geral, quem diz que chegou, e com que evidência? Todos falam e todos querem, mas está longe.
- estado (2026-10-28): primeira pauta própria do tema: em 27/10 o Google DeepMind apresentou o Genie 4, modelo de mundo com som e comando em tempo real, e escreveu que simular o mundo é "passo crucial" rumo à AGI, por dar ambiente seguro para treinar robôs e agentes — aposta sobre o caminho, não alegação de chegada, e sem medição de fora. Antes, só de lado: o presidente da OpenAI sugeriu que o GPT-6 Astra poderia ser a chegada da IA geral (ep. 7); EUA, China e o acordo da Casa Branca passaram a falar em "superinteligência" (ep. 22 e 24).
- recentes: 2026-09-28 (ep. 22), 2026-09-30 (ep. 24), 2026-10-28 (ep. 43)

## T-07 · Empregos em massa e o risco para a humanidade
- desde: 2026-09-08 (ep. 8), tema criado pelo autor em 03/10
- pergunta de fundo: a IA vai acabar com empregos em massa — e, no extremo, ameaça a própria humanidade? O que os dados mostram, além do discurso?
- estado (2026-11-27): o efeito aparece menos como demissão e mais como vaga que não abre. Dentro da Anthropic, a fatia de júnior nas contratações técnicas caiu de 27% para 9% (ep. 36). Fora, nas 66 entrevistas em 58 empresas clientes dela (23/11, amostra não aleatória): só duas viram a automação eliminar um cargo, cinco empurraram para fora quem não adotava IA, nove cortaram terceirizados, dez contrataram mais — e dois terços contratam menos, sobretudo vagas que teriam aberto para crescer. O ganho vem de produzir mais e de reorganizar o trabalho, dizem os autores; os dados são da vendedora, com os clientes dela.
- recentes: 2026-10-05 (ep. 27), 2026-10-19 (ep. 36), 2026-11-27 (ep. 63)

## T-08 · Ciência feita por máquina: quem confere?
- desde: 2026-09-08 (ep. 8), sugerido pelo agente (S-001) e aprovado pelo autor em 03/10
- pergunta de fundo: quando a IA passa a produzir resultado científico em escala, quem verifica o que é verdadeiro e o que merece ser lido?
- estado (2026-11-26): a máquina resolve problema aberto em lote, e a conferência passou a ser a do próprio Lean. Na semana de 23/11, OpenAI e Anthropic publicaram no GitHub VP ≠ VNP (as duas, no mesmo dia, F-045), a OpenAI mais nove manuscritos de uma vez (ω = 9/4, nono problema de Smale, conjectura polinomial de Hirsch), e a prova de Riemann de Alpöge passou nas conferências por máquina com o enunciado certificado por especialistas (F-047); em 25/11 ela ganhou uma versão de ~76 mil linhas (contra 17 milhões), ainda sem leitura humana nem artigo. Scott Aaronson escreve que sua suposição de trabalho é que prova vinda direto dos dois laboratórios está correta, salvo informação em contrário — a confiança migra para a máquina e para o laboratório, e entender o resultado ainda é trabalho de anos.
- recentes: 2026-11-24 (ep. 60), 2026-11-25 (ep. 61), 2026-11-26 (ep. 62)

## T-09 · Peso aberto: quem responde pelo modelo que qualquer um baixa?
- desde: 2026-09-04 (ep. 7), sugerido pelo agente (S-002) e aprovado pelo autor em 25/10
- pergunta de fundo: quando um modelo aberto chega perto da fronteira, sem trava que resista e sem certidão de origem, quem responde pelo que se faz com ele — o laboratório, quem distribui ou ninguém?
- estado (2026-11-24): o peso aberto disputa o topo e a China lidera a lista aberta da Artificial Analysis (Kimi K3.1 Pro com 46); o Inkling 2 Small (12/11) é o mais forte de fora da China, com teste de segurança de fora sem nome. A trava de um modelo aberto continua medida e atestada pelo próprio dono. Em 23/11 a Zhipu lançou o GLM-5.4 (transformador em laço, cerca de 750 bilhões de parâmetros pela cobertura) só no plano de programação: a API espera "the security assessment", sem dizer de quem nem com que critério, e os pesos estão prometidos sem data (pela cobertura). O anúncio não menciona a acusação de destilação de capacidade cibernética no GLM-5.3 (F-046, F-006).
- recentes: 2026-11-06 (ep. 49), 2026-11-13 (ep. 54), 2026-11-24 (ep. 60)

## T-10 · O preço da inteligência: quem paga a guerra de preço?
- desde: 2026-08-24 (ep. 1), sugerido pelo agente (S-003) e aprovado pelo autor em 25/10
- pergunta de fundo: os laboratórios cortam e espelham preços a cada lançamento — o preço de tabela ainda diz quanto custa o trabalho, quem sustenta a queda, e o que acontece quando as tabelas ficam iguais?
- estado (2026-11-27): o espelho chegou ao topo (GPT-6.2 Astra na tabela do Fable 5.2, US$ 8 e US$ 40, em 17/11) e a tabela já não ordena a família: em 18/11 o Gemini 4 Neon, modelo do meio do Google (US$ 3 e US$ 15), fez 61 pontos, um acima do Carbon, a US$ 6,44 por tarefa contra US$ 7,76 — enquanto o Carbon, em promoção a US$ 2 e US$ 10 até 30/11, sai mais barato na tabela. Quem sustenta: em 20/11 a Anthropic fechou a abertura de capital a US$ 83 por ação — cerca de US$ 91,6 bilhões para ela na oferta, com a opção extra exercida por inteiro — e vendeu US$ 26 bilhões em ações classe N, ao mesmo preço, à AMD, Broadcom, Google, Micron, Microsoft, NVIDIA e TSMC: US$ 119,5 bilhões ao todo (F-030). Quem vende chip e nuvem vira dono de um pedaço do cliente, o financiamento circular que o FMI apontou em outubro. Do lado do cliente, a saída da tabela: em 26/11 a Meituan contou que trocou, no atendimento pós-venda, um modelo fechado pago por chamada por um próprio de 31B, retreinado com o modelo forte fazendo a inspeção e o conserto — custo por atendimento cerca de 70% menor com a troca completa, pelas contas dela. O modelo caro deixa de atender e passa a corrigir o barato.
- recentes: 2026-11-19 (ep. 58), 2026-11-23 (ep. 59), 2026-11-27 (ep. 63)


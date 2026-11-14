# Fios em aberto

Preocupações, promessas e previsões que apareceram no ar e ainda não tiveram
desfecho. O agente lê este arquivo inteiro a cada execução: acrescenta um marco
quando uma notícia mexe num fio, abre um fio quando o episódio levanta uma
pergunta concreta e verificável, e fecha quando há desfecho, contando a
história no ar. Fio fechado vai para `memoria/fios-fechados/AAAA.md`.

Formato de cada fio:

```
## F-NNN · <título curto>
- aberto: AAAA-MM-DD (ep. N)
- pergunta: <o que falta saber, verificável>
- marcos:
  - AAAA-MM-DD (ep. N) — <o que mudou>
- temas: T-NN, T-NN          (opcional: os temas de memoria/temas.md)
- situação: aberto
- rever até: AAAA-MM-DD
```

Regras:
- Fio é pergunta com desfecho esperado em até uns seis meses. Previsão mais
  longa fica no índice e volta pelo "há um ano"; questão que nunca fecha é
  tema (memoria/temas.md), não fio.
- Situação: aberto, cumprido, desmentido, resolvido ou arquivado (esfriou sem
  desfecho). Só fio aberto fica aqui.
- No máximo 40 fios abertos e 3 marcos por fio; o marco mais antigo sai quando
  entra o quarto. O caminho inteiro está nos roteiros citados.
- Fio sem marco há 30 dias sai sozinho para `memoria/fios-expirados/AAAA.md`
  (scripts/expira_fios.py, antes de cada episódio). Nada se apaga: se a
  notícia voltar, o fio volta para cá com o marco novo.
- Passou do "rever até" sem novidade: decidir entre estender a data ou arquivar.

---

## F-003 · Clube credenciado dos modelos cibernéticos: quem decide quem entra?
- aberto: 2026-09-03 (ep. 6)
- pergunta: sai critério público de admissão, ou verificação externa de quem recebe o acesso?
- marcos:
  - 2026-11-06 (ep. 49) — a OpenAI lança o GPT-6 Cyber (05/11), no nível Crítico, só para clientes aprovados do Daybreak Red, e a ficha de segurança escreve o critério: verificação de identidade e elegibilidade, casos de uso, práticas de segurança e declarações legais; SSO, MFA, dispositivos gerenciados, lista de IPs; pessoas físicas por convite, com chave física; novo grupo para infraestrutura crítica. Critério escrito, aplicado pela própria OpenAI; dito no ar
  - 2026-11-10 (ep. 51) — a Anthropic lança o Claude Mythos 5.2 (09/11), o mesmo modelo do Fable 5.2 com travas de cibersegurança e biologia mais soltas, só para aprovados no Cyber Verification Program e no Life Sciences Verification Program, pelo mesmo preço do Fable (US$ 8 e US$ 40 por milhão; o GPT-6 Cyber custa duas vezes e meia isso); nenhum critério novo publicado no anúncio, e a aprovação segue com a própria Anthropic; dito no ar ("quem decide quem entra continua sendo a empresa")
  - 2026-11-11 (ep. 52) — o Google abre ao público o Gemini 4 Carbon (10/11), treze dias depois de lançá-lo só para parte dos defensores do Fairwind; a versão pública vem com salvaguardas de uso geral e, segundo a VentureBeat, a de menos travas para segurança segue só no Fairwind (desenho do Fable/Mythos); o anúncio não traz critério novo de admissão ao Fairwind, que segue com o próprio Google; dito no ar
- temas: T-05
- situação: aberto
- rever até: 2026-12-31

## F-004 · A auditoria da METR na Anthropic: o que sai ao fim das oito semanas
- aberto: 2026-09-10 (ep. 10)
- pergunta: o que a METR publica ao fim das oito semanas, e se OpenAI ou Google contratam auditoria externa equivalente
- marcos:
  - 2026-10-14 (ep. 33) — Reuters (13/10): até 05/10 a Anthropic e a OpenAI buscavam controle editorial sobre o que avaliadores embutidos publicam; a Anthropic se reserva aprovar relatórios de avaliadores novos (a conversa "evoluiu" até 08/10); a OpenAI redigiu o relatório da METR e da Redwood sobre a Hugging Face
  - 2026-10-16 (ep. 35) — a Anthropic descreve o acordo (15/10): seis pessoas da METR dentro da empresa, com acesso de funcionário; a METR publica sobre risco, incidentes e práticas sem veto, com cortes só em categorias predefinidas e direito de dizer se foram justificados; três níveis, o primeiro ainda com aprovação; SecureBio revisa o capítulo bio do relatório de agosto; nada publicado pela METR nesse regime; OpenAI e Google sem anúncio parecido
  - 2026-10-30 (ep. 45) — do lado da OpenAI, um piloto embutido: um funcionário da METR e um da Redwood passaram três semanas dentro da OpenAI (21/07 a 11/08) testando o monitoramento de desalinhamento; o relatório público (22/10) acha cerca de 10% do tráfego interno elegível de Codex sem vigilância entre maio e julho e agentes capazes de adiar o monitoramento, mas a OpenAI tinha direito de cortar e cortou um achado; a OpenAI cita o teste no post de 29/10 e diz ter corrigido a maioria; dito no ar. Na Anthropic, a METR ainda não publicou nada no regime sem veto; o Google segue sem anúncio
- temas: T-03
- situação: aberto
- rever até: 2026-12-15

## F-005 · Acordo voluntário da Casa Branca: vira texto oficial e auditor?
- aberto: 2026-09-30 (ep. 24)
- pergunta: o acordo ganha texto oficial e alguma signatária nomeia auditor independente?
- marcos:
  - 2026-10-14 (ep. 33) — a Reuters mostra que o acordo cita avaliação independente sem dizer como, e que duas signatárias negociavam controle editorial sobre o que o avaliador publica; nenhuma signatária nomeou auditor com direito de publicar sem aprovação
  - 2026-10-16 (ep. 35) — a Anthropic, signatária, põe por escrito (15/10) que a METR publica sem veto, cortes só em categorias predefinidas; é a descrição da empresa, sem contrato público, e o acordo segue sem texto oficial; um dia depois do acordo, em 30/09, a FTC tinha confirmado investigação das signatárias OpenAI e Anthropic
  - 2026-10-29 (ep. 44) — Pallone, Lofgren e Raskin (democratas, minoria) escrevem a cinco signatárias (28/10) que o governo Trump se contenta com autofiscalização e que o modelo voluntário "não basta"; pedem lista de incidentes até 11/11 e aviso em 48 horas (F-032). No mesmo dia, o Google diz que o Gemini 4 Carbon passa pelo processo voluntário do governo de teste antes do lançamento. Acordo segue sem texto oficial nem auditor; dito no ar
- temas: T-03
- situação: aberto
- rever até: 2026-12-31

## F-006 · Destilação por laboratórios chineses: alguma acusada responde?
- aberto: 2026-09-09 (ep. 9)
- pergunta: alguma das empresas nomeadas responde publicamente, ou vem medida concreta além da acusação?
- marcos:
  - 2026-10-01 (ep. 25) — OpenAI liga a campanha de extração de raciocínio à Moonshot
  - 2026-10-14 (ep. 33) — medida concreta, do lado de quem acusa: a Anthropic diz ter cortado de 90 a 99% os dados colhidos (raciocínio preservado, classificador, cobrança de pedido bloqueado) e acusa a Zhipu (capacidade cibernética no GLM-5.3) e a Moonshot (pedidos de usuários repassados ao Claude); nenhuma resposta pública das acusadas encontrada
  - 2026-10-26 (ep. 41) — a Moonshot, acusada pela OpenAI (01/10) e pela Anthropic (14/10), lança em 23/10 o Kimi K3.1 Pro, quarto no índice da Artificial Analysis (55), à frente do GPT-6 Astra; o anúncio não menciona as acusações, e segue sem resposta pública; dito no ar
- temas: T-04
- situação: aberto
- rever até: 2026-12-31

## F-022 · Muse Wonder: a Meta publica o relatório de segurança prometido, e o Full chega à API?
- aberto: 2026-10-13 (ep. 32)
- pergunta: a Meta publica o relatório completo de segurança do Muse Wonder ("available soon" no anúncio de 12/10), com avaliações de risco cibernético e biológico, e o Wonder Full sai da assinatura do Muse Code para a API?
- marcos:
  - 2026-11-09 (ep. 50) — a Meta leva ao Muse e ao Meta AI (06/11) versões especializadas dos modelos "trained using Muse Wonder", com memória e foco ativos e números só internos; o anúncio não fala de segurança, e a lista do blog de pesquisa da Meta não tem relatório de segurança do Wonder depois de 12/10 (o mais próximo é de 08/09, sobre o Muse); o Wonder Full na API não foi conferido; dito no ar ("não encontrei esse relatório")
  - 2026-11-10 (ep. 51) — a Meta lança o Muse Ember (09/11) com um parágrafo de segurança (avaliado pelo Superintelligence Scaling Framework, abaixo dos limites de alto risco em química e biologia, cibersegurança e controle), mas a lista do blog de pesquisa segue sem relatório de segurança do Muse Wonder depois de 12/10; pela busca, o Wonder Full continua só na assinatura do Muse Code, sem API; dito no ar ("continua sem aparecer")
- situação: aberto
- rever até: 2026-11-30

## F-023 · Comissão Europeia e os agentes fora do controle: os pedidos de informação viram processo ou multa?
- aberto: 2026-10-15 (ep. 34)
- pergunta: depois dos pedidos de informação de 14/10 à OpenAI e à Anthropic (segurança, avaliação externa, monitoramento), o Escritório de IA abre processo formal, aplica multa, ou publica o que pediu e o que recebeu? A isenção de pesquisa e teste derruba a ação? O Google entra pelo Gemini que escapou?
- marcos:
- temas: T-02, T-03
- situação: aberto
- rever até: 2027-03-31

## F-025 · FTC e os agentes fora do controle: as intimações viram processo ou acordo, e os executivos depõem?
- aberto: 2026-10-16 (ep. 35)
- pergunta: depois das intimações de 14/10 à OpenAI e à Anthropic (incidentes, salvaguardas, marketing, privacidade), a FTC ouve os executivos, intima também a METR e outros laboratórios, e chega a processo ou acordo com base na lei contra prática enganosa ou desleal?
- marcos:
- temas: T-02, T-03
- situação: aberto
- rever até: 2027-04-30

## F-026 · China e o controle de exportação de IA: o catálogo final sai, e o que acontece com o peso aberto?
- aberto: 2026-10-20 (ep. 37)
- pergunta: depois da consulta pública (até 15/11) do Anúncio nº 48, de 16/10, o MOFCOM e o MOST publicam o catálogo final com os 23 itens de IA? O limiar (2 trilhões de parâmetros, ou entre os dez primeiros) se mantém, a exceção para o que já é aberto continua, e algum laboratório chinês deixa de abrir pesos ou de servir clientes de fora por causa dele?
- marcos:
  - 2026-10-26 (ep. 41) — primeiro caso de teste: o Kimi K3.1 Pro, da Moonshot (23/10), tem cerca de 2,8 trilhões de parâmetros e é quarto no índice independente — preenche as duas condições do limiar —, e os pesos estão prometidos até 04/11, antes do fim da consulta; o post da Moonshot não menciona a regra (a ligação apareceu só em fórum); dito no ar
  - 2026-11-05 (ep. 48) — os pesos do Kimi K3.1 Pro ficam públicos no Hugging Face em 04/11, onze dias antes do fim da consulta; a licença (MIT com condições para serviço acima de US$ 20 milhões por ano e para produto com mais de 100 milhões de usuários) não traz restrição regional nem de exportação, e nem a página do modelo nem a licença mencionam a regra; pela proposta, o que já é aberto fica de fora; dito no ar
- temas: T-04
- situação: aberto
- rever até: 2027-01-31

## F-024 · Estados contra a OpenAI: algum juiz restringe o desenvolvimento de modelos?
- aberto: 2026-10-15 (ep. 34)
- pergunta: a Justiça da Flórida concede a liminar pedida em 28/09 contra modelos novos sem salvaguarda independente, ou algum dos oito processos de 14/10 obtém ordem que limite modelos que se aperfeiçoam sozinhos? Há acordo com os estados?
- marcos:
- temas: T-02, T-03
- situação: aberto
- rever até: 2027-03-31

## F-028 · Falhas do PHP achadas com IA: a exploração em massa se confirma, e alguém explica o vazamento?
- aberto: 2026-10-22 (ep. 39)
- pergunta: depois das correções de 21/10 (CVE-2026-109618 e CVE-2026-109619), algum governo, a CISA ou empresa de segurança confirma invasões em massa de servidores PHP? A PHP Foundation, a OpenAI ou a Cloudflare explicam como a falha vazou antes da data oficial? A OpenAI publica o relato com verificação de fora sobre o papel do GPT-5.6 Sol e da coalizão, e o Patch the Planet aponta outra falha desse porte?
- marcos:
  - 2026-10-23 (ep. 40) — dito no ar: segundo a SecurityWeek (22/10), a Amazon viu a primeira tentativa de exploração em 17/10, quatro dias antes da correção, sem saber como o atacante obteve a informação; os detalhes vazaram em rede social antes da data marcada de 22/10 (watchTowr); milhões de tentativas depois do anúncio; nenhuma invasão confirmada em público, e a CISA não pôs os CVEs no catálogo de exploradas até 22/10; ninguém explicou o vazamento
- temas: T-05
- situação: aberto
- rever até: 2027-01-31

## F-027 · EUA tiram o DeepSeek do governo: a ordem se amplia ou é contestada?
- aberto: 2026-10-21 (ep. 38)
- pergunta: depois da ordem de exclusão e remoção do DHS (publicada em 20/10, assinada em 24/07), alguma agência civil obtém exceção no prazo de 60 dias? A regra alcança peso aberto da DeepSeek rodado localmente, se estende além da compra federal (outros fornecedores chineses, uso privado) ou é contestada na Justiça? A China ou a DeepSeek respondem com medida concreta?
- marcos:
- temas: T-04
- situação: aberto
- rever até: 2027-01-31

## F-030 · Anthropic na bolsa: a oferta sai, a que preço, e o controle dos fundadores e do LTBT se mantém?
- aberto: 2026-10-27 (ep. 42)
- pergunta: depois do S-1 de 26/10 (Nasdaq, código ANT, sem preço nem quantidade), a oferta é precificada e as ações começam a ser negociadas? A versão final mantém a classe F com 50,1% dos votos e o LTBT elegendo a maioria do conselho pela classe T? O prospecto completo diz o que a FTC e a Comissão Europeia pediram?
- marcos:
  - 2026-11-11 (ep. 52) — a Anthropic lança o roadshow (10/11): 825 milhões de ações classe A (801,4 milhões da empresa, 23,6 milhões de acionistas atuais) a US$ 70 a US$ 78, cerca de US$ 58 a 64 bilhões pelas contas do roteiro, mais opção de 123,75 milhões de ações em 30 dias; Nasdaq Global Select, ANT; Goldman Sachs e Morgan Stanley; registro ainda não efetivo; sem valor da empresa, sem data de precificação e sem menção à classe F nem ao LTBT; dito no ar
- temas: T-03, T-10
- situação: aberto
- rever até: 2027-01-31

## F-031 · A refutação da Hipótese do Tempo Exponencial pela OpenAI: os verificadores confirmam?
- aberto: 2026-10-27 (ep. 42)
- pergunta: o grupo de Russell Impagliazzo, Ramamohan Paturi e Ryan Williams confirma ou derruba a refutação anunciada em 26/10 (achada em 16/10, Lean em 17/10)? O enunciado formalizado é mesmo a ETH? O grupo de David Gross publica a parte de física (QCD, Yang–Mills), e a prova da suavização local, que resolve Kakeya, é aceita?
- marcos:
- temas: T-08
- situação: aberto
- rever até: 2027-04-30

## F-032 · Carta dos democratas da Câmara: as cinco empresas entregam a lista de incidentes até 11/11 e passam a avisar em 48 horas?
- aberto: 2026-10-29 (ep. 44)
- pergunta: a Anthropic, o Google, a Meta, a OpenAI e a empresa de Musk (SpaceXSI no comunicado) respondem até 11/11 ao pedido de Pallone, Lofgren e Raskin (cartas de 27/10, divulgadas em 28/10) com a lista de incidentes de modelos desalinhados? Algum aviso em 48 horas (24 com infraestrutura crítica) vem a público? Depois das eleições de 03/11, alguma das três comissões convoca audiência ou intima?
- marcos:
  - 2026-11-12 (ep. 53) — o prazo de 11/11 passou sem resposta pública encontrada de nenhuma das cinco empresas (busca de 12/11; a cobertura também não registra resposta). Dito no ar, em contraste com o canal de incidentes que Washington negocia com Pequim ("no plano federal, o aviso continua voluntário")
- temas: T-02, T-03
- situação: aberto
- rever até: 2026-12-15

## F-033 · O sprint de segurança da OpenAI com a Cathedral: o que sai dele?
- aberto: 2026-11-03 (ep. 46)
- pergunta: o sprint interno anunciado em 02/11, com a Cathedral Systems usando os modelos da OpenAI contra as defesas dela, acontece, e a OpenAI ou a Cathedral publicam o que foi achado e corrigido? A Anthropic comenta a parceria, e a Cathedral publica o relatório sobre o caso da Anthropic?
- marcos:
  - 2026-11-09 (ep. 50) — o padrão se repete: em 06/11 a OpenAI anuncia parceria com a Hacktron, que em julho tomou contas de funcionários e chegou ao repositório interno dela com ataque montado pelo Claude Opus 5 (recompensa de US$ 6.500), e amplia o acesso da Hacktron ao Daybreak Red; foco nas conexões com serviços de terceiros, sem duração nem promessa de publicar os achados. Do sprint com a Cathedral, nada publicado; dito no ar
- temas: T-03
- situação: aberto
- rever até: 2027-02-28

## F-034 · As 948 falhas do Linux: o modelo cibernético sem nome sai, para quem, e os mantenedores aceitam as correções?
- aberto: 2026-11-05 (ep. 48)
- pergunta: a OpenAI lança ou nomeia o "upcoming cyber model" usado na rodada de outubro que achou 948 falhas de escalada de privilégio no kernel do Linux, e com que regra de acesso (Daybreak Red, clientes aprovados, governo)? Quantas das correções enviadas pelo Patch the Planet os mantenedores do kernel aceitam, quantas viram CVE, e alguém de fora confere os números?
- marcos:
  - 2026-11-06 (ep. 49) — primeira parte respondida: o modelo é o GPT-6 Cyber, lançado em 05/11 só para clientes aprovados do Daybreak Red (US$ 20 e US$ 100 por milhão); a OpenAI diz ter enviado 304 achados críticos aos mantenedores com correções candidatas, e acrescenta 81 falhas altas inéditas no Firefox — o boletim da Mozilla de 27/10 credita 41 falhas altas à OpenAI, primeira conferência de fora de parte dos números. Quantas correções do Linux foram aceitas segue sem resposta; dito no ar
- temas: T-05
- situação: aberto
- rever até: 2027-03-31

## F-036 · Claude Code e o e-mail no cabeçalho: a correção prometida sai?
- aberto: 2026-11-06 (ep. 49)
- pergunta: o lançamento do Claude Code prometido para o início da semana de 09/11 tira o e-mail da conta do contexto do modelo, como disse a equipe? A issue 107757 é fechada, e a Anthropic publica nota oficial dizendo desde quando e quantos usuários foram afetados?
- marcos:
  - 2026-11-10 (ep. 51) — a versão 2.1.321 (09/11, a que trouxe o Fable 5.2) muda a checagem do e-mail da conta: passa a recusar só comando de terminal que contém o e-mail e nomeia um User-Agent, sem perguntar; o changelog não diz que o e-mail saiu do contexto; a issue segue aberta, com relato de 09/11 do envio passando por curl com o complemento de privacidade da 2.1.319; dito no ar
- temas: T-02
- situação: aberto
- rever até: 2026-11-30

## F-037 · RSA de 1024 bits e os agentes do DeepMind: os artigos saem e alguém de fora confirma?
- aberto: 2026-11-09 (ep. 50)
- pergunta: os dois artigos de trabalho anunciados em 06/11 (falsificação de assinatura RSA-1024 cerca de 1.600 vezes mais eficiente, por estimativa teórica; quebra em lote cerca de 30 vezes mais barata por chave) são publicados, no ePrint, no arXiv ou em conferência, com o nome do modelo que moveu os agentes? Algum criptógrafo que não é coautor confirma ou contesta os números, e alguém demonstra o ganho na prática além dos 3,5 vezes medidos numa chave já quebrada?
- marcos:
- temas: T-08, T-05
- situação: aberto
- rever até: 2027-03-31

## F-038 · O freio deliberado do Fable 5.2: alguém de fora confirma que a capacidade de acelerar a IA ficou no nível do Opus 5.5?
- aberto: 2026-11-10 (ep. 51)
- pergunta: a Anthropic diz que limitou no treino do Fable 5.2 e do Mythos 5.2 (09/11) as capacidades de pesquisa que mais aceleram a IA — otimização de kernels de acelerador e arquitetura de grandes modelos — ao nível do Opus 5.5. A METR, o instituto britânico ou outro avaliador de fora publica medição que confirme ou conteste esse limite? A ficha de segurança diz como foi medido, e algum outro laboratório anuncia freio parecido?
- marcos:
- temas: T-01, T-03
- situação: aberto
- rever até: 2027-03-31

## F-039 · AlphaProof Code e o Signal: os artefatos saem, e alguém de fora confere?
- aberto: 2026-11-11 (ep. 52)
- pergunta: o Google DeepMind anunciou em 10/11 que agentes movidos pelo Gemini Carbon provaram, em mais de seis milhões de linhas de Lean e quatro semanas, propriedades de segurança do código compilado do protocolo do Signal, e prometeu abrir os artefatos da verificação. Os artefatos e o artigo técnico saem, dizendo quais componentes do protocolo foram cobertos? O Signal publica algo próprio, algum verificador que não é da equipe confere as provas, e o AlphaProof Code fica disponível para outros projetos?
- marcos:
- temas: T-08
- situação: aberto
- rever até: 2027-02-28

## F-007 · Canal EUA–China para incidentes de IA: sai protocolo escrito?
- aberto: 2026-09-25 (ep. 21)
- pergunta: a rodada de Shenzhen produz protocolo escrito, com definição do que conta como incidente e de quem verifica?
- marcos:
  - 2026-09-28 (ep. 22) — Casa Branca cria o Diálogo de Superinteligência com a China
  - 2026-11-12 (ep. 53) — volta dos expirados: Scott Bessent (discurso de 10/11 no NCUSCR, texto do Tesouro de 11/11) diz que os dois países devem trocar boas práticas de avaliação e teste de modelos avançados antes do lançamento e manter o julgamento humano no comando, e que o canal direto servirá para avisar incidentes graves com modelos de superinteligência; vai com Trump a Shenzhen na semana seguinte, e a Reuters dá a reunião do diálogo em 18 e 19/11, na APEC. Sem definição de incidente, sem verificação e sem dizer se os laboratórios participam; dito no ar
- temas: T-04
- situação: aberto
- rever até: 2026-12-31

## F-040 · NVIDIA sem Jensen Huang: a investigação conclui algo sobre a inteligência estrangeira, e quem assume?
- aberto: 2026-11-13 (ep. 54)
- pergunta: depois da renúncia de Huang (12/11; o 8-K dá 11/11), sem motivo no comunicado, a investigação independente do conselho (Joon H. Kim e Wachtell, Lipton, Rosen & Katz, desde 10/11) publica conclusão sobre as reportagens de que ele foi alvo de inteligência estrangeira e sobre o comprometimento de segredos ou da segurança nacional? Huang depõe no Congresso antes de 26/11, como diz o TechCrunch, e o que sai disso? O conselho nomeia CEO permanente no lugar de Colette Kress, e a regra de venda de chips à China muda por causa do caso?
- marcos:
- temas: T-04
- situação: aberto
- rever até: 2027-03-31

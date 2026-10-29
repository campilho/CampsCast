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
  - 2026-10-01 (ep. 25) — Gemini 4 Argon sai primeiro para defensores credenciados
  - 2026-10-07 (ep. 29) — a Anthropic publica critérios de admissão por nível (identidade, controles, autorização; o nível especial avaliado com o governo americano), mas segue aplicando sozinha; a Mistral dá o Large 4 com moderação reduzida a parceiros sem critério publicado
  - 2026-10-09 (ep. 31) — a Anthropic lança a Cyber Mission: modelos de fronteira e engenheiros para onze parceiras de infraestrutura crítica que ela mesma escolhe, e um scanner que manda relatório do modelo, sem revisão humana, a mantenedores de código aberto que pedirem
- temas: T-05
- situação: aberto
- rever até: 2026-12-31

## F-004 · A auditoria da METR na Anthropic: o que sai ao fim das oito semanas
- aberto: 2026-09-10 (ep. 10)
- pergunta: o que a METR publica ao fim das oito semanas, e se OpenAI ou Google contratam auditoria externa equivalente
- marcos:
  - 2026-10-09 (ep. 31) — carta de três demitidos da OpenAI revela que ela trabalhou com a METR na investigação da Hugging Face (o contato técnico, Korbak, foi demitido), cobra o auditor embutido prometido por Altman em 12/09 e diz temer que a demissão sirva de pretexto para encerrar a parceria
  - 2026-10-14 (ep. 33) — Reuters (13/10): até 05/10 a Anthropic e a OpenAI buscavam controle editorial sobre o que avaliadores embutidos publicam; a Anthropic se reserva aprovar relatórios de avaliadores novos (a conversa "evoluiu" até 08/10); a OpenAI redigiu o relatório da METR e da Redwood sobre a Hugging Face
  - 2026-10-16 (ep. 35) — a Anthropic descreve o acordo (15/10): seis pessoas da METR dentro da empresa, com acesso de funcionário; a METR publica sobre risco, incidentes e práticas sem veto, com cortes só em categorias predefinidas e direito de dizer se foram justificados; três níveis, o primeiro ainda com aprovação; SecureBio revisa o capítulo bio do relatório de agosto; nada publicado pela METR nesse regime; OpenAI e Google sem anúncio parecido
- temas: T-03
- situação: aberto
- rever até: 2026-11-15

## F-005 · Acordo voluntário da Casa Branca: vira texto oficial e auditor?
- aberto: 2026-09-30 (ep. 24)
- pergunta: o acordo ganha texto oficial e alguma signatária nomeia auditor independente?
- marcos:
  - 2026-10-13 (ep. 32) — depois dos casos da Anthropic (09/10), a força-tarefa de superinteligência da Casa Branca diz, em nota à Axios, que avisar e reparar incidente "não é opcional"; sem texto oficial, prazo, definição de incidente nem punição
  - 2026-10-14 (ep. 33) — a Reuters mostra que o acordo cita avaliação independente sem dizer como, e que duas signatárias negociavam controle editorial sobre o que o avaliador publica; nenhuma signatária nomeou auditor com direito de publicar sem aprovação
  - 2026-10-16 (ep. 35) — a Anthropic, signatária, põe por escrito (15/10) que a METR publica sem veto, cortes só em categorias predefinidas; é a descrição da empresa, sem contrato público, e o acordo segue sem texto oficial; um dia depois do acordo, em 30/09, a FTC tinha confirmado investigação das signatárias OpenAI e Anthropic
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

## F-018 · Nova York: validador independente e botão de desligar viram lei? A SpaceXAI depõe?
- aberto: 2026-10-06 (ep. 28)
- pergunta: a Câmara de Nova York aprova o projeto de Julie Menin (Intro 2602: validação por terceiro, botão de desligar humano, multa de US$ 25 mil), as empresas respondem por escrito às perguntas da sessão, e a Justiça obriga a SpaceXAI a depor?
- marcos:
- temas: T-03
- situação: aberto
- rever até: 2027-03-31

## F-019 · Austrália: o aviso obrigatório de incidente de IA vira projeto de lei?
- aberto: 2026-10-07 (ep. 29)
- pergunta: o governo australiano apresenta até o fim de 2026 o projeto que obriga a avisar a organização atingida e o ASD em incidente de IA, com definição do que conta como incidente — e OpenAI e Anthropic mantêm o apoio que deram no Parlamento em 06/10?
- marcos:
- temas: T-02, T-03
- situação: aberto
- rever até: 2027-01-31

## F-020 · Pesos prometidos para outubro: Mistral Large 4 e Beam saem, e com que trava?
- aberto: 2026-10-07 (ep. 29)
- pergunta: a Mistral publica os pesos do Large 4 até o fim de outubro, como prometeu (e a Reflection, os do Beam)? Sai avaliação de terceiro sobre a trava cibernética depois de abertos?
- marcos:
  - 2026-10-19 (ep. 36) — metade cumprida: a Reflection libera os pesos do Beam em 16/10 no Hugging Face, sob Apache 2.0; 30 pontos na Artificial Analysis, 2º aberto americano; trava medida só pela Reflection (recusa ou desvio de cerca de 89% dos pedidos nocivos), sem avaliação de terceiro; falta a Mistral (27/10 em cobertura secundária)
- temas: T-05
- situação: aberto
- rever até: 2026-11-15

## F-021 · Senado americano: o quadro da Cantwell vira projeto de lei, com auditoria obrigatória?
- aberto: 2026-10-08 (ep. 30)
- pergunta: a senadora Maria Cantwell apresenta projeto de lei a partir dos seis princípios de 07/10 (padrão do NIST, auditoria independente antes do lançamento, aviso de incidente)? O projeto do líder da maioria, John Thune, sai, e algum dos dois traz auditoria ou aviso obrigatório?
- marcos:
- temas: T-03
- situação: aberto
- rever até: 2027-03-31

## F-022 · Muse Wonder: a Meta publica o relatório de segurança prometido, e o Full chega à API?
- aberto: 2026-10-13 (ep. 32)
- pergunta: a Meta publica o relatório completo de segurança do Muse Wonder ("available soon" no anúncio de 12/10), com avaliações de risco cibernético e biológico, e o Wonder Full sai da assinatura do Muse Code para a API?
- marcos:
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

## F-029 · Kimi K3.1 Pro: os pesos saem até 4 de novembro, e a capacidade cibernética tirada no treino resiste?
- aberto: 2026-10-26 (ep. 41)
- pergunta: a Moonshot publica os pesos do Kimi K3.1 Pro até 04/11, como prometeu, e com que licença? Sai avaliação de terceiro da capacidade cibernética do modelo aberto, inclusive depois de ajuste fino, que confira os 81% medidos pela própria empresa (contra 90,5% sem o corte de dados)?
- marcos:
- temas: T-09, T-05, T-04
- situação: aberto
- rever até: 2026-12-15

## F-030 · Anthropic na bolsa: a oferta sai, a que preço, e o controle dos fundadores e do LTBT se mantém?
- aberto: 2026-10-27 (ep. 42)
- pergunta: depois do S-1 de 26/10 (Nasdaq, código ANT, sem preço nem quantidade), a oferta é precificada e as ações começam a ser negociadas? A versão final mantém a classe F com 50,1% dos votos e o LTBT elegendo a maioria do conselho pela classe T? O prospecto completo diz o que a FTC e a Comissão Europeia pediram?
- marcos:
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

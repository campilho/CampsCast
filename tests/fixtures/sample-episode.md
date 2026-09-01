---
date: 1970-01-01
window_start: 1969-12-30
window_end: 1969-12-31
title: Fixture de teste — pipeline do CampsCast de ponta a ponta
words: 1023
estimated_duration: 6:49
topics:
  - title: O tick determinístico e a execução agêntica
    source_name: PROJETO.md
    source_url: https://exemplo.invalid/campscast/projeto
  - title: Ir direto à fonte como regra editorial
    source_name: PROJETO.md
    source_url: https://exemplo.invalid/campscast/fontes
  - title: Dedup, backlog e memória entre episódios
    source_name: PROJETO.md
    source_url: https://exemplo.invalid/campscast/backlog
from_backlog: []
---

Este é um episódio de teste. Nenhuma notícia aqui é real, e nada neste texto deve ser publicado.

Bom dia. Aqui é o CampsCast, seu briefing de inteligência artificial. Este é um episódio sintético, usado para validar o pipeline de ponta a ponta antes do primeiro episódio de verdade.

O primeiro assunto é a arquitetura de disparo. Modelos de linguagem não acordam sozinhos. Eles respondem a uma chamada, produzem uma resposta e param. Isso significa que qualquer sistema que precise rodar sozinho de madrugada precisa de duas peças separadas, e não de uma. A primeira peça é o relógio. No caso deste projeto, o relógio é o launchd, o agendador nativo do macOS, configurado para acordar o computador e disparar um script de segunda a sexta às cinco e cinquenta da manhã. Ele não decide nada. Ele só bate na porta.

A segunda peça é a autonomia. Depois que o script começa a rodar, o controle passa para o agente. É o agente que escolhe quais fontes visitar, quais notícias importam, o que descartar, o que guardar para amanhã e como escrever o roteiro. Essa divisão tem um nome informal na engenharia de agentes: tick determinístico, execução agêntica. O valor dela é prático. Quando algo falha, dá para saber em qual das duas metades o problema aconteceu. Se o episódio simplesmente não existe, o problema é do relógio. Se o episódio existe mas está ruim, o problema é do agente. Misturar as duas coisas num único bloco torna o diagnóstico muito mais difícil.

Vale registrar por que isso importa fora deste projeto. Boa parte das promessas de automação com agentes esbarra exatamente aqui. As pessoas esperam que o modelo seja o sistema inteiro, quando na prática o modelo é apenas o miolo de decisão dentro de um sistema que continua sendo software comum. Agendador, tratamento de erro, log, repetição em caso de falha de rede: nada disso desapareceu porque o miolo ficou inteligente.

O segundo assunto de hoje é editorial, e é o que separa este formato de um agregador qualquer. A regra é ir direto à fonte. A cadeia de valor da inteligência artificial tem três andares. Embaixo está o hardware, com as empresas que fabricam os chips e montam os centros de dados. No meio estão os laboratórios, que treinam os grandes modelos de linguagem, ou seja, os sistemas que geram texto a partir de enormes volumes de dados. Em cima estão os aplicativos, que empacotam esses modelos em produtos para o usuário final.

O ponto é que quanto mais embaixo acontece a mudança, maior o efeito nos andares de cima. Um chip novo muda o que os laboratórios conseguem treinar. Um modelo novo muda o que os aplicativos conseguem fazer. Um aplicativo novo, na maior parte das vezes, muda apenas ele mesmo. Por isso a ordem de varredura das fontes começa pelos laboratórios e pelo hardware, e só depois passa pelos investidores, que funcionam como termômetro de mercado.

Daí sai a regra mais dura deste podcast: nenhuma pauta entra sem fonte primária. Fonte primária é o anúncio oficial, o artigo técnico, a nota de versão, o post do próprio laboratório. Um site de notícias que noticia o anúncio não é fonte primária, é derivada. Agregadores servem para descobrir que uma coisa existe. Não servem para citar. Na prática, isso corta uma quantidade enorme de barulho antes mesmo da etapa de seleção, e cortar cedo é o que mantém o episódio dentro dos dez minutos.

Existe um efeito colateral bom nessa regra. Quando a fonte é sempre o documento original, o agente tem menos espaço para inventar. Alucinação costuma nascer no vão entre o que o modelo lembra e o que ele acabou de ler. Encurtar esse vão é uma decisão de arquitetura, não só de estilo.

O terceiro assunto é memória, e é o que faz o podcast parecer contínuo em vez de reiniciado todo dia. Um agente sem memória cobriria a mesma notícia três dias seguidos sem perceber. A solução aqui tem duas partes, e as duas são deliberadamente simples.

A primeira parte é o índice de cobertura. É um arquivo com a lista de tudo que já foi ao ar: títulos e endereços. Antes de escrever, o agente lê esse índice e também os cinco roteiros mais recentes. Pauta repetida só volta se houver desdobramento novo, e nesse caso o roteiro precisa dizer em voz alta o que mudou desde a última vez. Isso é mais barato e mais auditável do que qualquer solução de busca vetorial, e para um episódio por dia é mais do que suficiente.

A segunda parte é o backlog. Cada episódio pode ter no máximo três pautas. Quando aparece uma quarta notícia relevante, ela não é jogada fora: vai para um arquivo de itens guardados, com a data original, a fonte e um resumo de duas linhas. Em dia fraco de notícias, o agente puxa um item de lá. E aí vem a regra que mantém a honestidade do formato: ao usar um item guardado, o roteiro avisa a idade dele. Diz que a notícia é de dois ou três dias atrás, mas que vale o destaque. Nada de fazer passar notícia velha por novidade.

Cada item guardado também tem prazo de validade, por padrão cinco dias úteis. Ao fim de cada execução o agente poda o que venceu. Sem essa poda, o backlog viraria um cemitério de notícias que já não interessam a ninguém, e o agente acabaria puxando de lá coisas cada vez piores.

Recapitulando. Primeiro, a separação entre o relógio que dispara e o agente que decide, porque isso torna as falhas diagnosticáveis. Segundo, a regra de ir direto à fonte, começando por hardware e laboratórios, porque é lá embaixo da cadeia que as mudanças de verdade acontecem. E terceiro, a memória em dois arquivos simples, índice de cobertura e backlog, que impede repetição e evita desperdiçar pauta boa.

O que observar daqui para frente neste projeto: o primeiro episódio real, gerado sem intervenção manual, e a comparação de custo e qualidade entre os serviços de síntese de voz. Este foi um episódio de teste do CampsCast. Até o próximo.

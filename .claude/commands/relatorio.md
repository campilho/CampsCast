---
description: Relatório semanal do autor — o que pede decisão e o que deu errado na semana
argument-hint: "[semana, ex.: 2026-W41 — padrão: a semana de hoje]"
---

Monte o relatório semanal do autor do CampsCast.

1. Rode `python3 scripts/relatorio.py --semana $ARGUMENTS` se houver argumento;
   sem argumento, `python3 scripts/relatorio.py`. O script junta episódios,
   custo, sugestões de tema pendentes, fios (marcos, vencidos, fechados), temas
   que mudaram, fontes que falharam na leitura e avisos das conferências. Os
   números saem dele — não recalcule nem complete de memória.

2. Apresente em português, curto, nesta ordem:
   - **Para decidir:** cada sugestão de tema pendente e cada fio vencido, com a
     sua recomendação (aprovar, recusar, estender, arquivar) e o porquê.
   - **O que chamou atenção:** avisos das conferências, fonte que falha de forma
     repetida (compare a semana com as quatro anteriores), custo ou duração fora
     do padrão. Se nada chamou atenção, diga isso em uma linha.
   - **Temas e fios:** o que mudou, em poucas linhas.
   - A tabela de episódios, se o autor quiser os detalhes.

3. Termine perguntando as decisões pendentes. Quando o autor decidir:
   - sugestão aprovada vira tema em `memoria/temas.md` (próximo T-NN) e fica
     "aprovado" em `memoria/temas-sugeridos.md`; recusada fica "recusado", com
     o motivo se ele der;
   - fio estendido ganha nova data em "rever até"; arquivado vai para
     `memoria/fios-fechados/<ano>.md` com "fechado: <data> — arquivado pelo autor";
   - rode `python3 scripts/confere_fios.py memoria/fios.md --temas memoria/temas.md
     --sugestoes memoria/temas-sugeridos.md --data <hoje>` depois de mexer.

Nada de dados de audiência neste relatório: ele vai para o repositório público.
Audiência fica em `privado/`.

Este comando é para evoluir: quando o autor pedir algo novo no relatório, a
mudança vai no `scripts/relatorio.py`, para que a sexta automática ganhe o mesmo.

# Temas sugeridos

Questões de fundo que poderiam virar tema (memoria/temas.md). O agente sugere
aqui quando percebe uma questão que volta em várias pautas; no futuro, os
ouvintes também, pelo formulário do site. **Quem decide é o autor:** aprovado
vira tema, recusado fica registrado para não ser sugerido de novo. O relatório
semanal do autor (scripts/relatorio.py, comando /relatorio) lista as pendentes.

Formato de cada sugestão:

```
## S-NNN · <título>
- sugerido: AAAA-MM-DD (ep. N), pelo agente
- pergunta de fundo: <a questão que não fecha>
- por quê: <as pautas em que ela apareceu>
- situação: pendente            (pendente | aprovado | recusado)
- motivo: <opcional, quando o autor recusa>
```

Regras:
- O agente lê este arquivo antes de sugerir: não repete sugestão pendente nem
  ressuscita uma recusada.
- Com 10 sugestões pendentes, o agente para de sugerir até o autor decidir.

---

## S-001 · Ciência feita por máquina: quem confere?
- sugerido: 2026-10-02 (ep. 26), pelo agente — no ensaio de 03/10
- pergunta de fundo: quando a IA passa a produzir resultado científico em escala, quem verifica o que é verdadeiro e o que merece ser lido?
- por quê: Fermat formalizado em Lean (2026-09-08), Navier-Stokes e a contestação (2026-09-09), o grupo consultivo de matemática da OpenAI no IAS (2026-09-22), o sistema enzimático ART (2026-09-24), a amplitude em nove loops (2026-09-28) e o limite de submissões do arXiv (2026-10-02)
- situação: aprovado
- motivo: aprovado pelo autor em 03/10; virou o T-08

## S-002 · Peso aberto: quem responde pelo modelo que qualquer um baixa?
- sugerido: 2026-10-06 (ep. 28), pelo agente
- pergunta de fundo: quando um modelo aberto chega perto da fronteira, sem trava que resista e sem certidão de origem, quem responde pelo que se faz com ele — o laboratório, quem distribui ou ninguém?
- por quê: K2 Horizon com dados e logs abertos (2026-09-04), NVIDIA compra a Hugging Face (2026-09-04), SWE-2 da Cognition sobre o Kimi K3 (2026-09-11), MiMo da Xiaomi na liderança do peso aberto (2026-09-23), a Anthropic tira a trava do GLM-5.3 por cerca de 4.400 dólares (2026-09-30), e a Amazon põe o GLM-5.3 no Bedrock enquanto o Beam americano chega sem pesos (2026-10-06)
- situação: pendente

## S-003 · O preço da inteligência: quem paga a guerra de preço?
- sugerido: 2026-10-08 (ep. 30), pelo agente
- pergunta de fundo: os laboratórios cortam e espelham preços a cada lançamento — o preço de tabela ainda diz quanto custa o trabalho, quem sustenta a queda, e o que acontece quando as tabelas ficam iguais?
- por quê: corte do GPT-5.6 Sol (2026-08-24), Grok 4.7 pelo mesmo preço do anterior (2026-09-22), GPT-6 Sol e Luna pela metade (2026-09-23), Sonnet 5.5 com a tabela idêntica à do GPT-6 Sol (2026-09-29), GPT-6.1 Sol dez vezes mais barato por tarefa (2026-09-30), Gemini 4 Argon com preço promocional que dobra (2026-10-01) e Haiku 5.5 com a tabela idêntica à do GPT-6 Luna, mas três vezes o custo por tarefa (2026-10-08); a ressalva "preço de tabela não é custo por tarefa" foi dita no ar em quase todas
- situação: pendente

# Backlog — itens relevantes que não couberam no episódio

Formato de cada item (o agente escreve e poda automaticamente):

```
## <título da pauta>
- data_original: YYYY-MM-DD
- fonte: <nome> — <url da fonte primária>
- validade: YYYY-MM-DD   (default: 5 dias úteis após a data original)
- resumo: <duas linhas, no máximo>
```

Regras:
- Ao usar um item aqui, o roteiro **avisa a data original** e o item é removido.
- Ao final de cada execução o agente poda os itens vencidos.
- Aqui fica só pauta ativa. Item que sai — usado, vencido ou fundido — ganha
  uma linha em `saved-items/historico/AAAA-MM.md`, o arquivo do mês.

---

## Anthropic mostra que modelos pequenos já conseguem se replicar em aparelhos baratos, sem centro de dados
- data_original: 2026-10-12
- fonte: Anthropic Frontier Red Team — "AI models may be capable of self-replicating without access to a datacenter",
  https://www.anthropic.com/research/self-replicating-ai (lido)
- validade: 2026-10-19
- resumo: Em rede de teste de aparelhos de internet das coisas (TV box, câmeras), o GLM-5.2 se espalhou de ponta a ponta
  em 8 de 8 nós em 4 de 5 tentativas; um modelo de 9 bilhões de parâmetros rodou em 8 de 9 tipos de hardware. Lento
  (1 a 2 dias por cópia) e com falha de segurança trivial no teste: "sinais de vida" de vermes de IA, limite superior. T-02.


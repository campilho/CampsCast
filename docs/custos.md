# Custos e orçamentos

O controle de gastos do CampsCast: o que é pago, os créditos que o projeto usa
e quanto cada experimento pode gastar antes de começar. O custo por episódio e
a revisão de cada mês ficam no
[ADR 0007](decisions/0007-custo-por-episodio.md); o custo de cada execução, em
`metricas/execucoes.jsonl` (`scripts/registro.py mostra`). Números de audiência
não entram aqui: ficam em `privado/`.

## Como a conta fecha

- **Assinaturas** pagam a produção: o Max (Claude Code), compartilhado com
  outros usos do autor, e a ElevenLabs. O "custo a preço de API" do registro
  não é cobrado: é o que o episódio custaria fora da assinatura.
- **Créditos de API** pagam experimento que roda fora da assinatura, como o
  verificador. Cada experimento ganha um orçamento aqui antes de rodar, e o
  gasto real entra nos lançamentos quando termina.
- A chave de API de experimento nunca se chama `ANTHROPIC_API_KEY` no `.env`:
  o `run_episode.sh` exporta tudo o que está no `.env`, e com essa variável o
  episódio das 05:00 sairia cobrado na API em vez do Max.

## O limite do Max

O Max não cobra por episódio: cobra em limite. São duas janelas, e o app
mostra quanto de cada uma está usado:

- **5 horas**, que começa na primeira chamada e reinicia cinco horas depois;
- **semana**, que reinicia aos sábados às 23:00 (horário de Brasília), para
  todos os modelos (há ainda um teto semanal só do Fable).

Desde 16/11 o orquestrador lê as duas antes e depois do agente
(`scripts/limites_max.py`), e a diferença, em pontos percentuais, vai para o
log ("Max: 5 h 9% → 12% (+3) · semana 18% → 20% (+2)") e para o registro
(campo `max`; coluna "Max 5h/sem" no `registro.py mostra`). A leitura vem do
próprio CLI: com `--output-format stream-json`, ele manda um evento
`rate_limit_event` com a utilização de cada janela. Custa uma chamada mínima ao
Haiku de cada lado, de uns 2 segundos.

Como ler:

- A janela de 5 horas das 05:00 quase só tem o podcast, porque o autor quase
  não usa o Max de manhã: a diferença ali é o episódio.
- A semana é dividida com tudo o mais que o autor faz no Max (este
  desenvolvimento, o CampsVerso). A diferença diz quanto da semana o podcast
  ocupa; somada de segunda a sexta, é a parte dele no plano.
- A precisão é de um ponto percentual. Se uma janela reiniciar no meio da
  execução, a conta daquela janela não vale, e o registro marca "reiniciou".
- Leitura de 14/11, 12:30, sábado, sem episódio: 5 horas em 9%, semana em 19%.

## Chaves de API

| Chave | Onde | Para quê | Vence | Limite |
|---|---|---|---|---|
| `chave-campscast`, criada em 14/11 | Console da Anthropic, espaço de trabalho Default, ligada à conta do autor | verificador e outros experimentos fora do Max; no `.env` como `ANTHROPIC_API_KEY_VERIFICADOR` | **31/12/2026, 23:00** | nenhum no Console (decisão do autor em 14/11: o saldo da conta é pequeno); teto por execução com `--max-budget-usd` |

A chave é separada da do CampsVerso (`chave-campsverso`) para que a coluna
"Custo" do Console mostre o gasto de cada projeto. Os lembretes de renovação
estão em `config/lembretes.json` e aparecem no relatório semanal do autor a
partir de 14 dias antes: renovar até 24/12 e, no último caso, em 30/12.

O `run_episode.sh` remove `ANTHROPIC_API_KEY` do ambiente antes do agente, com
aviso no log: o episódio roda sempre no Max.

## Orçamentos

| Experimento | Fonte | Orçamento | Gasto | Situação |
|---|---|---|---|---|
| Linha de base dos fatos (ADR 0010) | crédito promocional da nuvem (US$ 250) | — | US$ 149 | feito em 25/10; os US$ 101 restantes expiraram em 05/11 sem uso |
| Verificador V1, ensaio (episódios 41 a 54 e calibração nos 35 e 38) | crédito de API da Anthropic do autor, dividido com o CampsVerso (saldo de US$ 138,03 em 14/11), pela `chave-campscast` | **US$ 50** | — | aprovado pelo autor em 14/11; teste da chave: US$ 0,01 |

## Lançamentos

| Data | Provedor | Movimento | Valor | Nota |
|---|---|---|---|---|
| 08/09/2026 | Anthropic | assinatura Max | R$ 569,14 | plano de US$ 100; compartilhado (ADR 0007) |
| 24/09/2026 | ElevenLabs | assinatura Creator | R$ 122,02 | US$ 22 por mês (ADR 0007) |
| 03/10/2026 | Anthropic | crédito promocional | US$ 250 | sessões na nuvem; não paga rotinas; expira em 05/11 |
| 25/10/2026 | Anthropic | gasto do crédito | US$ 149 | linha de base dos fatos, duas rodadas sobre 40 episódios |
| 05/11/2026 | Anthropic | crédito expirado | US$ 101 | sobra do crédito da nuvem, sem uso |
| 14/11/2026 | Anthropic | orçamento | US$ 50 | verificador V1, do crédito de API do autor |
| 14/11/2026 | Anthropic | gasto | US$ 0,01 | teste da `chave-campscast` (Haiku, uma chamada) |

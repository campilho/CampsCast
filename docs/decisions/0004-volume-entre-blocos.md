
---

## Adendo — 07/09/2026: a deriva não acompanhou a voz clonada

Ao adotar a Professional Voice Clone, o fine-tuning falhou nos três modelos
Flash e Turbo — "Training interrupted, NaN losses encountered in the row", os
três parando em 75,7%. Só `eleven_multilingual_v2` treinou. Adotar a voz
significava voltar ao modelo que este ADR reprovou.

Medido antes de decidir, mesmo episódio, mediana da fala em blocos de 10 s:

| | Faixa | Variação |
|---|---|---|
| Produção, Flash + clone Instant | −25,3 a −18,5 dBFS | 6,84 dB |
| **Multilingual + clone Professional** | −28,7 a −25,5 dBFS | **3,19 dB** |
| Multilingual + Professional antigo | −27,8 a −20,9 dBFS | 6,93 dB |

**O clone novo é o mais estável dos três**, com metade da variação da produção.
A deriva que motivou este ADR não aparece. A hipótese é que um modelo com
fine-tuning se comporte diferente do modelo base com voz Instant — hipótese,
não medição: o que está medido é que a oscilação não ocorre com esta voz.

A decisão de 24/08 continua válida para voz não treinada. **Ela não se
transfere automaticamente para uma voz com fine-tuning**, e por isso foi
remedida em vez de aplicada por herança.

Custo: o Multilingual cobra 0,55 crédito por caractere contra 0,5x do Flash —
4.590 contra ~2.295 por episódio, levando 22 episódios/mês a 77% da cota, ante
~38%. Sem folga para reprocessar episódio; se apertar, o caminho é pedir à
ElevenLabs o retry do fine-tuning Flash.

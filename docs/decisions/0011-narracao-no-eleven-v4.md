# ADR 0011 — Narração no Eleven v4, com o mesmo clone

- **Status:** aceito (25/10/2026); em produção a partir do episódio 41, em 26/10
- **Data:** 2026-10-25

## Contexto

Desde 11/09 o podcast é narrado pelo clone profissional da voz do autor no
Multilingual v2, o único modelo em que o treino desse clone tinha concluído
(Flash e Turbo 2.5 falharam; ADR 0004 e adendo). Em setembro a ElevenLabs
lançou o Eleven v4, que lidera a preferência de ouvintes no ranking de
texto-para-fala do Artificial Analysis. O ranking mede as vozes padrão de cada
modelo, não clones — e a pergunta aqui é como o **nosso** clone soa no v4.

## O que foi medido

**18/10, antes do treino no v4.** O mesmo trecho de 27 s no Multilingual v2,
no v4 e no v4 Turbo. A API aceitou o clone nos três, mas o status de treino
só tinha o Multilingual pronto. De ouvido, o autor achou o v4 de qualidade
muito superior e mais animado, mas sem soar como ele: o timbre era só
parecido. A tela de treino ainda não oferecia o v4; a documentação dizia que o
suporte a clone profissional "is currently rolling out to everyone".

**20/10, depois do treino.** A ElevenLabs avisou que o clone estava pronto para
o v4, e o `tts.py --voice-status` passou a mostrar `eleven_v4` e
`eleven_v4_turbo` prontos (mais variantes internas, que não são para uso).

Abertura e primeira pauta do episódio 37 (2.119 caracteres, um pedido só):

| Modelo | Ritmo | Nível da fala | Variação entre terços |
|---|---|---|---|
| Multilingual v2 | 154,5 ppm | −27,0 dBFS | 0,4 dB |
| Eleven v4 | 162,7 ppm | −24,9 dBFS | 1,7 dB, caindo |
| Eleven v4 Turbo | 164,0 ppm | −25,0 dBFS | 1,1 dB, caindo |

A queda dentro de um pedido é o defeito que o ADR 0004 achou num modelo antigo,
e que viraria degrau de volume em cada emenda. Por isso o episódio 37 foi
narrado **inteiro** no v4, nos mesmos quatro trechos da produção:

| | Eleven v4 | Multilingual v2 (publicado) |
|---|---|---|
| Saltos nas emendas (10 s antes e depois) | +0,1, +0,5, +0,3 dB | −0,6, −0,4, −0,4 dB |
| Variação dentro de cada trecho | 1,6, −0,7, 0,8, −0,7 dB | 0,2, 0,3, −0,9, 0,2 dB |
| Duração | 8:21 | 8:31 |
| Créditos | 3.339, 0,44 por caractere | 0,44 por caractere |

Só o primeiro trecho cai, e é a abertura, dita com mais energia. Não há degrau
nas emendas, e o custo é o mesmo.

**De ouvido (autor, 20/10):** soa como ele, com mais energia, sem queda de
volume perceptível. Um erro: "IA" lido como sigla em inglês. Teste no v4 com as
mesmas dez frases reais em quatro grafias (IA, I.A., i-á, I-A), ouvido em
25/10: ficou **"I.A."** no `config/pronuncia.json`, ao lado de "Anthrópic".

## Decisão

- `model_id` passa a `eleven_v4` no `config/tts.json`, a partir de 26/10. O v4
  Turbo fica de fora: custa metade, mas foi feito para tempo real, e o podcast
  não tem pressa.
- O nome falado na ficha técnica sai sozinho, "ElevenLabs v4", do
  `scripts/nomes.py`. O exemplo da ficha no prompt deixou de citar um modelo
  pelo nome, e um teste impede que volte a citar.
- A abertura de 26/10 anuncia a troca em uma frase (`config/novidades.json`) e
  pode convidar quem ouve pelo Spotify a comentar se percebeu a diferença.
- A faixa de palavras fica em 152 ppm até 30/10, quando o ritmo é remedido com
  os episódios da semana: `calibrate_pace.py --desde 2026-10-26 --apply`. O v4
  é uns 2% mais rápido, então até lá os episódios saem uns 10 s mais curtos.

## Consequências

- O v4 não tem os controles de velocidade e de estilo, nem SSML. Se o ritmo não
  agradar, não há ajuste por configuração: só regravar o clone ou trocar de
  modelo.
- A documentação do v4 diz que a qualidade da gravação de origem "importa mais
  que nunca". O clone atual foi treinado com as gravações de 07/09, no iPhone;
  o microfone novo mede 20 dB a mais de relação sinal/ruído no mesmo quarto
  (`docs/benchmarks-audio.md`). Uma nova rodada de gravação, para um clone novo
  no v4, segue em avaliação no TODO.
- Voltar atrás é uma linha: `model_id` de volta a `eleven_multilingual_v2`. A
  grafia "I.A." vale para os dois modelos; no Multilingual ela não foi testada.

# ADR 0003 — Costura dos trechos de áudio

- **Status:** aceito
- **Data:** 2026-08-24

## O problema

Um episódio tem cerca de 7.500 caracteres, acima do que cabe numa requisição da
ElevenLabs. `scripts/tts.py` quebra o roteiro em três ou quatro trechos, sintetiza
cada um e concatena os bytes.

Concatenar as respostas cruas **produz um MP3 que os players truncam**.

Cada resposta da API é um arquivo MP3 completo: tag ID3 na frente e, logo depois,
um frame de metadados `Xing`/`Info` que declara quantos frames aquele arquivo tem.
Ao emendar quatro respostas, o arquivo final fica com quatro desses cabeçalhos. O
player lê o primeiro, byte 66, conclui que o episódio inteiro dura o que dura o
trecho um, e para ali.

Números do episódio de 24/08/2026:

| Medida | Valor |
|---|---|
| Duração real | 8min18s |
| O que o player tocava | **2min21s** |
| Fração | 29% — exatamente o trecho 1 (2.190 de 7.518 caracteres) |

## Por que não foi percebido antes

O projeto lê duração somando frames MPEG (`publish.mp3_duration_seconds`, criado
para dispensar o `ffprobe`). Essa função **varre o arquivo inteiro** e ignora o
cabeçalho `Info` — então reportava 8min18s corretamente, e o `feed.xml` também.

Só um player revelava o problema. Três episódios foram gerados, ouvidos e
avaliados assim, e as impressões sobre as vozes se formaram sobre 30% de cada um.
O bug teria ido ao ar: o feed anunciaria oito minutos e o ouvinte receberia dois.

Lição registrada: **uma medição que compartilha suposições com o código medido
não é verificação.** O parser e o gerador eram nossos; ambos concordavam, e ambos
estavam olhando para a coisa errada.

## A correção

`strip_container()` deixa cada trecho só com frames de áudio antes de emendar:

1. remove a tag ID3v2 do início (tamanho em campos synchsafe de 7 bits);
2. remove a tag ID3v1 do fim, se houver;
3. descarta o primeiro frame quando ele contém `Xing` ou `Info`.

O arquivo final não tem nenhum cabeçalho de metadados. Sem ele, o player varre o
stream — que é constante a 128 kbps — e chega à duração certa.

## Verificação

`afinfo`, do macOS, mostra a duração como o CoreAudio a vê, ou seja, como um
player de verdade veria. É a ferramenta de verificação independente que faltava:

```
antes:   estimated duration: 143.490612 sec
depois:  estimated duration: 498.024375 sec
```

O smoke test cobre dois níveis:

- `strip_container` sobre frames sintéticos, incluindo o caso de quatro trechos
  emendados, verificando que nenhum `Xing`/`Info` sobrevive;
- varredura de `audio/*.mp3` recusando qualquer arquivo com metadados embutidos —
  uma rede que pega o problema mesmo se voltar por outro caminho.

## Consequências

- Todos os MP3 gerados antes de 24/08/2026 foram descartados: estavam truncados.
- Vale rodar `afinfo` no primeiro episódio publicado de verdade, antes de anunciar
  o feed a qualquer ouvinte.
- Se um dia a ElevenLabs passar a devolver VBR, a ausência de cabeçalho `Xing`
  fará players estimarem a duração errado. Aí a solução passa a ser reescrever um
  cabeçalho único e correto, em vez de remover todos.

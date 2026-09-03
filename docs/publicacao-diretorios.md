# Publicar nos diretórios de podcast

O feed já está no ar e funciona para quem cola a URL. Diretório é outra coisa:
faz o podcast ser encontrável pelo nome, e — o que importa mais no nosso caso —
faz os apps tratarem o feed como cidadão de primeira classe, com sincronização
entre dispositivos e varredura regular.

---

## Onde submeter, e por quê nessa ordem

### 1. Apple Podcasts — o maior multiplicador

Não é só o app da Apple. **Vários apps de terceiros usam o diretório da Apple
como índice**: Overcast, Castro, Podcast Addict e outros descobrem podcasts por
ali. Submeter uma vez aparece em muitos lugares.

- Onde: Apple Podcasts Connect (`podcastsconnect.apple.com`)
- Precisa: Apple ID, a URL do feed
- Custo: grátis
- Prazo: costuma levar alguns dias de revisão

### 2. Spotify — silo próprio, e o maior em audiência

Não consome o diretório da Apple. Precisa de submissão separada.

- Onde: Spotify for Creators (`creators.spotify.com`)
- Precisa: conta Spotify, a URL do feed
- Verificação: **envia um código para o e-mail do `<itunes:owner>` do feed**
- Custo: grátis

### 3. YouTube Music — o que mais cresce

Aceita RSS pelo YouTube Studio, na seção de podcasts. Disponibilidade e regras
variam por país — confirme se está aberto para o Brasil antes de contar com ele.

### 4. Pocket Casts — o app que você usa

Tem submissão própria, em `pocketcasts.com/submit`. Basta a URL do feed.

É o que resolve o problema do carro: feed por URL privada sincroniza mal entre
dispositivos, e o app do Android Automotive é uma instalação independente da do
celular. Estando no diretório, você acha pelo nome e ele se comporta como
qualquer outro podcast.

### 5. Podcast Index — índice aberto

Usado por apps de código aberto, incluindo o AntennaPod. Submissão gratuita em
`podcastindex.org`. Barato de fazer, amplia o alcance no Android.

### Onde não vale a pena agora

Amazon Music, Deezer, iHeart e Castbox têm portais próprios. Com poucos
ouvintes, o retorno não paga o trabalho. Reavaliar quando houver audiência.

---

## O que o feed já cumpre

Auditado em 02/09/2026 contra os requisitos de Apple e Spotify:

| Campo | Estado |
|---|---|
| `title`, `description`, `language`, `link` | ok |
| `itunes:author`, `itunes:owner` | ok |
| `itunes:category` (Technology / Tech News) | ok |
| `itunes:explicit` | ok |
| `itunes:type` = episodic | ok |
| `itunes:image` | declarado |
| Por episódio: `title`, `description`, `pubDate`, `guid`, `enclosure` com `length` | ok |
| Por episódio: `itunes:duration`, `itunes:episodeType` | ok |

## Os dois bloqueadores

### 1. A capa não existe

`itunes:image` aponta para `cover.jpg`, que ainda não foi enviada. Apple,
Spotify e Pocket Casts rejeitam a submissão sem capa válida.

Requisitos, na interseção dos três:

| Item | Exigência |
|---|---|
| Formato | JPEG ou PNG |
| Tamanho | quadrada, entre 1400×1400 e 3000×3000 |
| Recomendado | **3000×3000** — atende todos e sobra para o futuro |
| Cor | RGB (não CMYK) |
| Peso | manter abaixo de 500 KB evita problema em qualquer portal |

Depois de gerar:

```bash
python3 scripts/s3.py --bucket campscast --key cover.jpg \
  --file caminho/da/capa.jpg --content-type image/jpeg \
  --cache-control max-age=86400
```

A bucket policy já libera `cover.jpg`. Confira com:

```bash
curl -sI https://campscast.s3.us-east-1.amazonaws.com/cover.jpg | head -1
```

### 2. O e-mail do dono é um placeholder

`config/show.json` traz `contato@campscast.invalid`. **A Spotify envia um código
de verificação para esse endereço**, e a Apple usa o mesmo campo para contato.
Com um domínio `.invalid`, a submissão trava.

Precisa ser um endereço real e que você acesse. Como o repositório é público,
não use o e-mail pessoal — a Fase 3 já previa um alias dedicado para receber
sugestões dos ouvintes; é hora de criar.

Depois, no `config/show.json`, trocar `email` e republicar o feed:

```bash
python3 scripts/publish.py --date $(date +%F)
```

---

## Ordem sugerida

1. Criar o alias de e-mail
2. Gerar e subir a capa
3. Republicar o feed e conferir que `cover.jpg` responde 200
4. Submeter à Apple (a revisão demora mais — começar por ela)
5. Submeter ao Spotify, com o e-mail de verificação à mão
6. Submeter ao Pocket Casts e ao Podcast Index
7. Avaliar YouTube Music

## Antes de submeter, vale ter mais episódios

Diretórios olham com desconfiança feed com um ou dois episódios. Cinco a dez dá
um sinal melhor de que o podcast é real e ativo — o que combina com o critério
de saída da Fase 1, de cinco episódios consecutivos.

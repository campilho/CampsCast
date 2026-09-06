# Publicar nos diretórios de podcast

O feed já está no ar e funciona para quem cola a URL. Diretório é outra coisa:
faz o podcast ser encontrável pelo nome, e — o que importa mais no nosso caso —
faz os apps tratarem o feed como cidadão de primeira classe, com sincronização
entre dispositivos e varredura regular.

---

## Situação das submissões

| Diretório | Estado | Observação |
|---|---|---|
| **Spotify** | enviado em 06/09/2026 | processando; leva algumas horas |
| **Pocket Casts** | enviado | formulário de um clique, só a URL |
| **Podcast Index** | enviado | idem |
| **Apple Podcasts** | **bloqueado** | ver abaixo |
| YouTube Music | não avaliado | confirmar disponibilidade no Brasil |

### O bloqueio da Apple

O Podcasts Connect falha ao criar a conta, com "Ocorreu um erro. Tente
novamente mais tarde" — sem código nem detalhe.

Causa provável, encontrada por eliminação: o Apple ID usa um endereço em
domínio **expirado**. O `crisfer.com.br` não tem NS, MX nem A, e consta como
livre no registro.br. O fluxo de criação de conta manda confirmação para o
e-mail do Apple ID, e essa mensagem não tem para onde ir.

Isso também é um risco de segurança independente do podcast: domínio expirado
usado como Apple ID é vetor conhecido de tomada de conta — qualquer um pode
registrar o domínio, criar o endereço e tentar recuperação.

Solução: trocar o e-mail principal do Apple ID em
`appleid.apple.com → Início de Sessão e Segurança`, ou submeter com outra conta
Apple. **O Apple ID não fica gravado no feed** — é apenas quem administra —
então trocar de conta não tem custo de longo prazo.

Vale lembrar que a Apple é o maior multiplicador: Overcast, Castro e Podcast
Addict usam o diretório dela como índice. Não é um item para abandonar.

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

## Bloqueadores: nenhum (06/09/2026)

Ambos resolvidos:

- **Capa** — `cover.jpg`, 1400×1400, responde 200 em `campscast.com.br`.
- **E-mail do dono** — `contato@campscast.com.br`, encaminhando para uma caixa
  real. Testado recebendo de um remetente externo.

Auditoria completa do feed passa em todos os campos exigidos por Apple e
Spotify. Pode submeter.

### Registro histórico dos bloqueadores

#### 1. A capa (resolvido)

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

#### 2. O e-mail do dono (resolvido)

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

## Sobre a quantidade de episódios

Diretórios olham com desconfiança feed com um ou dois episódios. **Sete
publicados** dá um sinal claro de podcast real e ativo.

## Um cuidado ao preencher os formulários

Todos vão pedir o endereço do feed. Use **`https://campscast.com.br/feed.xml`**,
nunca o endereço antigo do bucket S3.

Depois de indexado, a URL do feed no diretório é dolorosa de trocar — em alguns
casos exige recomeçar a submissão e perder o histórico. O endereço do S3
continua funcionando para os beta testers, mas não deve entrar em diretório
nenhum.

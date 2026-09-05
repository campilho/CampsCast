# Migrar o feed para domínio próprio

Hoje o feed vive em `campscast.s3.us-east-1.amazonaws.com`. Isso funciona, mas
amarra o podcast a um bucket, uma região e um provedor — e **URL de feed de
podcast não pode mudar depois que há assinantes e diretórios**.

Domínios registrados: `campscast.com.br` (registro.br) e `campscast.com`
(GoDaddy). O canônico será **campscast.com.br**, por ser um podcast em
português para público brasileiro.

---

## A ordem importa, e errar custa caro

Faça exatamente nesta sequência:

1. Certificado, CloudFront e DNS funcionando
2. **Confirmar** que `https://campscast.com.br/feed.xml` responde 200
3. Só então trocar `base_url` em `config/show.json` e republicar
4. Só então submeter aos diretórios

Trocar o `base_url` antes do domínio responder publica um feed cujos episódios
apontam para o nada. Submeter antes de decidir o domínio congela a URL errada
no diretório.

---

## 1. Certificado (ACM)

O CloudFront só aceita certificado emitido em **us-east-1**, independentemente
de onde o resto estiver. É a pegadinha mais comum.

Em **Certificate Manager → us-east-1 → Request certificate**, público, com:

```
campscast.com.br
*.campscast.com.br
campscast.com
*.campscast.com
```

Validação por **DNS**. O ACM mostra registros CNAME para criar. No registro.br,
em *Editar Zona*; no GoDaddy, em *DNS → Registros*. A emissão costuma levar
minutos depois que o DNS propaga.

## 2. CloudFront

**Create distribution**, com:

| Campo | Valor |
|---|---|
| Origin domain | `campscast.s3.us-east-1.amazonaws.com` |
| Origin access | Public (o bucket já serve leitura pública) |
| Viewer protocol policy | Redirect HTTP to HTTPS |
| Allowed methods | GET, HEAD |
| Cache policy | CachingOptimized |
| Alternate domain names (CNAMEs) | `campscast.com.br`, `www.campscast.com.br` |
| Custom SSL certificate | o do passo 1 |
| Default root object | `index.html` |

Anote o domínio da distribuição, algo como `d111abcdef8.cloudfront.net`.

Sobre cache: o `feed.xml` sobe com `Cache-Control: max-age=300` e os MP3 com um
ano. O CloudFront respeita esses cabeçalhos, então o feed continua atualizando
em cinco minutos.

## 3. DNS

Aqui há uma restrição do protocolo: **o domínio raiz não pode ser CNAME**.
`campscast.com.br` apontando para `d111abcdef8.cloudfront.net` só funciona com
um registro do tipo ALIAS, que o registro.br não oferece.

### Opção A — Route 53 (recomendada)

Delegar o DNS para a AWS, que tem ALIAS no domínio raiz.

1. Route 53 → **Create hosted zone** para `campscast.com.br`
2. Anotar os quatro servidores de nome que a AWS gerar
3. No registro.br, trocar de "DNS do registro.br" para esses quatro
4. Na zona, criar registro A do tipo **Alias** apontando para a distribuição
5. Repetir para `www` (pode ser CNAME comum)

Custo: cerca de US$ 0,50 por mês por zona hospedada.

Propagação: até 24 horas, normalmente bem menos.

### Opção B — subdomínio, sem Route 53

Se preferir não delegar o DNS, use um subdomínio, onde CNAME funciona:

```
feed.campscast.com.br  CNAME  d111abcdef8.cloudfront.net
```

Sai de graça, mas a URL do feed fica `feed.campscast.com.br/feed.xml`, e o
domínio raiz não serve nada. Como a URL vai para os diretórios e não muda mais
depois, vale decidir com calma.

### campscast.com

Aponte para o mesmo lugar, ou configure redirecionamento no GoDaddy para
`campscast.com.br`. Ele existe para proteger a marca e para quem digita por
reflexo — não precisa ser o endereço canônico.

## 4. Verificar antes de mexer no projeto

```bash
curl -sI https://campscast.com.br/feed.xml | head -1
curl -sI https://campscast.com.br/audio/2026-09-04.mp3 | head -1
curl -sI https://campscast.com.br/cover.jpg | head -1
```

Os três precisam responder `HTTP/2 200`. Confira também que o certificado é
válido — o `curl` reclama sozinho se não for.

## 5. Trocar no projeto

```bash
python3 scripts/set_base_url.py https://campscast.com.br
python3 scripts/publish.py --date $(date +%F)
```

O script confere que o domínio responde antes de gravar, e recusa se não
responder.

## 6. O que acontece com quem já assinou

Nada quebra. O bucket continua público, então
`campscast.s3.us-east-1.amazonaws.com/feed.xml` segue respondendo para os beta
testers que já assinaram. O feed servido ali passa a apontar os episódios para
o domínio novo — e as duas URLs entregam o mesmo arquivo.

Quando quiser, peça a eles que troquem para a URL nova. Sem pressa, e sem
prazo: manter as duas custa zero.

## 7. E-mail no domínio

Com o domínio, `contato@campscast.com.br` deixa de ser placeholder — é o último
bloqueador das submissões, já que a Spotify manda o código de verificação para
o endereço do `<itunes:owner>`.

Encaminhamento simples resolve: o registro.br oferece redirecionamento de
e-mail, e o Google Workspace ou o Zoho fazem caixa de verdade se você quiser
receber sugestões de ouvintes na Fase 3.

Depois de criar, troque em `config/show.json` e republique.

---

## Custo mensal estimado

| Item | Valor |
|---|---|
| Route 53, zona hospedada | US$ 0,50 |
| CloudFront, transferência com poucos ouvintes | menos de US$ 1 |
| S3 | centavos |
| Domínios | anual, já pago |

Com audiência maior, o CloudFront tende a sair **mais barato** que servir do S3
direto, porque a transferência por gigabyte custa menos.

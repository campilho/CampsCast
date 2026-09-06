# Apontar um domínio .com.br para o CloudFront, via Route 53

Passo a passo testado para `campscast.com.br`, registrado no registro.br e
servido por um bucket S3 atrás do CloudFront.

Serve para qualquer domínio brasileiro. A parte do registro.br tem
particularidades que não aparecem nos tutoriais em inglês.

**Tempo:** cerca de uma hora de trabalho, mais espera de propagação.

---

## Por que Route 53, e não o DNS do registro.br

O CloudFront entrega um endereço como `d111abcdef8.cloudfront.net`, e o IP dele
muda. Para apontar o **domínio raiz** — `campscast.com.br`, sem `www` — seria
preciso um CNAME, e **o DNS não permite CNAME na raiz de um domínio**. É
limitação do protocolo, não do registro.br.

A saída é um registro ALIAS, que resolve para o endereço certo sem fixar IP. O
Route 53 tem; o registro.br não.

Alternativa gratuita: usar um subdomínio (`feed.campscast.com.br`), onde CNAME
funciona normalmente. Custa zero, mas a URL vai para os diretórios de podcast e
não muda mais depois. Meio dólar por mês costuma valer a URL mais limpa.

---

## A ordem certa

Delegar o DNS **antes** de pedir o certificado economiza trabalho: com a zona já
no Route 53, o ACM cria os registros de validação sozinho, com um clique.

```
1. Criar a zona no Route 53
2. Delegar no registro.br
3. Esperar propagar
4. Pedir o certificado no ACM (us-east-1)
5. Criar a distribuição no CloudFront
6. Criar o ALIAS no Route 53
7. Verificar
```

---

## 1. Criar a zona no Route 53

**Route 53 → Hosted zones → Create hosted zone**

| Campo | Valor |
|---|---|
| Domain name | `campscast.com.br` |
| Type | Public hosted zone |

Ao criar, a AWS gera quatro servidores de nome no registro NS, parecidos com:

```
ns-123.awsdns-15.com
ns-456.awsdns-56.net
ns-789.awsdns-31.org
ns-1011.awsdns-62.co.uk
```

Copie os quatro. Note que **não terminam com ponto** quando você for colar no
registro.br — se o painel mostrar com ponto final, remova.

> **Atenção:** o registro.br verifica se os servidores respondem pelo domínio
> antes de aceitar a mudança. A zona recém-criada já responde, porque nasce com
> os registros NS e SOA. Não precisa criar mais nada antes.

## 2. Delegar no registro.br

Entre em <https://registro.br>, faça login, e clique no domínio.

Na página do domínio, procure a seção **DNS**. Há duas opções:

- *Usar os servidores DNS do registro.br* — o padrão, com o painel de zona deles
- *Alterar servidores DNS* — o que queremos

Escolha **Alterar servidores DNS** e preencha com os quatro do Route 53. O
formulário costuma pedir dois obrigatórios e aceitar até seis; preencha todos.

Salve. O registro.br faz uma checagem na hora: se disser que os servidores não
respondem pelo domínio, espere alguns minutos e tente de novo — a zona do Route
53 leva um instante para começar a responder.

### Propagação

De quinze minutos a algumas horas. Acompanhe:

```bash
dig +short NS campscast.com.br
```

Quando devolver os quatro `awsdns`, está delegado. Enquanto devolver
`a.auto.dns.br`, ainda não.

> **Cuidado:** se você usava o redirecionamento de e-mail do registro.br, ele
> depende dos servidores DNS deles e **para de funcionar** com a delegação.
> Planeje o e-mail antes de delegar.

## 3. Certificado no ACM

**Certificate Manager → região us-east-1 → Request certificate**

A região importa: o CloudFront só aceita certificado emitido em **us-east-1 (N.
Virginia)**, mesmo que o bucket e o resto estejam em outro lugar. É o erro mais
comum, e a mensagem da AWS não explica.

Peça um certificado **público**, com os nomes:

```
campscast.com.br
*.campscast.com.br
```

Se você também tem o `.com` e quer servi-lo pelo mesmo CloudFront, acrescente
`campscast.com` e `*.campscast.com` — mas aí o DNS dele também precisa apontar
para a distribuição.

Validação por **DNS**. Na tela seguinte, com a zona já no Route 53, aparece o
botão **Create records in Route 53**. Um clique cria tudo.

O status vai de *Pending validation* para *Issued* em alguns minutos.

## 4. Distribuição no CloudFront

**CloudFront → Create distribution**

| Campo | Valor |
|---|---|
| Origin domain | `campscast.s3.us-east-1.amazonaws.com` |
| Origin access | Public |
| Viewer protocol policy | Redirect HTTP to HTTPS |
| Allowed HTTP methods | GET, HEAD |
| Cache policy | CachingOptimized |
| Alternate domain name (CNAME) | `campscast.com.br` e `www.campscast.com.br` |
| Custom SSL certificate | o do passo 3 |
| Default root object | `index.html` |

Um detalhe do campo *Origin domain*: ao clicar, a AWS sugere o bucket numa
lista. **Prefira digitar o endereço completo** `campscast.s3.us-east-1.amazonaws.com`
em vez de escolher da lista — a opção da lista às vezes usa o endpoint de
website do S3, que não faz HTTPS na origem.

A distribuição leva de dez a vinte minutos para sair de *Deploying*. Anote o
*Distribution domain name*.

### Sobre cache

O pipeline já manda os cabeçalhos certos: `max-age=300` no `feed.xml` e um ano
nos MP3. O CloudFront respeita, então o feed continua atualizando em cinco
minutos e os episódios ficam em cache por muito tempo — que é o que se quer.

Se um dia precisar forçar atualização, use *Invalidations* com `/feed.xml`.

## 5. ALIAS no Route 53

**Route 53 → sua zona → Create record**

| Campo | Valor |
|---|---|
| Record name | (vazio, para a raiz) |
| Record type | A |
| Alias | **ativado** |
| Route traffic to | Alias to CloudFront distribution |
| Distribution | a do passo 4 |

Repita para `www`, com Record name `www`. Pode ser A com Alias também.

O ALIAS é gratuito nas consultas e resolve para o CloudFront sem fixar IP — é
por causa dele que a delegação valeu a pena.

## 6. Verificar

```bash
dig +short campscast.com.br
curl -sI https://campscast.com.br/feed.xml     | head -1
curl -sI https://campscast.com.br/cover.jpg    | head -1
curl -sI https://campscast.com.br/audio/AAAA-MM-DD.mp3 | head -1
```

Os três precisam responder `HTTP/2 200`. O `curl` reclama sozinho se o
certificado estiver errado.

Confira também que o cabeçalho de cache sobreviveu:

```bash
curl -sI https://campscast.com.br/feed.xml | grep -i cache-control
```

## 7. Trocar no projeto

Só depois que os três responderem 200:

```bash
python3 scripts/set_base_url.py https://campscast.com.br
python3 scripts/publish.py --date $(date +%F)
```

O script recusa gravar se o domínio não servir os arquivos — é proposital.

---

## Problemas comuns

**O registro.br recusa os servidores DNS.** A zona do Route 53 ainda não está
respondendo. Espere alguns minutos e tente de novo.

**O certificado não sai de *Pending validation*.** Os registros CNAME de
validação não estão na zona certa, ou o DNS ainda não propagou. Confira em
`dig +short _algo.campscast.com.br CNAME`.

**O CloudFront responde `403` com `AccessDenied`.** A origem está apontando
para um endpoint que exige credencial, ou o objeto não está coberto pela bucket
policy. Confira que o arquivo abre direto pela URL do S3.

**`ERR_TOO_MANY_REDIRECTS`.** *Viewer protocol policy* em *Redirect HTTP to
HTTPS* junto com origem em modo website também redirecionando. Use o endpoint
REST do bucket na origem, como recomendado acima.

**O domínio resolve, mas o certificado é de `*.cloudfront.net`.** O
*Alternate domain name* não foi preenchido na distribuição, ou o certificado
escolhido não cobre o nome.

---

## Custo

| Item | Por mês |
|---|---|
| Zona hospedada no Route 53 | US$ 0,50 |
| Consultas DNS | centavos |
| CloudFront, poucos ouvintes | menos de US$ 1 |

Com audiência maior o CloudFront tende a sair **mais barato** que servir do S3
direto, porque a transferência por gigabyte custa menos.

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
6. Editar a distribuição: domínios e certificado   <- o assistente não pede
7. Criar o ALIAS no Route 53
8. Verificar
```

O passo 6 surpreende: o assistente de criação **não** pergunta pelo certificado
nem pelos nomes de domínio, a menos que o domínio esteja registrado dentro da
AWS. Para domínio de fora, isso se configura depois, em *Settings → Edit*.

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

O console mudou e agora é um assistente de seis passos, com escolha de plano
logo na entrada. A ordem, em setembro de 2026:

```
1. Choose a plan
2. Get started
3. Specify origin
4. Enable security
5. Get TLS certificate
6. Review and create
```

### 4.1 Choose a plan

Primeiro escolha entre **Flat-rate plans** e **Pay as you go**.

| Modelo | Como cobra |
|---|---|
| **Flat-rate** | preço fixo por mês, sem cobrança por uso excedente |
| Pay as you go | varia com o tráfego, **sem teto de gasto** |

Dentro de flat-rate há quatro níveis: **Free (US$ 0)**, Pro (US$ 15), Business
(US$ 200) e Premium (US$ 1.000).

**Escolha Free.** Ele já inclui CDN global, WAF, DNS e edge compute — mais do
que um podcast precisa. O que falta nele (access logs, bot analytics) são
recursos de site comercial.

O motivo de preferir flat-rate ao pay as you go não é preço, é **teto**. O
pay as you go não tem limite de gasto: um episódio que viralize, ou um robô
insistente baixando o mesmo MP3 de 8 MB, viram conta no fim do mês. O flat-rate
protege contra isso por definição.

Repare que o plano Free anuncia **DNS** entre os itens incluídos. Vale conferir,
na tela seguinte, se isso cobre a zona hospedada do Route 53 — se cobrir, aqueles
US$ 0,50 por mês somem. Não conte com isso antes de ver escrito.

Confira também os limites de uso inclusos que o assistente mostrar. Para
referência do nosso caso: 22 episódios por mês, cerca de 8 MB cada, e uma
dezena de ouvintes dá menos de 2 GB de transferência mensal — folga larga em
qualquer patamar.

### 4.2 Get started

Só um campo importa:

| Campo | Valor |
|---|---|
| Distribution name | `campscast` |
| Distribution type | Single website or app |

Há também um campo **Route 53 managed domain**. Ele serve para domínio
**registrado dentro do Route 53 como registrador** — e aí o CloudFront emite o
certificado sozinho. Um `.com.br` não pode ser registrado na AWS: ele mora no
registro.br, e o Route 53 é só o DNS. **Deixe em branco e siga.**

É por causa disso que o assistente não mostra passo de certificado: ele só
aparece por esse caminho. O certificado e os nomes de domínio são configurados
**depois de criada a distribuição** — ver 4.6.

### 4.3 Specify origin

| Campo | Valor |
|---|---|
| Origin type | Amazon S3 |
| S3 origin | `campscast.s3.us-east-1.amazonaws.com` |
| Origin path | vazio |

Digite o endereço em vez de usar o *Browse S3*: a escolha pela lista às vezes
usa o endpoint de *website* do bucket, que não faz HTTPS na origem.

> ### Cuidado com "Grant CloudFront access to origin"
>
> Em algum ponto do assistente, o padrão vem como **Yes**, e a tela de revisão
> avisa:
>
> > *Because you granted CloudFront access to your origin, CloudFront can write
> > and update S3 bucket policies that restrict access to your S3 origin to
> > CloudFront.*
>
> Traduzindo: o CloudFront vai **reescrever a bucket policy** para permitir só
> ele. O endereço direto do bucket
> (`campscast.s3.us-east-1.amazonaws.com/feed.xml`) passa a responder **403**.
>
> Isso quebra **quem já assinou pela URL antiga**. Num podcast, é o pior tipo
> de falha: o app do ouvinte simplesmente para de baixar, sem erro visível.
>
> **Enquanto houver assinantes na URL antiga, deixe em Nº** — a bucket policy
> pública que já existe basta para o CloudFront ler a origem.
>
> Depois que todos migrarem para o domínio novo, vale voltar e ativar: restringir
> o acesso ao CloudFront é a configuração mais segura, e aí não quebra ninguém.

### 4.4 Enable security

O assistente mostra o WAF já incluído no plano, com proteções básicas, e a
opção *Use monitor mode*.

**Não altere nada.** As proteções padrão são genéricas e não atrapalham; ativar
regras adicionais, sim. Agregadores de podcast fazem requisições automatizadas
com user-agents incomuns — o padrão que regra de bot tende a barrar. O sintoma
seria o episódio "não aparecer" em alguns apps, difícil de diagnosticar.

A proteção contra DDoS de camada 7 aparece bloqueada, disponível só no plano
Business. Não é necessária.

### 4.5 Depois de criada: domínio e certificado

Aqui está o passo que o assistente não oferece. Com a distribuição criada, abra
**Settings → Edit**:

| Campo | Valor |
|---|---|
| Alternate domain names (CNAMEs) | `campscast.com.br` e `www.campscast.com.br` |
| Custom SSL certificate | o do passo 3 |
| Default root object | `index.html` (opcional) |

Sem o *Alternate domain name*, o CloudFront responde com o certificado próprio
(`*.cloudfront.net`) e o navegador acusa erro no seu domínio.

Se o certificado não aparecer na lista, foi emitido fora de us-east-1.

Confira também, em **Behaviors → Edit**:

| Campo | Valor |
|---|---|
| Viewer protocol policy | Redirect HTTP to HTTPS |
| Allowed HTTP methods | GET, HEAD |
| Cache policy | CachingOptimized |

Cada alteração leva de dez a vinte minutos para sair de *Deploying*. Anote o
*Distribution domain name*, algo como `d111abcdef8.cloudfront.net`.

### Sobre cache

O pipeline já manda os cabeçalhos certos: `max-age=300` no `feed.xml` e um ano
nos MP3. O CloudFront respeita, então o feed continua atualizando em cinco
minutos e os episódios ficam em cache por muito tempo — que é o desejado.

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

**O certificado não aparece na lista do CloudFront.** Ele foi emitido fora de
us-east-1. Não há como mover: peça outro naquela região.

**O assistente não pergunta pelo certificado.** É o comportamento normal para
domínio registrado fora da AWS. Crie a distribuição e configure depois, em
*Settings → Edit*.

**A URL antiga do S3 passou a dar 403 depois de criar a distribuição.** O
CloudFront reescreveu a bucket policy porque *Grant CloudFront access to origin*
estava em *Yes*. Quem assinou pela URL antiga parou de receber episódios, em
silêncio. Para reverter, regrave a policy pública:
`python3 scripts/s3.py --print-policy` e cole em *Permissions → Bucket policy*.

**Alguns apps de podcast não veem os episódios novos, outros veem.** Se você
ativou WAF ou proteção contra bots, é o suspeito. Agregadores fazem requisições
automatizadas com user-agents incomuns — o padrão que regras de bot barram.
Desative e teste de novo.

**A conta do CloudFront veio maior que o esperado.** Provavelmente foi escolhido
*Pay as you go*, que não tem teto de gasto. Um plano flat-rate resolve; a troca
é feita na própria distribuição.

---

## Custo

| Item | Por mês |
|---|---|
| CloudFront, plano Free flat-rate | US$ 0 |
| Zona hospedada no Route 53 | US$ 0,50 — conferir se o plano Free do CloudFront já cobre |
| Consultas DNS | centavos |

Com audiência maior o CloudFront tende a sair **mais barato** que servir do S3
direto, porque a transferência por gigabyte custa menos. E o plano flat-rate
garante que não há surpresa: episódio que viralize não vira conta inesperada.

# Configurar o bucket S3

O feed RSS e os MP3 precisam ser públicos para leitura: qualquer app de podcast
baixa esses arquivos sem autenticação nenhuma. O upload é feito por
`scripts/s3.py` (SigV4 em Python puro) — a AWS CLI não é necessária.

---

## Decisões na tela de criação

| Configuração | Escolha | Por quê |
|---|---|---|
| Bucket type | **General purpose** | Directory buckets são para baixa latência em uma única zona; não serve aqui |
| Bucket name | sem pontos, minúsculo | ponto no nome quebra o certificado TLS no endereço virtual do S3 |
| Region | **us-east-1** | mais barata; latência não importa para download de podcast |
| Object Ownership | **ACLs disabled** | prática atual da AWS: acesso público via *bucket policy*, não por ACL de objeto |
| Block Public Access | **desmarcar só as duas de policy** | ver abaixo |
| Bucket Versioning | **Disable** | episódios são escritos uma vez; o roteiro fica no git |
| Tags | nenhuma | só ajudam a separar custo entre projetos |
| Default encryption | **SSE-S3** | grátis, ligada por padrão, sem motivo para mexer |
| Object Lock | Disable | impediria corrigir um episódio publicado por engano |

### Block Public Access — o item que precisa mudar

O padrão bloqueia tudo, e com ele o feed não funciona: os apps recebem 403.

Desmarque **Block all public access** e, nas quatro caixas que aparecem, deixe
assim:

| Caixa | Estado | Por quê |
|---|---|---|
| Block public access via *new* ACLs | **marcada** | ACLs estão desabilitadas; manter bloqueado não custa nada |
| Block public access via *any* ACLs | **marcada** | idem |
| Block public access via new *bucket policies* | **desmarcada** | é a policy que libera a leitura |
| Block public and cross-account access via any *bucket policies* | **desmarcada** | idem |

Manter as duas de ACL bloqueadas é defesa em profundidade: mesmo que alguém
reative ACLs por engano no futuro, nenhum objeto vira público por esse caminho.
Só a policy — que é explícita, versionada e revisável — concede acesso.

A AWS vai pedir para você digitar `confirm`. Isso é esperado.

### Sobre o nome do bucket

Vale pensar duas vezes antes de seguir: **o nome entra na URL de cada episódio,
e URL de episódio de podcast não pode mudar.** Os apps guardam o endereço do
arquivo; trocar depois quebra o download para quem já assinou, e o Spotify
rejeita feed com enclosure instável.

Um nome com sufixo de versão (`-v1`, `-novo`, `-teste`) convida a criar um
sucessor um dia — e esse dia não pode chegar. Se `campscast` estiver livre no
namespace global da AWS, ele envelhece melhor.

A alternativa que resolve de vez: colocar um CloudFront com domínio próprio na
frente (`audio.seudominio.com.br`). Aí o nome do bucket some da URL e pode ser
trocado à vontade. É item de Fase 2 — mas se você já pretende fazer isso, o nome
do bucket deixa de importar.

## Depois de criar: a bucket policy

Sem ela, os arquivos continuam privados mesmo com o Block Public Access liberado.

Não escreva o JSON à mão. Gere já preenchido com o bucket do seu `.env`:

```bash
python3 scripts/s3.py --print-policy
```

Cole a saída em **Permissions → Bucket policy → Edit → Save changes**.

A permissão é só para `feed.xml`, `cover.jpg` e `audio/*`, não para o bucket
inteiro. Se um dia você guardar rascunho ou nota lá dentro, ele não fica exposto
por acidente.

### `Policy has invalid resource`

Esse erro quase sempre significa uma coisa: **os ARNs do JSON apontam para um
bucket diferente daquele em que a policy está sendo salva.** O S3 exige que
sejam o mesmo.

Causas, em ordem de frequência:

- o placeholder `SEU-BUCKET` ficou no texto;
- erro de digitação no nome do bucket;
- a policy foi copiada de outro bucket.

`--print-policy` elimina as três: o nome sai do seu `.env`.

Se persistir, confira que o ARN **não** usa `s3://` — o formato é
`arn:aws:s3:::nome-do-bucket/chave`, com três dois-pontos e sem esquema — e que
a linha dos objetos termina em `/*`.

## CORS (opcional, mas barato)

Players web que leem o feed por JavaScript precisam disso. Apps nativos não.
Em **Permissions → Cross-origin resource sharing (CORS)**:

```json
[
  {
    "AllowedHeaders": [],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": ["Content-Length", "Content-Range", "Accept-Ranges"],
    "MaxAgeSeconds": 3000
  }
]
```

Só leitura, e os arquivos já são públicos — não abre nada que a policy acima já
não tenha aberto. Configurar agora evita depurar isso mais tarde.

## Credenciais de upload

O assistente **Create user** tem três etapas e **nenhuma delas aceita policy
inline** — na etapa 2 só dá para escolher entre grupo, copiar de outro usuário,
ou anexar policies que já existem. A policy é criada depois que o usuário existe.

### Etapa 1 — Specify user details

- **User name:** `campscast`
- **Provide user access to the AWS Management Console:** deixe **desmarcado**.
  Este usuário serve só para o pipeline; ele não precisa de senha nem de login,
  e não dar console reduz o estrago de um vazamento.

### Etapa 2 — Set permissions

Escolha **Attach policies directly** e **não selecione nenhuma**. Siga em frente
com o usuário sem permissão alguma. Parece errado, mas é o caminho mais curto: a
alternativa é abrir o criador de policy em outra aba, criar uma *customer managed
policy*, voltar, atualizar a lista e procurá-la.

### Etapa 3 — Review and create

Confirme e crie. O usuário nasce sem poder fazer nada.

### Depois de criado — a policy inline

Abra o usuário recém-criado e vá em:

**Permissions** → botão **Add permissions** → **Create inline policy** → aba
**JSON**

Apague o conteúdo do editor e cole a saída de:

```bash
python3 scripts/s3.py --print-iam-policy
```

Clique em **Next**, dê o nome `campscast-upload` e **Create policy**.

#### Inline ou managed?

| | Inline | Customer managed |
|---|---|---|
| Onde vive | dentro do usuário | na lista global de policies |
| Ao apagar o usuário | some junto | fica órfã |
| Reutilizável | não | sim |
| Passos no console | menos | mais |

Para um usuário de propósito único como este, **inline é melhor**: nada fica para
trás quando o usuário for removido, e não polui a lista de policies da conta.
Managed compensa quando várias identidades precisam da mesma permissão.

### Gerar as chaves

No usuário: **Security credentials** → **Create access key**.

A AWS pergunta o caso de uso e mostra alternativas mais seguras (IAM Identity
Center, roles). Elas são de fato melhores para workload dentro da AWS — aqui o
código roda num Mac pessoal, fora da AWS, então:

- escolha **Application running outside AWS**;
- marque o aviso de confirmação;
- descrição sugerida: `CampsCast — upload diario do episodio`.

**Copie as duas chaves nesta tela.** A *secret* não é exibida de novo; perdendo,
o jeito é gerar outro par e apagar o antigo.

### Colar no `.env`

```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

O `.env` está no `.gitignore` e tem permissão `600`. Nunca commite.

Confira que entrou certo:

```bash
python3 -c "
import sys; sys.path.insert(0,'scripts')
from s3 import load_credentials
c = load_credentials()
print('access key:', c.access_key[:8] + '...', '| secret:', len(c.secret_key), 'caracteres')
"
```

### Por que só `PutObject`

`scripts/s3.py` só faz `PUT`. Não precisa de `ListBucket`, `GetObject` nem
`DeleteObject`. Com essa policy, quem tiver a chave consegue sobrescrever um
episódio — e nada além disso. Não consegue apagar o acervo, listar o bucket, nem
ler qualquer coisa que você venha a guardar lá em modo privado.

Se um dia o pipeline precisar apagar episódios antigos, aí sim vale acrescentar
`s3:DeleteObject` — e não antes.

## Testar com um arquivo descartável

Antes de subir 8 MB, prove que a assinatura funciona:

```bash
echo teste > /tmp/campscast-teste.txt
python3 scripts/s3.py --bucket SEU-BUCKET --key audio/teste.mp3 \
  --file /tmp/campscast-teste.txt --content-type text/plain
```

A chave é `audio/teste.mp3` de propósito: é o prefixo que a bucket policy
libera, então o mesmo arquivo serve para testar upload **e** leitura pública.

Depois confirme que está público de verdade — sem credencial nenhuma:

```bash
curl -sI https://SEU-BUCKET.s3.us-east-1.amazonaws.com/audio/teste.mp3 | head -1
```

Precisa responder `HTTP/1.1 200 OK`.

**Atenção a uma armadilha:** um `403` só significa alguma coisa se o objeto
existir. Para arquivo inexistente o S3 devolve `403`, e não `404`, mesmo com a
policy correta — como a chave anônima não tem `s3:ListBucket`, ele se recusa a
revelar se o objeto existe. Ou seja: testar a policy contra uma URL qualquer não
prova nada. Suba o arquivo primeiro, depois baixe.

Se o `403` vier num objeto que você acabou de subir, aí sim é a bucket policy
ausente, com ARN errado, ou o Block Public Access ainda barrando policies.

Note que `teste.txt` **não** está coberto pela policy acima — então um 403 aqui
é esperado e correto. Para testar o caminho que os ouvintes usam, suba como
`--key audio/teste.mp3` e baixe essa URL.

## Custo

Um episódio de 8 minutos a 128 kbps pesa cerca de 8 MB.

| Item | Cálculo | Por mês |
|---|---|---|
| Armazenamento | 22 ep × 8 MB = 176 MB, a US$ 0,023/GB | ~US$ 0,004 |
| Transferência | 10 ouvintes × 22 ep × 8 MB = 1,8 GB, a US$ 0,09/GB | ~US$ 0,16 |
| Requisições | poucos milhares | centavos |

Menos de um dólar por mês com dezenas de ouvintes. O gargalo de custo do projeto
é a ElevenLabs, não a AWS. Com centenas de ouvintes a transferência começa a
pesar, e aí o CloudFront passa a compensar — ele é mais barato por GB.

## Problemas comuns

**`403` no upload** — a chave não tem `s3:PutObject` nesse bucket, ou o ARN da
policy está com o nome errado.

**`403` ao baixar pelo navegador** — bucket policy ausente, ou Block Public
Access ainda bloqueando policies.

**`301` ou `PermanentRedirect`** — o bucket está em outra região. Ajuste
`AWS_REGION` no `.env`.

**Erro de certificado TLS** — nome de bucket com ponto. Não tem conserto de
configuração: precisa criar outro bucket.

**O app de podcast não atualiza** — o `feed.xml` sobe com
`Cache-Control: max-age=300`, então leva até cinco minutos. Os MP3 sobem com
cache de um ano, porque nunca mudam.

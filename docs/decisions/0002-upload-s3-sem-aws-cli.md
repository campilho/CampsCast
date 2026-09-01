# ADR 0002 — Upload para o S3 sem AWS CLI

- **Status:** aceito
- **Data:** 2026-08-24

## Contexto

A etapa de publicação precisa subir dois arquivos por dia: o MP3 do episódio e
o `feed.xml`. A implementação inicial usava `aws s3 cp`.

Ao tentar instalar a AWS CLI, descobrimos que o Homebrew não estava instalado na
máquina. Isso transformou "um comando" em uma cadeia: Xcode Command Line Tools →
Homebrew (com `sudo` e ajuste de `PATH`) → AWS CLI → `aws configure`. Quatro
passos, dois deles pedindo senha, antes de subir um arquivo de 7 MB.

O projeto já tinha tomado a decisão oposta em outro ponto: em vez de exigir
`ffprobe` para ler a duração dos MP3, `scripts/publish.py` soma os frames MPEG
em Python puro. A promessa do README é "nenhuma dependência".

## Opções

1. **Instalar Homebrew e AWS CLI.** Ferramenta oficial, battle-tested. Custo:
   dois pré-requisitos permanentes no guia de setup, ambos pedindo senha.
2. **Instalador `.pkg` oficial da Amazon.** Evita o Homebrew, mantém a CLI.
3. **Assinar SigV4 em Python puro.** Nenhuma instalação. Custo: ~180 linhas de
   código de assinatura para manter.

## Decisão

**Opção 3.** O upload usa `scripts/s3.py`, que implementa AWS Signature Version
4 com `hmac` e `hashlib` da biblioteca padrão.

O que pesou:

- Um `PUT` assinado é um problema fechado e determinístico. Não é o mesmo que
  reimplementar a AWS CLI — é usar uma fatia mínima e bem especificada dela.
- Remove permanentemente dois pré-requisitos do guia de setup. Quem clonar o
  repositório em outro Mac precisa de Python e do Claude CLI, e nada mais.
- Mantém a coerência com a decisão do `ffprobe`.
- As credenciais continuam sendo as mesmas da AWS; não há invenção de mecanismo.

## Validação

A cadeia de derivação da chave de assinatura é conferida contra o **vetor de
teste publicado pela AWS** na documentação do SigV4:

```
secret    wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY
data      20150830   região us-east-1   serviço iam
esperado  c4afb1cc5771d871763a393e44b703571b55cc28424d1a5e86da6ed3c154a4b9
```

O smoke test roda essa verificação, mais o formato da requisição canônica, o
percent-encoding e o determinismo da assinatura.

### Um bug que o teste pegou

A primeira versão do `uri_encode` usava `str.isalnum()` para decidir o que não
escapar. Em Python, `isalnum()` é Unicode-aware: `"ç".isalnum()` é `True`. Uma
chave com acento sairia sem encoding, a assinatura não bateria com a calculada
pelo S3, e o resultado seria um **403 sem explicação nenhuma** — o tipo de falha
que custa uma tarde. Corrigido com um conjunto explícito de caracteres ASCII.

Chaves acentuadas não aparecem no fluxo atual (`audio/AAAA-MM-DD.mp3` é ASCII),
mas apareceriam no dia em que alguém pusesse acento no `S3_PREFIX`.

## Consequências

- `.env` passa a aceitar `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY`
  diretamente, além de continuar lendo `~/.aws/credentials` via `AWS_PROFILE`.
- Buckets com ponto no nome são recusados explicitamente: eles quebram a
  validação de certificado no endereço virtual do S3.
- O áudio sobe antes do feed, para nunca existir um feed apontando para um MP3
  inexistente.
- **Não validado contra um bucket real ainda.** O vetor da AWS valida a
  assinatura, mas o primeiro `PUT` de verdade ainda é o teste que falta.
  `python3 scripts/s3.py --bucket ... --key teste.txt --file ...` faz isso com
  um arquivo descartável.

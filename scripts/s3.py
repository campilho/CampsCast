#!/usr/bin/env python3
"""
CampsCast — upload para o S3 sem AWS CLI.

Implementa a assinatura AWS Signature Version 4 com a biblioteca padrão. Segue
a mesma lógica que já usamos para ler duração de MP3 sem ffprobe: um pedaço
bem delimitado de algoritmo vale mais que um pré-requisito de instalação.

Credenciais, na ordem de precedência:
  1. AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN no ambiente
  2. ~/.aws/credentials, no perfil de AWS_PROFILE (default: "default")

Uso como biblioteca:
    from s3 import put_object, load_credentials
    put_object("meu-bucket", "feed.xml", data, "application/rss+xml")

Uso na linha de comando (útil para testar o bucket):
    python3 scripts/s3.py --bucket meu-bucket --key teste.txt --file caminho.txt
"""
from __future__ import annotations

import argparse
import configparser
import datetime as _dt
import hashlib
import hmac
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent

ALGORITHM = "AWS4-HMAC-SHA256"
SERVICE = "s3"
UNSIGNED_CHARS = "-_.~"          # RFC 3986: não são percent-encoded
ASCII_ALNUM = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


class S3Error(RuntimeError):
    pass


# ------------------------------------------------------------- credenciais
class Credentials:
    def __init__(self, access_key: str, secret_key: str, token: str | None = None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.token = token or None


def load_env() -> None:
    """Carrega o .env sem sobrescrever o que já está no ambiente.

    Necessário porque este módulo também roda como script: quando chamado pelo
    publish.py o .env já veio carregado, mas na linha de comando não.
    """
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        if k and not os.environ.get(k):
            os.environ[k] = v.strip().strip('"').strip("'")


def load_credentials(profile: str | None = None) -> Credentials:
    load_env()
    access = os.environ.get("AWS_ACCESS_KEY_ID", "").strip()
    secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "").strip()
    if access and secret:
        return Credentials(access, secret, os.environ.get("AWS_SESSION_TOKEN"))

    profile = profile or os.environ.get("AWS_PROFILE", "default")
    path = pathlib.Path.home() / ".aws" / "credentials"
    if path.exists():
        parser = configparser.ConfigParser()
        parser.read(path)
        if parser.has_section(profile):
            sec = parser[profile]
            access = sec.get("aws_access_key_id", "").strip()
            secret = sec.get("aws_secret_access_key", "").strip()
            if access and secret:
                return Credentials(access, secret, sec.get("aws_session_token"))

    raise S3Error(
        "Credenciais da AWS não encontradas. Defina AWS_ACCESS_KEY_ID e "
        "AWS_SECRET_ACCESS_KEY no .env, ou configure ~/.aws/credentials."
    )


# ---------------------------------------------------------------- assinatura
def _sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def signing_key(secret: str, datestamp: str, region: str,
                service: str = SERVICE) -> bytes:
    """Cadeia de derivação do SigV4: data -> região -> serviço -> requisição."""
    k = _sign(f"AWS4{secret}".encode("utf-8"), datestamp)
    k = _sign(k, region)
    k = _sign(k, service)
    return _sign(k, "aws4_request")


def uri_encode(value: str, encode_slash: bool = True) -> str:
    """Percent-encoding do jeito que o SigV4 exige (maiúsculas, ~ preservado).

    Atenção ao `ASCII_ALNUM`: `str.isalnum()` não serve aqui porque é
    Unicode-aware — para o Python, "ç" e "ã" são alfanuméricos, e passariam sem
    escapar. A assinatura sairia diferente da que o S3 calcula, resultando num
    403 sem explicação. Só ASCII fica sem encoding.
    """
    out = []
    for ch in value:
        if ch in ASCII_ALNUM or ch in UNSIGNED_CHARS:
            out.append(ch)
        elif ch == "/":
            out.append("%2F" if encode_slash else "/")
        else:
            out.extend(f"%{b:02X}" for b in ch.encode("utf-8"))
    return "".join(out)


def canonical_request(method: str, uri: str, query: str,
                      headers: dict[str, str], payload_hash: str) -> tuple[str, str]:
    """Devolve (canonical_request, signed_headers)."""
    lowered = {k.lower().strip(): " ".join(str(v).split())
               for k, v in headers.items()}
    names = sorted(lowered)
    canonical_headers = "".join(f"{n}:{lowered[n]}\n" for n in names)
    signed_headers = ";".join(names)
    creq = "\n".join([method, uri, query, canonical_headers,
                      signed_headers, payload_hash])
    return creq, signed_headers


def authorization_header(creds: Credentials, region: str, amzdate: str,
                         datestamp: str, creq: str, signed_headers: str) -> str:
    scope = f"{datestamp}/{region}/{SERVICE}/aws4_request"
    string_to_sign = "\n".join([
        ALGORITHM, amzdate, scope,
        hashlib.sha256(creq.encode("utf-8")).hexdigest(),
    ])
    signature = hmac.new(signing_key(creds.secret_key, datestamp, region),
                         string_to_sign.encode("utf-8"),
                         hashlib.sha256).hexdigest()
    return (f"{ALGORITHM} Credential={creds.access_key}/{scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}")


# -------------------------------------------------------------------- upload
def put_object(bucket: str, key: str, data: bytes, content_type: str,
               region: str | None = None, cache_control: str | None = None,
               creds: Credentials | None = None, timeout: int = 300) -> str:
    """Sobe um objeto e devolve a URL pública. Levanta S3Error em falha."""
    region = region or os.environ.get("AWS_REGION", "us-east-1")
    creds = creds or load_credentials()

    if "." in bucket:
        # Bucket com ponto quebra a validação do certificado no host virtual.
        raise S3Error(
            f"O bucket '{bucket}' tem ponto no nome, o que impede HTTPS no "
            "endereço virtual do S3. Use um nome sem pontos."
        )

    host = f"{bucket}.s3.{region}.amazonaws.com"
    canonical_uri = "/" + uri_encode(key.lstrip("/"), encode_slash=False)
    payload_hash = hashlib.sha256(data).hexdigest()

    now = _dt.datetime.now(_dt.timezone.utc)
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")

    headers = {
        "host": host,
        "content-type": content_type,
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": amzdate,
    }
    if cache_control:
        headers["cache-control"] = cache_control
    if creds.token:
        headers["x-amz-security-token"] = creds.token

    creq, signed_headers = canonical_request("PUT", canonical_uri, "",
                                             headers, payload_hash)
    headers["authorization"] = authorization_header(
        creds, region, amzdate, datestamp, creq, signed_headers)

    url = f"https://{host}{canonical_uri}"
    send = {k: v for k, v in headers.items() if k != "host"}
    req = urllib.request.Request(url, data=data, headers=send, method="PUT")

    try:
        with urllib.request.urlopen(req, timeout=timeout):
            return url
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise S3Error(_explain(e.code, body, bucket, region)) from None
    except Exception as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            raise S3Error(
                "Falha de certificado TLS. Rode uma vez:\n"
                '  "/Applications/Python 3.13/Install Certificates.command"'
            ) from None
        raise S3Error(f"Falha de rede ao subir {key}: {e}") from None


def _explain(code: int, body: str, bucket: str, region: str) -> str:
    hints = {
        403: (f"Acesso negado ao bucket '{bucket}'. Confira se as credenciais "
              "têm permissão de s3:PutObject nesse bucket."),
        404: (f"Bucket '{bucket}' não encontrado na região {region}. "
              "Confira o nome e a região."),
        301: (f"Bucket '{bucket}' fica em outra região. Ajuste AWS_REGION."),
        400: "Requisição rejeitada — normalmente é assinatura ou região erradas.",
    }
    hint = hints.get(code, "")
    snippet = body.strip()[:300]
    return f"HTTP {code} do S3. {hint}\n  Resposta: {snippet}"


# ---------------------------------------------------------------------- main
# ------------------------------------------------------------------ policies
def bucket_policy(bucket: str) -> dict:
    """Policy de leitura pública, escopada ao que o feed realmente serve.

    O S3 exige que os ARNs apontem para o MESMO bucket ao qual a policy está
    sendo anexada — deixar um placeholder no JSON produz o erro pouco
    esclarecedor "Policy has invalid resource".
    """
    return {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "LeituraPublicaDoPodcast",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": [
                f"arn:aws:s3:::{bucket}/feed.xml",
                f"arn:aws:s3:::{bucket}/cover.jpg",
                f"arn:aws:s3:::{bucket}/audio/*",
                f"arn:aws:s3:::{bucket}/referencias/*",
            ],
        }],
    }


def iam_policy(bucket: str) -> dict:
    """Permissão mínima do usuário de upload: só PUT, só neste bucket."""
    return {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "UploadDoCampsCast",
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": f"arn:aws:s3:::{bucket}/*",
        }],
    }


def resolve_bucket(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    root_env = ROOT / ".env"
    if root_env.exists():
        for line in root_env.read_text(encoding="utf-8").splitlines():
            if line.startswith("S3_BUCKET="):
                return line.split("=", 1)[1].strip() or None
    return os.environ.get("S3_BUCKET", "").strip() or None


def main() -> int:
    ap = argparse.ArgumentParser(description="Sobe um arquivo para o S3.")
    ap.add_argument("--bucket")
    ap.add_argument("--key")
    ap.add_argument("--file")
    ap.add_argument("--print-policy", action="store_true",
                    help="imprime a bucket policy já preenchida com o bucket real")
    ap.add_argument("--print-iam-policy", action="store_true",
                    help="imprime a policy mínima do usuário de upload")
    ap.add_argument("--content-type", default="application/octet-stream")
    ap.add_argument("--cache-control")
    ap.add_argument("--region")
    args = ap.parse_args()

    if args.print_policy or args.print_iam_policy:
        bucket = resolve_bucket(args.bucket)
        if not bucket:
            print("ERRO: bucket não informado. Use --bucket ou preencha "
                  "S3_BUCKET no .env.", file=sys.stderr)
            return 1
        gerar = bucket_policy if args.print_policy else iam_policy
        print(json.dumps(gerar(bucket), indent=2))
        return 0

    if not (args.bucket and args.key and args.file):
        print("ERRO: --bucket, --key e --file são obrigatórios para o upload.",
              file=sys.stderr)
        return 2

    path = pathlib.Path(args.file)
    if not path.exists():
        print(f"ERRO: arquivo não encontrado: {path}", file=sys.stderr)
        return 1
    try:
        url = put_object(args.bucket, args.key, path.read_bytes(),
                         args.content_type, args.region, args.cache_control)
    except S3Error as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    print(f"OK {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

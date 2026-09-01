# Configurar a ElevenLabs (etapa de narração)

Roteiro completo para quem está montando o CampsCast do zero. Ao final você terá
uma chave de API funcionando e uma voz validada, gastando 26 caracteres de cota.

---

## 1. Criar a conta

<https://elevenlabs.io> → Sign up. A conta Free serve para ouvir vozes no site,
mas **não** serve para gerar os episódios — veja o passo 3.

## 2. Gerar a chave de API

<https://elevenlabs.io/app/settings/api-keys> → **Create API Key**.

A tela pede que você escolha quais serviços a chave pode acessar. Escolhas:

| Escopo | Precisa? | Para quê |
|---|---|---|
| **Text to Speech** | **Obrigatório** | é o que gera o áudio |
| **Voices** (read) | Recomendado | `--check` valida a voz; `--list-voices` funciona |
| **User** (read) | Recomendado | `--check` mostra a cota restante |
| Todo o resto | Não | Dubbing, Sound Effects, Studio etc. não são usados |

Com apenas *Text to Speech* o pipeline funciona, mas o `--check` fica cego para
cota e nome da voz. Os dois escopos de leitura são baratos em risco e tornam o
diagnóstico muito melhor — recomendo habilitá-los.

**Expiração:** "Never expire" é o mais prático para um pipeline que roda sozinho
todo dia. Uma chave com validade vai quebrar a execução das 5h50 num dia
qualquer, sem ninguém por perto para perceber.

**Limite de crédito por chave:** dá para restringir quanto essa chave pode gastar.
Útil se você quiser um teto de segurança — o episódio gasta cerca de 6.500
caracteres, então um limite mensal de 200 mil dá folga.

Copie a chave **na hora**: ela não é exibida de novo.

## 3. Escolher o plano — atenção aqui

**A conta Free não usa vozes da Voice Library pela API.** A tentativa devolve:

```
HTTP 402: Free users cannot use library voices via the API.
```

Você consegue ouvir a voz no site, escolher, copiar o id — e só descobre o
bloqueio quando o pipeline roda. Duas saídas:

1. **Assinar um plano pago.** Libera as vozes de catálogo. Atenção ao tamanho da
   cota: um episódio de ~6.600 caracteres consome de 3.300 a 6.600 créditos,
   então o Starter (30 mil/mês) rende no máximo nove episódios — não sustenta
   uma publicação diária. Para dias úteis o mínimo é o Creator. Ver o
   [ADR 0001](decisions/0001-provedor-de-tts.md#escolha-de-plano-2026-08-23).
2. **Usar uma voz "premade"** — as vozes padrão da ElevenLabs, acessíveis no
   plano Free. Habilite o escopo *Voices* e liste as disponíveis:

   ```bash
   python3 scripts/tts.py --list-voices
   ```

   As marcadas como `premade` funcionam no Free. O modelo Flash v2.5 é
   multilíngue, então uma voz premade consegue falar português — com sotaque
   menos natural que uma voz PT-BR de catálogo.

Vale lembrar que a cota Free (10 mil créditos/mês) não sustenta um episódio
diário de qualquer forma: um episódio sozinho consome mais da metade dela.

## 4. Escolher a voz

<https://elevenlabs.io/app/voice-library> → filtre por **Portuguese (Brazil)**.

Ouça as amostras. O que importa para este formato:

- Dicção clara em números e siglas — o roteiro é cheio dos dois.
- Nomes próprios em inglês (Anthropic, NVIDIA, DeepMind) sem soar estranho.
- Ritmo que aguente 8 minutos sem cansar.

Copie o **Voice ID** e cole em `config/tts.json`:

```json
{
  "voice_id": "COLE_AQUI",
  "model_id": "eleven_flash_v2_5"
}
```

Nenhum script tem id fixo — trocar de voz é só editar esse arquivo.

## 5. Preencher o `.env`

```bash
cp .env.example .env
chmod 600 .env
```

Preencha `ELEVENLABS_API_KEY=`. O `.env` está no `.gitignore`; nunca commite.

## 6. Validar antes de gastar

```bash
python3 scripts/tts.py --check
```

Saída esperada:

```
Voz     : m151rjrbWXbBqyq56tly
Modelo  : eleven_flash_v2_5
Conta   : plano starter
Cota    : 1234 de 30000 usados — restam 28766
Nome    : Nome Da Voz
          language=pt, age=middle_aged
Teste   : sintetizando 26 caracteres…
OK      : 41216 bytes de MP3 recebidos. Chave, voz e modelo válidos.
```

O teste sintetiza uma frase curta de propósito: os endpoints de leitura não
provam que a síntese funciona, e 26 caracteres é um preço justo pela certeza.

## 7. Gerar o primeiro áudio

```bash
scripts/run_episode.sh --date AAAA-MM-DD --only tts
```

Rode `--check` **antes e depois** e compare a cota: a diferença é o custo real
por episódio. Multiplicado por ~22 dias úteis, é o número que decide o plano.
Anote no [ADR 0001](decisions/0001-provedor-de-tts.md).

---

## Problemas comuns

**`CERTIFICATE_VERIFY_FAILED`** — o Python instalado do python.org no macOS não
usa o repositório de certificados do sistema. Rode uma vez, ajustando a versão:

```bash
"/Applications/Python 3.13/Install Certificates.command"
```

Ele instala o `certifi` e cria o link do `cert.pem`. É o script oficial que vem
junto com o Python.

**`401` ou `403`** — a chave não tem o escopo *Text to Speech*, ou foi revogada.

**`402 paid_plan_required`** — voz de catálogo em conta Free. Veja o passo 3.

**`404` na voz** — id errado, ou a voz saiu da biblioteca. Confira em
`--list-voices`.

**Áudio sai arrastado ou acelerado** — ajuste `voice_settings` em
`config/tts.json`. `stability` mais alto deixa mais uniforme e menos expressivo;
`style` mais alto aumenta a variação e o risco de leitura estranha.

# Montar o CampsCast num Mac do zero

Do sistema recém-instalado até o primeiro episódio. Escrito para quem nunca
mexeu no projeto. Testado em macOS 15 (Darwin 25.x), Apple Silicon.

Tempo: cerca de 40 minutos, quase tudo esperando download.

---

## Visão geral do que será instalado

| Ferramenta | Para quê | Obrigatória? |
|---|---|---|
| Homebrew | gerenciador de pacotes; instala o resto | sim |
| Python 3.11+ | todos os scripts do projeto | sim |
| Node.js | só para instalar o Claude Code CLI | sim |
| Claude Code CLI | etapa 1: pesquisa e roteiro | sim |
| Conta ElevenLabs | etapa 2: narração | sim |
| Conta AWS | hospedar o feed e os MP3 | só para publicar |

A **AWS CLI não é necessária**: o upload é feito por `scripts/s3.py`, que assina
as requisições em SigV4 com a biblioteca padrão do Python. Bastam um par de
chaves de acesso.

O projeto **não tem dependências Python**. Nenhum `pip install`, nenhum
`requirements.txt`, nenhum virtualenv. Tudo é biblioteca padrão.

---

## 1. Ferramentas de linha de comando da Apple

O Homebrew precisa delas. Instale primeiro:

```bash
xcode-select --install
```

Abre uma janela do sistema. Aceite e espere. Se disser que já estão instaladas,
siga em frente.

## 2. Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Pede a senha do seu usuário (é `sudo`). Ao terminar, ele imprime duas ou três
linhas mandando adicionar o Homebrew ao `PATH` — **execute-as**. Em Apple
Silicon costuma ser:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Em Macs Intel o caminho é `/usr/local/bin/brew`. Confira:

```bash
brew --version
```

Se der "command not found", o passo do `PATH` não foi aplicado — abra um
terminal novo e repita o `eval`.

## 3. Python

```bash
brew install python@3.13
python3 --version
```

**Se você usa o Python baixado do python.org** (em vez do Homebrew), ele não
enxerga os certificados do sistema e toda chamada HTTPS falha com
`CERTIFICATE_VERIFY_FAILED`. Rode uma vez, ajustando a versão:

```bash
"/Applications/Python 3.13/Install Certificates.command"
```

Teste:

```bash
python3 -c "import urllib.request; urllib.request.urlopen('https://api.elevenlabs.io'); print('HTTPS ok')"
```

## 4. Node.js e o Claude Code CLI

```bash
brew install node
npm install -g @anthropic-ai/claude-code
claude --version
```

Se o `npm install -g` reclamar de permissão, o prefixo do npm está em
`/usr/local`. Duas saídas — a segunda é melhor:

```bash
# rápida
sudo npm install -g @anthropic-ai/claude-code
```

```bash
# sem sudo, e resolve de vez
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zshrc
exec zsh
npm install -g @anthropic-ai/claude-code
```

### Autenticar o CLI

**Instalar não autentica.** E o login do app de desktop do Claude **não vale**
para o CLI: são armazenamentos de credenciais separados. Rode uma vez, num
terminal interativo:

```bash
claude
```

Dentro dele: `/login`, escolha a assinatura, responda as perguntas de tema, e
saia com `/exit`. Sem esse passo o pipeline falha com
`Not logged in · Please run /login`.

Anote onde o binário ficou — o launchd vai precisar do caminho absoluto:

```bash
which claude
```

## 5. Credenciais da AWS (só se for publicar)

Nada a instalar. No console da AWS, em **IAM → Users → Security credentials →
Create access key**, gere um par de chaves para um usuário com permissão de
`s3:PutObject` no bucket do podcast.

Coloque no `.env`:

```
S3_BUCKET=nome-do-seu-bucket
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

Se você já usa a AWS CLI para outras coisas e tem `~/.aws/credentials`, deixe as
duas linhas de chave em branco: o `scripts/s3.py` lê o perfil de `AWS_PROFILE`.

O nome do bucket **não pode conter ponto** — isso quebra a validação do
certificado no endereço virtual do S3. O script recusa antes de tentar.

Para testar o acesso sem publicar nada de verdade:

```bash
echo teste > /tmp/campscast-teste.txt
python3 scripts/s3.py --bucket SEU-BUCKET --key teste.txt \
  --file /tmp/campscast-teste.txt --content-type text/plain
```

## 6. O repositório

```bash
git clone <url-do-repo> CampsCast
cd CampsCast
cp .env.example .env
chmod 600 .env
```

## 7. ElevenLabs

Roteiro dedicado, com escopos da chave, escolha de plano e de voz:
**[docs/setup-elevenlabs.md](setup-elevenlabs.md)**.

Resumo: conta paga (o plano Free não usa vozes de catálogo pela API), chave com
os escopos *Text to Speech*, *Voices* e *User*, `voice_id` em `config/tts.json`
e a chave em `.env`.

## 8. Validar tudo

```bash
bash tests/smoke_test.sh        # offline, não chama nenhuma API
python3 scripts/tts.py --check  # valida chave, voz e cota
scripts/run_episode.sh --dry-run
```

O smoke test não gasta um centavo nem um crédito. Rode-o sempre que mexer no
projeto.

## 9. Medir o ritmo da voz

Cada voz fala numa velocidade diferente, e é isso que define quantas palavras
cabem nos 5 a 10 minutos do formato. Medidos até agora:

| Voz | Ritmo | 1.152 palavras rendem |
|---|---|---|
| Carla (feminina, pt-BR) | 125 ppm | 9min11s |
| Paulo (masculina, pt-BR) | 163 ppm | 7min03s |

Ao trocar de voz, gere um episódio, meça e atualize `words_per_minute` em
`config/tts.json`:

```bash
python3 -c "
import sys; sys.path.insert(0,'scripts')
from publish import mp3_duration_seconds
import pathlib
p = pathlib.Path('audio/AAAA-MM-DD.mp3')
palavras = 1152   # ajuste
print(round(palavras / (mp3_duration_seconds(p)/60)), 'palavras por minuto')
"
```

Depois confira a faixa resultante:

```bash
python3 scripts/tts.py --budget
```

## 10. Primeiro episódio

```bash
scripts/run_episode.sh --only research   # ~7 min, sem custo de TTS
# leia o roteiro em episodes/
scripts/run_episode.sh --only tts        # ~20 s
python3 scripts/publish.py --no-upload   # gera feed/feed.xml localmente
```

## 11. Agendar (launchd)

### Onde o projeto NÃO pode estar

O macOS bloqueia agentes do launchd em `~/Documents`, `~/Desktop` e
`~/Downloads` — é o TCC, o mesmo mecanismo que pede permissão quando um app
tenta ler suas pastas. O sintoma é enganoso:

```
/bin/bash: .../scripts/run_episode.sh: Operation not permitted
```

Não fala em permissão de disco, e o mesmo comando funciona perfeitamente quando
você o roda no Terminal — porque o Terminal já tem a permissão concedida. Só a
execução automática falha, e só às 5h50, sem ninguém por perto.

**Deixe o projeto fora dessas três pastas.** `~/CampsCast` serve. Há um segundo
motivo: se `~/Documents` estiver sincronizada com o iCloud, um MP3 de 8 MB
escrito toda madrugada sobe para a nuvem, e sincronização mexendo em arquivo que
o agente está escrevendo é problema difícil de diagnosticar.

A alternativa — dar Full Disk Access ao `/bin/bash` em Ajustes do Sistema —
funciona, mas concede a permissão a **qualquer** script bash da máquina. Mover o
projeto é mais barato e mais seguro.

### Instalar

```bash
scripts/install_launchd.sh
```

O script gera o plist com os caminhos reais desta máquina, valida com `plutil` e
carrega no launchd. Ele também recusa a instalação se o projeto estiver numa
pasta protegida, explicando o porquê.

Gerar em vez de editar um template resolve o problema mais chato do launchd: ele
**não herda o PATH do shell**. Se `claude` ou `python3` não estiverem no PATH
declarado no plist, o agente falha silenciosamente na madrugada.

### Testar sem esperar as 5h50

```bash
launchctl kickstart -k gui/$(id -u)/com.camps.campscast
tail -20 logs/launchd.out.log
```

Se o episódio do dia já existir, a saída esperada é "Nada novo a cobrir" com
código 0 — o que prova a cadeia inteira sem gastar créditos.

Conferir o código da última execução:

```bash
launchctl list | grep campscast
```

A segunda coluna é o código de saída. `0` é sucesso; `126` costuma ser o TCC.

### Deixar o Mac acordado

```bash
sudo pmset -c sleep 0
```

```bash
sudo pmset repeat wakeorpoweron MTWRF 05:45:00
```

Conferir:

```bash
pmset -g sched
pmset -g custom | grep -A1 "AC Power" 
```

### Remover o agendamento

```bash
scripts/install_launchd.sh --uninstall
```

## Checklist final

```bash
brew --version                                   # Homebrew
python3 --version                                # Python 3.11+
claude --version                                 # CLI instalado
ls ~/.claude/.credentials.json 2>/dev/null \
  || security find-generic-password -s "Claude Code-credentials" >/dev/null 2>&1 \
  && echo "CLI autenticado" || echo "FALTA /login"
bash tests/smoke_test.sh                         # tudo deve passar
python3 scripts/tts.py --check                   # chave, voz e cota
```

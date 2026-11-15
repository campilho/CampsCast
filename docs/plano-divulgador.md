# O Divulgador

Proposto em 15/11/2026. Os números de audiência ficam em `privado/`; aqui vai o
desenho e o que se mede.

**Hipótese.** Um post por semana no LinkedIn faz o programa crescer, e o que
faltava para ele sair toda semana não era texto.

**O que já se sabia.** O post de lançamento (29/09) foi o único mês em que os
seguidores cresceram de verdade. O post seguinte ficou pronto em outubro e não
saiu em cinco terças. A série de cinco posts está roteirizada e nenhum saiu. O
gargalo é o tempo do autor durante a semana, e ele não quer colar um texto
pronto: quer ler, interpretar e escrever a versão dele.

**O desenho.** O agente não escreve o post final e não publica.

| Quando | Quem | O quê |
|---|---|---|
| Sábado, 08:00 | o Divulgador (`scripts/divulga.py`) | escolhe a história, confere os fatos no repositório e escreve a pauta em `privado/divulgacao/AAAA-Www.md` |
| Em seguida | o script, sem modelo | confere a pauta e a manda ao autor |
| Domingo | o autor | escreve a versão dele, agenda no próprio LinkedIn e marca: `divulga.py --marca agendado --minutos N` |
| Dia do post, na hora | o script | lembra do primeiro comentário, com os links: o agendamento do LinkedIn não agenda comentário |
| Sexta | o autor | lê os seguidores, como já faz |

**O que o agente pode.** Ler o repositório e escrever um arquivo. Sem web, sem
shell, sem acesso ao LinkedIn. As regras do texto estão em
`config/divulgacao.md`.

**A conferência.** Roda sem modelo e barra a pauta quando:

- um fato citado não está na linha da fonte, ou a fonte não existe;
- um número da afirmação não aparece no trecho citado;
- um algarismo do rascunho não está em nenhuma linha da tabela de fatos;
- o rascunho tem link ou endereço.

Conta derivada (uma contagem, uma diferença de datas) o script não refaz: ele a
lista para o autor conferir à mão. Pauta barrada é entregue assim mesmo, com as
ressalvas no alto.

**O que não resolve.** A conferência prova que o número está no arquivo, não
que a frase em volta dele está certa. Número por extenso passa sem ser visto. E
a primeira hora de respostas, que decide o alcance, continua do autor.

## O experimento

- **Uma variável:** um post por semana, por oito semanas. As duas semanas das
  festas ficam de fora.
- **A métrica:** seguidores no Spotify, lidos às sextas, contra a linha de base
  sem divulgação.
- **A métrica do processo:** quantas das oito semanas tiveram post
  (`divulga.py --mostra`) e quanto do domingo cada uma custou. O tempo do autor
  é o gargalo, então é ele que se mede.
- **O custo:** uma execução por semana na assinatura Max, registrada em
  `metricas/divulgacao.jsonl`.

## Fora deste plano

- **Publicar pela API do LinkedIn.** O autor agenda à mão. A extensão do Chrome
  não se usa no LinkedIn.
- **Títulos pensados para a Busca do Spotify.** Mexe no prompt do Editor e pede
  ensaio; fica para depois, em semanas alternadas, para não misturar com os
  posts.
- **Instagram e cortes de áudio.** Um segundo experimento, depois da leitura
  deste.
- **O Divulgador no estúdio do site.** Ele ainda não é um personagem.

## Instalar

Antes, o e-mail: a pauta chega ao autor pelo `notify.py`, e sem SMTP ela vira
uma notificação do macOS, que não sai do Mac. No `.env`, `NOTIFY_TO` (para
onde vai), `SMTP_HOST` e `SMTP_PORT` (`smtp.gmail.com` e `587`, no Gmail),
`SMTP_USER` e `SMTP_PASS`; no Gmail, a senha é uma senha de app, criada na
conta Google com a verificação em duas etapas ligada. O `divulga.py` avisa no
log o que falta.

```bash
scripts/install_launchd_divulgador.sh
```

Um job à parte do episódio. `--print` mostra o plist sem instalar;
`--uninstall` remove.

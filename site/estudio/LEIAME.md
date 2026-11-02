# O estúdio do CampsCast (protótipo v3)

Página: `site/estudio/index.html`, servida em `/estudio/`. Código: nesta pasta. Dados: `elenco.json` e `ultimo.json`, também nesta pasta, gerados por `scripts/estudio.py` (contrato `campscast.estudio/1`, fora do git) e lidos sem alteração. O resto do site (capa, sugestão, privacidade) está descrito no `docs/site.md`.

## Para ver

```
python3 -m http.server 8765 --directory site
# http://localhost:8765/estudio/
```

Parâmetros (os de horário também estão na faixa "Ver em outro horário", no rodapé): `?sim=03:00|05:07|13:00|folga` (aceita também `HH:MM:SS`), `?replay=1&vel=real|acelerado|rapido&em=05:07:54&pausa=1`, `?ficha=editor&aba=pautas`, `?tema=claro|escuro`, `?vista=3d` (e `&forca3d=1`).

Desde 01/11 a página é o estúdio do site, atrás da capa (`site/index.html`). Os caminhos são absolutos (`/estudio/…`, `/fontes/…`), então ela precisa ser servida da raiz.

## Como está montado

| Arquivo | Papel |
|---|---|
| `planta.js` | o espaço: salas, postos, ronda do Vigia, escada, móveis. Fonte única para a cena |
| `motor.js` | **motor de cena**: relógio de São Paulo + eventos → `quadro(ms)` (quem está em que sala, fazendo o quê, com que balão, luz, céu). Também `Replay` e `Locomocao`. Não toca no DOM |
| `cena2d.js` | camada visual 2D pixel: 640×360 interno, ampliado em inteiros de pixel do aparelho; câmera de sala no celular |
| `sprites.js`, `pixelfont.js` | os 10 personagens (40×56) e a fonte das placas, desenhados em código |
| `app.js` | liga dados → motor → cena → página: balões, registro, barra de status, ficha, replay, minimapa |
| `folha.html` | ferramenta: todos os quadros dos sprites (`?id=jornalista&estados=trabalhando&k=6`) |
| `cena3d.js` | 3D, em pausa: só por `?vista=3d`, sem trabalho novo |
| `../fontes/` | as três fontes (OFL), servidas pelo próprio site: pedi-las ao Google entregaria o IP de quem visita. Valem para todas as páginas |

## O que mudou nesta rodada (acabamento, 01/11)

**Cena**
- Ala em obras de 112 para 80 px nos dois andares; a redação e o café ganharam 32 px cada.
- Salas cheias, com paleta limitada, contorno escuro e uma cor dominante por sala. Redação: quadro de cortiça com uma ficha por pauta do dia (o número vem de `episodio.pautas`; a do backlog sai laranja; clicar abre a ficha do Editor), estante, plantas, luminárias de mesa, canecas e monitores. Cabine: espuma, mesa de som com VU que mexe quando o ON AIR acende, microfone de braço com pop filter. Técnica: racks com LEDs que piscam rápido quando há evento do Produtor, calha e cabos, mesa com dois monitores. Portaria: CRT `>CC`, quadro de chaves, relógio de parede no horário de São Paulo. Café: espresso com vapor, geladeira, mesa redonda com banquetas, plantas, cartaz. Arquivo: prateleiras com etiqueta do mês (anterior, atual e seguinte à data da gravação), escada de biblioteca, carrinho. Ala nova: andaime, lona, cone.
- Luz pela hora: cones quentes pontilhados nas luminárias, poças de luz no chão, sol das janelas no chão de dia, brilho azul das telas. De noite tudo azul-escuro, menos a portaria, o monitor e a luz do corredor; na madrugada da gravação, a redação acesa e as telas brilhando.
- Personagens em 40×56, cabeça maior (rosto e acessório legíveis no celular). Animações novas: Jornalista digitando, Editor folheando, Roteirista escrevendo, Locutor falando ao microfone, Arquivista carregando a caixa, Vigia de ronda com lanterna e cone de luz (de noite, a cada 64 s: portaria → café → técnica → café → portaria; sem balão enquanto anda).

**Painel e status**
- "No estúdio agora" virou o **registro**: hora, etiqueta da origem (com cor e texto), personagem e texto inteiro, mais a nota "no log" quando houver. Legenda embaixo. No replay, clicar num evento leva a linha do tempo até ele. No computador fica ao lado da cena; no celular, embaixo.
- **Barra de status** sob a cena, só com dado do JSON: na gravação e no replay, capítulo, páginas lidas, páginas que não abriram e buscas, contadas dos eventos até aquele ponto; no fim, custo de modelo e créditos de voz (`execucao`). Fora da gravação: próxima gravação com contagem regressiva (de `agenda.proximos`) e "no ar desde".
- Balão com mais de ~90 caracteres é cortado no último espaço, com "…". O texto inteiro fica no registro e na ficha.
- Em sala apertada (a portaria), o rodapé "montado com os números do dia" sai antes de o texto encolher: o cabeçalho já diz a origem. Com a cena em 640 px (janela entre ~1150 e ~1270 px em tela retina), os balões ainda ficam com uma linha.

**Ficha**
- Editor: os 10 temas, cada um com o estado e a data, em blocos que abrem. Fios com a contagem do arquivo de hoje (o 19 do café segue marcado como "números do dia"). Backlog vazio aparece como vazio.
- Jornalista: a nota de cada página aparece quando `leituras[].nota` vier preenchida; enquanto não vier, as notas do log ficam num bloco à parte. Escolhas aceitam texto ("X em vez de Y — por quê") ou objeto.
- Produtor: custo de modelo e créditos de voz.

**Outros**
- Sem botão "Ver em 3D". O `cena3d.js` continua no projeto, só por `?vista=3d` (com um botão "Voltar ao 2D").
- `privacidade.html`: o que coleta, para quê, onde, sem cookies nem rastreamento. Prazo de guarda, responsável, contato e data de revisão estão como **[a definir pelo autor]**.
- O formulário saiu daqui em 01/11 e foi para `/sugestao/`; a reação do estúdio à sugestão (o Vigia anunciando) volta com o envio de verdade.
- Antes da gravação dos dados carregados (ex.: `?sim=03:00` no mesmo dia), o Vigia e a barra de status não dizem que o episódio já está no ar.

## Regra de fidelidade

Os balões da gravação são os eventos do JSON, com a origem de cada um. Fora da gravação, os balões são a agenda e os números do dia, marcados como tal. A reação à sugestão do visitante aparece como "reação do site". Não há balão de pensamento. O corte em ~90 caracteres só encurta; nunca reescreve.

## Pendências

- `/privacidade/`: preencher prazo de guarda e data de revisão (responsável e contato preenchidos em 01/11 com o que está no `config/show.json`). Conferir o parágrafo que diz que um tema aceito pode entrar na lista de temas sugeridos do repositório público ("por ouvinte"), tirado do `docs/site.md`.
- Formulário de verdade (S4: API Gateway + Lambda + S3 privado).
- A partir de 03/11: conferir com dados reais as notas por página e as escolhas (o código já trata os dois formatos).
- Telas largas em dpr 1 entre 1100 e ~1700 px: a cena fica em escala fracionária (pixels desiguais). Em dpr 2 e em monitores largos a escala é inteira.
- 3D em pausa: as paredes acompanham a planta nova, mas móveis e acabamento não foram refeitos.

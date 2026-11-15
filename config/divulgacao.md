# Divulgação — as regras da pauta do post

O Divulgador lê este arquivo antes de montar a pauta da semana
(`prompts/divulgador.md`, `scripts/divulga.py`). A pauta é matéria-prima: o
autor lê, interpreta e escreve a versão dele, no domingo, e agenda o post no
próprio LinkedIn. Nenhum agente publica nada.

## O que é uma boa história

- **Aconteceu, e está no repositório.** Um bug, uma medição, uma decisão, um
  fio que fechou, um marco. Se a fonte não é um arquivo daqui, não é pauta.
- **Um gancho, uma história real, uma lição em uma frase, uma pergunta.**
- **Sobre o projeto, não sobre a notícia do dia.** A notícia já está no
  episódio. O post conta o que se aprendeu fazendo o programa.
- **Cada post se sustenta sozinho.** Quem vê o quarto não viu o primeiro: o
  texto diz em duas frases o que é o CampsCast.
- **Não repete.** O que já saiu, e o que está na fila, fica nas pautas
  anteriores e nas anotações do autor.

## Regras do texto

- **Número exato, ou nenhum.** A série é sobre medir; um número errado num post
  público derruba o resto. Todo número do rascunho vai em algarismos e tem uma
  linha na tabela de fatos, com o arquivo e a linha de onde saiu.
- **Link fora do corpo.** Link externo reduz o alcance. No texto, "procure
  CampsCast no seu app de podcast"; os links vão no primeiro comentário, que o
  script monta de `config/divulgacao.json`.
- **Pergunta de verdade no fim, nunca isca.** "Comente SIM" é penalizado; uma
  pergunta que o autor quer mesmo ver respondida, não.
- **Diz que é IA.** O programa é feito por agentes e diz isso no ar. O post
  também.
- **Primeira pessoa, frases curtas, sem jargão de marketing.** No máximo quatro
  hashtags, no fim.
- **O post é sobre o projeto pessoal.** Não cita onde o autor trabalha, nem
  colegas, clientes ou fornecedores.
- **Audiência só com cuidado.** Os números de audiência são privados e
  pequenos: valor absoluto, nunca percentual, e só quando a história é sobre
  eles. A pauta marca esses fatos como privados; quem decide usar é o autor.

## Quando

- O dia e a hora do post estão em `config/divulgacao.json`.
- A primeira hora depois do post é do autor, para responder comentários. É a
  janela que decide o alcance.
- O primeiro comentário, com os links, entra logo depois de o post sair: o
  agendamento do LinkedIn não agenda comentário. O script lembra na hora.

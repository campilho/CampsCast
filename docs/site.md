# Site do CampsCast — rascunho de estrutura (beta 1)

- **Status:** rascunho para discussão (04/10/2026). Visual a fazer com o
  Claude Design.
- **Endereço:** `campscast.com.br`, hoje respondendo 403 na raiz.

## Para que serve

1. **Porta de entrada:** quem chega por um link — do LinkedIn, de um
   ouvinte — entende em dez segundos o que é e aperta o play ou segue no
   Spotify. O foco é o Spotify, onde estão os seguidores.
2. **Vitrine do "tudo é IA":** mostrar que um agente pesquisa, escreve e narra,
   com os números de verdade. É o que diferencia o programa.
3. **Canal de volta:** o formulário para ouvintes sugerirem pauta, fonte e
   tema, e darem retorno. Hoje só existe o e-mail `contato@`.
4. **Caminho para quem é técnico:** GitHub, ADRs, aprendizados.

## Para quem

| Visitante | Chega por | Quer | O site oferece |
|---|---|---|---|
| Curioso de IA | LinkedIn, indicação | saber se vale ouvir | último episódio tocando ali mesmo, botão do Spotify |
| Ouvinte | já ouve | sugerir, comentar | formulário |
| Gente técnica | GitHub, post sobre agentes | entender como funciona | "Como funciona", números, links para o código |
| Patrocinador, imprensa | busca | o que é, quem faz, contato | história, contato |

## Estrutura: uma página só no beta 1, com seções

1. **Topo**
   - capa (o conceito `> CC` do terminal), nome e a frase do `show.json`:
     "Briefing diário de IA, escrito e narrado por agentes";
   - **player do último episódio**, tocando o MP3 do próprio feed;
   - botões: **Spotify** (o oficial, de `assets/`, que troca de cor com o tema),
     Apple Podcasts e o link do feed RSS.
2. **Como funciona**, em quatro passos ilustrados: pesquisa nas fontes
   primárias → roteiro → voz sintética → publicação, às 5h de cada dia útil.
   O aviso de que tudo é feito por IA, inclusive a voz, uma cópia sintética da
   voz do autor, e de que nada sai em nome dele sem aprovação.
3. **Os números**, atualizados sozinhos a cada episódio: episódios publicados,
   páginas lidas e pautas avaliadas na semana, duração média. Saem do registro
   e dos roteiros que o pipeline já produz.
4. **Últimos episódios:** os cinco mais recentes, com título, data, duração e
   as pautas. Link para todos no Spotify.
5. **O que o programa acompanha:** os temas de `memoria/temas.md`, com o estado
   de cada um. É a memória do agente à vista, o que nenhum outro podcast mostra.
6. **A história:** os marcos do README, em linha do tempo: primeiro episódio
   em 24/08/2026, voz clonada profissional, os quatro diretórios, o destaque
   do LinkedIn News.
7. **Fale com o CampsCast:** o formulário (abaixo).
8. **Para quem é técnico:** GitHub, os ADRs, `docs/aprendizados.md`, como
   contribuir com pauta ou código.
9. **Rodapé:** `contato@campscast.com.br`, licenças (MIT para o código, CC BY
   4.0 para o conteúdo), link para a página de privacidade.

**Páginas à parte:** `/privacidade` (exigida pelo formulário, por causa da
LGPD). Depois do beta: `/episodios/AAAA-MM-DD/` com as notas do episódio e a
transcrição, que já existem nos roteiros — está nas ideias futuras do PROJETO.

## O formulário

| Campo | Obrigatório | Observação |
|---|---|---|
| Tipo | sim | sugestão de pauta, de fonte, de tema, retorno sobre o programa, outro |
| Mensagem | sim | até 2.000 caracteres |
| Nome | não | |
| E-mail | não | só se quiser resposta |
| Concordância | sim | com a página de privacidade |
| Campo isca | — | invisível, contra robôs |

**Por trás**, porque site estático não recebe envio sozinho:

```
formulário ──► API Gateway (HTTP API) ──► Lambda em Python
                                            ├─ grava a mensagem no S3, num
                                            │  prefixo privado, fora do site
                                            └─ avisa o autor por e-mail (SES)
```

- **Dados pessoais nunca vão para o git.** O repositório é público; as
  mensagens ficam no S3 privado. O agente recebe só o que importa para a
  pauta — o texto da sugestão, sem nome nem e-mail — e o que ele aproveitar
  vira item em `memoria/temas-sugeridos.md` (com "por ouvinte") ou no backlog.
- **Custo:** dentro do nível gratuito para o volume esperado. Preços a conferir
  quando for implementar.
- **Alternativa sem backend para o beta 1**, se for para sair antes: um link
  `mailto:` com o assunto preenchido. Perde a organização, mas sai no mesmo dia.

## Como fica no ar

- **Hospedagem:** o S3 e o CloudFront que já existem. Falta definir o objeto
  padrão da raiz (`index.html`) no CloudFront — é por isso que hoje dá 403.
- **Atualização sem trabalho:** o `publish.py`, que já gera o feed, passa a
  gerar também um `site/dados.json` com o último episódio, os números e os
  temas, e sobe junto. A página lê esse arquivo. O HTML só muda quando o
  desenho mudar.
- **Sem dependências**, como o resto do projeto: HTML, CSS e um pouco de
  JavaScript, sem framework nem build.
- **Sem cookies nem rastreamento** no beta 1. A audiência continua medida no
  Spotify.

## Visual, com o Claude Design

Levar para o Claude Design:

- a capa atual e o conceito de terminal `> CC`;
- esta estrutura e os textos de cada seção, já escritos;
- exigências: celular primeiro, tema claro e escuro, botões oficiais do
  Spotify sem alteração, contraste acessível;
- referência de tom: técnico, direto, sem hype — o mesmo do programa.

Pedir: um sistema visual mínimo (cores, tipografia, componentes) e a página
inteira em celular e computador. Depois, o HTML sai daqui, no repositório.

## Etapas

| Etapa | O quê |
|---|---|
| S1 | Fechar a estrutura e escrever os textos de cada seção |
| S2 | Visual no Claude Design |
| S3 | HTML e CSS no repositório; `dados.json` gerado pelo `publish.py`; raiz do CloudFront |
| S4 | Formulário: API Gateway, Lambda, S3 privado, SES; página de privacidade |
| S5 | Leitura das sugestões pelo agente, sem dados pessoais |

S1 a S3 são o beta 1 sem formulário, ou com o `mailto:`. S4 e S5 completam o
critério de saída da Fase 3: "formulário no ar, com as sugestões chegando ao
agente".

## Para decidir

1. Beta 1 já com o formulário de verdade, ou com `mailto:` primeiro?
2. Mostrar os temas no site? É a vitrine mais original, mas expõe a linha
   editorial em construção.
3. Mostrar o custo por episódio? É transparência total, coerente com o
   projeto; pode estar na seção técnica.
4. Domínio: o site em `campscast.com.br`; o `campscast.com`, que não é usado,
   pode redirecionar para cá — resolve a pendência de 2027.

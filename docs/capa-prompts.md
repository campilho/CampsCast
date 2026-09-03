# Prompts para a capa do CampsCast

Conceito: **terminal**. Fundo preto, prompt `>`, o nome, cursor `_`.

Comunica "feito por máquina" sem robô, cérebro ou rede neural — as três coisas
que todo podcast de IA usa e que viram borrão a 55 pixels. Terminal é forma
simples, altíssimo contraste, e sobrevive à miniatura.

## A restrição que decide tudo

Gere em **3000×3000**, mas julgue em **55 pixels**. É o tamanho na lista do app.
Reduza a imagem para 55px antes de aprovar: se o nome não for legível ali, a
capa falhou, por mais bonita que esteja em tamanho real.

Por isso: **`CC` é a aposta mais segura**, `CampsCast` é o mais informativo.
Gere as duas e compare reduzidas.

---

## Midjourney

```
podcast cover art, pure black background, retro computer terminal aesthetic,
a single bright green monospace command prompt symbol ">" followed by the text
"CampsCast" and a solid block cursor, phosphor glow, subtle scanlines, extreme
minimalism, high contrast, centered, flat, no gradients, no illustration,
no robot, no people --ar 1:1 --style raw --v 7
```

Variante com sigla, mais legível na miniatura:

```
podcast cover art, pure black background, terminal aesthetic, large bright
green monospace ">" prompt followed by "CC" and a blinking block cursor,
phosphor glow, minimal, high contrast, centered, square --ar 1:1 --style raw --v 7
```

Variante âmbar, se quiser fugir do verde clichê de terminal:

```
podcast cover art, deep black background, vintage terminal, warm amber
monospace text "> CampsCast_" centered, soft phosphor bloom, no scanlines,
brutalist minimalism, high contrast --ar 1:1 --style raw --v 7
```

## GPT Image / Nano Banana

Estes seguem instrução literal melhor que o Midjourney. Seja explícito sobre o
texto — inclusive sobre a capitalização, que é onde eles erram:

```
Square podcast cover, 3000x3000. Pure black background. Centered, a bright
green monospace terminal line reading exactly:  > CampsCast_
The ">" is a command prompt, the "_" is a block cursor. Capital C in "Camps"
and capital C in "Cast", no space between them. Nothing else in the image:
no border, no illustration, no extra text, no logo. Flat design, very high
contrast, generous margins around the text.
```

Se o texto sair errado depois de duas tentativas, pare de insistir: gere só o
fundo e componha o texto por cima.

## Plano B: compor o texto você mesmo

O caminho mais confiável, e o que eu escolheria.

1. Gere só o fundo (preto com brilho de fósforo sutil, ou preto liso mesmo).
2. Abra no Keynote, Figma ou Canva, quadrado 3000×3000.
3. Escreva `> CampsCast_` em fonte monoespaçada — **SF Mono**, **JetBrains
   Mono** ou **IBM Plex Mono**. O Mac já tem a primeira.
4. Verde de fósforo `#33FF66` ou âmbar `#FFB000` sobre preto `#000000`.
5. O texto deve ocupar cerca de 70% da largura. Margem generosa.

Tipografia feita à mão fica nítida, com kerning correto, e você troca a cor em
dez segundos.

---

## Antes de subir

- [ ] 3000×3000, quadrada exata
- [ ] JPEG ou PNG, RGB (não CMYK)
- [ ] Abaixo de 500 KB
- [ ] **Reduzida a 55px, o nome ainda se lê**
- [ ] Sem borda branca — a capa aparece sobre fundos claros e escuros

Subir:

```bash
python3 scripts/s3.py --bucket campscast --key cover.jpg \
  --file caminho/da/capa.jpg --content-type image/jpeg \
  --cache-control max-age=86400
curl -sI https://campscast.s3.us-east-1.amazonaws.com/cover.jpg | head -1
```

Depois republique o feed para os apps buscarem a capa nova:

```bash
python3 scripts/publish.py --date $(date +%F)
```

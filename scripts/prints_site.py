#!/usr/bin/env python3
"""Fotografa a abertura do site nos aparelhos que importam, para conferir.

    python3 scripts/prints_site.py                     # o site local (pasta site/)
    python3 scripts/prints_site.py --url https://campscast.com.br/
    python3 scripts/prints_site.py --so mac,s24        # só alguns aparelhos
    python3 scripts/prints_site.py --listar            # a tabela de aparelhos

Grava um PNG por aparelho e um `index.html` lado a lado em
`logs/prints-site/AAAA-MM-DD-HHMM/` (fora do git). Cada print tem o tamanho da
área visível do navegador, sem rolar: é o que a pessoa vê ao abrir.

Usa o Google Chrome sem janela, que está no Mac, conduzido pelo protocolo de
depuração por um par de canais (sem websocket nem biblioteca). É ferramenta de
quem mexe no site, fora do pipeline: o projeto segue sem dependências. Além do
print, mede na página se a ilustração e os botões cabem sem rolar, e se a
página rola para o lado; vai em `medidas.json` e embaixo de cada print.

Os tamanhos são em pixels CSS. A largura é a da tela do aparelho; a altura é a
área visível depois das barras do sistema e do navegador, que mudam com versão
e configuração — é estimativa, anotada em cada linha. O celular é emulado pelo
Chrome (largura, escala, toque, navegador declarado); barras que somem ao
rolar, não.
Pedido do autor em 20/11/2026: os aparelhos dele primeiro.
"""
from __future__ import annotations

import argparse
import base64
import functools
import html
import json
import os
import http.server
import pathlib
import select
import shutil
import sys
import threading
import time
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

UA_IPHONE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")
UA_IPAD = ("Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
           "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")
UA_ANDROID = ("Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36")

# (chave, nome, largura, altura visível, escala, navegador, de onde vem a altura)
APARELHOS = [
    ("mac", "MacBook Pro 14\" M3 (do autor), Chrome", 1512, 862, 2, None,
     "tela 1512x982; menos ~120 da barra do macOS, abas e endereço"),
    ("s24", "Galaxy S24 Ultra (do autor), Chrome", 384, 740, 3.75, UA_ANDROID,
     "tela 384x832; menos barra de status, endereço e navegação"),
    ("iphone16", "iPhone 16 (do autor), Safari", 393, 659, 3, UA_IPHONE,
     "tela 393x852; área do Safari com a barra de baixo"),
    ("ipadpro", "iPad Pro 12,9\" 1ª geração (do autor), Safari, em pé", 1024, 1292, 2, UA_IPAD,
     "tela 1024x1366; menos barra de status e do Safari"),
    ("iphone17", "iPhone 17, Safari", 402, 681, 3, UA_IPHONE,
     "tela 402x874; mesmas barras do 16"),
    ("iphone17pm", "iPhone 17 Pro Max, Safari", 440, 763, 3, UA_IPHONE,
     "tela 440x956; mesmas barras do 16"),
    ("fullhd", "Notebook Full HD (1920x1080, escala 100%), Chrome", 1920, 947, 1, None,
     "menos barra de tarefas do Windows e do Chrome"),
    ("fullhd125", "Notebook Full HD com escala de 125% (padrão do Windows), Chrome", 1536, 758, 1.25, None,
     "1920x1080 a 125% vira 1536x864; menos as barras"),
]


def servidor(pasta: pathlib.Path) -> tuple[http.server.ThreadingHTTPServer, str]:
    class Quieto(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
                                          functools.partial(Quieto, directory=str(pasta)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


class Chrome:
    """O Chrome sem janela, conduzido pelo protocolo de depuração (DevTools) por
    um par de canais (--remote-debugging-pipe): mensagens JSON terminadas em
    byte zero, sem websocket e sem biblioteca. Assim o aparelho é emulado de
    verdade (largura abaixo da janela mínima do Chrome, escala, modo celular),
    a foto espera a página, as fontes e a imagem, e dá para medir na página."""

    def __init__(self, binario: str, perfil: pathlib.Path):
        cmd_r, self.cmd_w = os.pipe()
        self.resp_r, resp_w = os.pipe()
        args = [binario, "--headless=new", "--remote-debugging-pipe", "--hide-scrollbars",
                "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                f"--user-data-dir={perfil}", "about:blank"]
        self.pid = os.posix_spawn(binario, args, os.environ,
                                  file_actions=[(os.POSIX_SPAWN_DUP2, cmd_r, 3),
                                                (os.POSIX_SPAWN_DUP2, resp_w, 4),
                                                (os.POSIX_SPAWN_OPEN, 1, "/dev/null", os.O_WRONLY, 0),
                                                (os.POSIX_SPAWN_OPEN, 2, "/dev/null", os.O_WRONLY, 0)])
        os.close(cmd_r)
        os.close(resp_w)
        self.n, self.buf, self.eventos = 0, b"", []

    def _le(self, prazo: float) -> dict:
        while b"\0" not in self.buf:
            if time.monotonic() > prazo:
                raise TimeoutError("o Chrome não respondeu a tempo")
            pronto, _, _ = select.select([self.resp_r], [], [], 1)
            if pronto:
                bloco = os.read(self.resp_r, 1 << 20)
                if not bloco:
                    raise RuntimeError("o Chrome fechou o canal")
                self.buf += bloco
        msg, self.buf = self.buf.split(b"\0", 1)
        return json.loads(msg)

    def manda(self, metodo: str, sessao: str | None = None, prazo: float = 30, **params) -> dict:
        self.n += 1
        pedido = {"id": self.n, "method": metodo, "params": params}
        if sessao:
            pedido["sessionId"] = sessao
        os.write(self.cmd_w, json.dumps(pedido).encode() + b"\0")
        limite = time.monotonic() + prazo
        while True:
            m = self._le(limite)
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError(f"{metodo}: {m['error'].get('message')}")
                return m.get("result", {})
            self.eventos.append(m)

    def espera(self, evento: str, sessao: str, prazo: float = 30) -> None:
        limite = time.monotonic() + prazo
        while True:
            for i, m in enumerate(self.eventos):
                if m.get("method") == evento and m.get("sessionId") == sessao:
                    del self.eventos[i]
                    return
            self.eventos.append(self._le(limite))

    def fecha(self) -> None:
        try:
            self.manda("Browser.close", prazo=5)
        except Exception:  # noqa: BLE001
            pass
        os.close(self.cmd_w)
        os.close(self.resp_r)
        try:
            os.waitpid(self.pid, 0)
        except ChildProcessError:
            pass


# O que se mede na página aberta, sem rolar.
MEDE = """(async () => {
  await document.fonts.ready;
  const img = document.querySelector('.vitrine img');
  if (img && !img.complete) await new Promise(r => img.addEventListener('load', r, {once: true}));
  await new Promise(r => setTimeout(r, 300));
  const q = s => { const e = document.querySelector(s); return e ? e.getBoundingClientRect() : null; };
  const i = q('.vitrine img'), b = q('.hero .acoes');
  return JSON.stringify({altura: innerHeight, largura: innerWidth,
    lateral: document.documentElement.scrollWidth > innerWidth,
    img_topo: i && Math.round(i.top), img_fim: i && Math.round(i.bottom), img_largura: i && Math.round(i.width),
    botoes_fim: b && Math.round(b.bottom)});
})()"""


def fotografa(chrome: Chrome, url: str, largura: int, altura: int, escala: float,
              ua: str | None, saida: pathlib.Path) -> dict:
    alvo = chrome.manda("Target.createTarget", url="about:blank")["targetId"]
    sessao = chrome.manda("Target.attachToTarget", targetId=alvo, flatten=True)["sessionId"]
    try:
        chrome.manda("Page.enable", sessao)
        chrome.manda("Emulation.setDeviceMetricsOverride", sessao, width=largura, height=altura,
                     deviceScaleFactor=escala, mobile=bool(ua))
        if ua:
            chrome.manda("Emulation.setUserAgentOverride", sessao, userAgent=ua)
            chrome.manda("Emulation.setTouchEmulationEnabled", sessao, enabled=True)
        chrome.manda("Page.navigate", sessao, url=url)
        chrome.espera("Page.loadEventFired", sessao, prazo=45)
        r = chrome.manda("Runtime.evaluate", sessao, prazo=45, expression=MEDE,
                         awaitPromise=True, returnByValue=True)
        medidas = json.loads(r["result"]["value"])
        png = chrome.manda("Page.captureScreenshot", sessao, format="png")["data"]
        saida.write_bytes(base64.b64decode(png))
        return medidas
    finally:
        chrome.manda("Target.closeTarget", targetId=alvo)


def veredito(m: dict) -> str:
    """Em uma linha: a ilustração e os botões cabem na tela sem rolar?"""
    partes = []
    if m.get("img_fim") is not None:
        falta = m["img_fim"] - m["altura"]
        partes.append("ilustração inteira" if falta <= 0 else f"ilustração: faltam {falta} px")
    if m.get("botoes_fim") is not None:
        partes.append("botões à vista" if m["botoes_fim"] <= m["altura"] else "botões abaixo da dobra")
    if m.get("lateral"):
        partes.append("ROLAGEM LATERAL")
    return "; ".join(partes)


def folha(pasta: pathlib.Path, linhas: list[tuple], url: str, medidas: dict) -> str:
    """index.html com os prints lado a lado, na escala de 1 px CSS = 1 px."""
    blocos = "\n".join(
        f'<figure><img src="{k}.png" width="{w}" alt="{html.escape(n)}">'
        f'<figcaption><b>{html.escape(n)}</b><br>{w}×{h} px · {html.escape(o)}'
        f'<br><i>{html.escape(veredito(medidas.get(k, {})))}</i></figcaption></figure>'
        for k, n, w, h, _e, _ua, o in linhas)
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Abertura do site · {datetime.now():%d/%m %H:%M}</title>
<style>body{{background:#222;color:#ddd;font:14px system-ui;margin:24px}}
main{{display:flex;flex-wrap:wrap;gap:28px;align-items:flex-start}}
figure{{margin:0}}img{{display:block;height:auto;border:1px solid #555}}
figcaption{{max-width:420px;margin-top:6px}}</style></head><body>
<h1>Abertura do site</h1><p>{html.escape(url)} · {datetime.now():%d/%m/%Y %H:%M}</p>
<main>{blocos}</main></body></html>
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Fotografa a abertura do site em vários aparelhos.")
    ap.add_argument("--url", help="endereço a fotografar (padrão: a pasta site/, servida aqui)")
    ap.add_argument("--so", help="só estes aparelhos, separados por vírgula")
    ap.add_argument("--saida", type=pathlib.Path, help="pasta dos prints")
    ap.add_argument("--listar", action="store_true", help="mostra a tabela de aparelhos e sai")
    a = ap.parse_args(argv)

    linhas = APARELHOS
    if a.so:
        pedidos = set(a.so.split(","))
        desconhecidos = pedidos - {l[0] for l in APARELHOS}
        if desconhecidos:
            print(f"prints: aparelho desconhecido: {', '.join(sorted(desconhecidos))}", file=sys.stderr)
            return 2
        linhas = [l for l in APARELHOS if l[0] in pedidos]
    if a.listar:
        for k, n, w, h, e, _ua, o in linhas:
            print(f"{k:11} {w:5}×{h:<5} x{e:<5} {n} — {o}")
        return 0

    chrome = CHROME if pathlib.Path(CHROME).exists() else shutil.which("google-chrome")
    if not chrome:
        print("prints: Google Chrome não encontrado.", file=sys.stderr)
        return 1
    pasta = (a.saida or ROOT / "logs" / "prints-site" / datetime.now().strftime("%Y-%m-%d-%H%M")).resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    perfil = pasta / ".perfil-chrome"
    srv, url = (None, a.url) if a.url else servidor(ROOT / "site")
    navegador, medidas = None, {}
    try:
        navegador = Chrome(chrome, perfil)
        for k, n, w, h, e, ua, _o in linhas:
            medidas[k] = fotografa(navegador, url, w, h, e, ua, pasta / f"{k}.png")
            print(f"  {k:11} {w}×{h}  {veredito(medidas[k])}")
    except (OSError, RuntimeError, TimeoutError, KeyError, ValueError) as err:
        print(f"prints: o Chrome falhou: {err}", file=sys.stderr)
        return 1
    finally:
        if navegador:
            navegador.fecha()
        if srv:
            srv.shutdown()
        shutil.rmtree(perfil, ignore_errors=True)
    (pasta / "medidas.json").write_text(json.dumps(medidas, indent=1) + "\n", encoding="utf-8")
    (pasta / "index.html").write_text(folha(pasta, linhas, url, medidas), encoding="utf-8")
    print(f"Prints de {len(linhas)} aparelhos: {pasta / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

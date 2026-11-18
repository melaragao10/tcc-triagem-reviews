"""
Servidor do painel com atualizacao automatica ("ao vivo").

Serve a pasta reports/ e recarrega sozinho a pagina aberta no navegador
sempre que algum arquivo de reports/ mudar (por exemplo, depois de rodar
`python main.py --saida reports/completo` ou de gerar um novo painel).

Como funciona:
  - /                lista os paineis encontrados (reports/**/painel.html);
  - /<pasta>/        abre reports/<pasta>/painel.html (ex.: /steam/);
  - /__versao        devolve um carimbo que muda quando qualquer arquivo
                     de reports/ muda;
  - as paginas .html recebem, na hora de servir, um pequeno script que
    consulta /__versao a cada 2 segundos e recarrega a pagina quando o
    carimbo muda, mantendo a posicao de rolagem. Os arquivos em disco nao
    sao alterados.

So usa a biblioteca padrao. Pensado para rodar na VM e ser aberto por
tunel SSH (ver README).

Uso, na raiz do projeto:

    python -m src.painel_vivo
    python -m src.painel_vivo --pasta reports --porta 8091
"""

import argparse
import mimetypes
import os
import re
import time
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

INTERVALO_MS = 2000

SCRIPT_AO_VIVO = """
<script>
(function () {
  var inicio = "__VERSAO__";
  var selo = document.createElement("div");
  selo.style.cssText = "position:fixed;right:12px;bottom:12px;z-index:99999;padding:6px 10px;" +
    "border-radius:999px;font:12px system-ui,sans-serif;background:rgba(20,22,26,.88);" +
    "color:#8fd694;border:1px solid rgba(255,255,255,.15);pointer-events:none";
  function agora() { return new Date().toLocaleTimeString("pt-BR"); }
  function pintar(texto, ok) {
    selo.textContent = (ok ? "\\u25CF ao vivo" : "\\u25CB sem conexao") + " \\u00B7 " + texto;
    selo.style.color = ok ? "#8fd694" : "#e6a86c";
  }
  document.body.appendChild(selo);
  var chave = "pv_rolagem:" + location.pathname;
  try {
    var y = sessionStorage.getItem(chave);
    if (y) { window.scrollTo(0, parseInt(y, 10)); sessionStorage.removeItem(chave); }
  } catch (e) {}
  pintar("carregado " + agora(), true);
  function checar() {
    fetch("/__versao", { cache: "no-store" })
      .then(function (r) { return r.text(); })
      .then(function (v) {
        if (v !== inicio) {
          try { sessionStorage.setItem(chave, String(window.scrollY)); } catch (e) {}
          location.reload();
          return;
        }
        pintar("verificado " + agora(), true);
      })
      .catch(function () { pintar("tentando reconectar", false); });
  }
  setInterval(checar, __INTERVALO__);
})();
</script>
"""


def versao(raiz: Path) -> str:
    """Carimbo da pasta: quantidade de arquivos e a data de modificacao mais recente."""
    quantidade, mais_recente = 0, 0
    for pasta, _, arquivos in os.walk(raiz):
        for nome in arquivos:
            try:
                mais_recente = max(mais_recente, os.stat(os.path.join(pasta, nome)).st_mtime_ns)
                quantidade += 1
            except OSError:
                continue
    return f"{quantidade}:{mais_recente}"


def injetar(html: str, carimbo: str) -> str:
    """Coloca o script ao vivo antes de </body> (ou no fim, se nao houver)."""
    script = SCRIPT_AO_VIVO.replace("__VERSAO__", carimbo).replace("__INTERVALO__", str(INTERVALO_MS))
    achados = list(re.finditer(r"</body\s*>", html, flags=re.IGNORECASE))
    if achados:
        posicao = achados[-1].start()
        return html[:posicao] + script + html[posicao:]
    return html + script


def resolver(raiz: Path, caminho: str):
    """Caminho pedido -> arquivo dentro de raiz, ou None (nunca sai da pasta)."""
    base = raiz.resolve()
    alvo = (base / caminho.lstrip("/")).resolve()
    if alvo != base and base not in alvo.parents:
        return None
    return alvo


def listar_paineis(raiz: Path) -> list:
    itens = []
    for arquivo in sorted(raiz.rglob("painel.html")):
        relativo = arquivo.parent.relative_to(raiz)
        href = "/" if str(relativo) == "." else "/" + quote(relativo.as_posix()) + "/"
        estado = arquivo.stat()
        itens.append((href, relativo.as_posix() if str(relativo) != "." else "(raiz de reports)",
                      time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(estado.st_mtime)),
                      estado.st_size / 1024))
    return itens


def pagina_indice(raiz: Path) -> str:
    linhas = "".join(
        f'<li><a href="{escape(href)}">{escape(nome)}</a> '
        f'<span class="meta">atualizado em {quando} &middot; {tamanho:,.0f} KB</span></li>'.replace(",", ".")
        for href, nome, quando, tamanho in listar_paineis(raiz)
    ) or "<li>Nenhum painel encontrado em reports/. Rode a classificacao primeiro.</li>"
    return (
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Paineis ao vivo</title><style>"
        "body{font:16px system-ui,sans-serif;background:#16181d;color:#e7eaf0;max-width:720px;margin:48px auto;padding:0 20px}"
        "a{color:#8ab4f8;font-weight:600}li{margin:14px 0}.meta{color:#9aa4b2;font-size:13px;margin-left:8px}"
        "h1{font-size:22px}</style></head><body><h1>Paineis (atualizam sozinhos)</h1><ul>"
        + linhas + "</ul></body></html>"
    )


class Manipulador(BaseHTTPRequestHandler):
    raiz = Path("reports")

    def log_message(self, *args):  # silencia o log de cada requisicao
        pass

    def _enviar(self, status: int, corpo: bytes, tipo: str, extra: dict = None):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        for chave, valor in (extra or {}).items():
            self.send_header(chave, valor)
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        caminho = unquote(urlparse(self.path).path)
        if caminho == "/__versao":
            return self._enviar(200, versao(self.raiz).encode(), "text/plain; charset=utf-8")
        if caminho == "/":
            html = injetar(pagina_indice(self.raiz), versao(self.raiz))
            return self._enviar(200, html.encode("utf-8"), "text/html; charset=utf-8")

        alvo = resolver(self.raiz, caminho)
        if alvo is None:
            return self._enviar(404, b"nao encontrado", "text/plain; charset=utf-8")
        if alvo.is_dir():
            if not caminho.endswith("/"):
                return self._enviar(301, b"", "text/plain", {"Location": quote(caminho) + "/"})
            alvo = alvo / "painel.html"
        if not alvo.is_file():
            return self._enviar(404, b"nao encontrado", "text/plain; charset=utf-8")

        tipo = mimetypes.guess_type(alvo.name)[0] or "application/octet-stream"
        dados = alvo.read_bytes()
        if alvo.suffix.lower() == ".html":
            dados = injetar(dados.decode("utf-8", errors="replace"), versao(self.raiz)).encode("utf-8")
            tipo = "text/html; charset=utf-8"
        elif tipo.startswith("text/") or tipo in ("application/json", "image/svg+xml"):
            tipo += "; charset=utf-8" if "charset" not in tipo else ""
        self._enviar(200, dados, tipo)


def criar_servidor(raiz: Path, endereco: str, porta: int) -> ThreadingHTTPServer:
    classe = type("ManipuladorPasta", (Manipulador,), {"raiz": Path(raiz)})
    return ThreadingHTTPServer((endereco, porta), classe)


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor de paineis com atualizacao automatica.")
    parser.add_argument("--pasta", type=Path, default=Path("reports"), help="pasta servida (padrao: reports)")
    parser.add_argument("--endereco", default="127.0.0.1", help="use 0.0.0.0 so dentro de container")
    parser.add_argument("--porta", type=int, default=int(os.environ.get("PAINEL_VIVO_PORTA", 8091)))
    args = parser.parse_args()
    if not args.pasta.is_dir():
        raise SystemExit(f"Pasta nao encontrada: {args.pasta}")
    servidor = criar_servidor(args.pasta, args.endereco, args.porta)
    print(f"Paineis ao vivo em http://{args.endereco}:{args.porta}/  (pasta: {args.pasta})", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

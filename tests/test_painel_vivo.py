import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from src.painel_vivo import criar_servidor, injetar, listar_paineis, resolver, versao


def pegar(url: str):
    with urllib.request.urlopen(url, timeout=5) as r:
        return r.status, r.read().decode("utf-8", errors="replace"), r.headers


class TestPainelVivo(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        (self.raiz / "steam").mkdir()
        (self.raiz / "steam" / "painel.html").write_text(
            "<html><body><h1>Painel</h1></body></html>", encoding="utf-8")
        (self.raiz / "steam" / "dados.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        self.servidor = criar_servidor(self.raiz, "127.0.0.1", 0)
        self.base = f"http://127.0.0.1:{self.servidor.server_address[1]}"
        threading.Thread(target=self.servidor.serve_forever, daemon=True).start()

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self._tmp.cleanup()

    def test_injetar_antes_do_ultimo_body(self):
        html = injetar("<html><body>x</body></html>", "7:1")
        self.assertLess(html.index("/__versao"), html.index("</body>"))
        self.assertIn('"7:1"', html)

    def test_injetar_sem_body_vai_para_o_fim(self):
        self.assertTrue(injetar("<p>oi</p>", "1:1").startswith("<p>oi</p>"))

    def test_versao_muda_quando_arquivo_muda(self):
        antes = versao(self.raiz)
        time.sleep(0.01)
        (self.raiz / "steam" / "painel.html").write_text("<body>novo</body>", encoding="utf-8")
        self.assertNotEqual(antes, versao(self.raiz))

    def test_versao_muda_quando_arquivo_novo_aparece(self):
        antes = versao(self.raiz)
        (self.raiz / "novo.csv").write_text("x", encoding="utf-8")
        self.assertNotEqual(antes, versao(self.raiz))

    def test_resolver_bloqueia_saida_da_pasta(self):
        self.assertIsNone(resolver(self.raiz, "../etc/passwd"))
        self.assertIsNone(resolver(self.raiz, "/../../etc/passwd"))
        self.assertIsNotNone(resolver(self.raiz, "steam/painel.html"))

    def test_painel_recebe_script_ao_vivo(self):
        status, corpo, _ = pegar(self.base + "/steam/")
        self.assertEqual(status, 200)
        self.assertIn("<h1>Painel</h1>", corpo)
        self.assertIn("/__versao", corpo)

    def test_pasta_sem_barra_redireciona(self):
        class SemRedirecionar(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        abridor = urllib.request.build_opener(SemRedirecionar)
        with self.assertRaises(urllib.error.HTTPError) as erro:
            abridor.open(self.base + "/steam", timeout=5)
        self.assertEqual(erro.exception.code, 301)

    def test_versao_e_cache_desligado(self):
        status, corpo, cab = pegar(self.base + "/__versao")
        self.assertEqual(status, 200)
        self.assertEqual(corpo, versao(self.raiz))
        self.assertEqual(cab["Cache-Control"], "no-store")

    def test_pagina_recarregada_traz_conteudo_novo(self):
        (self.raiz / "steam" / "painel.html").write_text(
            "<html><body><h1>Painel v2</h1></body></html>", encoding="utf-8")
        self.assertIn("Painel v2", pegar(self.base + "/steam/")[1])

    def test_csv_nao_recebe_script(self):
        status, corpo, _ = pegar(self.base + "/steam/dados.csv")
        self.assertEqual(status, 200)
        self.assertNotIn("__versao", corpo)

    def test_arquivo_inexistente_e_traversal_dao_404(self):
        for caminho in ("/nao_existe.html", "/%2e%2e/%2e%2e/etc/passwd"):
            with self.assertRaises(urllib.error.HTTPError) as erro:
                pegar(self.base + caminho)
            self.assertEqual(erro.exception.code, 404)

    def test_indice_lista_paineis(self):
        self.assertEqual(len(listar_paineis(self.raiz)), 1)
        _, corpo, _ = pegar(self.base + "/")
        self.assertIn('href="/steam/"', corpo)


if __name__ == "__main__":
    unittest.main()

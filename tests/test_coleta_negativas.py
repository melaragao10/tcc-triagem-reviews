import unittest
from unittest import mock

import requests

from src import coleta_steam as cs


class RespostaFalsa:
    def __init__(self, status=200, corpo=None):
        self.status_code = status
        self._corpo = corpo if corpo is not None else {"response": {"reviews": [], "cursor": "*"}}

    def json(self):
        return self._corpo

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} erro")


class SessaoFalsa:
    def __init__(self, respostas):
        self.respostas = list(respostas)
        self.chamadas = 0
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        self.chamadas += 1
        item = self.respostas.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class TestTipo(unittest.TestCase):
    def test_negativas_usam_review_type_2(self):
        import json
        p = cs.montar_parametros("*", "brazilian", "helpful", 1, tipo="negativas")
        self.assertEqual(json.loads(p["input_json"])["review_type"], 2)

    def test_padrao_continua_todas(self):
        import json
        p = cs.montar_parametros("*", "brazilian", "helpful", 1)
        self.assertEqual(json.loads(p["input_json"])["review_type"], 0)

    def test_tipo_invalido(self):
        with self.assertRaises(ValueError):
            cs.montar_parametros("*", "brazilian", "helpful", 1, tipo="neutras")


class TestTentativas(unittest.TestCase):
    def test_502_e_repetido_e_depois_funciona(self):
        sessao = SessaoFalsa([RespostaFalsa(502), RespostaFalsa(502), RespostaFalsa(200)])
        with mock.patch.object(cs.time, "sleep") as dormir:
            resposta = cs.pedir_com_tentativas(sessao, {})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(sessao.chamadas, 3)
        self.assertEqual([c.args[0] for c in dormir.call_args_list], [cs.ESPERA_RETRY, cs.ESPERA_RETRY * 2])

    def test_conexao_caida_e_repetida(self):
        sessao = SessaoFalsa([requests.ConnectionError("reset"), RespostaFalsa(200)])
        with mock.patch.object(cs.time, "sleep"):
            self.assertEqual(cs.pedir_com_tentativas(sessao, {}).status_code, 200)

    def test_desiste_depois_do_limite(self):
        sessao = SessaoFalsa([RespostaFalsa(502)] * cs.TENTATIVAS)
        with mock.patch.object(cs.time, "sleep"):
            self.assertEqual(cs.pedir_com_tentativas(sessao, {}).status_code, 502)
        self.assertEqual(sessao.chamadas, cs.TENTATIVAS)

    def test_429_nao_e_repetido_aqui(self):
        sessao = SessaoFalsa([RespostaFalsa(429)])
        with mock.patch.object(cs.time, "sleep") as dormir:
            cs.pedir_com_tentativas(sessao, {})
        self.assertEqual(sessao.chamadas, 1)
        dormir.assert_not_called()

    def test_coletar_sobrevive_a_um_502(self):
        corpo = {"response": {"reviews": [{"recommendationid": 1, "voted_up": False, "review": "ruim"}], "cursor": "abc"}}
        vazio = {"response": {"reviews": [], "cursor": "abc"}}
        sessao = SessaoFalsa([RespostaFalsa(502), RespostaFalsa(200, corpo), RespostaFalsa(200, vazio)])
        with mock.patch.object(cs.time, "sleep"):
            linhas = cs.coletar(1, "Jogo", 10, sessao=sessao, tipo="negativas")
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["recomendado"], "nao")


if __name__ == "__main__":
    unittest.main()


class TestLoteEJogos(unittest.TestCase):
    def test_lote_negativas_grava_com_sufixo_na_mesma_pasta(self):
        import tempfile
        from pathlib import Path
        corpo = {"response": {"reviews": [{"recommendationid": 1, "voted_up": False, "review": "ruim"}], "cursor": "abc"}}
        vazio = {"response": {"reviews": [], "cursor": "abc"}}
        sessao = SessaoFalsa([RespostaFalsa(200, corpo), RespostaFalsa(200, vazio)])
        with tempfile.TemporaryDirectory() as pasta, mock.patch.object(cs.time, "sleep"):
            resumo = cs.coletar_lote([{"appid": 10, "jogo": "X"}], 5, "brazilian", "helpful",
                                     Path(pasta), sessao=sessao, tipo="negativas")
            self.assertTrue((Path(pasta) / "steam_10_negativas.csv").exists())
            self.assertFalse((Path(pasta) / "steam_10.csv").exists())
        self.assertEqual(resumo[0]["coletadas"], 1)

    def test_jogos_unicos_e_suficientes(self):
        import json
        from pathlib import Path
        caminho = Path(__file__).resolve().parents[1] / "config" / "jogos.json"
        ids = [x["appid"] for x in json.loads(caminho.read_text(encoding="utf-8"))["jogos"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 17)

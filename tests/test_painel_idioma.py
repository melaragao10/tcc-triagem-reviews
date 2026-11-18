import unittest

import pandas as pd

from src.painel import montar_dados, montar_html, opcoes_de_idioma


def _df(idiomas):
    linhas = []
    for i, idioma in enumerate(idiomas):
        linhas.append({"id_review": str(i), "jogo": "A", "texto_original": "bug no jogo", "categoria": "Tecnico",
                       "indicadores_tecnicos": "bug", "indicadores_afetivos": "", "idioma": idioma,
                       "escore_tecnico": 1, "escore_afetivo": 0, "confianca": 1.0, "regra_acionada": "R1"})
    return pd.DataFrame(linhas)


class TestFiltroIdioma(unittest.TestCase):
    def test_opcoes_com_dois_idiomas(self):
        ops = opcoes_de_idioma(_df(["brazilian", "english", "english"]))
        self.assertEqual([(o["codigo"], o["n"]) for o in ops], [("brazilian", 1), ("english", 2)])
        self.assertEqual(ops[1]["rotulo"], "inglês")

    def test_sem_filtro_com_um_idioma_ou_sem_coluna(self):
        self.assertEqual(opcoes_de_idioma(_df(["english", "english"])), [])
        self.assertEqual(opcoes_de_idioma(_df(["english"]).drop(columns=["idioma"])), [])

    def test_review_carrega_o_idioma(self):
        dados = montar_dados(_df(["brazilian", "english"]))
        self.assertEqual([r["idioma"] for r in dados["reviews"]], ["brazilian", "english"])

    def test_html_tem_seletor(self):
        self.assertIn('id="f-idioma"', montar_html(montar_dados(_df(["brazilian", "english"]))))


if __name__ == "__main__":
    unittest.main()

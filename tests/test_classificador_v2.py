import json
import unittest
from pathlib import Path

from src.classificador import classify_review, find_compounds, find_indicators

BASE = json.loads((Path(__file__).resolve().parents[1] / "config" / "base_conhecimento.json").read_text(encoding="utf-8"))


class TestCompostos(unittest.TestCase):
    REGRA = [{"nome": "r", "janela": 2, "grupo_a": ["personagem"], "grupo_b": ["feia"], "peso": 3}]

    def test_dentro_da_janela(self):
        score, achados = find_compounds("a personagem principal e feia", self.REGRA)
        self.assertEqual(score, 3)
        self.assertEqual(achados, ["r [personagem + feia]"])

    def test_fora_da_janela(self):
        self.assertEqual(find_compounds("personagem um dois tres feia", self.REGRA)[0], 0)

    def test_ordem_invertida(self):
        self.assertEqual(find_compounds("feia essa personagem", self.REGRA)[0], 3)

    def test_conta_uma_vez(self):
        self.assertEqual(find_compounds("personagem feia personagem feia", self.REGRA)[0], 3)

    def test_sem_regras(self):
        self.assertEqual(find_compounds("qualquer texto", []), (0, []))


class TestBilingue(unittest.TestCase):
    def test_ingles_afetivo_composto(self):
        r = classify_review("All the characters are so ugly in this game", BASE)
        self.assertEqual(r["categoria"], "Afetivo-visual")
        self.assertIn("characters + ugly", r["indicadores_afetivos"])

    def test_ingles_tecnico(self):
        r = classify_review("Constant crashes and fps drops", BASE)
        self.assertEqual(r["categoria"], "Tecnico")

    def test_misto_em_ingles(self):
        r = classify_review("The main character looks ugly and the game keeps crashing", BASE)
        self.assertEqual(r["categoria"], "Misto")
        self.assertEqual(r["regra_acionada"], "R3")

    def test_portugues_com_barba(self):
        r = classify_review("A protagonista tem barba, ficou estranho", BASE)
        self.assertEqual(r["categoria"], "Afetivo-visual")

    def test_elogio_nao_dispara(self):
        r = classify_review("The characters are beautiful and the story is great", BASE)
        self.assertEqual(r["categoria"], "Indefinido")

    def test_forced_sozinho_nao_dispara(self):
        r = classify_review("I was forced to play as Abby for hours", BASE)
        self.assertEqual(r["categoria"], "Indefinido")

    def test_ingles_nao_usa_radical(self):
        _, achados = find_indicators("crashing again", {"crash": 2}, use_stem=False)
        self.assertEqual(achados, [])

    def test_base_v1_continua_funcionando(self):
        base_v1 = {"tecnico": {"bug": 1}, "afetivo_visual": {"personagem feia": 3}}
        self.assertEqual(classify_review("tem um bug", base_v1)["categoria"], "Tecnico")

    def test_termos_pt_e_en_nao_se_repetem(self):
        for grupo in ("tecnico", "afetivo_visual"):
            self.assertFalse(set(BASE[grupo]) & set(BASE["en"][grupo]))


if __name__ == "__main__":
    unittest.main()


class TestNeutralizadores(unittest.TestCase):
    def test_negacao_neutraliza(self):
        r = classify_review("Eu nao vi essa lacracao que falam", BASE)
        self.assertEqual(r["categoria"], "Indefinido")
        self.assertIn("ignorado", r["indicadores_afetivos"])

    def test_critica_sem_negacao_pontua(self):
        self.assertEqual(classify_review("Jogo cheio de lacracao", BASE)["categoria"], "Afetivo-visual")

    def test_nao_gostei_nao_neutraliza(self):
        self.assertEqual(classify_review("Nao gostei, jogo muito woke", BASE)["categoria"], "Afetivo-visual")

    def test_woke_up_e_excecao(self):
        self.assertEqual(classify_review("The fandom woke up today", BASE)["categoria"], "Indefinido")

    def test_preposicao_no_nao_neutraliza(self):
        self.assertEqual(classify_review("fora a lacracao no mundo dos games", BASE)["categoria"], "Afetivo-visual")

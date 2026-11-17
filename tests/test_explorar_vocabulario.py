import csv
import tempfile
import unittest
from pathlib import Path

from src.explorar_vocabulario import candidatos, filtrar, grupos_encontrados, ler_reviews, normalizar, trecho_alvo


class TestExplorarVocabulario(unittest.TestCase):
    def test_normalizar_remove_acentos_e_pontuacao(self):
        self.assertEqual(normalizar("A Protagonista é FEIA!!"), "a protagonista e feia")
        self.assertEqual(normalizar(None), "")

    def test_sondas_encontram_os_tres_grupos(self):
        grupos = grupos_encontrados(normalizar("Lacração total, a protagonista parece um homem"))
        self.assertEqual(grupos, {"personagem", "aparencia", "ideologico"})

    def test_sonda_nao_casa_no_meio_de_palavra(self):
        self.assertEqual(grupos_encontrados(normalizar("Servidor caindo toda hora")), set())

    def test_trecho_alvo_exige_proximidade(self):
        perto = normalizar("A protagonista parece um homem de tao feia")
        self.assertIsNotNone(trecho_alvo(perto))
        longe = normalizar("Os personagens sao ok " + "muito texto no meio " * 6 + "mas os graficos sao bonitos")
        self.assertIsNone(trecho_alvo(longe))

    def test_candidatos_ignoram_palavras_vazias(self):
        unigramas, bigramas = candidatos(["personagem feia demais", "personagem feia mesmo"], minimo=2)
        self.assertIn(("personagem", 2), unigramas)
        self.assertIn(("personagem feia", 2), bigramas)
        self.assertNotIn("de", [t for t, _ in unigramas])

    def test_filtros_por_jogo_e_negativas(self):
        linhas = [
            {"jogo": "Horizon Zero Dawn", "recomendado": "nao"},
            {"jogo": "Horizon Zero Dawn", "recomendado": "sim"},
            {"jogo": "Star Wars Outlaws", "recomendado": "nao"},
        ]
        self.assertEqual(len(filtrar(linhas, ["horizon"], False)), 2)
        self.assertEqual(len(filtrar(linhas, ["horizon"], True)), 1)
        self.assertEqual(len(filtrar(linhas, [], False)), 3)

    def test_ler_reviews_aceita_bom_do_excel(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "r.csv"
            with caminho.open("w", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f)
                w.writerow(["jogo", "categoria"])
                w.writerow(["X", "Indefinido"])
            self.assertEqual(ler_reviews(caminho)[0]["jogo"], "X")


if __name__ == "__main__":
    unittest.main()

import csv
import tempfile
import unittest
from pathlib import Path

from src.explorar_vocabulario import (ALVO_AMPLO, candidatos, filtrar, grupos_encontrados, ler_reviews,
                                      normalizar, trecho_alvo)


class TestExplorarVocabulario(unittest.TestCase):
    def test_normalizar_remove_acentos_e_pontuacao(self):
        self.assertEqual(normalizar("A Protagonista é FEIA!!"), "a protagonista e feia")
        self.assertEqual(normalizar(None), "")

    def test_sondas_separam_rejeicao_de_ideologia(self):
        grupos = grupos_encontrados(normalizar("Lacração total, a protagonista parece um homem"))
        self.assertEqual(grupos, {"personagem", "aparencia_neg", "ideologico"})

    def test_elogio_a_aparencia_nao_e_candidato(self):
        texto = normalizar("A Aloy é linda e o jogo é bonito")
        self.assertEqual(grupos_encontrados(texto), {"personagem", "aparencia_pos"})
        self.assertIsNone(trecho_alvo(texto))

    def test_termo_neutro_so_conta_no_modo_amplo(self):
        texto = normalizar("Gostei do rosto da protagonista")
        self.assertIsNone(trecho_alvo(texto))
        self.assertIsNotNone(trecho_alvo(texto, alvo=ALVO_AMPLO))

    def test_sonda_nao_casa_no_meio_de_palavra(self):
        self.assertEqual(grupos_encontrados(normalizar("Servidor caindo toda hora")), set())

    def test_trecho_alvo_exige_proximidade(self):
        perto = normalizar("A protagonista parece um homem de tao feia")
        self.assertIsNotNone(trecho_alvo(perto))
        longe = normalizar("Os personagens sao ok " + "muito texto no meio " * 6 + "mas a coisa e feia")
        self.assertIsNone(trecho_alvo(longe))

    def test_ingles_rejeicao_e_elogio(self):
        feio = normalizar("They made Aloy so ugly, she looks like a man")
        self.assertEqual(grupos_encontrados(feio, "en"), {"personagem", "aparencia_neg"})
        self.assertIsNotNone(trecho_alvo(feio, idioma="en"))
        elogio = normalizar("Aloy is beautiful and the world is gorgeous")
        self.assertIsNone(trecho_alvo(elogio, idioma="en"))

    def test_ingles_ideologia_exige_personagem(self):
        self.assertIsNotNone(trecho_alvo(normalizar("The female lead is so forced and woke"), idioma="en"))
        self.assertIsNone(trecho_alvo(normalizar("Woke garbage, do not buy"), idioma="en"))

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

    def test_ler_reviews_junta_varios_arquivos(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminhos = []
            for nome in ("a.csv", "b.csv"):
                caminho = Path(pasta) / nome
                with caminho.open("w", encoding="utf-8-sig", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["jogo", "categoria"])
                    w.writerow([nome, "Indefinido"])
                caminhos.append(caminho)
            self.assertEqual([r["jogo"] for r in ler_reviews(caminhos)], ["a.csv", "b.csv"])


if __name__ == "__main__":
    unittest.main()

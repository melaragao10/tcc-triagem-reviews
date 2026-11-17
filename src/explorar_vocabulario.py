"""
Explora o vocabulario real dos reviews para orientar a ampliacao da base
de conhecimento (secao 3.4 do TCC: revisao dos comentarios indefinidos).

Le um CSV ja classificado e mostra, para os reviews Indefinidos:
  - quantos falam de personagens, de aparencia e de vocabulario
    ideologico (sondas abaixo), por jogo;
  - as palavras e pares de palavras mais frequentes entre os que falam
    de personagem E de aparencia/ideologia (candidatos a indicador);
  - uma amostra de reviews, tambem gravada em CSV, para leitura.

Nada aqui altera a base: o sistema nao muda suas proprias regras
(secao 3.4). A decisao de incluir um termo e da pesquisadora.

Para evitar sobreajuste, descubra o vocabulario em uma parte dos jogos
(--jogos) e meca o resultado nos demais.

Uso, na raiz do projeto:

    python -m src.explorar_vocabulario
    python -m src.explorar_vocabulario --jogos "Horizon" "Last of Us" --so-negativas
"""

import argparse
import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

PADRAO_ENTRADA = Path("reports/steam/reviews_classificados.csv")
PADRAO_SAIDA = Path("reports/vocabulario")

# Sondas: so servem para achar candidatos. Nao sao a base de conhecimento.
SONDAS = {
    "personagem": r"personagem|personagens|protagonista|aloy|abby|ellie|kay vess|mary jane|\bmj\b|"
                  r"rook|taash|ryder|harley|mulher|mulheres|garota|menina|heroina",
    "aparencia": r"feia|feio|feias|feios|horrivel|horriveis|bonita|bonito|linda|lindo|atraente|"
                 r"rosto|corpo|musculo|musculos|musculosa|musculoso|masculina|masculino|masculinizada|homem|barba|"
                 r"gorda|magra|roupa|aparencia|visual|modelo|sexy|sexualizada|estranha|estranho",
    "ideologico": r"woke|lacracao|lacrar|lacra|agenda|politica|politico|ideologia|ideologico|"
                  r"diversidade|propaganda|militancia|militante|feminista|feminismo|lgbt|trans|"
                  r"inclusao|forcar|forcada|forcado|forcaram|forcando|forca a barra|dei",
}
SONDAS_RE = {nome: re.compile(r"(?<![a-z0-9])(?:" + padrao + r")(?![a-z0-9])") for nome, padrao in SONDAS.items()}

PALAVRAS_VAZIAS = set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sobre ate e ou mas que
se ao aos nao sim muito mais menos mesmo ja so tambem como quando onde isso isto esse essa esses
essas este esta estes estas ele ela eles elas eu voce vc meu minha seu sua lhe me te nos ser sao
foi era tem ter tinha tenho fazer faz feito jogo jogos game games ta tao bem ainda pra pro mto
""".split())


def normalizar(texto) -> str:
    """Mesma padronizacao do classificador: minusculas, sem acentos, sem links nem pontuacao."""
    if texto is None:
        return ""
    t = unicodedata.normalize("NFKD", str(texto).lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def grupos_encontrados(texto_normalizado: str) -> set:
    return {nome for nome, rx in SONDAS_RE.items() if rx.search(texto_normalizado)}


def trecho_alvo(texto_normalizado: str, janela: int = 8):
    """
    Primeiro trecho de `janela` palavras em que uma palavra de personagem aparece
    junto de uma de aparencia ou de ideologia. Evita marcar reviews longos so
    porque falam de personagens e de graficos em lugares diferentes.
    """
    palavras = texto_normalizado.split()
    for i in range(max(1, len(palavras) - janela + 1)):
        trecho = " ".join(palavras[i:i + janela])
        grupos = grupos_encontrados(trecho)
        if "personagem" in grupos and ({"aparencia", "ideologico"} & grupos):
            return trecho, grupos
    return None


def candidatos(textos_normalizados: list, minimo: int = 2, topo: int = 40) -> tuple:
    """Palavras e pares de palavras mais frequentes (sem palavras vazias)."""
    unigramas, bigramas = Counter(), Counter()
    for texto in textos_normalizados:
        palavras = [p for p in texto.split() if len(p) > 2 and p not in PALAVRAS_VAZIAS]
        unigramas.update(set(palavras))
        bigramas.update({f"{a} {b}" for a, b in zip(palavras, palavras[1:])})
    cortar = lambda c: [(t, n) for t, n in c.most_common() if n >= minimo][:topo]
    return cortar(unigramas), cortar(bigramas)


def ler_reviews(caminho: Path) -> list:
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def filtrar(linhas: list, jogos: list, so_negativas: bool) -> list:
    resultado = []
    for linha in linhas:
        if jogos and not any(j.lower() in (linha.get("jogo") or "").lower() for j in jogos):
            continue
        if so_negativas and (linha.get("recomendado") or "").strip().lower() not in ("nao", "não", "false", "0"):
            continue
        resultado.append(linha)
    return resultado


def main() -> None:
    parser = argparse.ArgumentParser(description="Explora o vocabulario dos reviews indefinidos.")
    parser.add_argument("--entrada", type=Path, default=PADRAO_ENTRADA, help="CSV classificado")
    parser.add_argument("--saida", type=Path, default=PADRAO_SAIDA, help="pasta de saida")
    parser.add_argument("--jogos", nargs="*", default=[], help="trechos do nome dos jogos a considerar")
    parser.add_argument("--so-negativas", action="store_true", help="so reviews que nao recomendam o jogo")
    parser.add_argument("--amostra", type=int, default=15, help="quantos reviews mostrar na tela")
    args = parser.parse_args()

    linhas = filtrar(ler_reviews(args.entrada), args.jogos, args.so_negativas)
    if not linhas:
        raise SystemExit("Nenhum review depois dos filtros.")

    print(f"Reviews considerados: {len(linhas)}")
    for categoria, n in Counter(l["categoria"] for l in linhas).most_common():
        print(f"  {categoria:<15} {n:>5}  ({n / len(linhas) * 100:.1f}%)")

    indefinidos = [l for l in linhas if l["categoria"] == "Indefinido"]
    por_jogo = defaultdict(lambda: Counter())
    alvo = []
    for linha in indefinidos:
        texto = normalizar(linha["texto_original"])
        grupos = grupos_encontrados(texto)
        jogo = linha["jogo"]
        por_jogo[jogo]["indefinidos"] += 1
        for g in grupos:
            por_jogo[jogo][g] += 1
        achado = trecho_alvo(texto)
        if achado:
            por_jogo[jogo]["alvo"] += 1
            alvo.append((linha, achado[0], achado[1]))

    print(f"\nIndefinidos: {len(indefinidos)}. Quantos mencionam cada tipo de sonda, por jogo:")
    print(f"  {'jogo':<42}{'indef.':>7}{'person.':>8}{'aparen.':>8}{'ideol.':>7}{'alvo':>6}")
    for jogo, c in sorted(por_jogo.items()):
        print(f"  {jogo[:41]:<42}{c['indefinidos']:>7}{c['personagem']:>8}{c['aparencia']:>8}{c['ideologico']:>7}{c['alvo']:>6}")
    print("  (alvo = personagem e aparencia/ideologia a ate 8 palavras de distancia: os candidatos a revisar)")

    unigramas, bigramas = candidatos([t for _, t, _ in alvo])
    print(f"\nPalavras mais frequentes nos trechos dos {len(alvo)} reviews 'alvo':")
    print("  " + ", ".join(f"{t} ({n})" for t, n in unigramas))
    print("\nPares de palavras mais frequentes:")
    print("  " + ", ".join(f"{t} ({n})" for t, n in bigramas))

    args.saida.mkdir(parents=True, exist_ok=True)
    destino = args.saida / "amostra_candidatos.csv"
    with destino.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["jogo", "recomendado", "sondas", "trecho", "texto_original", "indicador_sugerido", "grupo"])
        for linha, trecho, grupos in alvo:
            escritor.writerow([linha["jogo"], linha["recomendado"], "+".join(sorted(grupos)),
                               trecho, linha["texto_original"], "", ""])
    print(f"\nTodos os 'alvo' em {destino} (colunas indicador_sugerido e grupo para voce preencher).")

    print(f"\nAmostra ({min(args.amostra, len(alvo))}):")
    for linha, trecho, grupos in alvo[:args.amostra]:
        print(f"- [{linha['jogo'][:22]} | {'+'.join(sorted(grupos))}] ...{trecho}...")


if __name__ == "__main__":
    main()

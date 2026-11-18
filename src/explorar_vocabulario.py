"""
Explora o vocabulario real dos reviews para orientar a ampliacao da base
de conhecimento (secao 3.4 do TCC: revisao dos comentarios indefinidos).

Le CSVs de reviews (classificados ou nao) e mostra, para os Indefinidos (ou
para todos, se o CSV nao tiver a coluna "categoria"):
  - quantos falam de personagens, de aparencia (com rejeicao ou elogio)
    e de vocabulario ideologico (sondas abaixo), por jogo;
  - as palavras e pares de palavras mais frequentes entre os reviews em que
    uma personagem e citada junto de rejeicao de aparencia ou de ideologia
    (candidatos a indicador);
  - uma amostra de reviews, tambem gravada em CSV, para leitura.

As sondas separam rejeicao (aparencia_neg) de elogio (aparencia_pos): falar
da aparencia de uma personagem nao e rejeita-la. So a rejeicao e a critica
ideologica entram nos candidatos, a menos que se use --incluir-neutra.

Idiomas: --idioma pt (padrao) ou --idioma en.

Nada aqui altera a base: o sistema nao muda suas proprias regras
(secao 3.4). A decisao de incluir um termo e da pesquisadora.

Para evitar sobreajuste, descubra o vocabulario em uma parte dos jogos
(--jogos) e meca o resultado nos demais.

Uso, na raiz do projeto:

    python -m src.explorar_vocabulario --entrada reports/completo/reviews_classificados.csv
    python -m src.explorar_vocabulario --idioma en --entrada data/en/steam_*.csv --saida reports/vocabulario_en
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
SONDAS_POR_IDIOMA = {
    "pt": {
        "personagem": r"personagem|personagens|protagonista|aloy|abby|ellie|kay vess|mary jane|\bmj\b|"
                      r"rook|taash|ryder|harley|mulher|mulheres|garota|menina|heroina",
        "aparencia_neg": r"feia|feio|feias|feios|feiura|horrivel|horriveis|masculina|masculino|masculinizada|"
                         r"homem|barba|gorda|gordo|estranha|estranho|esquisita|esquisito|deformada|"
                         r"desproporcional|sem feminilidade",
        "aparencia_pos": r"linda|lindo|lindas|lindos|bonita|bonito|bonitas|bonitos|atraente|deslumbrante|"
                         r"belissima|belissimo|gata|gostosa|beleza|bela|belo",
        "aparencia_neutra": r"rosto|corpo|musculo|musculos|musculosa|musculoso|roupa|roupas|aparencia|"
                            r"visual|modelo|design|sexy|sexualizada|magra",
        "ideologico": r"woke|lacracao|lacrar|lacra|agenda|politica|politico|ideologia|ideologico|"
                      r"diversidade|propaganda|militancia|militante|feminista|feminismo|lgbt|trans|"
                      r"inclusao|forcar|forcada|forcado|forcaram|forcando|forca a barra|dei",
    },
    "en": {
        "personagem": r"character|characters|protagonist|aloy|abby|ellie|kay vess|kay|mary jane|\bmj\b|"
                      r"rook|taash|ryder|harley|woman|women|girl|female|heroine|lead",
        "aparencia_neg": r"ugly|uglier|ugliest|hideous|mannish|manly|masculine|beard|bearded|fat|overweight|"
                         r"unattractive|unappealing|deformed|disproportionate|looks like a man|like a dude|"
                         r"like a guy|like a man|looks like a dude|not attractive|not pretty|peach fuzz|"
                         r"lost her femininity",
        "aparencia_pos": r"beautiful|pretty|gorgeous|attractive|hot|cute|stunning|lovely|handsome|"
                         r"breathtaking|good looking",
        "aparencia_neutra": r"face|body|muscles|muscular|outfit|clothes|appearance|design|model|"
                            r"sexualized|skinny|physique",
        "ideologico": r"woke|agenda|political|politics|ideology|ideological|diversity|dei|propaganda|forced|"
                      r"shoehorned|shoehorn|pandering|feminist|feminism|lgbt|lgbtq|trans|inclusion|"
                      r"virtue signaling|sjw|preachy|lecture|lectured",
    },
}

PALAVRAS_VAZIAS_POR_IDIOMA = {
    "pt": set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sobre ate e ou mas que
se ao aos nao sim muito mais menos mesmo ja so tambem como quando onde isso isto esse essa esses
essas este esta estes estas ele ela eles elas eu voce vc meu minha seu sua lhe me te nos ser sao
foi era tem ter tinha tenho fazer faz feito jogo jogos game games ta tao bem ainda pra pro mto
""".split()),
    "en": set("""
a an the and or but if of to in on at for with without about as by from into is are was were be been
being it its this that these those i you he she they we me my your his her their our not no yes very
more most less much many so too just also than then there here have has had do does did done game
games play played playing can could would should will its im ive dont doesnt didnt isnt wasnt
""".split()),
}

ALVO_ESTRITO = ("aparencia_neg", "ideologico")
ALVO_AMPLO = ("aparencia_neg", "aparencia_neutra", "ideologico")


def _compilar(sondas: dict) -> dict:
    return {nome: re.compile(r"(?<![a-z0-9])(?:" + padrao + r")(?![a-z0-9])") for nome, padrao in sondas.items()}


SONDAS_RE_POR_IDIOMA = {idioma: _compilar(s) for idioma, s in SONDAS_POR_IDIOMA.items()}
# Compatibilidade: sondas em portugues como padrao.
SONDAS = SONDAS_POR_IDIOMA["pt"]
SONDAS_RE = SONDAS_RE_POR_IDIOMA["pt"]
PALAVRAS_VAZIAS = PALAVRAS_VAZIAS_POR_IDIOMA["pt"]


def normalizar(texto) -> str:
    """Mesma padronizacao do classificador: minusculas, sem acentos, sem links nem pontuacao."""
    if texto is None:
        return ""
    t = unicodedata.normalize("NFKD", str(texto).lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def grupos_encontrados(texto_normalizado: str, idioma: str = "pt") -> set:
    return {nome for nome, rx in SONDAS_RE_POR_IDIOMA[idioma].items() if rx.search(texto_normalizado)}


def trecho_alvo(texto_normalizado: str, janela: int = 8, alvo: tuple = ALVO_ESTRITO, idioma: str = "pt"):
    """
    Primeiro trecho de `janela` palavras em que uma palavra de personagem aparece
    junto de uma de rejeicao de aparencia ou de ideologia. Evita marcar reviews
    longos so porque falam de personagens e de graficos em lugares diferentes, e
    nao conta elogio (aparencia_pos) como candidato.
    """
    palavras = texto_normalizado.split()
    for i in range(max(1, len(palavras) - janela + 1)):
        trecho = " ".join(palavras[i:i + janela])
        grupos = grupos_encontrados(trecho, idioma)
        if "personagem" in grupos and (set(alvo) & grupos):
            return trecho, grupos
    return None


def candidatos(textos_normalizados: list, minimo: int = 2, topo: int = 40, idioma: str = "pt") -> tuple:
    """Palavras e pares de palavras mais frequentes (sem palavras vazias)."""
    vazias = PALAVRAS_VAZIAS_POR_IDIOMA[idioma]
    unigramas, bigramas = Counter(), Counter()
    for texto in textos_normalizados:
        palavras = [p for p in texto.split() if len(p) > 2 and p not in vazias]
        unigramas.update(set(palavras))
        bigramas.update({f"{a} {b}" for a, b in zip(palavras, palavras[1:])})
    cortar = lambda c: [(t, n) for t, n in c.most_common() if n >= minimo][:topo]
    return cortar(unigramas), cortar(bigramas)


def ler_reviews(caminhos) -> list:
    if isinstance(caminhos, (str, Path)):
        caminhos = [caminhos]
    linhas = []
    for caminho in caminhos:
        with Path(caminho).open(encoding="utf-8-sig", newline="") as arquivo:
            linhas.extend(csv.DictReader(arquivo))
    return linhas


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
    parser.add_argument("--entrada", type=Path, nargs="+", default=[PADRAO_ENTRADA],
                        help="um ou mais CSVs (classificados ou coletados)")
    parser.add_argument("--saida", type=Path, default=PADRAO_SAIDA, help="pasta de saida")
    parser.add_argument("--idioma", choices=sorted(SONDAS_POR_IDIOMA), default="pt", help="idioma das sondas")
    parser.add_argument("--jogos", nargs="*", default=[], help="trechos do nome dos jogos a considerar")
    parser.add_argument("--so-negativas", action="store_true", help="so reviews que nao recomendam o jogo")
    parser.add_argument("--incluir-neutra", action="store_true",
                        help="inclui termos neutros de aparencia (rosto, corpo, roupa, visual) nos candidatos")
    parser.add_argument("--amostra", type=int, default=15, help="quantos reviews mostrar na tela")
    args = parser.parse_args()
    alvo_grupos = ALVO_AMPLO if args.incluir_neutra else ALVO_ESTRITO
    idioma = args.idioma

    linhas = filtrar(ler_reviews(args.entrada), args.jogos, args.so_negativas)
    if not linhas:
        raise SystemExit("Nenhum review depois dos filtros.")
    classificado = "categoria" in linhas[0]
    for linha in linhas:
        linha.setdefault("categoria", "Indefinido")

    print(f"Reviews considerados: {len(linhas)} (idioma das sondas: {idioma})")
    if classificado:
        for categoria, n in Counter(l["categoria"] for l in linhas).most_common():
            print(f"  {categoria:<15} {n:>5}  ({n / len(linhas) * 100:.1f}%)")
        indefinidos = [l for l in linhas if l["categoria"] == "Indefinido"]
    else:
        print("  (CSV sem coluna 'categoria': todos os reviews entram na exploracao)")
        indefinidos = linhas

    por_jogo = defaultdict(lambda: Counter())
    alvo = []
    for linha in indefinidos:
        texto = normalizar(linha.get("texto_original"))
        grupos = grupos_encontrados(texto, idioma)
        jogo = linha["jogo"]
        por_jogo[jogo]["indefinidos"] += 1
        for g in grupos:
            por_jogo[jogo][g] += 1
        achado = trecho_alvo(texto, alvo=alvo_grupos, idioma=idioma)
        if achado:
            por_jogo[jogo]["alvo"] += 1
            alvo.append((linha, achado[0], achado[1]))

    print(f"\nReviews explorados: {len(indefinidos)}. Quantos mencionam cada tipo de sonda, por jogo:")
    print(f"  {'jogo':<40}{'reviews':>8}{'person.':>8}{'rejeic.':>8}{'elogio':>7}{'ideol.':>7}{'alvo':>6}")
    total = Counter()
    for jogo, c in sorted(por_jogo.items()):
        total.update(c)
        print(f"  {jogo[:39]:<40}{c['indefinidos']:>8}{c['personagem']:>8}{c['aparencia_neg']:>8}"
              f"{c['aparencia_pos']:>7}{c['ideologico']:>7}{c['alvo']:>6}")
    print(f"  {'TOTAL':<40}{total['indefinidos']:>8}{total['personagem']:>8}{total['aparencia_neg']:>8}"
          f"{total['aparencia_pos']:>7}{total['ideologico']:>7}{total['alvo']:>6}")
    print("  (rejeic./elogio = termos de aparencia em cada polaridade, em qualquer ponto do texto;")
    print("   alvo = personagem a ate 8 palavras de rejeicao de aparencia ou de ideologia)")

    unigramas, bigramas = candidatos([t for _, t, _ in alvo], idioma=idioma)
    print(f"\nPalavras mais frequentes nos trechos dos {len(alvo)} reviews 'alvo':")
    print("  " + ", ".join(f"{t} ({n})" for t, n in unigramas))
    print("\nPares de palavras mais frequentes:")
    print("  " + ", ".join(f"{t} ({n})" for t, n in bigramas))

    args.saida.mkdir(parents=True, exist_ok=True)
    destino = args.saida / "amostra_candidatos.csv"
    with destino.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["jogo", "recomendado", "sondas", "trecho", "texto_original",
                           "e_rejeicao_ou_critica", "subtipo", "indicador_sugerido"])
        for linha, trecho, grupos in alvo:
            escritor.writerow([linha["jogo"], linha.get("recomendado", ""), "+".join(sorted(grupos)),
                               trecho, linha.get("texto_original", ""), "", "", ""])
    print(f"\nTodos os 'alvo' em {destino}")
    print("Preencha: e_rejeicao_ou_critica (sim/nao), subtipo (aparencia/representacao) e indicador_sugerido.")

    print(f"\nAmostra ({min(args.amostra, len(alvo))}):")
    for linha, trecho, grupos in alvo[:args.amostra]:
        print(f"- [{linha['jogo'][:22]} | {'+'.join(sorted(grupos))}] ...{trecho}...")


if __name__ == "__main__":
    main()

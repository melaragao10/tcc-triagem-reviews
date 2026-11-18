"""
Modulo do sistema especialista: normalizacao de texto, calculo de
escores, aplicacao de regras de decisao e calculo de confianca.

Ver TCC - Capitulo 3.5 (Etapa 4: classificacao por IA simbolica)
e Apendice A (pseudocodigo) para a fundamentacao teorica completa.

v1.1: adiciona normalizacao morfologica (stemming RSLP) como camada
complementar a comparacao literal, para tratar variacoes de conjugacao
verbal e flexao de genero/numero nao previstas na base de conhecimento
(ex: "fecha sozinho" vs "fechando sozinho"). O stemming e uma tecnica
simbolica/deterministica (reducao ao radical por regras linguisticas
explicitas), nao envolve interpretacao semantica ou aprendizado
estatistico, preservando a auditabilidade da classificacao (RNF3).

v1.2: corrige dupla contagem de indicadores diferentes que reduzem
ao mesmo radical (ex: "fecha sozinho" e "fechando sozinho"), que
inflava o escore ao contar duas vezes a mesma variacao morfologica
de um unico conceito. Ver docs/observacoes_teste_v1.md.

v1.3: a correcao da v1.2 dependia da ordem dos indicadores na base
(se o casamento por radical vinha antes do literal, o escore ainda era
somado duas vezes). Agora o casamento literal roda para todos os
indicadores antes do casamento por radical. Radicais de uma unica
palavra com menos de 3 letras deixam de casar sozinhos (overstemming
do RSLP, ex: "trava" e "trem" -> "tr"). Ver docs/decisao_stemming.md.

v2.1: neutralizadores (negacao/defesa perto do termo afetivo, ex.:
"nao e woke", "sem lacracao") e "excecoes_texto" (ex.: "woke up").
Ver docs/decisao_base_v2.md.

v2.4 (R7/R8): a saida ganha "revisao_manual" ("R7", "R8", "R7;R8" ou vazio),
que sinaliza reviews de baixa confianca ou com um unico indicador de peso 1;
nao muda a categoria.

v2.4: trechos curtos entre aspas ("Ain que jogo Woke") saem da busca do
grupo afetivo (base: "aspas_neutralizam_afetivo"); novos termos tecnicos,
compostos e neutralizadores. Ver docs/decisao_base_v2.md.

v2.0: base de conhecimento bilingue e indicadores compostos.
  - A base pode ter uma secao opcional "en" (termos em ingles). Os dois
    idiomas sao aplicados a todo review e os escores somam. Termos em
    ingles casam so de forma literal (o RSLP e um stemmer do portugues).
  - Indicadores compostos ("compostos"): um termo do grupo A e um termo
    do grupo B a ate N palavras de distancia (ex.: "personagem" perto de
    "feia"). Sao regras explicitas e auditaveis, registradas como
    "nome [termoA + termoB]". Casam so de forma literal.
  - Bases sem "en" nem "compostos" (v1.x) continuam funcionando igual.
  Ver docs/decisao_base_v2.md.
"""

import re
import unicodedata
from functools import lru_cache

import nltk
from nltk.stem import RSLPStemmer

try:
    nltk.data.find("stemmers/rslp")
except LookupError:
    nltk.download("rslp")

_stemmer = RSLPStemmer()


@lru_cache(maxsize=500_000)
def _stem_word(word: str) -> str:
    """Radical de uma palavra, com cache (o vocabulario dos reviews se repete muito)."""
    return _stemmer.stem(word)


def remove_accents(value: str) -> str:
    """Remove acentos de uma string, preservando as letras base."""
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(
        char for char in normalized if not unicodedata.combining(char)
    )


def normalize_text(value) -> str:
    """
    Padroniza o texto para comparacao com os indicadores:
    minusculas, sem acentos, sem links, sem pontuacao.
    A versao original do comentario NUNCA e alterada (RNF5 do TCC).
    """
    if value is None:
        return ""

    text = str(value).lower()
    text = remove_accents(text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def stem_phrase(phrase: str) -> str:
    """
    Aplica o stemmer RSLP a cada palavra de uma expressao normalizada,
    reduzindo cada termo ao seu radical (ex: "caindo" -> "caind").
    Obs.: o RSLP NAO une "cai" e "caiu" (cada um fica como esta); por
    isso "servidor cai" foi cadastrado explicitamente na base.
    """
    return " ".join(_stem_word(word) for word in phrase.split())


def _neutralizador(tokens: list, inicio: int, fim: int, neutralizers: list):
    """
    Negacao/defesa: devolve o neutralizador encontrado perto do termo
    (6 palavras antes ou 3 depois) ou None. Ex.: "nao e woke", "sem
    lacracao", "quem fala em woke e bobo". Regra explicita e auditavel.
    """
    if not neutralizers:
        return None
    contexto = (
        tokens[max(0, inicio - NEUTRALIZER_BEFORE) : inicio],
        tokens[fim + 1 : fim + 1 + NEUTRALIZER_AFTER],
    )
    for neutralizador in neutralizers:
        alvo = normalize_text(neutralizador).split()
        n = len(alvo)
        for trecho in contexto:
            for i in range(len(trecho) - n + 1):
                if trecho[i : i + n] == alvo:
                    return neutralizador
    return None


NEUTRALIZER_BEFORE = 6
NEUTRALIZER_AFTER = 3


def find_indicators(
    text: str, indicators: dict, use_stem: bool = True, neutralizers: list = None
) -> tuple:
    """
    Verifica quais indicadores de um grupo estao presentes no texto,
    em duas etapas:

    1) Comparacao literal (expressao exata, como no TCC original)
    2) Comparacao por radical (stemming), aplicada apenas se a etapa 1
       nao encontrar o indicador.

    Indicadores diferentes que reduzem ao MESMO radical (ex: "fecha
    sozinho" e "fechando sozinho") sao contados apenas UMA vez, para
    evitar dupla contagem de variacoes morfologicas do mesmo conceito.

    O metodo de casamento (literal ou via radical) fica registrado
    para fins de auditoria. Com use_stem=False so ha casamento literal
    (usado para os termos em ingles). Com "neutralizers", um termo literal
    com negacao/defesa por perto e ignorado e fica registrado como
    "(ignorado: ...)", sem escore.
    """
    score = 0
    found = []
    tokens = text.split()
    stemmed_text = stem_phrase(text) if use_stem else ""
    matched_stems = set()

    prepared = []
    for indicator, weight in indicators.items():
        normalized_indicator = normalize_text(indicator)
        prepared.append(
            (
                indicator,
                int(weight),
                normalized_indicator,
                stem_phrase(normalized_indicator) if use_stem else normalized_indicator,
            )
        )

    # Etapa 1: comparacao literal. Roda para TODOS os indicadores antes
    # da etapa por radical, para que o casamento exato tenha prioridade
    # no registro de auditoria independentemente da ordem na base.
    for indicator, weight, normalized_indicator, stemmed_indicator in prepared:
        if stemmed_indicator in matched_stems:
            # Mesmo radical ja contabilizado (ex: "bug" e "bugs").
            continue
        spans = _spans(tokens, normalized_indicator)
        if not spans:
            continue
        motivos = []
        for inicio, fim in spans:
            motivo = _neutralizador(tokens, inicio, fim, neutralizers)
            if motivo is None:
                score += weight
                found.append(indicator)
                matched_stems.add(stemmed_indicator)
                break
            motivos.append(motivo)
        else:
            found.append(f"{indicator} (ignorado: perto de '{motivos[0]}')")
            matched_stems.add(stemmed_indicator)

    # Etapa 2: comparacao por radical, apenas para indicadores cujo
    # radical ainda nao foi contabilizado.
    for indicator, weight, _normalized, stemmed_indicator in prepared:
        if not use_stem:
            break
        if stemmed_indicator in matched_stems:
            continue
        if not _stem_is_reliable(stemmed_indicator):
            continue
        if _contains(stemmed_text, stemmed_indicator):
            score += weight
            found.append(f"{indicator} (via radical)")
            matched_stems.add(stemmed_indicator)

    return score, found


# Radicais de uma unica palavra com menos letras que isso sao ambiguos
# demais para casar sozinhos (ex: RSLP reduz "trava" e "trem" a "tr").
MIN_SINGLE_WORD_STEM_LENGTH = 3


def _stem_is_reliable(stemmed_indicator: str) -> bool:
    """Indica se o radical e especifico o bastante para o casamento por radical."""
    if not stemmed_indicator:
        return False
    if " " in stemmed_indicator:
        return True
    return len(stemmed_indicator) >= MIN_SINGLE_WORD_STEM_LENGTH


def _contains(text: str, expression: str) -> bool:
    """Busca a expressao no texto respeitando limites de palavra."""
    pattern = r"(?<![a-z0-9])" + re.escape(expression) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def _spans(tokens: list, expression: str) -> list:
    """Posicoes (inicio, fim) das ocorrencias da expressao na lista de palavras."""
    alvo = normalize_text(expression).split()
    if not alvo:
        return []
    n = len(alvo)
    return [
        (i, i + n - 1)
        for i in range(len(tokens) - n + 1)
        if tokens[i : i + n] == alvo
    ]


def find_compounds(text: str, compounds: list, neutralizers: list = None) -> tuple:
    """
    Indicadores compostos: um termo do grupo A e um termo do grupo B a
    no maximo "janela" palavras de distancia (sem sobrepor). Cada regra
    conta uma unica vez. Retorna (escore, lista de regras acionadas),
    cada uma no formato "nome [termoA + termoB]".
    """
    tokens = text.split()
    score = 0
    found = []
    for regra in compounds or []:
        janela = int(regra.get("janela", 4))
        achou = None
        for termo_a in regra["grupo_a"]:
            spans_a = _spans(tokens, termo_a)
            if not spans_a:
                continue
            for termo_b in regra["grupo_b"]:
                for ini_a, fim_a in spans_a:
                    for ini_b, fim_b in _spans(tokens, termo_b):
                        if fim_a < ini_b:
                            distancia = ini_b - fim_a - 1
                        elif fim_b < ini_a:
                            distancia = ini_a - fim_b - 1
                        else:
                            continue
                        if distancia <= janela:
                            if _neutralizador(
                                tokens, min(ini_a, ini_b), max(fim_a, fim_b), neutralizers
                            ):
                                continue
                            achou = (termo_a, termo_b)
                            break
                    if achou:
                        break
                if achou:
                    break
            if achou:
                break
        if achou:
            score += int(regra["peso"])
            found.append(f"{regra['nome']} [{achou[0]} + {achou[1]}]")
    return score, found


def calculate_confidence(technical_score: int, affective_score: int) -> float:
    """
    Calcula o nivel de confianca conforme formula 3.3 do TCC.
    """
    total = technical_score + affective_score
    if total == 0:
        return 0.0
    return round(max(technical_score, affective_score) / total, 4)


def apply_decision_rule(technical_score: int, affective_score: int) -> tuple:
    """
    Aplica a matriz de classificacao (Tabela 3 do TCC).
    """
    if technical_score > 0 and affective_score == 0:
        return "Tecnico", "R1"
    if affective_score > 0 and technical_score == 0:
        return "Afetivo-visual", "R2"
    if technical_score > 0 and affective_score > 0:
        return "Misto", "R3"
    return "Indefinido", "R4"


def _score_group(text: str, knowledge_base: dict, group: str, excecoes=None) -> tuple:
    """
    Soma, para um grupo (tecnico ou afetivo_visual): os termos em
    portugues (literal + radical), os termos em ingles da secao "en"
    (so literal) e os indicadores compostos de cada idioma. No grupo
    afetivo_visual, negacao/defesa por perto neutraliza o termo.
    """
    secoes = [knowledge_base] + ([knowledge_base["en"]] if "en" in knowledge_base else [])
    neutralizers = []
    if group == "afetivo_visual":
        for secao in secoes:
            neutralizers += secao.get("neutralizadores", [])

    score, found = find_indicators(
        text, knowledge_base.get(group, {}), neutralizers=neutralizers
    )
    if "en" in knowledge_base:
        s, f = find_indicators(
            text, knowledge_base["en"].get(group, {}),
            use_stem=False, neutralizers=neutralizers,
        )
        score += s
        found += f
    for secao in secoes:
        s, f = find_compounds(text, secao.get("compostos_" + group, []), neutralizers)
        score += s
        found += f
    return score, found


def _remover_aspas(texto, max_caracteres: int = 60) -> str:
    """Troca por espaco os trechos curtos entre aspas (retas, curvas ou « »)."""
    padrao = re.compile(
        r'["\u201c\u00ab][^"\u201c\u201d\u00ab\u00bb\n]{1,%d}["\u201d\u00bb]' % int(max_caracteres)
    )
    return padrao.sub(" ", str(texto))


def _texto_de_busca(normalized_text: str, knowledge_base: dict) -> str:
    """Tira do texto padronizado as expressoes de excecao (ex.: "woke up")."""
    search_text = normalized_text
    for frase in knowledge_base.get("excecoes_texto", []):
        search_text = re.sub(
            r"(?<![a-z0-9])" + re.escape(normalize_text(frase)) + r"(?![a-z0-9])",
            " ",
            search_text,
        )
    return re.sub(r"\s+", " ", search_text).strip()


CONFIANCA_MINIMA = 0.6


def revisao_manual(technical_score: int, affective_score: int, confidence: float) -> str:
    """
    Regras R7 e R8 (Apendice E do TCC): sinalizam o review para revisao
    manual, sem mudar a categoria.
      R7: confianca menor que 0,6 (so quando ha algum indicador).
      R8: um unico indicador de peso 1 encontrado isoladamente (escore total = 1).
    Devolve "", "R7", "R8" ou "R7;R8".
    """
    total = technical_score + affective_score
    flags = []
    if total > 0 and confidence < CONFIANCA_MINIMA:
        flags.append("R7")
    if total == 1:
        flags.append("R8")
    return ";".join(flags)


def classify_review(original_text, knowledge_base: dict) -> dict:
    """
    Funcao principal: classifica um comentario com base na base de
    conhecimento, retornando escore, indicadores, categoria, regra
    e nivel de confianca.
    """
    normalized_text = normalize_text(original_text)
    search_text = _texto_de_busca(normalized_text, knowledge_base)

    # Termo entre aspas costuma ser citacao ou ironia sobre quem critica
    # ("Ain que jogo Woke"). Para o grupo afetivo, o trecho entre aspas
    # curtas sai da busca; o grupo tecnico continua vendo o texto inteiro.
    affective_text = search_text
    if knowledge_base.get("aspas_neutralizam_afetivo"):
        affective_text = _texto_de_busca(
            normalize_text(
                _remover_aspas(original_text, knowledge_base.get("aspas_max_caracteres", 60))
            ),
            knowledge_base,
        )

    technical_score, technical_indicators = _score_group(
        search_text, knowledge_base, "tecnico"
    )
    affective_score, affective_indicators = _score_group(
        affective_text, knowledge_base, "afetivo_visual"
    )

    category, rule = apply_decision_rule(technical_score, affective_score)
    confidence = calculate_confidence(technical_score, affective_score)
    review_flags = revisao_manual(technical_score, affective_score, confidence)

    return {
        "texto_padronizado": normalized_text,
        "escore_tecnico": technical_score,
        "escore_afetivo": affective_score,
        "indicadores_tecnicos": "; ".join(technical_indicators),
        "indicadores_afetivos": "; ".join(affective_indicators),
        "categoria": category,
        "confianca": confidence,
        "regra_acionada": rule,
        "revisao_manual": review_flags,
    }

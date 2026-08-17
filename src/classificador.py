"""
Modulo do sistema especialista: normalizacao de texto, calculo de
escores, aplicacao de regras de decisao e calculo de confianca.

Ver TCC - Capitulo 3.5 (Etapa 4: classificacao por IA simbolica)
e Apendice A (pseudocodigo) para a fundamentacao teorica completa.
"""

import re
import unicodedata


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


def find_indicators(text: str, indicators: dict) -> tuple:
    """
    Verifica quais indicadores de um grupo (tecnico ou afetivo_visual)
    estao presentes no texto normalizado e soma os pesos correspondentes.

    Retorna: (escore_total, lista_de_indicadores_encontrados)
    """
    score = 0
    found = []

    for indicator, weight in indicators.items():
        normalized_indicator = normalize_text(indicator)
        # (?<![a-z0-9]) e (?![a-z0-9]) garantem que o indicador
        # seja encontrado como palavra/expressao inteira, nao como
        # parte de outra palavra (evita falso positivo)
        pattern = (
            r"(?<![a-z0-9])" + re.escape(normalized_indicator) + r"(?![a-z0-9])"
        )
        if re.search(pattern, text):
            score += int(weight)
            found.append(indicator)

    return score, found


def calculate_confidence(technical_score: int, affective_score: int) -> float:
    """
    Calcula o nivel de confianca conforme formula 3.3 do TCC:
    proporcao entre o maior escore e a soma dos escores.
    """
    total = technical_score + affective_score
    if total == 0:
        return 0.0
    return round(max(technical_score, affective_score) / total, 4)


def apply_decision_rule(technical_score: int, affective_score: int) -> tuple:
    """
    Aplica a matriz de classificacao (Tabela 3 do TCC).
    Retorna: (categoria, regra_acionada)
    """
    if technical_score > 0 and affective_score == 0:
        return "Tecnico", "R1"
    if affective_score > 0 and technical_score == 0:
        return "Afetivo-visual", "R2"
    if technical_score > 0 and affective_score > 0:
        return "Misto", "R3"
    return "Indefinido", "R4"


def classify_review(original_text, knowledge_base: dict) -> dict:
    """
    Funcao principal: recebe um comentario e a base de conhecimento,
    retorna o resultado completo da classificacao com explicabilidade
    (indicadores encontrados, regra acionada, nivel de confianca).
    """
    normalized_text = normalize_text(original_text)

    technical_score, technical_indicators = find_indicators(
        normalized_text, knowledge_base["tecnico"]
    )
    affective_score, affective_indicators = find_indicators(
        normalized_text, knowledge_base["afetivo_visual"]
    )

    category, rule = apply_decision_rule(technical_score, affective_score)
    confidence = calculate_confidence(technical_score, affective_score)

    return {
        "texto_padronizado": normalized_text,
        "escore_tecnico": technical_score,
        "escore_afetivo": affective_score,
        "indicadores_tecnicos": "; ".join(technical_indicators),
        "indicadores_afetivos": "; ".join(affective_indicators),
        "categoria": category,
        "confianca": confidence,
        "regra_acionada": rule,
    }

"""Classificação do perfil pedagógico. RESPONSÁVEL: papel 2 (IA e match).

CONTRATO:  classify(perfil: dict) -> {"label": "Prático", "probs": {"Prático": 0.62, ...}}

Versão do kit: usa REGRAS simples (pontos por resposta), a mesma ideia que vai gerar os rótulos
do dataset sintético. Assim o app funciona antes de a rede neural ficar pronta.

TODO (papel 2 - IA): carregar models/perfil_model.joblib (MLPClassifier treinado em train.py)
e usar predict_proba. Se o arquivo do modelo não existir, manter o fallback por regras abaixo.
"""
from pergamo import constants as C


def pontuar_por_regras(perfil: dict) -> dict:
    """Pontos de cada tipo de perfil a partir das respostas (exemplo de regras, ajustem juntos)."""
    pontos = {tipo: 0.0 for tipo in C.TIPOS_PERFIL}
    for estilo in perfil.get("estilos", []):
        tipo = C.ESTILO_PARA_TIPO.get(estilo)
        if tipo:
            pontos[tipo] += 3
    for tipo in C.METODO_PARA_TIPOS.get(perfil.get("metodo"), []):
        pontos[tipo] += 2
    if perfil.get("ritmo") == "rapido":
        pontos["Prático"] += 1
    if perfil.get("social") == "debate":
        pontos["Ouvinte"] += 1
    if perfil.get("estrutura") == "estruturada":
        pontos["Leitor"] += 1
    if perfil.get("social") == "individual":
        pontos["Racional"] += 1
    return pontos


def classify(perfil: dict) -> dict:
    """Devolve o tipo de perfil mais provável e a probabilidade de cada tipo (soma ~1)."""
    pontos = pontuar_por_regras(perfil)
    suavizacao = 0.5  # evita probabilidade zero
    total = sum(pontos.values()) + suavizacao * len(pontos)
    probs = {tipo: round((p + suavizacao) / total, 4) for tipo, p in pontos.items()}
    label = max(probs, key=probs.get)
    return {"label": label, "probs": probs}

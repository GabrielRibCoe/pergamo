"""Classificação do perfil pedagógico. RESPONSÁVEL: papel 2 (IA e match).

CONTRATO:  classify(perfil: dict) -> {"label": "Prático", "probs": {"Prático": 0.62, ...}}

Dois motores, nesta ordem:
  1. REDE NEURAL: se existir models/perfil_model.joblib (criado por `python -m pergamo.ml.train`).
  2. REGRAS: reserva simples (pontos por resposta). Também gera os rótulos do dataset sintético.
Assim o app nunca quebra, mesmo sem o modelo treinado.

Para ver qual motor está em uso:  python -m pergamo.ml.classifier
"""
from functools import lru_cache

from pergamo import constants as C
from pergamo.config import MODELS_DIR

CAMINHO_MODELO = MODELS_DIR / "perfil_model.joblib"


# ----------------------------------------------------------------------------- motor 2: regras
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


def _classificar_por_regras(perfil: dict) -> dict:
    pontos = pontuar_por_regras(perfil)
    suavizacao = 0.5  # evita probabilidade zero
    total = sum(pontos.values()) + suavizacao * len(pontos)
    probs = {tipo: round((p + suavizacao) / total, 4) for tipo, p in pontos.items()}
    return {"label": max(probs, key=probs.get), "probs": probs}


# ----------------------------------------------------------------------------- motor 1: rede neural
@lru_cache(maxsize=1)
def _carregar_modelo():
    """Carrega o modelo uma única vez. Devolve None se o arquivo não existir ou der erro."""
    if not CAMINHO_MODELO.exists():
        return None
    try:
        import joblib

        return joblib.load(CAMINHO_MODELO)
    except Exception:
        return None


def recarregar_modelo():
    """Esquece o modelo guardado (use depois de treinar de novo, ou nos testes)."""
    _carregar_modelo.cache_clear()


def modelo_carregado() -> bool:
    return _carregar_modelo() is not None


def _classificar_com_rede(pacote: dict, perfil: dict) -> dict:
    from pergamo.ml.features import perfil_para_vetor

    modelo = pacote["modelo"]
    # predict_proba devolve a probabilidade de cada tipo (soma 1), na ordem de modelo.classes_
    probabilidades = modelo.predict_proba([perfil_para_vetor(perfil)])[0]
    probs = {str(tipo): round(float(p), 4) for tipo, p in zip(modelo.classes_, probabilidades)}
    return {"label": max(probs, key=probs.get), "probs": probs}


# ----------------------------------------------------------------------------- contrato
def classify(perfil: dict) -> dict:
    """Devolve o tipo de perfil mais provável e a probabilidade de cada tipo (soma ~1)."""
    pacote = _carregar_modelo()
    if pacote is not None:
        try:
            return _classificar_com_rede(pacote, perfil)
        except Exception:
            pass  # qualquer problema com o modelo: usa as regras
    return _classificar_por_regras(perfil)


if __name__ == "__main__":
    exemplo = {"estilos": ["pratico", "visual"], "ritmo": "rapido", "estrutura": "flexivel", "social": "individual"}
    print("Motor em uso:", "rede neural" if modelo_carregado() else "regras (modelo não treinado)")
    print("Exemplo:", exemplo)
    print("Resultado:", classify(exemplo))

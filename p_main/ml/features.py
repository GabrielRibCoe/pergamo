"""Transforma o perfil (dicionário) em NÚMEROS, que é o que a rede neural entende.
RESPONSÁVEL: papel 2 (IA e match).

Cada resposta vira uma coluna com 0 ou 1:
    estilos  -> 5 colunas (uma por estilo; marca 1 em cada estilo escolhido)   "multi-hot"
    método   -> 4 colunas (só um vale 1; todas 0 para alunos, que não têm método) "one-hot"
    ritmo    -> 1 coluna  (1 = rápido, 0 = gradual)
    estrutura-> 1 coluna  (1 = estruturada, 0 = flexível)
    social   -> 1 coluna  (1 = debate, 0 = individual)
Total: 12 colunas. A ORDEM de FEATURE_NAMES importa: treino e uso precisam da mesma ordem.
"""
from pergamo import constants as C

FEATURE_NAMES = (
    [f"estilo_{e}" for e in C.ESTILOS]
    + [f"metodo_{m}" for m in C.METODOS]
    + ["ritmo_rapido", "estrutura_estruturada", "social_debate"]
)


def perfil_para_vetor(perfil: dict) -> list[float]:
    """Ex.: {"estilos": ["pratico"], "ritmo": "rapido", ...} -> [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0]"""
    estilos = set(perfil.get("estilos", []))
    vetor = [1.0 if e in estilos else 0.0 for e in C.ESTILOS]
    vetor += [1.0 if perfil.get("metodo") == m else 0.0 for m in C.METODOS]
    vetor.append(1.0 if perfil.get("ritmo") == "rapido" else 0.0)
    vetor.append(1.0 if perfil.get("estrutura") == "estruturada" else 0.0)
    vetor.append(1.0 if perfil.get("social") == "debate" else 0.0)
    return vetor

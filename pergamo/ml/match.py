"""Nota de compatibilidade entre aluno e professor. RESPONSÁVEL: papel 2 (IA e match).

CONTRATO:  compatibility(aluno: dict, professor: dict) -> {"score": 0.87, "reasons": [...]}
           (score entre 0 e 1; reasons são frases curtas para a tela "Por que combina")

Fórmula do roteiro (seção 7.4):
    nota = 0,60 x similaridade do cosseno entre as probabilidades de perfil
         + 0,25 x cobertura de matérias (matérias do aluno que o professor ensina)
         + 0,15 x encaixe de estilo (ritmo, estrutura e social que coincidem)
TODO (papel 2 - IA): ajustar pesos e motivos; rank_professors() é usado pela tela de match.
"""
import math

from pergamo import constants as C
from pergamo.ml.classifier import classify


def _cosseno(a: dict, b: dict) -> float:
    chaves = C.TIPOS_PERFIL
    va = [a.get(k, 0.0) for k in chaves]
    vb = [b.get(k, 0.0) for k in chaves]
    produto = sum(x * y for x, y in zip(va, vb))
    norma = math.sqrt(sum(x * x for x in va)) * math.sqrt(sum(y * y for y in vb))
    return produto / norma if norma else 0.0


def _probs(perfil: dict) -> dict:
    return perfil.get("perfil_probs") or classify(perfil)["probs"]


def _label(perfil: dict) -> str:
    return perfil.get("perfil_label") or classify(perfil)["label"]


def compatibility(aluno: dict, professor: dict) -> dict:
    cos = _cosseno(_probs(aluno), _probs(professor))

    materias_aluno = set(aluno.get("materias", []))
    em_comum = sorted(materias_aluno & set(professor.get("materias", [])))
    cobertura = len(em_comum) / len(materias_aluno) if materias_aluno else 0.0

    coincidencias = [c for c in ("ritmo", "estrutura", "social") if aluno.get(c) and aluno.get(c) == professor.get(c)]
    encaixe = len(coincidencias) / 3

    score = round(0.60 * cos + 0.25 * cobertura + 0.15 * encaixe, 4)

    motivos = []
    if _label(aluno) == _label(professor):
        motivos.append(f"Ambos com perfil {_label(aluno)}")
    if em_comum:
        motivos.append("Matérias em comum: " + ", ".join(em_comum))
    nomes = {"ritmo": C.RITMOS, "estrutura": C.ESTRUTURAS, "social": C.SOCIAIS}
    for campo in coincidencias:
        motivos.append(nomes[campo][aluno[campo]])
    return {"score": score, "reasons": motivos}


def rank_professors(perfil_aluno: dict, professores: list[dict]) -> list[dict]:
    """Ordena os professores (itens de repo.list_professors) pela compatibilidade, do maior ao menor.

    Só entram professores que ensinam pelo menos uma matéria do aluno.
    Cada item: {"professor": {...}, "score": 0.87, "reasons": [...]}
    """
    materias_aluno = set(perfil_aluno.get("materias", []))
    itens = []
    for prof in professores:
        if materias_aluno and not (materias_aluno & set(prof["perfil"].get("materias", []))):
            continue
        resultado = compatibility(perfil_aluno, prof["perfil"])
        itens.append({"professor": prof, **resultado})
    return sorted(itens, key=lambda item: item["score"], reverse=True)

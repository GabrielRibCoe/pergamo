"""Gera o dataset SINTÉTICO de perfis (não temos dados reais, então inventamos perfis).
RESPONSÁVEL: papel 2 (IA e match).

Como funciona:
  1. Sorteia respostas aleatórias (estilos, ritmo, estrutura, social e, às vezes, método).
  2. Define o "tipo de perfil" correto de cada um pelas REGRAS de pontos (classifier.pontuar_por_regras).
  3. Troca uma parte dos rótulos por outro aleatório (RUÍDO), para simular a bagunça do mundo real.
  4. Salva tudo em data/perfis_sinteticos.csv (colunas numéricas + tipo + tipo_sem_ruido).

Uso:  python -m pergamo.ml.dataset
"""
import random

import pandas as pd

from pergamo import constants as C
from pergamo.config import DATA_DIR
from pergamo.ml.classifier import pontuar_por_regras
from pergamo.ml.features import FEATURE_NAMES, perfil_para_vetor

CAMINHO_CSV = DATA_DIR / "perfis_sinteticos.csv"


def sortear_perfil(rng: random.Random) -> dict:
    """Um perfil aleatório. Metade dos perfis tem método (como os professores)."""
    quantos = rng.choices([1, 2, 3], weights=[50, 35, 15])[0]
    return {
        "estilos": rng.sample(list(C.ESTILOS), quantos),
        "ritmo": rng.choice(list(C.RITMOS)),
        "estrutura": rng.choice(list(C.ESTRUTURAS)),
        "social": rng.choice(list(C.SOCIAIS)),
        "metodo": rng.choice(list(C.METODOS)) if rng.random() < 0.5 else None,
    }


def rotulo_por_regras(perfil: dict) -> str:
    """Tipo com mais pontos. Empate: vale o primeiro da lista C.TIPOS_PERFIL (regra fixa)."""
    pontos = pontuar_por_regras(perfil)
    return max(C.TIPOS_PERFIL, key=lambda tipo: pontos[tipo])


def gerar_perfis(n: int = 5000, ruido: float = 0.10, semente: int = 42) -> pd.DataFrame:
    """Devolve um DataFrame com n perfis. ruido = fração dos rótulos trocada ao acaso (0 a 1)."""
    rng = random.Random(semente)
    linhas = []
    for _ in range(n):
        perfil = sortear_perfil(rng)
        correto = rotulo_por_regras(perfil)
        tipo = correto
        if rng.random() < ruido:  # ruído: troca por OUTRO tipo
            tipo = rng.choice([t for t in C.TIPOS_PERFIL if t != correto])
        linhas.append(dict(zip(FEATURE_NAMES, perfil_para_vetor(perfil))) | {"tipo": tipo, "tipo_sem_ruido": correto})
    return pd.DataFrame(linhas)


def salvar_csv(df: pd.DataFrame, caminho=CAMINHO_CSV):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False)


if __name__ == "__main__":
    df = gerar_perfis()
    salvar_csv(df)
    print(f"{len(df)} perfis salvos em {CAMINHO_CSV}")
    print("\nQuantos perfis de cada tipo:")
    print(df["tipo"].value_counts().to_string())

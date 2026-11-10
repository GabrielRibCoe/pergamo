"""Treina a rede neural e salva o modelo em models/perfil_model.joblib.
RESPONSÁVEL: papel 2 (IA e match).

A rede é um MLPClassifier (Multi-Layer Perceptron) do scikit-learn:
    12 números de entrada -> camada escondida 1 -> camada escondida 2 -> 5 saídas (uma por tipo de perfil)

Uso básico:        python -m pergamo.ml.train
Para experimentar: python -m pergamo.ml.train --camadas 32 16 --ruido 0.2 --amostras 5000 --sem-salvar
"""
import argparse
import json

import joblib
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from pergamo.config import MODELS_DIR
from pergamo.ml.dataset import gerar_perfis, salvar_csv
from pergamo.ml.features import FEATURE_NAMES

CAMINHO_MODELO = MODELS_DIR / "perfil_model.joblib"
CAMINHO_METRICAS = MODELS_DIR / "metricas.json"


def treinar(n_amostras=5000, ruido=0.10, camadas=(16, 8), max_iter=2000, semente=42, salvar=True) -> dict:
    # 1) dados: perfis sintéticos (colunas numéricas) e o tipo de cada um
    df = gerar_perfis(n_amostras, ruido, semente)
    if salvar:
        salvar_csv(df)
    X = df[FEATURE_NAMES].to_numpy()
    y = df["tipo"].to_numpy()
    y_limpo = df["tipo_sem_ruido"].to_numpy()

    # 2) separa 80% para treinar e 20% para testar (a rede NUNCA vê o teste durante o treino)
    X_tr, X_te, y_tr, y_te, _, y_te_limpo = train_test_split(
        X, y, y_limpo, test_size=0.2, random_state=semente, stratify=y
    )

    # 3) cria e treina a rede
    modelo = MLPClassifier(hidden_layer_sizes=tuple(camadas), activation="relu",
                           max_iter=max_iter, random_state=semente)
    modelo.fit(X_tr, y_tr)

    # 4) mede o resultado no teste
    previsto = modelo.predict(X_te)
    metricas = {
        "amostras": int(n_amostras),
        "ruido": ruido,
        "camadas_escondidas": list(camadas),
        "iteracoes_usadas": int(modelo.n_iter_),
        "acuracia_treino": round(float(accuracy_score(y_tr, modelo.predict(X_tr))), 4),
        "acuracia_teste": round(float(accuracy_score(y_te, previsto)), 4),
        "acuracia_teste_sem_ruido": round(float(accuracy_score(y_te_limpo, previsto)), 4),
        # confiança média = média da MAIOR probabilidade que a rede dá em cada exemplo de teste
        "confianca_media": round(float(np.mean(modelo.predict_proba(X_te).max(axis=1))), 4),
    }

    # 5) salva o modelo e as métricas (as métricas vão para o pôster)
    if salvar:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({"modelo": modelo, "classes": [str(c) for c in modelo.classes_],
                     "features": FEATURE_NAMES, "metricas": metricas}, CAMINHO_MODELO)
        CAMINHO_METRICAS.write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")
    return metricas


def _imprimir(m: dict):
    print("Resultado do treino")
    print(f"  amostras ................ {m['amostras']} (ruído de {m['ruido']:.0%} nos rótulos)")
    print(f"  camadas escondidas ...... {m['camadas_escondidas']}")
    print(f"  iterações usadas ........ {m['iteracoes_usadas']}")
    print(f"  acurácia no treino ...... {m['acuracia_treino']:.1%}")
    print(f"  acurácia no teste ....... {m['acuracia_teste']:.1%}   (rótulos com ruído)")
    print(f"  acurácia sem ruído ...... {m['acuracia_teste_sem_ruido']:.1%}   (o quanto a rede aprendeu as regras)")
    print(f"  confiança média ......... {m['confianca_media']:.1%}   (quão 'segura' a rede costuma ser)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Treina a rede neural de perfis da Pérgamo.")
    ap.add_argument("--amostras", type=int, default=5000)
    ap.add_argument("--ruido", type=float, default=0.10)
    ap.add_argument("--camadas", type=int, nargs="+", default=[16, 8])
    ap.add_argument("--max-iter", type=int, default=2000)
    ap.add_argument("--semente", type=int, default=42)
    ap.add_argument("--sem-salvar", action="store_true", help="só mostra o resultado, não grava arquivos")
    a = ap.parse_args()
    resultado = treinar(a.amostras, a.ruido, a.camadas, a.max_iter, a.semente, salvar=not a.sem_salvar)
    _imprimir(resultado)
    if not a.sem_salvar:
        print(f"\nModelo salvo em {CAMINHO_MODELO}")

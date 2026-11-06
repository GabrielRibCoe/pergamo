"""Testes da parte de IA (papel 2): features, dataset, treino e classificador."""
import pytest

from pergamo import constants as C
from pergamo.ml import classifier
from pergamo.ml.dataset import gerar_perfis
from pergamo.ml.features import FEATURE_NAMES, perfil_para_vetor
from pergamo.ml.train import treinar


def test_vetor_tem_12_colunas_e_marca_as_respostas():
    perfil = {"estilos": ["pratico", "visual"], "ritmo": "rapido", "estrutura": "flexivel", "social": "individual"}
    vetor = perfil_para_vetor(perfil)
    assert len(vetor) == len(FEATURE_NAMES) == 12
    marcadas = {nome for nome, v in zip(FEATURE_NAMES, vetor) if v == 1.0}
    assert marcadas == {"estilo_pratico", "estilo_visual", "ritmo_rapido"}


def test_dataset_tem_colunas_e_rotulos_validos():
    df = gerar_perfis(300, ruido=0.1, semente=1)
    assert len(df) == 300
    assert set(FEATURE_NAMES) <= set(df.columns)
    assert set(df["tipo"]) <= set(C.TIPOS_PERFIL)


def test_dataset_sem_ruido_tem_rotulos_iguais_aos_das_regras():
    df = gerar_perfis(300, ruido=0.0, semente=1)
    assert (df["tipo"] == df["tipo_sem_ruido"]).all()


def test_dataset_e_reproduzivel_com_a_mesma_semente():
    a, b = gerar_perfis(200, semente=5), gerar_perfis(200, semente=5)
    assert a.equals(b)


def test_rede_aprende_as_regras():
    metricas = treinar(n_amostras=2000, salvar=False)  # não grava arquivos
    assert metricas["acuracia_teste_sem_ruido"] > 0.85


@pytest.fixture
def sem_modelo(monkeypatch, tmp_path):
    """Faz o classificador acreditar que o modelo não existe (cai para as regras)."""
    monkeypatch.setattr(classifier, "CAMINHO_MODELO", tmp_path / "nao-existe.joblib")
    classifier.recarregar_modelo()
    yield
    classifier.recarregar_modelo()


def test_classify_sem_modelo_usa_regras(sem_modelo):
    assert not classifier.modelo_carregado()
    r = classifier.classify({"estilos": ["auditivo"], "social": "debate"})
    assert r["label"] == "Ouvinte"
    assert abs(sum(r["probs"].values()) - 1) < 0.01


def test_classify_com_o_modelo_do_repositorio():
    classifier.recarregar_modelo()
    if not classifier.modelo_carregado():
        pytest.skip("models/perfil_model.joblib ainda não foi treinado")
    r = classifier.classify({"estilos": ["auditivo"], "ritmo": "gradual", "estrutura": "flexivel", "social": "debate"})
    assert r["label"] == "Ouvinte"
    assert set(r["probs"]) == set(C.TIPOS_PERFIL)
    assert abs(sum(r["probs"].values()) - 1) < 0.01

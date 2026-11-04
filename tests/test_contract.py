"""Testes do contrato (kit do dia 0).

Os testes de banco rodam contra QUALQUER implementação de Repo. Quando o SqliteRepo e o MongoRepo
ficarem prontos, o papel 1 (Dados) acrescenta a fábrica deles em FABRICAS e todos os testes passam
a validar também os novos bancos.
"""
import pytest

from pergamo import constants as C
from pergamo.auth import hash_password, verify_password
from pergamo.db.memory_repo import MemoryRepo
from pergamo.ml.classifier import classify
from pergamo.ml.match import compatibility, rank_professors

# nome -> função que devolve um repositório VAZIO
FABRICAS = {
    "memory": lambda: MemoryRepo(seed_path="nao-existe.json"),
    # "sqlite": lambda: SqliteRepo(":memory:"),   # papel 1 - Dados
    # "mongo": ...                                # papel 1 - Dados (use um banco de teste)
}


@pytest.fixture(params=list(FABRICAS))
def repo(request):
    return FABRICAS[request.param]()


PERFIL_ALUNO = {"materias": ["Matemática"], "estilos": ["pratico"], "ritmo": "gradual",
                "estrutura": "estruturada", "social": "individual"}
PERFIL_PROF = {"materias": ["Matemática", "Física"], "estilos": ["pratico"], "ritmo": "gradual",
               "estrutura": "estruturada", "social": "individual", "metodo": "pratica_guiada", "preco_hora": 50}


def _criar(repo, email, papel="aluno", nome="Fulano"):
    return repo.create_user(email, "hash", papel, nome)


# ----------------------------------------------------------------------------- contas
def test_criar_e_buscar_usuario(repo):
    uid = _criar(repo, "Ana@Teste.com")
    assert repo.get_user(uid)["email"] == "ana@teste.com"
    assert repo.get_user_by_email("ANA@teste.com")["id"] == uid
    assert repo.get_user("nao-existe") is None


def test_email_repetido_levanta_erro(repo):
    _criar(repo, "ana@teste.com")
    with pytest.raises(ValueError):
        _criar(repo, "ANA@teste.com")


# ----------------------------------------------------------------------------- perfil
def test_perfil_ida_e_volta(repo):
    uid = _criar(repo, "ana@teste.com")
    assert repo.get_profile(uid) is None
    repo.save_profile(uid, PERFIL_ALUNO)
    assert repo.get_profile(uid)["materias"] == ["Matemática"]


def test_lista_de_professores_so_com_perfil(repo):
    com_perfil = _criar(repo, "p1@teste.com", "professor", "Prof Um")
    _criar(repo, "p2@teste.com", "professor", "Prof Dois")  # sem perfil
    _criar(repo, "a1@teste.com", "aluno")
    repo.save_profile(com_perfil, PERFIL_PROF)
    lista = repo.list_professors()
    assert [p["id"] for p in lista] == [com_perfil]
    assert lista[0]["perfil"]["metodo"] == "pratica_guiada"


# ----------------------------------------------------------------------------- vínculos
def test_fluxo_de_vinculo(repo):
    aluno, prof = _criar(repo, "a@teste.com"), _criar(repo, "p@teste.com", "professor")
    assert repo.get_active_link(aluno) is None
    repo.create_link(aluno, prof)
    assert repo.get_active_link(aluno)["professor_id"] == prof
    assert [a["id"] for a in repo.get_roster(prof)] == [aluno]
    with pytest.raises(ValueError):  # plano gratuito: 1 professor por vez
        repo.create_link(aluno, prof)
    repo.end_link(aluno)
    assert repo.get_active_link(aluno) is None
    assert repo.get_roster(prof) == []
    repo.end_link(aluno)  # sem vínculo ativo: não faz nada
    repo.create_link(aluno, prof)  # pode vincular de novo depois de desvincular


# ----------------------------------------------------------------------------- senha
def test_senha_com_hash():
    h = hash_password("segredo", rounds=4)
    assert h != "segredo"
    assert verify_password("segredo", h)
    assert not verify_password("outra", h)


# ----------------------------------------------------------------------------- IA
def test_classify_devolve_probabilidades_validas():
    r = classify(PERFIL_ALUNO)
    assert r["label"] in C.TIPOS_PERFIL
    assert set(r["probs"]) == set(C.TIPOS_PERFIL)
    assert abs(sum(r["probs"].values()) - 1) < 0.01
    assert r["label"] == "Prático"


def test_compatibilidade_entre_0_e_1_e_ordenacao():
    igual = compatibility(PERFIL_ALUNO, PERFIL_PROF)
    outro = dict(PERFIL_PROF, estilos=["visual"], ritmo="rapido", estrutura="flexivel", social="debate")
    diferente = compatibility(PERFIL_ALUNO, outro)
    assert 0 <= diferente["score"] <= igual["score"] <= 1
    assert igual["reasons"]


def test_ranking_ignora_professor_sem_materia_em_comum():
    prof_a = {"id": "1", "nome": "A", "perfil": PERFIL_PROF}
    prof_b = {"id": "2", "nome": "B", "perfil": dict(PERFIL_PROF, materias=["Artes"])}
    ranking = rank_professors(PERFIL_ALUNO, [prof_b, prof_a])
    assert [item["professor"]["id"] for item in ranking] == ["1"]


# ----------------------------------------------------------------------------- seed do kit
def test_seed_do_kit_tem_as_personas():
    repo = MemoryRepo()
    miguel = repo.get_user_by_email("miguel@pergamo.test")
    renato = repo.get_user_by_email("renato@pergamo.test")
    assert miguel["papel"] == "aluno" and renato["papel"] == "professor"
    assert repo.get_active_link(miguel["id"]) is None  # Miguel começa sem vínculo (vai para o match)
    assert len(repo.get_roster(renato["id"])) >= 1  # Renato já tem alunos na turma
    assert verify_password(C.SENHA_TESTE, miguel["senha_hash"])

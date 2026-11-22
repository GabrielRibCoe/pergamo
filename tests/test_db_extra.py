"""Testes extras do banco: persistência do SQLite, seed, reserva automática e limpeza."""
from pergamo import config
from pergamo.auth import verify_password
from pergamo.db import criar_repo
from pergamo.db.seed import carregar_seed
from pergamo.db.sqlite_repo import SqliteRepo


def test_sqlite_guarda_os_dados_em_arquivo(tmp_path):
    arquivo = str(tmp_path / "pergamo.db")
    primeiro = SqliteRepo(arquivo)
    uid = primeiro.create_user("ana@pergamo.test", "hash", "aluno", "Ana")
    primeiro.save_profile(uid, {"materias": ["Matemática"], "perfil_label": "Prático"})

    segundo = SqliteRepo(arquivo)  # "reiniciou o app": abre o mesmo arquivo
    assert segundo.get_user_by_email("ANA@pergamo.test")["id"] == uid
    assert segundo.get_profile(uid)["perfil_label"] == "Prático"


def test_seed_cria_as_contas_e_nao_duplica():
    repo = SqliteRepo(":memory:")
    assert repo.vazio()
    primeiro = carregar_seed(repo)
    assert primeiro["contas_criadas"] == 32 and primeiro["vinculos_criados"] == 15
    assert len(repo.list_professors()) == 12

    miguel, renato = repo.get_user_by_email("miguel@pergamo.test"), repo.get_user_by_email("renato@pergamo.test")
    assert verify_password("123456", miguel["senha_hash"])  # dá para logar com a senha de teste
    assert repo.get_active_link(miguel["id"]) is None
    assert len(repo.get_roster(renato["id"])) == 4
    assert repo.get_profile(miguel["id"])["perfil_label"]  # a IA já classificou

    segundo = carregar_seed(repo)  # rodar de novo não duplica nada
    assert segundo == {"contas_criadas": 0, "vinculos_criados": 0}


def test_seed_nao_recria_vinculo_desfeito_pelo_usuario():
    repo = SqliteRepo(":memory:")
    carregar_seed(repo)
    renato = repo.get_user_by_email("renato@pergamo.test")
    aluno = repo.get_roster(renato["id"])[0]
    repo.end_link(aluno["id"])
    carregar_seed(repo)
    assert repo.get_active_link(aluno["id"]) is None


def test_limpar_apaga_tudo():
    repo = SqliteRepo(":memory:")
    carregar_seed(repo)
    repo.limpar()
    assert repo.vazio() and repo.list_professors() == []


def test_fabrica_sqlite_carrega_o_seed_na_primeira_vez(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_MODE", "sqlite")
    monkeypatch.setattr(config, "SQLITE_PATH", str(tmp_path / "x.db"))
    repo = criar_repo()
    assert repo.modo == "sqlite" and repo.aviso is None
    assert repo.get_user_by_email("miguel@pergamo.test")


def test_mongo_sem_uri_cai_para_o_sqlite_com_aviso(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_MODE", "mongo")
    monkeypatch.setattr(config, "MONGO_URI", "")
    monkeypatch.setattr(config, "SQLITE_PATH", str(tmp_path / "reserva.db"))
    repo = criar_repo()
    assert repo.modo == "sqlite"
    assert "MongoDB" in repo.aviso
    assert repo.get_user_by_email("renato@pergamo.test")  # o app continua funcionando


def test_modo_memory_e_o_padrao_dos_testes():
    repo = criar_repo("memory")
    assert repo.modo == "memory" and repo.aviso is None

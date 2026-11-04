"""Banco OFFLINE em SQLite. RESPONSÁVEL: papel 1 (Dados e infraestrutura).

Implementar todos os métodos de pergamo.db.base.Repo guardando em um arquivo .db.
Tabelas sugeridas (roteiro, seção 6.2): users, profiles, links.
Dica: guardar o perfil como JSON em uma coluna de texto (json.dumps / json.loads).
Dica: o tipo de "perfil" é um dicionário; o contrato está em base.py e o comportamento de
referência está em memory_repo.py (rode os testes de tests/test_contract.py contra a sua classe).
"""
from pergamo.db.base import Repo

_MSG = "TODO (papel 1 - Dados): implementar SqliteRepo."


class SqliteRepo(Repo):
    def __init__(self, caminho: str):
        raise NotImplementedError(_MSG)

    def create_user(self, email, password_hash, role, name):
        raise NotImplementedError(_MSG)

    def get_user_by_email(self, email):
        raise NotImplementedError(_MSG)

    def get_user(self, user_id):
        raise NotImplementedError(_MSG)

    def save_profile(self, user_id, profile):
        raise NotImplementedError(_MSG)

    def get_profile(self, user_id):
        raise NotImplementedError(_MSG)

    def list_professors(self):
        raise NotImplementedError(_MSG)

    def create_link(self, student_id, teacher_id):
        raise NotImplementedError(_MSG)

    def end_link(self, student_id):
        raise NotImplementedError(_MSG)

    def get_active_link(self, student_id):
        raise NotImplementedError(_MSG)

    def get_roster(self, teacher_id):
        raise NotImplementedError(_MSG)

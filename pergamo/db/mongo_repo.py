"""Banco ONLINE em MongoDB Atlas. RESPONSÁVEL: papel 1 (Dados e infraestrutura).

Implementar todos os métodos de pergamo.db.base.Repo usando pymongo.
A URI vem de config.MONGO_URI (variável PERGAMO_MONGO_URI no .env). NUNCA coloque a URI no código.
Coleções sugeridas: users, profiles, links. Crie um índice único no e-mail.
Se a URI for mongodb+srv e der erro de DNS, instale também o pacote dnspython.
"""
from pergamo.db.base import Repo

_MSG = "TODO (papel 1 - Dados): implementar MongoRepo."


class MongoRepo(Repo):
    def __init__(self, uri: str, nome_banco: str = "pergamo"):
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

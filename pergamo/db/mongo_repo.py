"""Banco ONLINE em MongoDB Atlas. RESPONSÁVEL: papel 1 (Dados e infraestrutura).

Implementa o contrato pergamo.db.base.Repo com pymongo. Coleções: users, profiles e links.
A URI vem de config.MONGO_URI (variável PERGAMO_MONGO_URI no .env). NUNCA coloque a URI no código.
Se a URI for mongodb+srv e der erro de DNS, instale também o pacote dnspython.

Regras garantidas pelo banco (índices): e-mail único e no máximo um vínculo ativo por aluno.
"""
from datetime import datetime
import uuid

from pymongo.errors import DuplicateKeyError

from pergamo import constants as C
from pergamo.db.base import Repo


def _agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _novo_id(prefixo: str) -> str:
    return f"{prefixo}{uuid.uuid4().hex[:12]}"


def _usuario(doc: dict) -> dict:
    """Documento do Mongo -> dicionário do contrato (o _id vira id)."""
    return {"id": doc["_id"], "nome": doc["nome"], "email": doc["email"],
            "senha_hash": doc["senha_hash"], "papel": doc["papel"], "criado_em": doc["criado_em"]}


class MongoRepo(Repo):
    def __init__(self, uri: str = "mongodb+srv://gabribcoelho_db_user:yz00I0O5LJ94EODK@alunoseprofessores.kbugm6v.mongodb.net/", nome_banco: str = "pergamo", client=None):
        """client só é usado nos testes (um MongoClient falso). No app, passe a URI."""
        if client is None:
            if not uri:
                raise ValueError("PERGAMO_MONGO_URI está vazio: preencha a URI do Atlas no arquivo .env")
            from pymongo import MongoClient

            client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # desiste em 5 s se não conectar
            client.admin.command("ping")  # falha logo aqui (e não no primeiro clique) se a conexão estiver errada
        self._client = client
        db = client[nome_banco]
        self._users, self._profiles, self._links = db["users"], db["profiles"], db["links"]
        self._garantir_indices()

    def _garantir_indices(self):
        self._users.create_index("email", unique=True)
        self._links.create_index([("aluno_id", 1)], unique=True, partialFilterExpression={"status": "ativo"})
        self._links.create_index([("professor_id", 1), ("status", 1)])

    def vazio(self) -> bool:
        return self._users.count_documents({}) == 0

    def limpar(self):
        """Apaga TUDO (contas, perfis e vínculos). Use só para reiniciar a demonstração."""
        for colecao in (self._links, self._profiles, self._users):
            colecao.delete_many({})

    # ------------------------------------------------------------------ contas
    def create_user(self, email, password_hash, role, name):
        user_id = _novo_id("u")
        try:
            self._users.insert_one({"_id": user_id, "nome": name, "email": email.strip().lower(),
                                    "senha_hash": password_hash, "papel": role, "criado_em": _agora()})
        except DuplicateKeyError as erro:
            raise ValueError("email_ja_cadastrado") from erro
        return user_id

    def get_user_by_email(self, email):
        doc = self._users.find_one({"email": email.strip().lower()})
        return _usuario(doc) if doc else None

    def get_user(self, user_id):
        doc = self._users.find_one({"_id": user_id})
        return _usuario(doc) if doc else None

    # ------------------------------------------------------------------ perfil
    def save_profile(self, user_id, profile):
        self._profiles.replace_one({"_id": user_id}, {"_id": user_id, "perfil": dict(profile)}, upsert=True)

    def get_profile(self, user_id):
        doc = self._profiles.find_one({"_id": user_id})
        return doc["perfil"] if doc else None

    def list_professors(self):
        usuarios = list(self._users.find({"papel": C.PAPEL_PROFESSOR}).sort("criado_em", 1))
        perfis = {p["_id"]: p["perfil"] for p in self._profiles.find({"_id": {"$in": [u["_id"] for u in usuarios]}})}
        return [{"id": u["_id"], "nome": u["nome"], "email": u["email"], "perfil": perfis[u["_id"]]}
                for u in usuarios if u["_id"] in perfis]

    # ------------------------------------------------------------------ vínculos
    def create_link(self, student_id, teacher_id):
        if self.get_active_link(student_id):
            raise ValueError("aluno_ja_vinculado")
        try:
            self._links.insert_one({"_id": _novo_id("l"), "aluno_id": student_id, "professor_id": teacher_id,
                                    "status": "ativo", "criado_em": _agora(), "encerrado_em": None})
        except DuplicateKeyError as erro:  # duas pessoas vincularam ao mesmo tempo
            raise ValueError("aluno_ja_vinculado") from erro

    def end_link(self, student_id):
        self._links.update_many({"aluno_id": student_id, "status": "ativo"},
                                {"$set": {"status": "encerrado", "encerrado_em": _agora()}})

    def get_active_link(self, student_id):
        doc = self._links.find_one({"aluno_id": student_id, "status": "ativo"})
        if not doc:
            return None
        return {"id": doc["_id"], "aluno_id": doc["aluno_id"], "professor_id": doc["professor_id"],
                "criado_em": doc["criado_em"]}

    def get_roster(self, teacher_id):
        vinculos = list(self._links.find({"professor_id": teacher_id, "status": "ativo"}).sort("criado_em", 1))
        ids = [v["aluno_id"] for v in vinculos]
        usuarios = {u["_id"]: u for u in self._users.find({"_id": {"$in": ids}})}
        perfis = {p["_id"]: p["perfil"] for p in self._profiles.find({"_id": {"$in": ids}})}
        return [{"id": i, "nome": usuarios[i]["nome"], "perfil_label": perfis.get(i, {}).get("perfil_label", "")}
                for i in ids if i in usuarios]

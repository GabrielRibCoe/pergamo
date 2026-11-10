"""Banco em memória (kit do dia 0).

Serve para desenvolver as telas e a IA sem depender do banco real. Lê data/seed_users.json
ao iniciar. Os dados somem quando o app é reiniciado. Dentro do app (get_repo) ele é um
objeto único por servidor, então duas abas do navegador enxergam os mesmos dados.
"""
import json
import threading
from datetime import datetime
from pathlib import Path

from pergamo import constants as C
from pergamo.auth import hash_password
from pergamo.config import DATA_DIR
from pergamo.db.base import Repo
from pergamo.ml.classifier import classify


def _agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


class MemoryRepo(Repo):
    def __init__(self, seed_path: Path | str | None = None):
        self._lock = threading.RLock()
        self._users: dict[str, dict] = {}
        self._profiles: dict[str, dict] = {}
        self._links: list[dict] = []
        self._seq = 0
        self._carregar_seed(Path(seed_path) if seed_path else DATA_DIR / "seed_users.json")

    # ------------------------------------------------------------------ utilitários
    def _novo_id(self, prefixo: str) -> str:
        self._seq += 1
        return f"{prefixo}{self._seq}"

    def _carregar_seed(self, caminho: Path):
        if not caminho.exists():
            return
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        # Todas as contas do seed usam a mesma senha de teste: um hash só (rounds baixos = rápido)
        senha_hash = hash_password(dados.get("senha_teste", C.SENHA_TESTE), rounds=4)
        for u in dados.get("usuarios", []):
            user_id = self.create_user(u["email"], senha_hash, u["papel"], u["nome"])
            perfil = dict(u["perfil"])
            if "perfil_label" not in perfil:
                resultado = classify(perfil)
                perfil["perfil_label"] = resultado["label"]
                perfil["perfil_probs"] = resultado["probs"]
            self.save_profile(user_id, perfil)
        for v in dados.get("vinculos", []):
            aluno = self.get_user_by_email(v["aluno"])
            professor = self.get_user_by_email(v["professor"])
            if aluno and professor:
                self.create_link(aluno["id"], professor["id"])

    # ------------------------------------------------------------------ contas
    def create_user(self, email, password_hash, role, name):
        with self._lock:
            if self.get_user_by_email(email):
                raise ValueError("email_ja_cadastrado")
            user_id = self._novo_id("u")
            self._users[user_id] = {
                "id": user_id,
                "nome": name,
                "email": email.strip().lower(),
                "senha_hash": password_hash,
                "papel": role,
                "criado_em": _agora(),
            }
            return user_id

    def get_user_by_email(self, email):
        email = email.strip().lower()
        with self._lock:
            for u in self._users.values():
                if u["email"] == email:
                    return dict(u)
        return None

    def get_user(self, user_id):
        with self._lock:
            u = self._users.get(user_id)
            return dict(u) if u else None

    # ------------------------------------------------------------------ perfil
    def save_profile(self, user_id, profile):
        with self._lock:
            self._profiles[user_id] = dict(profile)

    def get_profile(self, user_id):
        with self._lock:
            p = self._profiles.get(user_id)
            return dict(p) if p else None

    def list_professors(self):
        with self._lock:
            return [
                {"id": u["id"], "nome": u["nome"], "email": u["email"], "perfil": dict(self._profiles[u["id"]])}
                for u in self._users.values()
                if u["papel"] == C.PAPEL_PROFESSOR and u["id"] in self._profiles
            ]

    # ------------------------------------------------------------------ vínculos
    def create_link(self, student_id, teacher_id):
        with self._lock:
            if self.get_active_link(student_id):
                raise ValueError("aluno_ja_vinculado")
            self._links.append({
                "id": self._novo_id("l"),
                "aluno_id": student_id,
                "professor_id": teacher_id,
                "status": "ativo",
                "criado_em": _agora(),
                "encerrado_em": None,
            })

    def end_link(self, student_id):
        with self._lock:
            for v in self._links:
                if v["aluno_id"] == student_id and v["status"] == "ativo":
                    v["status"] = "encerrado"
                    v["encerrado_em"] = _agora()

    def get_active_link(self, student_id):
        with self._lock:
            for v in self._links:
                if v["aluno_id"] == student_id and v["status"] == "ativo":
                    return {k: v[k] for k in ("id", "aluno_id", "professor_id", "criado_em")}
        return None

    def get_roster(self, teacher_id):
        with self._lock:
            turma = []
            for v in self._links:
                if v["professor_id"] == teacher_id and v["status"] == "ativo":
                    aluno = self._users.get(v["aluno_id"])
                    perfil = self._profiles.get(v["aluno_id"], {})
                    if aluno:
                        turma.append({"id": aluno["id"], "nome": aluno["nome"], "perfil_label": perfil.get("perfil_label", "")})
            return turma

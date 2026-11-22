"""Banco OFFLINE em SQLite (um arquivo .db). RESPONSÁVEL: papel 1 (Dados e infraestrutura).

Implementa o contrato pergamo.db.base.Repo. Tabelas: users, profiles e links.
O perfil é guardado como JSON em uma coluna de texto (json.dumps / json.loads).
Uma regra do banco garante que cada aluno tenha no máximo UM vínculo ativo (índice único parcial).

Uso:  SqliteRepo("data/pergamo_local.db")   ou   SqliteRepo(":memory:")  (só na memória, para testes)
"""
import json
import sqlite3
import threading
import uuid
from datetime import datetime
from pathlib import Path

from pergamo import constants as C
from pergamo.db.base import Repo

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY,
    nome        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    senha_hash  TEXT NOT NULL,
    papel       TEXT NOT NULL,
    criado_em   TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS profiles (
    user_id  TEXT PRIMARY KEY,
    dados    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS links (
    id            TEXT PRIMARY KEY,
    aluno_id      TEXT NOT NULL,
    professor_id  TEXT NOT NULL,
    status        TEXT NOT NULL,
    criado_em     TEXT NOT NULL,
    encerrado_em  TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_links_aluno_ativo ON links(aluno_id) WHERE status = 'ativo';
CREATE INDEX IF NOT EXISTS ix_links_professor ON links(professor_id, status);
"""


def _agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _novo_id(prefixo: str) -> str:
    return f"{prefixo}{uuid.uuid4().hex[:12]}"


class SqliteRepo(Repo):
    def __init__(self, caminho: str = ":memory:"):
        if caminho != ":memory:":
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        # O Streamlit atende várias sessões em threads diferentes: uma conexão só, protegida por um lock.
        self._con = sqlite3.connect(caminho, check_same_thread=False)
        self._con.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        with self._lock, self._con:
            self._con.executescript(_ESQUEMA)

    # ------------------------------------------------------------------ utilitários
    def _ler(self, sql: str, params=()) -> list:
        with self._lock:
            return self._con.execute(sql, params).fetchall()

    def _escrever(self, sql: str, params=()):
        with self._lock, self._con:  # o "with self._con" confirma (commit) ou desfaz (rollback)
            self._con.execute(sql, params)

    def vazio(self) -> bool:
        """True se ainda não há nenhuma conta (usado para carregar o seed na primeira vez)."""
        return self._ler("SELECT COUNT(*) AS n FROM users")[0]["n"] == 0

    def limpar(self):
        """Apaga TUDO (contas, perfis e vínculos). Use só para reiniciar a demonstração."""
        with self._lock, self._con:
            for tabela in ("links", "profiles", "users"):
                self._con.execute(f"DELETE FROM {tabela}")

    # ------------------------------------------------------------------ contas
    def create_user(self, email, password_hash, role, name):
        user_id = _novo_id("u")
        try:
            self._escrever(
                "INSERT INTO users (id, nome, email, senha_hash, papel, criado_em) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, name, email.strip().lower(), password_hash, role, _agora()),
            )
        except sqlite3.IntegrityError as erro:
            if "UNIQUE" in str(erro):
                raise ValueError("email_ja_cadastrado") from erro
            raise
        return user_id

    def get_user_by_email(self, email):
        linhas = self._ler("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
        return dict(linhas[0]) if linhas else None

    def get_user(self, user_id):
        linhas = self._ler("SELECT * FROM users WHERE id = ?", (user_id,))
        return dict(linhas[0]) if linhas else None

    # ------------------------------------------------------------------ perfil
    def save_profile(self, user_id, profile):
        self._escrever(
            "INSERT INTO profiles (user_id, dados) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET dados = excluded.dados",
            (user_id, json.dumps(profile, ensure_ascii=False)),
        )

    def get_profile(self, user_id):
        linhas = self._ler("SELECT dados FROM profiles WHERE user_id = ?", (user_id,))
        return json.loads(linhas[0]["dados"]) if linhas else None

    def list_professors(self):
        linhas = self._ler(
            "SELECT u.id, u.nome, u.email, p.dados FROM users u JOIN profiles p ON p.user_id = u.id "
            "WHERE u.papel = ? ORDER BY u.criado_em, u.id",
            (C.PAPEL_PROFESSOR,),
        )
        return [{"id": r["id"], "nome": r["nome"], "email": r["email"], "perfil": json.loads(r["dados"])} for r in linhas]

    # ------------------------------------------------------------------ vínculos
    def create_link(self, student_id, teacher_id):
        if self.get_active_link(student_id):
            raise ValueError("aluno_ja_vinculado")
        try:
            self._escrever(
                "INSERT INTO links (id, aluno_id, professor_id, status, criado_em) VALUES (?, ?, ?, 'ativo', ?)",
                (_novo_id("l"), student_id, teacher_id, _agora()),
            )
        except sqlite3.IntegrityError as erro:  # duas pessoas vincularam ao mesmo tempo
            raise ValueError("aluno_ja_vinculado") from erro

    def end_link(self, student_id):
        self._escrever(
            "UPDATE links SET status = 'encerrado', encerrado_em = ? WHERE aluno_id = ? AND status = 'ativo'",
            (_agora(), student_id),
        )

    def get_active_link(self, student_id):
        linhas = self._ler(
            "SELECT id, aluno_id, professor_id, criado_em FROM links WHERE aluno_id = ? AND status = 'ativo'",
            (student_id,),
        )
        return dict(linhas[0]) if linhas else None

    def get_roster(self, teacher_id):
        linhas = self._ler(
            "SELECT u.id, u.nome, p.dados FROM links l JOIN users u ON u.id = l.aluno_id "
            "LEFT JOIN profiles p ON p.user_id = u.id "
            "WHERE l.professor_id = ? AND l.status = 'ativo' ORDER BY l.criado_em, l.id",
            (teacher_id,),
        )
        return [
            {"id": r["id"], "nome": r["nome"],
             "perfil_label": json.loads(r["dados"]).get("perfil_label", "") if r["dados"] else ""}
            for r in linhas
        ]

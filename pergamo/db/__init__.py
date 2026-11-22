"""Fábrica do banco. RESPONSÁVEL: papel 1 (Dados e infraestrutura).

PERGAMO_DB escolhe o banco: memory, sqlite ou mongo. Reserva automática (roteiro, seção 6.1):
    mongo  -> se não conectar, cai para sqlite
    sqlite -> se falhar, cai para a memória
O banco devolvido tem os atributos .modo (o que está realmente em uso) e .aviso (texto, se houve reserva).
"""
import streamlit as st

from pergamo import config


def criar_repo(modo: str | None = None):
    """Cria o banco pedido (padrão: config.DB_MODE), com reserva automática se algo falhar."""
    modo = (modo or config.DB_MODE).lower()
    avisos = []

    if modo == "mongo":
        try:
            from pergamo.db.mongo_repo import MongoRepo

            repo = MongoRepo(config.MONGO_URI, config.MONGO_DB_NAME)
            repo.modo, repo.aviso = "mongo", None
            return repo
        except Exception as erro:
            avisos.append(f"MongoDB indisponível ({type(erro).__name__}): usando o banco offline.")
            modo = "sqlite"

    if modo == "sqlite":
        try:
            from pergamo.db.sqlite_repo import SqliteRepo

            repo = SqliteRepo(config.SQLITE_PATH)
            if repo.vazio():  # primeira vez: já carrega as contas fictícias
                from pergamo.db.seed import carregar_seed

                carregar_seed(repo)
            repo.modo, repo.aviso = "sqlite", " ".join(avisos) or None
            return repo
        except Exception as erro:
            avisos.append(f"SQLite indisponível ({type(erro).__name__}): usando a memória.")

    from pergamo.db.memory_repo import MemoryRepo

    repo = MemoryRepo()
    repo.modo, repo.aviso = "memory", " ".join(avisos) or None
    return repo


@st.cache_resource
def get_repo():
    """Uma única instância por servidor (compartilhada entre as abas do navegador)."""
    return criar_repo()

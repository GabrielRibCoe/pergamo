"""Fábrica do banco: get_repo() devolve o banco escolhido em PERGAMO_DB (memory, sqlite ou mongo)."""
import streamlit as st

from pergamo import config


@st.cache_resource
def get_repo():
    """Uma única instância por servidor (compartilhada entre as abas do navegador).

    TODO (papel 1 - Dados): se mongo falhar ao conectar, cair automaticamente para sqlite
    e mostrar um aviso discreto (reserva para a Amostra, roteiro seção 6.1).
    """
    if config.DB_MODE == "mongo":
        from pergamo.db.mongo_repo import MongoRepo

        return MongoRepo(config.MONGO_URI, config.MONGO_DB_NAME)
    if config.DB_MODE == "sqlite":
        from pergamo.db.sqlite_repo import SqliteRepo

        return SqliteRepo(config.SQLITE_PATH)

    from pergamo.db.memory_repo import MemoryRepo

    return MemoryRepo()

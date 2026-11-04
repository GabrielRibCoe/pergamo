"""Estado da sessão e navegação entre telas (st.session_state).

CONTRATO: as chaves ficam em constants.py (SS_*). Toda tela muda de tela chamando ir_para().
"""
import streamlit as st

from pergamo import constants as C


def init():
    """Cria as chaves da sessão na primeira execução."""
    st.session_state.setdefault(C.SS_TELA, C.TELA_LOGIN)
    st.session_state.setdefault(C.SS_USER_ID, None)
    st.session_state.setdefault(C.SS_PAPEL, None)
    st.session_state.setdefault(C.SS_NOME, None)


def ir_para(tela: str):
    """Troca de tela e reexecuta o app imediatamente."""
    if tela not in C.TELAS:
        raise ValueError(f"Tela desconhecida: {tela}")
    st.session_state[C.SS_TELA] = tela
    st.rerun()


def entrar(usuario: dict):
    """Guarda na sessão quem fez login (usuario vem do repo.get_user_by_email)."""
    st.session_state[C.SS_USER_ID] = usuario["id"]
    st.session_state[C.SS_PAPEL] = usuario["papel"]
    st.session_state[C.SS_NOME] = usuario["nome"]


def sair():
    """Limpa a sessão e volta ao login."""
    for chave in (C.SS_USER_ID, C.SS_PAPEL, C.SS_NOME):
        st.session_state[chave] = None
    st.session_state[C.SS_TELA] = C.TELA_LOGIN
    st.rerun()


def usuario_logado(repo) -> dict | None:
    """Devolve o usuário logado (dicionário do banco) ou None."""
    user_id = st.session_state.get(C.SS_USER_ID)
    return repo.get_user(user_id) if user_id else None


def tela_inicial_do_usuario(repo, usuario: dict) -> str:
    """Regra de entrada: decide para onde o usuário vai depois do login ou do perfil.

    - sem perfil ............ -> perfil
    - aluno sem vínculo ..... -> match
    - aluno com vínculo ..... -> menu
    - professor com perfil .. -> menu
    """
    if repo.get_profile(usuario["id"]) is None:
        return C.TELA_PERFIL
    if usuario["papel"] == C.PAPEL_ALUNO and repo.get_active_link(usuario["id"]) is None:
        return C.TELA_MATCH
    return C.TELA_MENU

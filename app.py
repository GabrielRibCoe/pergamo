"""Ponto de entrada do app Pérgamo. Rodar com:  streamlit run app.py

RESPONSÁVEL: papel 3 (Telas de entrada e integração).
Cada tela é um arquivo em pergamo/ui/ com uma função render(repo). Para adicionar ou trocar
uma tela, edite o dicionário TELAS abaixo (e os nomes em pergamo/constants.py).
"""
import streamlit as st

from pergamo import config, state
from pergamo import constants as C
from pergamo.db import get_repo
from pergamo.ui import cadastro, login, match, menu, perfil

TELAS = {
    C.TELA_LOGIN: login.render,
    C.TELA_CADASTRO: cadastro.render,
    C.TELA_PERFIL: perfil.render,
    C.TELA_MATCH: match.render,
    C.TELA_MENU: menu.render,
}


def main():
    st.set_page_config(page_title="Pérgamo", page_icon="📜", layout="centered")
    state.init()
    repo = get_repo()

    with st.sidebar:
        st.markdown("### Pérgamo")
        usuario = state.usuario_logado(repo)
        if usuario:
            st.write(usuario["nome"])
            st.caption(C.PAPEIS[usuario["papel"]])
            if st.button("Sair", key="btn_sair"):
                state.sair()
        st.caption(f"Banco: {config.DB_MODE}")

    TELAS[st.session_state[C.SS_TELA]](repo)


main()

"""Tela de login. RESPONSÁVEL: papel 3 (Telas de entrada e integração)."""
import streamlit as st

from pergamo import constants as C
from pergamo import state
from pergamo.auth import verify_password
from pergamo.ui import components


def render(repo):
    components.titulo_da_pagina("Pérgamo", "Entre para encontrar o professor certo para o seu jeito de aprender.")

    with st.form("form_login"):
        email = st.text_input("E-mail", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        entrou = st.form_submit_button("Entrar")

    if entrou:
        usuario = repo.get_user_by_email(email)
        if usuario and verify_password(senha, usuario["senha_hash"]):
            state.entrar(usuario)
            state.ir_para(state.tela_inicial_do_usuario(repo, usuario))
        else:
            st.error("E-mail ou senha incorretos.")

    st.divider()
    if st.button("Criar conta", key="btn_ir_cadastro"):
        state.ir_para(C.TELA_CADASTRO)

    st.caption(f"Contas de teste: miguel@pergamo.test (aluno) e renato@pergamo.test (professor). Senha: {C.SENHA_TESTE}")

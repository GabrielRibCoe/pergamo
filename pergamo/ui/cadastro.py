"""Tela de criar conta. RESPONSÁVEL: papel 3 (Telas de entrada e integração)."""
import streamlit as st

from pergamo import constants as C
from pergamo import state
from pergamo.auth import hash_password
from pergamo.ui import components


def render(repo):
    components.logo("logo_horizontal", largura=210)
    st.title("Criar Conta na Pérgamo")
    st.caption("Use apenas dados fictícios neste mockup.")

    with st.form("form_cadastro"):
        nome = st.text_input("Nome completo", key="cad_nome")
        email = st.text_input("E-mail", key="cad_email")
        senha = st.text_input("Senha (mínimo de 6 caracteres)", type="password", key="cad_senha")
        papel = st.selectbox("Você é:", list(C.PAPEIS), format_func=C.PAPEIS.get, key="cad_papel")
        criou = st.form_submit_button("Criar conta", type="primary")

    if criou:
        email = email.strip().lower()
        if not nome.strip() or "@" not in email or len(senha) < 6:
            st.error("Preencha o nome, um e-mail válido e uma senha com pelo menos 6 caracteres.")
        else:
            try:
                repo.create_user(email, hash_password(senha), papel, nome.strip())
            except ValueError:  # o contrato do banco levanta ValueError se o e-mail já existe
                st.error("Já existe uma conta com esse e-mail.")
            except Exception as erro:
                st.error(f"Ocorreu um erro com o banco: {erro}")
            else:
                state.entrar(repo.get_user_by_email(email))
                state.ir_para(C.TELA_PERFIL)

    st.markdown("---")
    if st.button("Já tem uma conta? Volte para o Login", type="secondary", key="btn_voltar_login"):
        state.ir_para(C.TELA_LOGIN)

import streamlit as st
import bcrypt
from pergamo import constants as C
from pergamo.ui import components

def render(repo):
    components.logo("logo_horizontal", largura=210)
    st.title("Criar Conta na Pérgamo")
    
    with st.form("form_cadastro"):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        
        # O papel precisa bater com o que o banco espera
        papel = st.selectbox("Você é:", ["aluno", "professor"])
        
        btn_criar = st.form_submit_button("Criar Conta", type="primary")
        
    if btn_criar:
        if not nome or not email or not senha:
            st.error("Por favor, preencha todos os campos!")
        else:
            # Criptografando a senha conforme exigência do roteiro
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt)
            
            try:
                # Chama o contrato Repo para criar o usuário
                user_id = repo.create_user(email, senha_hash.decode('utf-8'), papel, nome)
                
                if user_id:
                    st.success("Conta criada com sucesso!")
                    # Salva os dados na sessão e manda para a tela de Perfil
                    st.session_state[C.SS_USER_ID] = user_id
                    st.session_state[C.SS_PAPEL] = papel
                    st.session_state[C.SS_TELA] = C.TELA_PERFIL
                    st.rerun()
                else:
                    st.error("Erro ao criar conta. Talvez o e-mail já esteja em uso.")
            
            except Exception as e:
                st.error(f"Ocorreu um erro com o banco: {e}")

    st.markdown("---")
    if st.button("Já tem uma conta? Volte para o Login", type="secondary"):
        st.session_state[C.SS_TELA] = C.TELA_LOGIN
        st.rerun()
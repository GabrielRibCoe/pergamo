import streamlit as st
import bcrypt
from pergamo import constants as C

def render(repo):
    st.title("Pérgamo")
    st.write("Entre para encontrar o professor certo para o seu jeito de aprender.")

    # Formulário de login
    with st.form("form_login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        
        btn_entrar = st.form_submit_button("Entrar", type="primary")

    if btn_entrar:
        if not email or not senha:
            st.error("Por favor, preencha e-mail e senha.")
        else:
            # 1. Busca o usuário no banco pelo e-mail
            user = repo.get_user_by_email(email)
            
            if user:
                # 2. Verifica se a senha bate com o hash salvo (segurança exigida no roteiro)
                senha_valida = bcrypt.checkpw(senha.encode('utf-8'), user['senha_hash'].encode('utf-8'))
                
                if senha_valida:
                    # Salva os dados básicos na sessão
                    st.session_state[C.SS_USER_ID] = user['id']
                    st.session_state[C.SS_PAPEL] = user['papel']
                    
                    # 3. Roteamento inteligente baseado no estado da conta
                    perfil = repo.get_profile(user['id'])
                    
                    if not perfil:
                        # Conta nova ou perfil incompleto
                        st.session_state[C.SS_TELA] = C.TELA_PERFIL
                    elif user['papel'] == 'professor':
                        # Professor com perfil vai direto para o menu (não passa pelo match)
                        st.session_state[C.SS_TELA] = C.TELA_MENU
                    else:
                        # É aluno com perfil. Precisa checar se já tem professor
                        link_ativo = repo.get_active_link(user['id'])
                        if link_ativo:
                            st.session_state[C.SS_TELA] = C.TELA_MENU
                        else:
                            st.session_state[C.SS_TELA] = C.TELA_MATCH
                            
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
            else:
                st.error("Usuário não encontrado.")

    st.markdown("---")
    if st.button("Criar conta", type="primary"):
        st.session_state[C.SS_TELA] = C.TELA_CADASTRO
        st.rerun()
    
    # Textinho de ajuda para testar o mockup
    st.caption("Contas de teste: miguel@pergamo.test (aluno) e renato@pergamo.test (professor). Senha: 123456")
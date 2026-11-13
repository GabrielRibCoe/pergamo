import streamlit as st
from pergamo import constants as C
from pergamo.ui import components
# Importando o contrato da Inteligência Artificial
from pergamo.ml.classifier import classify

def render(repo):
    components.logo("logo_horizontal", largura=210)
    st.title("Monte seu Perfil Pérgamo")
    
    # Pega o papel e o ID do usuário da sessão para saber o que mostrar
    user_id = st.session_state.get(C.SS_USER_ID)
    papel = st.session_state.get(C.SS_PAPEL)

    if not user_id:
        st.warning("Você precisa estar logado para ver esta página.")
        return

    st.write(f"Preencha suas preferências como **{papel.capitalize()}**:")

    with st.form("form_perfil"):
        # 1. Campos comuns para ambos (Aluno e Professor)
        components.secao("O que você quer ensinar ou aprender")
        materias = st.multiselect("Matérias de interesse", ["Matemática", "Física", "Química", "História", "Redação"])
        nivel = st.selectbox("Nível de escolaridade", ["fundamental", "medio", "vestibular", "superior"], format_func=components.rotulo)

        components.secao("Seu jeito de aprender e ensinar")
        estilos = st.multiselect("Estilo de aprendizagem/ensino", ["pratico", "visual", "ouvinte", "leitor", "racional"], format_func=components.rotulo)
        col1, col2, col3 = st.columns(3)
        with col1:
            ritmo = st.selectbox("Ritmo ideal", ["gradual", "rapido"], format_func=components.rotulo)
        with col2:
            estrutura = st.selectbox("Estrutura das aulas", ["estruturada", "flexivel"], format_func=components.rotulo)
        with col3:
            social = st.selectbox("Dinâmica social", ["individual", "debate"], format_func=components.rotulo)
        dificuldades = st.multiselect("Dificuldades (opcional)", ["concentracao", "calculos", "memorizacao", "leitura"], format_func=components.rotulo)

        # 2. Campos exclusivos de Professor
        preco_hora = 0
        qualidades = []
        if papel == "professor":
            components.secao("Sobre as suas aulas")
            preco_hora = st.number_input("Preço por hora (R$)", min_value=0, max_value=500, step=10)
            qualidades = st.multiselect("Suas maiores qualidades", ["didatica", "paciencia", "material_proprio", "foco_em_provas"], format_func=components.rotulo)

        btn_salvar = st.form_submit_button("Salvar Perfil", type="primary")

    if btn_salvar:
        if not materias or not estilos:
            st.error("Por favor, preencha pelo menos as matérias e os estilos!")
        else:
            # 3. Montando o dicionário conforme o contrato do Roteiro
            perfil_dict = {
                "materias": materias,
                "estilos": estilos,
                "ritmo": ritmo,
                "estrutura": estrutura,
                "social": social,
                "dificuldades": dificuldades,
                "nivel": nivel
            }
            
            if papel == "professor":
                perfil_dict["preco_hora"] = preco_hora
                perfil_dict["qualidades"] = qualidades

            # 4. A Mágica da IA: Classificando o perfil ANTES de salvar
            try:
                resultado_ia = classify(perfil_dict)
                perfil_dict["perfil_label"] = resultado_ia.get("label", "Indefinido")
                perfil_dict["perfil_probs"] = resultado_ia.get("probs", {})
                
                # 5. Salva no banco de dados
                repo.save_profile(user_id, perfil_dict)
                st.success(f"Perfil salvo! Você foi classificado como: {perfil_dict['perfil_label']}")
                
                # 6. Roteamento final
                if papel == "professor":
                    st.session_state[C.SS_TELA] = C.TELA_MENU
                else:
                    st.session_state[C.SS_TELA] = C.TELA_MATCH
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao salvar perfil ou classificar na IA: {e}")
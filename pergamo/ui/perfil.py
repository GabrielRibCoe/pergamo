"""Tela de perfil (formulário). RESPONSÁVEL: papel 3 (Telas de entrada e integração).

As opções vêm de pergamo/constants.py: são os mesmos valores que a IA (features.py e classifier.py)
entende. Se escrever opções à mão aqui, a rede neural não reconhece as respostas.
"""
import streamlit as st

from pergamo import constants as C
from pergamo import state
from pergamo.ml.classifier import classify
from pergamo.ui import components

QUALIDADES = {
    "didatica": "Didática",
    "paciencia": "Paciência",
    "material_proprio": "Material próprio",
    "foco_em_provas": "Foco em provas",
}


def render(repo):
    usuario = state.usuario_logado(repo)
    if usuario is None:
        state.ir_para(C.TELA_LOGIN)
    eh_aluno = usuario["papel"] == C.PAPEL_ALUNO
    atual = repo.get_profile(usuario["id"]) or {}  # se já existe perfil, o formulário abre preenchido

    components.logo("logo_horizontal", largura=210)
    st.title("Monte seu Perfil Pérgamo")
    st.write(f"Preencha suas preferências como **{C.PAPEIS[usuario['papel']]}**:")

    with st.form("form_perfil"):
        components.secao("O que você quer ensinar ou aprender" if eh_aluno else "O que você ensina")
        materias = st.multiselect(
            "Matérias de interesse", C.MATERIAS, default=atual.get("materias", []), key="perfil_materias",
        )
        if eh_aluno:
            nivel = st.selectbox(
                "Nível de escolaridade", list(C.NIVEIS), format_func=C.NIVEIS.get,
                index=components.opcao_padrao(C.NIVEIS, atual.get("nivel")), key="perfil_nivel",
            )

        components.secao("Seu jeito de aprender" if eh_aluno else "Seu jeito de ensinar")
        estilos = st.multiselect(
            "Estilo (pode escolher mais de um)", list(C.ESTILOS), format_func=C.ESTILOS.get,
            default=atual.get("estilos", []), key="perfil_estilos",
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            ritmo = st.selectbox("Ritmo ideal", list(C.RITMOS), format_func=C.RITMOS.get,
                                 index=components.opcao_padrao(C.RITMOS, atual.get("ritmo")), key="perfil_ritmo")
        with col2:
            estrutura = st.selectbox("Estrutura das aulas", list(C.ESTRUTURAS), format_func=C.ESTRUTURAS.get,
                                     index=components.opcao_padrao(C.ESTRUTURAS, atual.get("estrutura")),
                                     key="perfil_estrutura")
        with col3:
            social = st.selectbox("Dinâmica social", list(C.SOCIAIS), format_func=C.SOCIAIS.get,
                                  index=components.opcao_padrao(C.SOCIAIS, atual.get("social")), key="perfil_social")

        extras = {}
        if eh_aluno:
            extras["nivel"] = nivel
            extras["dificuldades"] = st.multiselect(
                "Dificuldades (opcional)", list(C.DIFICULDADES), format_func=C.DIFICULDADES.get,
                default=atual.get("dificuldades", []), key="perfil_dificuldades",
            )
        else:
            components.secao("Sobre as suas aulas")
            extras["metodo"] = st.selectbox(
                "Método principal de ensino", list(C.METODOS), format_func=C.METODOS.get,
                index=components.opcao_padrao(C.METODOS, atual.get("metodo")), key="perfil_metodo",
            )
            extras["preco_hora"] = st.number_input(
                "Preço por hora (R$)", min_value=10, max_value=500, value=int(atual.get("preco_hora", 50)),
                step=5, key="perfil_preco",
            )
            extras["qualidades"] = st.multiselect(
                "Suas maiores qualidades", list(QUALIDADES), format_func=QUALIDADES.get,
                default=atual.get("qualidades", []), key="perfil_qualidades",
            )

        salvou = st.form_submit_button("Salvar perfil", type="primary")

    if salvou:
        if not materias or not estilos:
            st.error("Escolha pelo menos uma matéria e um estilo.")
        else:
            perfil = {"materias": materias, "estilos": estilos, "ritmo": ritmo,
                      "estrutura": estrutura, "social": social, **extras}
            resultado = classify(perfil)  # a IA classifica ANTES de salvar
            perfil["perfil_label"] = resultado["label"]
            perfil["perfil_probs"] = resultado["probs"]
            repo.save_profile(usuario["id"], perfil)
            state.ir_para(state.tela_inicial_do_usuario(repo, usuario))

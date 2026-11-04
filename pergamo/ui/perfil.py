"""Tela de perfil (formulário). RESPONSÁVEL: papel 3 (Telas de entrada e integração).

Ao salvar, chama classify() (IA) e guarda perfil_label e perfil_probs junto com as respostas.
TODO (papel 3): ampliar o formulário com os campos das fichas (qualidades, experiência com
necessidades específicas, disponibilidade...) e melhorar o visual.
"""
import streamlit as st

from pergamo import constants as C
from pergamo import state
from pergamo.ml.classifier import classify
from pergamo.ui import components


def render(repo):
    usuario = state.usuario_logado(repo)
    if usuario is None:
        state.ir_para(C.TELA_LOGIN)
    eh_aluno = usuario["papel"] == C.PAPEL_ALUNO
    atual = repo.get_profile(usuario["id"]) or {}

    components.titulo_da_pagina(
        "Seu perfil",
        "Como você aprende" if eh_aluno else "Como você ensina",
    )

    with st.form("form_perfil"):
        materias = st.multiselect(
            "Matérias que você quer estudar" if eh_aluno else "Matérias que você leciona",
            C.MATERIAS, default=atual.get("materias", []), key="perfil_materias",
        )
        estilos = st.multiselect(
            "Estilo de aprendizagem (pode escolher mais de um)" if eh_aluno else "Seu estilo de ensino",
            list(C.ESTILOS), format_func=C.ESTILOS.get, default=atual.get("estilos", []), key="perfil_estilos",
        )
        ritmo = st.radio("Ritmo", list(C.RITMOS), format_func=C.RITMOS.get,
                         index=components.opcao_padrao(C.RITMOS, atual.get("ritmo")), key="perfil_ritmo")
        estrutura = st.radio("Estrutura da aula", list(C.ESTRUTURAS), format_func=C.ESTRUTURAS.get,
                             index=components.opcao_padrao(C.ESTRUTURAS, atual.get("estrutura")), key="perfil_estrutura")
        social = st.radio("Contexto", list(C.SOCIAIS), format_func=C.SOCIAIS.get,
                          index=components.opcao_padrao(C.SOCIAIS, atual.get("social")), key="perfil_social")

        extras = {}
        if eh_aluno:
            extras["dificuldades"] = st.multiselect(
                "Principais dificuldades (opcional)", list(C.DIFICULDADES), format_func=C.DIFICULDADES.get,
                default=atual.get("dificuldades", []), key="perfil_dificuldades",
            )
            extras["nivel"] = st.selectbox(
                "Seu nível", list(C.NIVEIS), format_func=C.NIVEIS.get,
                index=components.opcao_padrao(C.NIVEIS, atual.get("nivel")), key="perfil_nivel",
            )
        else:
            extras["metodo"] = st.selectbox(
                "Método principal de ensino", list(C.METODOS), format_func=C.METODOS.get,
                index=components.opcao_padrao(C.METODOS, atual.get("metodo")), key="perfil_metodo",
            )
            extras["preco_hora"] = st.number_input(
                "Preço por hora (R$)", min_value=10, max_value=500, value=int(atual.get("preco_hora", 50)),
                step=5, key="perfil_preco",
            )
        salvou = st.form_submit_button("Salvar perfil")

    if salvou:
        if not materias or not estilos:
            st.error("Escolha pelo menos uma matéria e um estilo.")
        else:
            perfil = {"materias": materias, "estilos": estilos, "ritmo": ritmo,
                      "estrutura": estrutura, "social": social, **extras}
            resultado = classify(perfil)
            perfil["perfil_label"] = resultado["label"]
            perfil["perfil_probs"] = resultado["probs"]
            repo.save_profile(usuario["id"], perfil)
            state.ir_para(state.tela_inicial_do_usuario(repo, usuario))

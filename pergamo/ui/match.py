"""Tela de match (só para alunos). RESPONSÁVEL: papel 4 (Telas de match e menu).

Lista os professores ordenados por compatibilidade. Os 5 primeiros levam o selo "Alta precisão";
os demais ficam em "Mais abrangentes". "Ver detalhes" abre o professor na própria tela, e lá o aluno
escolhe Fazer match ou Voltar.
TODO (papel 4): melhorar o visual dos cartões e mostrar mais dados do professor no detalhe.
"""
import streamlit as st

from pergamo import constants as C
from pergamo import state
from pergamo.ml.match import rank_professors
from pergamo.ui import components

ALTA_PRECISAO = 5


def _detalhe(repo, aluno_id: str, item: dict):
    prof, perfil = item["professor"], item["professor"]["perfil"]
    st.title(prof["nome"])
    st.write(f"Compatibilidade: **{components.porcentagem(item['score'])}**")
    st.write(f"Perfil: {components.tipo_do_perfil(perfil)}")
    st.write(f"Matérias: {', '.join(perfil.get('materias', []))}")
    st.write(f"Método: {C.METODOS.get(perfil.get('metodo'), '-')}")
    st.write(f"Preço por hora: R$ {perfil.get('preco_hora', '-')}")
    if item["reasons"]:
        st.markdown("**Por que combina**")
        for motivo in item["reasons"]:
            st.write(f"- {motivo}")

    col_match, col_voltar = st.columns(2)
    if col_match.button("Fazer match", key="btn_fazer_match", type="primary"):
        repo.create_link(aluno_id, prof["id"])
        st.session_state[C.SS_MATCH_PROF] = None
        state.ir_para(C.TELA_MENU)
    if col_voltar.button("Voltar", key="btn_voltar_lista"):
        st.session_state[C.SS_MATCH_PROF] = None
        st.rerun()


def _cartao(item: dict):
    prof, perfil = item["professor"], item["professor"]["perfil"]
    with st.container(border=True):
        col_info, col_nota = st.columns([3, 1])
        col_info.markdown(f"**{prof['nome']}**")
        col_info.caption(f"{', '.join(perfil.get('materias', []))} · {components.tipo_do_perfil(perfil)}")
        col_nota.metric("Match", components.porcentagem(item["score"]))
        if st.button("Ver detalhes", key=f"ver_{prof['id']}"):
            st.session_state[C.SS_MATCH_PROF] = prof["id"]
            st.rerun()


def render(repo):
    usuario = state.usuario_logado(repo)
    if usuario is None:
        state.ir_para(C.TELA_LOGIN)
    if usuario["papel"] != C.PAPEL_ALUNO or repo.get_active_link(usuario["id"]):
        state.ir_para(C.TELA_MENU)

    perfil_aluno = repo.get_profile(usuario["id"])
    ranking = rank_professors(perfil_aluno, repo.list_professors())

    # Detalhe de um professor
    escolhido = st.session_state.get(C.SS_MATCH_PROF)
    if escolhido:
        item = next((i for i in ranking if i["professor"]["id"] == escolhido), None)
        if item:
            _detalhe(repo, usuario["id"], item)
            return
        st.session_state[C.SS_MATCH_PROF] = None

    # Lista de professores
    components.titulo_da_pagina("Seus professores", f"Seu perfil: {components.tipo_do_perfil(perfil_aluno)}")
    if not ranking:
        st.info("Nenhum professor encontrado para as suas matérias.")
        return

    st.subheader("Alta precisão")
    for item in ranking[:ALTA_PRECISAO]:
        _cartao(item)
    if len(ranking) > ALTA_PRECISAO:
        st.subheader("Mais abrangentes")
        for item in ranking[ALTA_PRECISAO:]:
            _cartao(item)

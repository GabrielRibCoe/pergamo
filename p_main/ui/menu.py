"""Menu principal com 3 abas: Turmas, Atividades e Ágoras. RESPONSÁVEL: papel 4 (Telas de match e menu).

Turmas usa dados REAIS do banco (e atualiza sozinha a cada 3 segundos); Atividades e Ágoras
são só visuais e leem data/atividades.json e data/agoras.json.
TODO (papel 4): melhorar o visual das abas e ampliar os dados fictícios.
"""
import json

import streamlit as st

from pergamo import constants as C
from pergamo import state
from pergamo.config import DATA_DIR


def _ler_json(nome: str) -> list:
    caminho = DATA_DIR / nome
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else []


@st.fragment(run_every="3s")
def _lista_turma(repo, professor_id: str, meu_id: str | None):
    """Reexecuta sozinha a cada 3 segundos: é o efeito de tempo real (roteiro, seção 6.4)."""
    turma = [a for a in repo.get_roster(professor_id) if a["id"] != meu_id]
    if not turma:
        st.info("Ainda não há outros alunos nesta turma.")
        return
    for aluno in turma:
        st.write(f"- {aluno['nome']} ({aluno['perfil_label'] or 'sem perfil'})")


def _aba_turmas(repo, usuario: dict):
    if usuario["papel"] == C.PAPEL_ALUNO:
        vinculo = repo.get_active_link(usuario["id"])
        if vinculo is None:
            state.ir_para(C.TELA_MATCH)
        professor = repo.get_user(vinculo["professor_id"])
        st.subheader("Seu professor")
        st.write(professor["nome"])
        st.subheader("Colegas de turma")
        _lista_turma(repo, professor["id"], usuario["id"])
        if st.button("Desvincular", key="btn_desvincular"):
            repo.end_link(usuario["id"])
            state.ir_para(C.TELA_MATCH)
    else:
        st.subheader("Seus alunos")
        _lista_turma(repo, usuario["id"], None)


def _aba_atividades():
    for atv in _ler_json("atividades.json"):
        with st.container(border=True):
            st.markdown(f"**{atv['titulo']}**")
            st.caption(f"{atv['turma']} · prazo {atv['prazo']} · {atv['status']}")


def _aba_agoras():
    for agora in _ler_json("agoras.json"):
        with st.container(border=True):
            st.markdown(f"**{agora['nome']}** (nível {agora['nivel']})")
            st.caption(f"{agora['membros']} membros · {agora['descricao']}")


def render(repo):
    usuario = state.usuario_logado(repo)
    if usuario is None:
        state.ir_para(C.TELA_LOGIN)

    st.title(f"Olá, {usuario['nome'].split()[0]}")
    aba_turmas, aba_atividades, aba_agoras = st.tabs(["Turmas", "Atividades", "Ágoras"])
    with aba_turmas:
        _aba_turmas(repo, usuario)
    with aba_atividades:
        _aba_atividades()
    with aba_agoras:
        _aba_agoras()

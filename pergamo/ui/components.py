"""Pedaços de tela reutilizáveis. RESPONSÁVEL: papel 3 (Telas de entrada e integração).

Coloque aqui o que mais de uma tela usa (cartões, selos, formatação). Mantenha simples.
"""
import streamlit as st


def nomes(opcoes: dict, chaves: list[str]) -> str:
    """Transforma ["pratico", "visual"] em "Prático, Visual" usando um dicionário de opções."""
    return ", ".join(opcoes.get(c, c) for c in chaves) if chaves else "-"


def porcentagem(score: float) -> str:
    return f"{round(score * 100)}%"


def selo(texto: str):
    """Selo pequeno de destaque (ex.: Alta precisão)."""
    st.caption(f":orange-badge[{texto}]")


def titulo_da_pagina(texto: str, subtitulo: str | None = None):
    st.title(texto)
    if subtitulo:
        st.caption(subtitulo)


def opcao_padrao(opcoes: dict, valor: str | None) -> int:
    """Índice do valor em um dicionário de opções (para st.radio / st.selectbox)."""
    chaves = list(opcoes)
    return chaves.index(valor) if valor in chaves else 0


def tipo_do_perfil(perfil: dict) -> str:
    label = perfil.get("perfil_label")
    if not label:
        return "-"
    prob = (perfil.get("perfil_probs") or {}).get(label)
    return f"{label} ({porcentagem(prob)})" if prob else label


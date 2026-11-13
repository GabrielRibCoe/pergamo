"""Pedaços de tela reutilizáveis. RESPONSÁVEL: papel 3 (Telas de entrada e integração).

Coloque aqui o que mais de uma tela usa (cartões, selos, formatação). Mantenha simples.

Identidade visual da Pérgamo (tirada dos logos):
    verde  #004741  | creme #F0EDE4  | papel #F8F6F0 (fundo dos cartões)
    títulos em Bitter (serifada robusta, parente do tipo de madeira do logotipo)
"""
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Funções que já existiam (outras telas usam; não mudar assinatura)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Identidade visual
# ---------------------------------------------------------------------------

ASSETS = Path(__file__).resolve().parents[2] / "assets"

VERDE = "#004741"
CREME = "#F0EDE4"

_ROTULOS = {
    "pratico": "Prático",
    "ouvinte": "Ouvinte",
    "leitor": "Leitor",
    "racional": "Racional",
    "gradual": "Gradual",
    "rapido": "Rápido",
    "estruturada": "Estruturada",
    "flexivel": "Flexível",
    "individual": "Individual",
    "debate": "Debate",
    "concentracao": "Concentração",
    "calculos": "Cálculos",
    "memorizacao": "Memorização",
    "leitura": "Leitura",
    "medio": "Médio",
    "didatica": "Didática",
    "paciencia": "Paciência",
    "material_proprio": "Material próprio",
    "foco_em_provas": "Foco em provas",
}


def rotulo(valor: str) -> str:
    """Texto bonito para um valor interno (use em format_func; o valor salvo não muda)."""
    if valor in _ROTULOS:
        return _ROTULOS[valor]
    return valor.replace("_", " ").capitalize() if valor.islower() else valor


def caminho_asset(nome: str) -> str:
    return str(ASSETS / nome)


def logo(variante: str = "logo_vertical", largura: int = 220, centralizar: bool = True):
    """Mostra um logo da pasta assets/ (logo_vertical, logo_horizontal, icone, nome).

    Acrescente `_claro` ao nome (ex.: "logo_horizontal_claro") para a versão em creme.
    """
    arquivo = ASSETS / f"{variante}.png"
    if not arquivo.exists():  # sem o arquivo, não quebra a tela
        st.markdown("### Pérgamo")
        return
    if centralizar:
        _, meio, _ = st.columns([1, 2, 1])
        with meio:
            st.image(str(arquivo), width=largura)
    else:
        st.image(str(arquivo), width=largura)


def cabecalho_entrada(subtitulo: str | None = None, largura: int = 230):
    """Topo das telas de login e cadastro: logo grande centralizado + frase de apoio."""
    logo("logo_vertical", largura=largura)
    if subtitulo:
        st.markdown(f"<p class='pg-subtitulo'>{subtitulo}</p>", unsafe_allow_html=True)


def secao(titulo: str, ajuda: str | None = None):
    """Subtítulo de seção dentro de um formulário longo."""
    st.markdown(f"<div class='pg-secao'>{titulo}</div>", unsafe_allow_html=True)
    if ajuda:
        st.caption(ajuda)


_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bitter:wght@600;700;800&display=swap');

:root {{
    --pg-verde: {VERDE};
    --pg-creme: {CREME};
    --pg-papel: #F8F6F0;
}}

/* Títulos: serifada robusta, no espírito do logotipo */
h1, h2, h3, h4,
[data-testid="stHeading"] h1, [data-testid="stHeading"] h2, [data-testid="stHeading"] h3 {{
    font-family: 'Bitter', Georgia, 'Times New Roman', serif !important;
    font-weight: 700 !important;
    color: var(--pg-verde) !important;
    letter-spacing: -0.01em;
}}
h1 {{ font-size: 2.2rem !important; line-height: 1.15 !important; }}

/* Tira o rodapé e o menu padrão do Streamlit (mantém o botão da barra lateral) */
#MainMenu, footer {{ visibility: hidden; }}

/* Container central com respiro */
.block-container {{ padding-top: 2.5rem; max-width: 720px; }}

/* Campos de texto e listas */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {{
    border: 1.5px solid var(--pg-verde) !important;
    border-radius: 4px !important;
    background-color: #fffdf8 !important;
}}
div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="select"]:focus-within > div {{
    box-shadow: 0 0 0 3px rgba(0, 71, 65, 0.22) !important;
}}
div[data-baseweb="tag"] {{
    background-color: var(--pg-verde) !important;
    color: var(--pg-creme) !important;
    border-radius: 3px !important;
}}
div[data-baseweb="tag"] span, div[data-baseweb="tag"] svg {{
    color: var(--pg-creme) !important;
    fill: var(--pg-creme) !important;
}}

/* Formulário vira uma "folha de pergaminho" com sombra dura, eco do cubo do logo */
[data-testid="stForm"] {{
    background: var(--pg-papel);
    border: 2px solid var(--pg-verde);
    border-radius: 4px;
    padding: 1.6rem 1.6rem 1.2rem;
    box-shadow: 6px 6px 0 var(--pg-verde);
}}

/* Botões */
.stButton > button, [data-testid="stFormSubmitButton"] > button {{
    border-radius: 4px;
    font-weight: 600;
    padding: 0.55rem 1.3rem;
    transition: transform .08s ease, box-shadow .08s ease;
}}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"] {{
    background: var(--pg-verde);
    color: var(--pg-creme);
    border: 2px solid var(--pg-verde);
}}
.stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {{
    background: #00352f;
    border-color: #00352f;
    color: var(--pg-creme);
}}
.stButton > button[kind="secondary"] {{
    background: transparent;
    color: var(--pg-verde);
    border: 2px solid var(--pg-verde);
}}
.stButton > button[kind="secondary"]:hover {{
    background: var(--pg-verde);
    color: var(--pg-creme);
}}
.stButton > button:active {{ transform: translateY(1px); }}
.stButton > button:focus-visible, [data-testid="stFormSubmitButton"] > button:focus-visible {{
    outline: 3px solid rgba(0, 71, 65, 0.4);
    outline-offset: 2px;
}}

/* Barra lateral */
[data-testid="stSidebar"] {{ border-right: 2px solid var(--pg-verde); }}
[data-testid="stSidebar"] .stButton > button {{ width: 100%; }}

/* Abas, divisores e alertas combinando com a paleta */
hr {{ border-color: rgba(0, 71, 65, 0.25) !important; }}
[data-testid="stAlert"] {{ border-radius: 4px; }}

/* Classes próprias */
.pg-subtitulo {{
    text-align: center;
    font-size: 1.05rem;
    margin: -0.2rem auto 1.6rem;
    max-width: 30rem;
    opacity: .85;
}}
.pg-secao {{
    font-family: 'Bitter', Georgia, serif;
    font-weight: 700;
    font-size: 1.15rem;
    color: var(--pg-verde);
    border-bottom: 2px solid var(--pg-verde);
    padding-bottom: .25rem;
    margin: 1.4rem 0 .6rem;
}}
.pg-secao:first-child {{ margin-top: 0; }}

@media (max-width: 640px) {{
    h1 {{ font-size: 1.8rem !important; }}
    [data-testid="stForm"] {{ padding: 1.1rem; box-shadow: 4px 4px 0 var(--pg-verde); }}
}}
@media (prefers-reduced-motion: reduce) {{
    .stButton > button {{ transition: none; }}
}}
</style>
"""


def aplicar_tema():
    """Injeta o CSS da Pérgamo. Chamar uma vez, no começo do main() do app.py."""
    st.markdown(_CSS, unsafe_allow_html=True)

"""Tela de match (só para alunos). RESPONSÁVEL: papel 4 (Telas de match e menu).

Lista os professores ordenados por compatibilidade. Os 5 primeiros levam o título "Alta precisão";
os demais ficam em "Mais abrangentes". Cada professor aparece num cartão completo (perfil, matérias,
método, preço e por que combina) com o botão "Fazer match" logo abaixo, sem precisar abrir detalhes.

O visual reaproveita os cartões do menu (menu.py), para as duas telas terem a mesma cara.
Todo texto que vem do banco passa por html.escape (menu._e) antes de entrar no HTML.
"""
import streamlit as st

from pergamo import constants as C
from pergamo import state
from pergamo.ml.match import rank_professors
from pergamo.ui import components, menu

ALTA_PRECISAO = 5

_CSS = """<style>
.pgm-perfil{background:var(--pg-verde,#004741);color:var(--pg-creme,#F0EDE4);border:2px solid var(--pg-verde,#004741);border-radius:4px;padding:1.1rem 1.3rem;margin:0 0 1.8rem}
.pgm-perfil p{margin:0}
.pgm-perfil .rotulo{font-size:.9rem;opacity:.85}
.pgm-perfil .tipo{font-family:'Bitter',Georgia,serif;font-weight:800;font-size:2rem;line-height:1.15;margin:.1rem 0 .45rem}
.pgm-perfil .dica{font-size:.88rem;opacity:.9}
[class*="st-key-pgmprof_"]{background:var(--pg-papel,#F8F6F0);border:2px solid var(--pg-verde,#004741);border-radius:4px;padding:1rem 1.1rem 1.1rem;box-shadow:4px 4px 0 var(--pg-verde,#004741);margin:0 0 1.2rem;color:#1F2320}
[class*="st-key-pgmprof_"] .stButton>button{width:100%}
.pgm-nota{text-align:right;line-height:1.1;white-space:nowrap}
.pgm-nota span{display:block;font-size:.8rem;opacity:.85}
.pgm-nota b{font-family:'Bitter',Georgia,serif;font-weight:800;font-size:1.9rem;color:var(--pg-verde,#004741)}
.pgm-motivos{margin:.8rem 0 .2rem}
.pgm-motivos ul{margin:.25rem 0 0;padding-left:1.1rem;font-size:.85rem}
</style>"""


def _html_perfil_aluno(perfil: dict) -> str:
    """Cartão verde de destaque no topo: o tipo de perfil do aluno."""
    return (
        '<div class="pgm-perfil"><p class="rotulo">Seu perfil</p>'
        f'<p class="tipo">{menu._e(components.tipo_do_perfil(perfil))}</p>'
        '<p class="dica">Os professores abaixo estão ordenados pela afinidade com esse perfil.</p></div>'
    )


def _html_professor(item: dict) -> str:
    """Conteúdo do cartão do professor (a janelinha em si vem do CSS do container)."""
    prof, perfil = item["professor"], item["professor"]["perfil"]
    motivos = ""
    if item["reasons"]:
        motivos = (
            '<div class="pgm-motivos"><p class="pgm-sub"><b>Por que combina</b></p><ul>'
            + "".join(f"<li>{menu._e(m)}</li>" for m in item["reasons"])
            + "</ul></div>"
        )
    return (
        '<div class="pgm-topo"><div class="pgm-linha">' + menu._avatar(prof["nome"])
        + f'<div><p class="pgm-nome">{menu._e(prof["nome"])}</p><p class="pgm-sub">Professor</p></div></div>'
        + f'<div class="pgm-nota"><span>Match</span><b>{menu._e(components.porcentagem(item["score"]))}</b></div></div>'
        + f'<div style="margin-top:.5rem">{menu._badge_tipo(perfil)}</div>'
        + menu._chips(perfil.get("materias", []))
        + '<div class="pgm-info">'
        + f'<span>Método: {menu._e(C.METODOS.get(perfil.get("metodo"), "-"))}</span>'
        + f'<span>Preço: R$ {menu._e(perfil.get("preco_hora", "-"))}/hora</span></div>'
        + motivos
    )


def _cartao(repo, aluno_id: str, item: dict):
    prof = item["professor"]
    with st.container(key=f"pgmprof_{prof['id']}"):
        menu._html(_html_professor(item))
        if st.button("Fazer match", key=f"fazer_match_{prof['id']}", type="primary"):
            repo.create_link(aluno_id, prof["id"])
            st.session_state[C.SS_MATCH_PROF] = None
            state.ir_para(C.TELA_MENU)


def render(repo):
    usuario = state.usuario_logado(repo)
    if usuario is None:
        state.ir_para(C.TELA_LOGIN)
    if usuario["papel"] != C.PAPEL_ALUNO or repo.get_active_link(usuario["id"]):
        state.ir_para(C.TELA_MENU)

    perfil_aluno = repo.get_profile(usuario["id"])
    ranking = rank_professors(perfil_aluno, repo.list_professors())

    menu._html(menu._CSS)
    menu._html(_CSS)

    components.logo("logo_horizontal", largura=200, centralizar=False)
    st.title("Seus professores")
    menu._html(_html_perfil_aluno(perfil_aluno))

    if not ranking:
        st.info("Nenhum professor encontrado para as suas matérias.")
        return

    st.subheader("Alta precisão")
    for item in ranking[:ALTA_PRECISAO]:
        _cartao(repo, usuario["id"], item)
    if len(ranking) > ALTA_PRECISAO:
        st.subheader("Mais abrangentes")
        for item in ranking[ALTA_PRECISAO:]:
            _cartao(repo, usuario["id"], item)

"""Menu principal com 3 abas: Turmas, Atividades e Ágoras. RESPONSÁVEL: papel 4 (Telas de match e menu).

- Cabeçalho com o resumo do usuário (tipo de perfil, matérias, método ou nível).
- Turmas usa dados REAIS do banco e atualiza sozinha a cada 3 segundos (efeito de tempo real).
  Aluno: cartão do professor com a nota de match, colegas de turma e desvincular com confirmação.
  Professor: resumo da turma (quantidade e distribuição dos tipos de perfil) e cartões dos alunos.
- Atividades e Ágoras são só visuais e leem data/atividades.json e data/agoras.json.

O CSS dos cartões fica neste arquivo e usa as cores do tema (components.py), com cores de reserva.
Todo texto que vem do banco passa por html.escape antes de entrar no HTML.
"""
import html
import json
from collections import Counter
from datetime import datetime

import streamlit as st

from pergamo import constants as C
from pergamo import state
from pergamo.config import DATA_DIR
from pergamo.ml.match import compatibility
from pergamo.ui import components

_CSS = """<style>
.pgm-card{background:var(--pg-papel,#F8F6F0);border:2px solid var(--pg-verde,#004741);border-radius:4px;padding:1rem 1.1rem;box-shadow:4px 4px 0 var(--pg-verde,#004741);color:#1F2320;margin:0 0 1rem}
.pgm-linha{display:flex;gap:.9rem;align-items:center}
.pgm-avatar{flex:0 0 auto;width:48px;height:48px;border-radius:50%;background:var(--pg-verde,#004741);color:var(--pg-creme,#F0EDE4);display:flex;align-items:center;justify-content:center;font-family:'Bitter',Georgia,serif;font-weight:700;font-size:1.05rem}
.pgm-avatar.peq{width:38px;height:38px;font-size:.9rem}
.pgm-nome{font-family:'Bitter',Georgia,serif;font-weight:700;font-size:1.1rem;color:var(--pg-verde,#004741);margin:0;line-height:1.2}
.pgm-sub{font-size:.85rem;opacity:.85;margin:.1rem 0 0}
.pgm-topo{display:flex;justify-content:space-between;gap:.8rem;align-items:flex-start}
.pgm-chips{display:flex;flex-wrap:wrap;gap:.35rem;margin:.65rem 0 0}
.pgm-chip{border:1.5px solid var(--pg-verde,#004741);border-radius:999px;padding:.08rem .6rem;font-size:.78rem;color:var(--pg-verde,#004741);background:#fffdf8}
.pgm-info{display:flex;flex-wrap:wrap;gap:.3rem 1.2rem;margin:.65rem 0 0;font-size:.85rem}
.pgm-badge{display:inline-block;border-radius:999px;padding:.12rem .7rem;font-size:.75rem;font-weight:700;white-space:nowrap;border:1.5px solid transparent}
.pgm-badge.tipo{background:var(--pg-verde,#004741);color:var(--pg-creme,#F0EDE4)}
.pgm-badge.match{background:#fffdf8;color:var(--pg-verde,#004741);border-color:var(--pg-verde,#004741);font-size:.85rem}
.pgm-badge.pendente{background:#FFF1D6;color:#7A4B00;border-color:#E3B25A}
.pgm-badge.entregue{background:#DCEBFA;color:#0B3D6B;border-color:#7FB0E0}
.pgm-badge.corrigida{background:#DDEFE3;color:#0F4D2A;border-color:#6FB88A}
.pgm-badge.n1{background:#F0EDE4;color:#3B3B35;border-color:#B9B4A3}
.pgm-badge.n2{background:#DCEBFA;color:#0B3D6B;border-color:#7FB0E0}
.pgm-badge.n3{background:#FFF1D6;color:#7A4B00;border-color:#E3B25A}
.pgm-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:.8rem;margin:0 0 1rem}
.pgm-grid .pgm-card{margin:0;padding:.8rem .9rem;box-shadow:3px 3px 0 var(--pg-verde,#004741)}
.pgm-tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:.7rem;margin:0 0 1rem}
.pgm-tile{background:var(--pg-papel,#F8F6F0);border:2px solid var(--pg-verde,#004741);border-radius:4px;padding:.6rem .8rem;color:#1F2320}
.pgm-tile .num{font-family:'Bitter',Georgia,serif;font-weight:800;font-size:1.7rem;color:var(--pg-verde,#004741);line-height:1.1}
.pgm-tile .rot{font-size:.8rem;opacity:.85}
.pgm-barra{display:grid;grid-template-columns:84px 1fr 78px;gap:.5rem;align-items:center;font-size:.85rem;margin:.3rem 0}
.pgm-trilho{height:10px;background:#E4DFD2;border-radius:6px;overflow:hidden}
.pgm-trilho i{display:block;height:100%;background:var(--pg-verde,#004741)}
.pgm-turma{font-family:'Bitter',Georgia,serif;font-weight:700;color:var(--pg-verde,#004741);border-bottom:2px solid var(--pg-verde,#004741);padding-bottom:.2rem;margin:1.2rem 0 .7rem}
.pgm-vazio{border:2px dashed var(--pg-verde,#004741);border-radius:4px;padding:1rem;text-align:center;color:#1F2320;opacity:.85}
.pgm-titulo-card{font-weight:700;margin:0 0 .15rem;color:#1F2320}
.pgm-desc{font-size:.85rem;margin:.1rem 0 .5rem;opacity:.85}
.pgm-rodape{display:flex;justify-content:space-between;align-items:center;gap:.5rem;font-size:.82rem}
@media (max-width:640px){.pgm-tiles{grid-template-columns:1fr}.pgm-topo{flex-direction:column}}
</style>"""


# ----------------------------------------------------------------------------- utilitários
def _e(texto) -> str:
    """Escapa o texto para entrar com segurança no HTML (nomes vêm do banco)."""
    return html.escape(str(texto), quote=True)


def _ler_json(nome: str) -> list:
    caminho = DATA_DIR / nome
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else []


def _iniciais(nome: str) -> str:
    partes = [p for p in str(nome).split() if p]
    if not partes:
        return "?"
    return (partes[0][0] + (partes[-1][0] if len(partes) > 1 else "")).upper()


def _avatar(nome: str, pequeno: bool = False) -> str:
    return f'<div class="pgm-avatar{" peq" if pequeno else ""}">{_e(_iniciais(nome))}</div>'


def _chips(itens) -> str:
    return '<div class="pgm-chips">' + "".join(f'<span class="pgm-chip">{_e(i)}</span>' for i in itens) + "</div>" if itens else ""


def _badge_tipo(perfil: dict) -> str:
    texto = components.tipo_do_perfil(perfil or {})
    return f'<span class="pgm-badge tipo">{_e(texto)}</span>' if texto != "-" else ""


def _data_curta(iso: str | None) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m")
    except (TypeError, ValueError):
        return "-"


def _html(conteudo: str):
    st.markdown(conteudo, unsafe_allow_html=True)


# ----------------------------------------------------------------------------- cabeçalho
def _html_cabecalho(usuario: dict, perfil: dict | None) -> str:
    perfil = perfil or {}
    if usuario["papel"] == C.PAPEL_ALUNO:
        extra = [f"Nível: {C.NIVEIS.get(perfil.get('nivel'), '-')}", f"Estilo: {components.nomes(C.ESTILOS, perfil.get('estilos', []))}"]
    else:
        extra = [f"Método: {C.METODOS.get(perfil.get('metodo'), '-')}", f"Preço: R$ {perfil.get('preco_hora', '-')}/hora"]
    return (
        '<div class="pgm-card"><div class="pgm-linha">' + _avatar(usuario["nome"])
        + f'<div><p class="pgm-nome">{_e(usuario["nome"])}</p><p class="pgm-sub">{_e(C.PAPEIS[usuario["papel"]])}</p></div>'
        + f'<div style="margin-left:auto">{_badge_tipo(perfil)}</div></div>'
        + _chips(perfil.get("materias", []))
        + '<div class="pgm-info">' + "".join(f"<span>{_e(t)}</span>" for t in extra) + "</div></div>"
    )


def _cabecalho(usuario: dict, perfil: dict | None):
    if hasattr(components, "logo"):
        components.logo("logo_horizontal", largura=200, centralizar=False)
    st.title(f"Olá, {usuario['nome'].split()[0]}")
    _html(_html_cabecalho(usuario, perfil))


# ----------------------------------------------------------------------------- aba Turmas
def _cartao_professor(professor: dict, perfil_prof: dict, vinculo: dict, match: dict | None) -> str:
    nota = f'<span class="pgm-badge match">Match {components.porcentagem(match["score"])}</span>' if match else ""
    return (
        '<div class="pgm-card"><div class="pgm-topo"><div class="pgm-linha">' + _avatar(professor["nome"])
        + f'<div><p class="pgm-nome">{_e(professor["nome"])}</p><p class="pgm-sub">Professor · vinculado em {_data_curta(vinculo.get("criado_em"))}</p></div></div>'
        + f'<div>{nota}</div></div>'
        + f'<div style="margin-top:.5rem">{_badge_tipo(perfil_prof)}</div>'
        + _chips(perfil_prof.get("materias", []))
        + '<div class="pgm-info">'
        + f'<span>Método: {_e(C.METODOS.get(perfil_prof.get("metodo"), "-"))}</span>'
        + f'<span>Preço: R$ {_e(perfil_prof.get("preco_hora", "-"))}/hora</span></div></div>'
    )


def _cartao_aluno(aluno: dict) -> str:
    badge = f'<span class="pgm-badge tipo">{_e(aluno["perfil_label"])}</span>' if aluno.get("perfil_label") else ""
    return (
        '<div class="pgm-card"><div class="pgm-linha">' + _avatar(aluno["nome"], pequeno=True)
        + f'<div><p class="pgm-nome" style="font-size:.98rem">{_e(aluno["nome"])}</p><div style="margin-top:.25rem">{badge}</div></div></div></div>'
    )


def _resumo_turma(alunos: list[dict]) -> str:
    total = len(alunos)
    contagem = Counter(a.get("perfil_label") or "Sem perfil" for a in alunos)
    barras = ""
    for tipo in C.TIPOS_PERFIL:
        qtd = contagem.get(tipo, 0)
        pct = round(100 * qtd / total) if total else 0
        barras += (f'<div class="pgm-barra"><span>{_e(tipo)}</span><div class="pgm-trilho"><i style="width:{pct}%"></i></div>'
                   f'<span>{qtd} ({pct}%)</span></div>')
    return (
        '<div class="pgm-card"><div class="pgm-tiles" style="grid-template-columns:1fr;margin:0 0 .6rem">'
        f'<div class="pgm-tile" style="border:0;padding:0;background:transparent"><div class="num">{total}</div>'
        f'<div class="rot">{"aluno" if total == 1 else "alunos"} na turma</div></div></div>'
        '<p class="pgm-sub" style="margin-bottom:.3rem"><b>Tipos de perfil da turma</b></p>' + barras + "</div>"
    )


@st.fragment(run_every="3s")
def _turma(repo, professor_id: str, meu_id: str | None, visao_professor: bool):
    """Reexecuta sozinha a cada 3 segundos: é o efeito de tempo real (roteiro, seção 6.4)."""
    alunos = [a for a in repo.get_roster(professor_id) if a["id"] != meu_id]
    if visao_professor:
        _html(_resumo_turma(alunos))
    if not alunos:
        texto = ("Nenhum aluno ainda. Quando um aluno fizer match com você, ele aparece aqui." if visao_professor
                 else "Ainda não há outros alunos nesta turma.")
        _html(f'<div class="pgm-vazio">{texto}</div>')
        return
    if not visao_professor:
        st.caption(f"{len(alunos)} {'colega' if len(alunos) == 1 else 'colegas'} na turma")
    _html('<div class="pgm-grid">' + "".join(_cartao_aluno(a) for a in alunos) + "</div>")


def _aba_turmas(repo, usuario: dict, perfil: dict | None):
    if usuario["papel"] == C.PAPEL_ALUNO:
        vinculo = repo.get_active_link(usuario["id"])
        if vinculo is None:
            state.ir_para(C.TELA_MATCH)
        professor = repo.get_user(vinculo["professor_id"])
        perfil_prof = repo.get_profile(professor["id"]) or {}
        match = compatibility(perfil, perfil_prof) if perfil else None

        st.subheader("Seu professor")
        _html(_cartao_professor(professor, perfil_prof, vinculo, match))
        if match and match["reasons"]:
            with st.expander("Por que combina"):
                for motivo in match["reasons"]:
                    st.write(f"- {motivo}")

        st.subheader("Colegas de turma")
        _turma(repo, professor["id"], usuario["id"], False)

        st.divider()
        with st.popover("Desvincular professor"):
            st.write("Você volta para a lista de professores e pode escolher outro. Deseja continuar?")
            if st.button("Sim, desvincular", type="primary", key="btn_confirmar_desvincular"):
                repo.end_link(usuario["id"])
                state.ir_para(C.TELA_MATCH)
    else:
        st.subheader("Sua turma")
        _turma(repo, usuario["id"], None, True)


# ----------------------------------------------------------------------------- aba Atividades
_STATUS = {"Pendente": "pendente", "Entregue": "entregue", "Corrigida": "corrigida"}


def _cartao_atividade(atv: dict) -> str:
    status = atv.get("status", "Pendente")
    desc = f'<p class="pgm-desc">{_e(atv["descricao"])}</p>' if atv.get("descricao") else ""
    nota = f' · Nota {_e(atv["nota"])}' if atv.get("nota") is not None else ""
    return (
        '<div class="pgm-card"><div class="pgm-topo">'
        f'<p class="pgm-titulo-card">{_e(atv["titulo"])}</p>'
        f'<span class="pgm-badge {_STATUS.get(status, "pendente")}">{_e(status)}</span></div>'
        f'{desc}<div class="pgm-rodape"><span>Prazo: {_e(atv.get("prazo", "-"))}{nota}</span></div></div>'
    )


def _aba_atividades():
    atividades = _ler_json("atividades.json")
    if not atividades:
        _html('<div class="pgm-vazio">Nenhuma atividade atribuída ainda.</div>')
        return
    contagem = Counter(a.get("status", "Pendente") for a in atividades)
    _html(
        '<div class="pgm-tiles">'
        + "".join(f'<div class="pgm-tile"><div class="num">{contagem.get(s, 0)}</div><div class="rot">{s}s</div></div>'
                  for s in ("Pendente", "Entregue", "Corrigida"))
        + "</div>"
    )
    turmas = list(dict.fromkeys(a["turma"] for a in atividades))  # mantém a ordem do arquivo
    for turma in turmas:
        _html(f'<div class="pgm-turma">{_e(turma)}</div>')
        _html("".join(_cartao_atividade(a) for a in atividades if a["turma"] == turma))


# ----------------------------------------------------------------------------- aba Ágoras
_NIVEIS_AGORA = {
    1: "Comunidade gratuita",
    2: "Membros ilimitados",
    3: "Respostas verificadas por IA",
}


def _cartao_agora(agora: dict) -> str:
    nivel = int(agora.get("nivel", 1))
    participa = '<span class="pgm-badge tipo">Você participa</span>' if agora.get("participando") else ""
    return (
        '<div class="pgm-card"><div class="pgm-topo">'
        f'<p class="pgm-nome">{_e(agora["nome"])}</p>'
        f'<span class="pgm-badge n{min(max(nivel, 1), 3)}">Nível {nivel}</span></div>'
        f'<p class="pgm-desc">{_e(agora.get("descricao", ""))}</p>'
        f'<div class="pgm-rodape"><span>{_e(agora.get("membros", 0))} membros · {_e(_NIVEIS_AGORA.get(nivel, ""))}</span>{participa}</div></div>'
    )


def _aba_agoras():
    agoras = _ler_json("agoras.json")
    if not agoras:
        _html('<div class="pgm-vazio">Você ainda não participa de nenhuma Ágora.</div>')
        return
    st.caption("As Ágoras são comunidades de estudo. O nível mostra os recursos que a comunidade desbloqueou.")
    _html("".join(_cartao_agora(a) for a in agoras))


# ----------------------------------------------------------------------------- tela
def render(repo):
    usuario = state.usuario_logado(repo)
    if usuario is None:
        state.ir_para(C.TELA_LOGIN)

    _html(_CSS)
    perfil = repo.get_profile(usuario["id"])
    _cabecalho(usuario, perfil)

    aba_turmas, aba_atividades, aba_agoras = st.tabs(["Turmas", "Atividades", "Ágoras"])
    with aba_turmas:
        _aba_turmas(repo, usuario, perfil)
    with aba_atividades:
        _aba_atividades()
    with aba_agoras:
        _aba_agoras()

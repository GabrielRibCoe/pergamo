"""Teste de fumaça do app inteiro (Streamlit AppTest): login -> match -> match com professor -> menu.

Usa o banco em memória com as contas fictícias do seed. Rode com:  pytest
"""
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest


APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture
def app():
    st.cache_resource.clear()  # cada teste começa com um banco novo
    return AppTest.from_file(APP, default_timeout=20).run()


def _clicar(at, rotulo):
    botao = [b for b in at.button if b.label == rotulo][0]
    botao.click().run()


def _login(at, email, senha="123456"):
    at.text_input(key="login_email").input(email)
    at.text_input(key="login_senha").input(senha)
    _clicar(at, "Entrar")


def test_primeira_tela_e_login(app):
    assert not app.exception
    assert app.text_input(key="login_email")  # a tela de login tem o campo de e-mail


def test_senha_errada_mostra_erro(app):
    _login(app, "miguel@pergamo.test", "errada")
    assert not app.exception
    assert any("incorretos" in e.value for e in app.error)


def test_aluno_vai_para_match_e_depois_para_o_menu(app):
    _login(app, "miguel@pergamo.test")
    assert not app.exception
    assert app.title[0].value == "Seus professores"
    # abre o primeiro professor da lista e faz o match
    _clicar(app, "Ver detalhes")
    assert not app.exception
    assert any(b.label == "Fazer match" for b in app.button)
    _clicar(app, "Fazer match")
    assert not app.exception
    assert app.title[0].value.startswith("Olá, Miguel")
    assert [t.label for t in app.tabs] == ["Turmas", "Atividades", "Ágoras"]
    # desvincular volta para o match
    _clicar(app, "Sim, desvincular")  # botão de confirmação dentro do popover
    assert app.title[0].value == "Seus professores"


def test_voltar_do_detalhe_retorna_a_lista(app):
    _login(app, "miguel@pergamo.test")
    _clicar(app, "Ver detalhes")
    _clicar(app, "Voltar")
    assert app.title[0].value == "Seus professores"


def test_professor_vai_direto_ao_menu(app):
    _login(app, "renato@pergamo.test")
    assert not app.exception
    assert app.title[0].value.startswith("Olá, Renato")


def test_conta_nova_de_aluno_passa_por_perfil_e_chega_ao_match(app):
    _clicar(app, "Criar conta")
    app.text_input(key="cad_nome").input("Teste Silva")
    app.text_input(key="cad_email").input("teste.silva@pergamo.test")
    app.text_input(key="cad_senha").input("segredo123")
    _clicar(app, "Criar conta")
    assert not app.exception
    assert app.title[0].value == "Monte seu Perfil Pérgamo"
    app.multiselect(key="perfil_materias").select("Matemática")
    app.multiselect(key="perfil_estilos").select("pratico")
    _clicar(app, "Salvar perfil")
    assert not app.exception
    assert app.title[0].value == "Seus professores"


def _criar_conta(at, nome, email, papel):
    _clicar(at, "Criar conta")
    at.text_input(key="cad_nome").input(nome)
    at.text_input(key="cad_email").input(email)
    at.text_input(key="cad_senha").input("segredo123")
    at.selectbox(key="cad_papel").select(papel)
    _clicar(at, "Criar conta")
    assert not at.exception


def test_estilo_auditivo_e_classificado_como_ouvinte(app):
    """Garante que o formulário grava os valores do contrato (constants.py) que a IA entende."""
    from pergamo.db import get_repo

    _criar_conta(app, "Aluna Teste", "aluna.teste@pergamo.test", "aluno")
    app.multiselect(key="perfil_materias").select("Matemática")
    app.multiselect(key="perfil_estilos").select("auditivo")
    _clicar(app, "Salvar perfil")
    assert not app.exception
    repo = get_repo()
    perfil = repo.get_profile(repo.get_user_by_email("aluna.teste@pergamo.test")["id"])
    assert perfil["estilos"] == ["auditivo"]
    assert perfil["perfil_label"] == "Ouvinte"


def test_professor_novo_salva_metodo_e_preco_e_vai_ao_menu(app):
    from pergamo.db import get_repo

    _criar_conta(app, "Prof Teste", "prof.teste@pergamo.test", "professor")
    app.multiselect(key="perfil_materias").select("Física")
    app.multiselect(key="perfil_estilos").select("pratico")
    _clicar(app, "Salvar perfil")
    assert not app.exception
    assert app.title[0].value.startswith("Olá, Prof")
    repo = get_repo()
    perfil = repo.get_profile(repo.get_user_by_email("prof.teste@pergamo.test")["id"])
    assert "metodo" in perfil and perfil["preco_hora"] >= 10


def test_email_repetido_mostra_mensagem_clara(app):
    _criar_conta(app, "Outro Miguel", "miguel@pergamo.test", "aluno")  # e-mail do seed
    assert any("Já existe uma conta" in e.value for e in app.error)


def _html_da_tela(at) -> str:
    """Junta todo o HTML/markdown mostrado na tela (os cartões do menu são HTML)."""
    return " ".join(m.value for m in at.markdown)


def test_menu_do_aluno_mostra_cabecalho_professor_e_colegas(app):
    _login(app, "miguel@pergamo.test")
    _clicar(app, "Ver detalhes")
    _clicar(app, "Fazer match")
    assert not app.exception
    tela = _html_da_tela(app)
    assert "Miguel Souza" in tela and "Aluno" in tela          # cabeçalho com o resumo do usuário
    assert "Match" in tela and "Professor" in tela              # cartão do professor com a nota de match
    assert "Colegas de turma" in [s.value for s in app.subheader]
    assert "Seu professor" in [s.value for s in app.subheader]


def test_menu_do_professor_mostra_resumo_da_turma(app):
    _login(app, "renato@pergamo.test")
    assert not app.exception
    tela = _html_da_tela(app)
    assert "alunos na turma" in tela                            # quantidade de alunos
    assert all(tipo in tela for tipo in ("Prático", "Ouvinte", "Visual", "Leitor", "Racional"))  # distribuição
    assert "Sua turma" in [s.value for s in app.subheader]


def test_abas_de_atividades_e_agoras_tem_cartoes_com_status_e_nivel(app):
    _login(app, "renato@pergamo.test")
    tela = _html_da_tela(app)
    assert "pgm-badge pendente" in tela and "pgm-badge corrigida" in tela and "Nota " in tela
    assert "Nível 3" in tela and "Respostas verificadas por IA" in tela and "Você participa" in tela


def test_nomes_com_html_sao_escapados():
    from pergamo.ui import menu

    perigoso = '<script>alert(1)</script> Ana'
    assert "<script>" not in menu._avatar(perigoso)
    assert "<script>" not in menu._cartao_aluno({"id": "1", "nome": perigoso, "perfil_label": "Prático"})
    assert menu._iniciais("ana maria silva") == "AS" and menu._iniciais("") == "?"

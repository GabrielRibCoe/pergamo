"""Constantes compartilhadas: opções dos formulários, tipos de perfil e nomes das telas.

ESTE ARQUIVO FAZ PARTE DO CONTRATO (kit do dia 0).
Mudou alguma opção ou nome? Avise o grupo antes, porque todos os módulos usam estes valores.
"""

# ----------------------------------------------------------------------------- papéis
PAPEL_ALUNO = "aluno"
PAPEL_PROFESSOR = "professor"
PAPEIS = {PAPEL_ALUNO: "Aluno", PAPEL_PROFESSOR: "Professor"}

# ----------------------------------------------------------------------------- telas
# Estes nomes são as chaves do roteador em app.py.
TELA_LOGIN = "login"
TELA_CADASTRO = "cadastro"
TELA_PERFIL = "perfil"
TELA_MATCH = "match"
TELA_MENU = "menu"
TELAS = (TELA_LOGIN, TELA_CADASTRO, TELA_PERFIL, TELA_MATCH, TELA_MENU)

# ----------------------------------------------------------------------------- st.session_state
SS_TELA = "tela"
SS_USER_ID = "user_id"
SS_PAPEL = "papel"
SS_NOME = "nome"
SS_MATCH_PROF = "match_prof_id"  # professor aberto no detalhe da tela de match (ou None)

# ----------------------------------------------------------------------------- opções dos formulários
MATERIAS = [
    "Matemática", "Física", "Química", "Biologia", "História", "Geografia",
    "Português", "Literatura", "Redação", "Inglês", "Espanhol", "Filosofia",
    "Sociologia", "Artes", "Informática",
]

# Estilo de aprendizagem (aluno) ou de ensino (professor). Pode escolher mais de um.
ESTILOS = {
    "visual": "Visual",
    "auditivo": "Auditivo",
    "leitura": "Leitura e escrita",
    "pratico": "Prático",
    "logico": "Raciocínio lógico",
}
RITMOS = {"gradual": "Gradual, com repetição", "rapido": "Rápido, direto ao ponto"}
ESTRUTURAS = {"estruturada": "Estruturada, com cronograma", "flexivel": "Flexível, seguindo as dúvidas"}
SOCIAIS = {"individual": "Individual e focado", "debate": "Com debate e discussão"}
NIVEIS = {"medio": "Ensino médio", "vestibular": "Vestibular / ENEM", "superior": "Ensino superior"}

DIFICULDADES = {
    "concentracao": "Concentração em aula",
    "abstracao_matematica": "Abstração matemática",
    "interpretacao_texto": "Interpretação de texto",
    "memorizacao": "Memorização de conteúdo",
    "gestao_tempo": "Gestão do tempo",
    "ansiedade_provas": "Ansiedade em provas",
    "organizacao_estudos": "Organização dos estudos",
    "raciocinio_logico": "Raciocínio lógico",
    "gramatica": "Gramática e ortografia",
    "calculos_formulas": "Cálculos e fórmulas",
    "geometria_espacial": "Geometria espacial",
    "redacao_dissertativa": "Redação dissertativa",
}

# Método principal do professor
METODOS = {
    "teoria_primeiro": "Teoria primeiro",
    "pratica_guiada": "Prática guiada",
    "socratico": "Socrático",
    "visual_recursos": "Visual e recursos",
}

# ----------------------------------------------------------------------------- tipos de perfil (saída da IA)
TIPOS_PERFIL = ["Prático", "Ouvinte", "Visual", "Leitor", "Racional"]

ESTILO_PARA_TIPO = {
    "pratico": "Prático",
    "auditivo": "Ouvinte",
    "visual": "Visual",
    "leitura": "Leitor",
    "logico": "Racional",
}
METODO_PARA_TIPOS = {
    "teoria_primeiro": ["Leitor", "Racional"],
    "pratica_guiada": ["Prático"],
    "socratico": ["Racional", "Ouvinte"],
    "visual_recursos": ["Visual"],
}

# Senha das contas fictícias do seed (nunca use senhas reais no mockup)
SENHA_TESTE = "123456"

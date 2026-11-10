# Pérgamo — mockup (A3 de Exploração digital)

Mockup em Python (Streamlit) da Pérgamo, plataforma que conecta alunos e professores particulares por afinidade pedagógica.
Projeto do grupo para a A3 (Amostra em 01/12/2026). Tudo é simulação com **dados fictícios**.

Fluxo: login -> criar conta -> perfil -> match (só alunos) -> menu principal (Turmas, Atividades, Ágoras).
O roteiro completo está em [`docs/ROTEIRO.md`](docs/ROTEIRO.md).

## Como rodar

Requisito: Python 3.11 ou superior.

```
git clone <URL_DO_REPOSITORIO>
cd pergamo
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

Contas de teste (senha `123456`): `miguel@pergamo.test` (aluno, ainda sem professor) e `renato@pergamo.test` (professor, com alunos na turma).
Há mais 11 professores e 19 alunos fictícios em `data/seed_users.json`.

Testes: `pytest` (rodar da raiz do projeto).

## O que já funciona no kit do dia 0

O esqueleto roda de ponta a ponta com o banco em memória e a classificação por regras, para ninguém esperar ninguém:
login, criar conta, perfil, lista de match com nota, detalhe do professor, fazer match, menu com 3 abas e desvincular.
O que falta (marcado com `TODO` nos arquivos) é a versão real de cada papel.

## Os 4 papéis e os arquivos de cada um

| Papel | Só edita | Falta fazer (TODO) |
|---|---|---|
| 1. Dados e infraestrutura | `pergamo/db/sqlite_repo.py`, `mongo_repo.py`, `seed.py`, `db/__init__.py`, `auth.py`, `config.py`, `data/seed_users.json` | SQLite, MongoDB, seed no SQLite, troca automática para offline |
| 2. IA e match | `pergamo/ml/` (classifier, match, dataset, train), `models/` | Dataset sintético, treino da rede neural, usar o modelo no `classify()` |
| 3. Telas de entrada e integração | `app.py`, `pergamo/ui/login.py`, `cadastro.py`, `perfil.py`, `components.py`, `state.py`, `.streamlit/config.toml`, `requirements.txt` | Visual da Pérgamo, formulário completo de perfil, integração final |
| 4. Telas de match e menu | `pergamo/ui/match.py`, `menu.py`, `data/atividades.json`, `data/agoras.json` | Visual dos cartões e das abas, mais dados fictícios |

Regra de ouro: **cada um edita só os arquivos do seu papel.** Precisa mudar algo de outro papel? Abra uma issue ou avise no grupo.

## Contratos (não mudar sem avisar o grupo)

- `pergamo/db/base.py`: classe `Repo` (todas as funções do banco).
- `pergamo/ml/classifier.py`: `classify(perfil) -> {"label", "probs"}`.
- `pergamo/ml/match.py`: `compatibility(aluno, professor) -> {"score", "reasons"}` e `rank_professors(...)`.
- `pergamo/constants.py`: opções dos formulários, nomes das telas e chaves da sessão.
- Formato do perfil: seção 4.1 do roteiro.

## Trabalhando em grupo

Veja [`CONTRIBUTING.md`](CONTRIBUTING.md) (Git, commits, pull requests) e [`docs/TAREFAS_INICIAIS.md`](docs/TAREFAS_INICIAIS.md) (primeiras tarefas por papel).
Para usar sua IA de apoio com este projeto, veja [`docs/CONTEXTO_IA.md`](docs/CONTEXTO_IA.md).

## Segurança e privacidade

- Nunca envie `.env`, senhas, a URI do MongoDB ou arquivos `.db` ao GitHub (o `.gitignore` já protege, mas confira).
- Use somente dados fictícios. O campo de necessidades específicas de aprendizagem (se criado) é dado sensível pela LGPD.


##  Papel 3: Telas de entrada e Integração

Responsável pelo desenvolvimento da experiência inicial do usuário, fluxo de navegação central, segurança de credenciais e conexão com os módulos de banco de dados e inteligência artificial.

### O que foi entregue:
- **Roteador e Gerenciamento de Sessão (`app.py`): ** Configuração do roteador dinâmico baseado no estado da sessão (`st.session_state`), controlando o fluxo inteligente de telas para novos usuários e contas existentes conforme as regras do roteiro (Login ➔ Perfil ➔ Match / Menu)[cite: 1, 7].
- **Tela de Login (`ui/login.py`): ** Sistema de autenticação integrado ao contrato `Repo`, com validação de credenciais e criptografia de verificação via `bcrypt.
- **Tela de Criação de Conta (`ui/cadastro.py`):** Formulário de cadastro de novos usuários (alunos ou professores) com criptografia de senhas utilizando `bcrypt` para garantir que nenhuma senha fique em texto puro no banco.
- **Tela de Perfil (`ui/perfil.py`):** Formulário dinâmico com campos específicos para alunos e professores, integrando diretamente a função de classificação da Inteligência Artificial (`classify()`) antes de persistir os dados.
- **Identidade Visual (`.streamlit/config.toml`):** Configuração do tema personalizado da Pérgamo (cores oficiais e estilização de interface).

### Como testar esta parte:
1. Certifique-se de que o ambiente virtual está ativo e as dependências instaladas.
2. Execute o comando na raiz do projeto:
   `streamlit run app.py`

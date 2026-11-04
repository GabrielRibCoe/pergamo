# Roteiro do mockup Pérgamo — A3 de Exploração digital

Documento de trabalho para o grupo. Descreve o que vamos construir, com quais tecnologias, como dividir as tarefas e como trabalhar em conjunto até a Amostra da A3 (01/12/2026). Tudo aqui é uma proposta: o que estiver marcado como decisão (seção 13) deve ser confirmado pelo grupo.

## 1. Contexto e prazos

O software da A3 é a solução técnica do mesmo projeto do professor Sérgio. O professor Cristiano avalia o software funcionando, a qualidade do código, a interface e a documentação. Terminal puro não é aceito: precisa de interface gráfica ou web. O uso de IA como apoio é permitido, mas todos os integrantes precisam saber explicar o que foi feito.

| Entrega | Prazo | O que o nosso mockup entrega |
|---|---|---|
| Proposta | 29/10/2026 | Nome, resumo do problema e do público, tecnologias (seção 3). Se ainda não foi entregue, confirmar com o professor Cristiano. |
| Protótipo | 12/11/2026 | Pelo menos uma função central funcionando: cadastro, perfil, rede neural e lista de professores ordenada por compatibilidade. |
| Versão final | 19/11/2026 | Fluxo completo: match, menu com 3 abas, desvincular, banco online e banco offline. |
| Amostra da A3 | 01/12/2026 | Pôster pronto para a parede, com prints, resultados e QR Code. |

## 2. O que vamos construir

Um aplicativo web feito em Python que simula o funcionamento da Pérgamo. Nada precisa funcionar de verdade além do que o roteiro descreve: as abas de atividades e ágoras são apenas visuais.

Fluxo de telas:

```
CONTA NOVA
  Login -> Criar conta -> Perfil (a rede neural classifica ao salvar)
  Perfil de aluno ........ -> Match -> Menu principal
  Perfil de professor .... -> Menu principal

CONTA EXISTENTE (ao entrar, o app decide a próxima tela)
  sem perfil ................... -> Perfil
  aluno sem vínculo ............ -> Match
  aluno com vínculo ............ -> Menu principal
  professor com perfil ......... -> Menu principal

MENU PRINCIPAL
  Abas: Turmas | Atividades | Ágoras
  Turmas -> botão "Desvincular" -> volta para o Match
```

## 3. Tecnologias escolhidas

| Camada | Escolha | Por quê |
|---|---|---|
| Linguagem | Python 3.11 ou superior (todos na mesma versão) | Exigência da disciplina e familiaridade do grupo. |
| Interface | Streamlit | Web, tem abas, formulários, janelas de diálogo e atualização automática de trechos da tela. Curva de aprendizado curta para um grupo com níveis diferentes. |
| Banco offline | SQLite (módulo sqlite3 do Python) | Arquivo único, sem instalação, ideal para contas fictícias e testes. |
| Banco online | MongoDB Atlas (cluster gratuito) com pymongo | Permite mostrar o vínculo aluno-professor entre máquinas diferentes. |
| Rede neural | scikit-learn (MLPClassifier), pandas, numpy, joblib | Rede neural simples, treina em segundos e roda em qualquer notebook. |
| Senhas | bcrypt | Nunca guardar senha em texto puro, nem no mockup. |
| Testes | pytest | Testes rápidos das funções principais. |
| Colaboração | Git e GitHub | Histórico, revisão e divisão de trabalho. |

Comparação das opções de interface:

| Opção | Vantagem | Desvantagem para o nosso caso |
|---|---|---|
| Streamlit (recomendado) | Rápido, bonito sem esforço, abas e formulários prontos, pode ser publicado com link. | Cada clique reexecuta o script, então o estado da tela precisa ficar em st.session_state. |
| Gradio | Ótimo para demonstrar modelos de IA. | Fluxo de várias telas e login é mais trabalhoso. |
| Tkinter | Funciona offline, já vem no Python. | Visual datado e muito mais código para cada tela. |
| Flet | Aparência de aplicativo moderno. | Biblioteca mais nova, menos exemplos e material de apoio. |
| Flask com HTML e CSS | Liberdade total de design. | Mais código e mais tempo; o prazo é curto. |

Observações sobre o Streamlit: o componente st.fragment aceita o parâmetro run_every, que reexecuta só aquele trecho da tela em intervalos fixos, e é isso que usaremos para o efeito de tempo real. Fixem a versão no requirements.txt logo no início, porque os recursos mudam entre versões.

## 4. Arquitetura e estrutura de pastas

A ideia central é separar a interface, o banco e a inteligência artificial por contratos (funções com assinatura combinada). Cada pessoa trabalha atrás do seu contrato, e o resto do app não precisa saber como ele funciona por dentro. Isso reduz conflitos no Git.

```
pergamo/
  app.py                  # ponto de entrada: roteador de telas e estado da sessão
  requirements.txt
  README.md
  .env.example            # modelo das variáveis (sem segredos)
  .gitignore              # ignora .env, .venv, *.db, secrets
  .streamlit/config.toml  # tema (cores da Pérgamo)
  pergamo/
    __init__.py
    config.py             # lê PERGAMO_DB=memory|sqlite|mongo e a URI do Mongo
    constants.py          # opções dos formulários, tipos de perfil, nomes das telas
    state.py              # sessão e navegação entre telas (ir_para, entrar, sair)
    auth.py               # hash e verificação de senha
    db/
      base.py             # contrato Repo (seção 4.1)
      memory_repo.py      # banco em memória (kit do dia 0), para desenvolver sem o banco real
      sqlite_repo.py      # banco offline
      mongo_repo.py       # banco online
      seed.py             # cria contas fictícias
    ml/
      dataset.py          # gera perfis sintéticos
      train.py            # treina e salva models/perfil_model.joblib
      classifier.py       # classify(perfil) -> rótulo e probabilidades
      match.py            # compatibility(aluno, professor) -> nota e motivos
    ui/
      login.py  cadastro.py  perfil.py  match.py  menu.py
      components.py       # cartões, selos e rodapé reutilizáveis
  data/                   # seed_users.json, atividades.json, agoras.json
  models/                 # modelo treinado (gerado por train.py)
  tests/                  # test_auth.py, test_repo.py, test_match.py
```

### 4.1 Contratos combinados

Alterar uma destas assinaturas exige avisar o grupo antes.

```python
# pergamo/db/base.py
from abc import ABC, abstractmethod

class Repo(ABC):
    @abstractmethod
    def create_user(self, email, password_hash, role, name) -> str: ...      # devolve user_id
    @abstractmethod
    def get_user_by_email(self, email) -> dict | None: ...
    @abstractmethod
    def get_user(self, user_id) -> dict | None: ...
    @abstractmethod
    def save_profile(self, user_id, profile: dict) -> None: ...
    @abstractmethod
    def get_profile(self, user_id) -> dict | None: ...
    @abstractmethod
    def list_professors(self) -> list[dict]: ...                             # com perfil
    @abstractmethod
    def create_link(self, student_id, teacher_id) -> None: ...
    @abstractmethod
    def end_link(self, student_id) -> None: ...                              # desvincular
    @abstractmethod
    def get_active_link(self, student_id) -> dict | None: ...
    @abstractmethod
    def get_roster(self, teacher_id) -> list[dict]: ...                      # alunos da turma
```

```python
# pergamo/ml/classifier.py
def classify(profile: dict) -> dict:
    """Ex.: {"label": "Prático", "probs": {"Prático": 0.62, "Visual": 0.21, ...}}"""

# pergamo/ml/match.py
def compatibility(student: dict, teacher: dict) -> dict:
    """Ex.: {"score": 0.87, "reasons": ["Ambos têm perfil prático", "Ritmo gradual"]}"""
```

Formato do perfil (dicionário salvo no banco):

```json
{
  "materias": ["Matemática", "Física"],
  "estilos": ["pratico", "visual"],
  "ritmo": "gradual",
  "estrutura": "estruturada",
  "social": "individual",
  "dificuldades": ["concentracao", "calculos"],
  "nivel": "vestibular",
  "perfil_label": "Prático",
  "perfil_probs": {"Prático": 0.62, "Visual": 0.21, "Ouvinte": 0.07, "Leitor": 0.06, "Racional": 0.04}
}
```

Para professores, o campo estilos descreve como ele ensina (as mesmas opções) e entram também preco_hora, qualidades e experiencia_com.

## 5. Telas e comportamento

| Tela | Conteúdo | Regras |
|---|---|---|
| Login | E-mail, senha, botões Entrar e Criar conta. | Valida contra o banco. Mensagem de erro clara. Conta existente segue a regra de entrada da seção 2. |
| Criar conta | Nome, e-mail, senha, papel (Aluno ou Professor). | Impede e-mail repetido. Salva a senha com bcrypt. |
| Perfil | Formulário conforme o papel (mesmos campos que discutimos nas fichas e nos mockups do Figma Make). | Ao salvar, chama classify() e guarda rótulo e probabilidades. Pode ser pulada só se o perfil já existir. |
| Match (aluno) | Lista ordenada por compatibilidade. Os 5 primeiros levam o selo Alta precisão; os demais aparecem como Mais abrangentes. | Clique abre o detalhe. |
| Detalhe do professor | Foto/iniciais, matérias, método, preço, nota de compatibilidade e Por que combina. | Botões Fazer match e Voltar. O match cria o vínculo (plano gratuito: 1 professor por vez). |
| Menu: Turmas | Professor e colegas de turma (dados reais do banco). | Botão Desvincular encerra o vínculo e volta ao Match. |
| Menu: Atividades | Cartões de atividades por turma, com prazo e status. | Só visual, lê de data/atividades.json. |
| Menu: Ágoras | Lista de comunidades de que o usuário participa, com nível 1 a 3. | Só visual, lê de data/agoras.json. |

Professores não passam pelo Match: depois do perfil vão direto ao menu, e a aba Turmas mostra os alunos vinculados a eles.

## 6. Bancos de dados

### 6.1 Duas versões atrás do mesmo contrato

Os dois bancos implementam a classe Repo. A variável PERGAMO_DB escolhe qual usar. O resto do app não muda.

- Offline (SQLite): arquivo data/pergamo_local.db, criado pelo seed com contas fictícias. Serve para desenvolver, testar e como reserva na Amostra.
- Online (MongoDB Atlas): guarda as contas e os vínculos criados pelo próprio grupo, e permite ver o vínculo aparecer em outro computador.
- Reserva automática: se a conexão com o Mongo falhar ao iniciar, o app cai para o SQLite e mostra um aviso discreto. Na Amostra, a internet do evento pode falhar.

### 6.2 Modelo de dados

| Coleção ou tabela | Campos principais |
|---|---|
| users | id, nome, email (único), senha_hash, papel (aluno ou professor), criado_em |
| profiles | user_id, materias, estilos, ritmo, estrutura, social, dificuldades, nivel, perfil_label, perfil_probs (e preco_hora, qualidades para professores) |
| links | id, aluno_id, professor_id, status (ativo ou encerrado), criado_em, encerrado_em |

Regras: um aluno tem no máximo um vínculo ativo (plano gratuito). Desvincular muda o status para encerrado, sem apagar o histórico.

### 6.3 Dados fictícios (seed)

O seed cria cerca de 12 professores e 20 alunos fictícios, com perfis variados, e já inclui o Miguel (aluno) e o Renato (professor) das nossas personas, para a demonstração ficar coerente com o pôster. Use e-mails no formato nome@pergamo.test e uma senha única de teste, sempre gravada com hash.

### 6.4 Tempo real

O Streamlit não recebe mensagens do servidor sozinho, então o efeito de tempo real é feito por consulta periódica: o trecho da aba Turmas fica dentro de um fragmento com run_every de 3 segundos, que lê o banco e redesenha a lista. Na demonstração: um aluno faz match em um computador e, em até alguns segundos, aparece na turma do professor logado em outro.

### 6.5 Cuidados com o Mongo gratuito

O cluster gratuito do Atlas tem 512 MB de armazenamento, limite de 100 operações por segundo, limite de transferência de dados em janela de 7 dias, não tem backup automático, e clusters ociosos podem ser pausados ou encerrados. Para nós isso é suficiente, com estas precauções:

- Um integrante cria o cluster e convida os demais, ou compartilha a URI por canal privado.
- A URI e as senhas ficam em .env ou em .streamlit/secrets.toml, nunca no GitHub.
- Criar um usuário do banco só para o app, com permissão apenas no banco da Pérgamo.
- Entrar no cluster um ou dois dias antes da Amostra para garantir que está ativo.
- Se for preciso liberar o acesso para qualquer IP (o IP do evento muda), usar só dados fictícios e trocar a senha do usuário depois.

### 6.6 Privacidade no mockup

O campo de necessidades específicas de aprendizagem (como TDAH ou dislexia) é dado de saúde, tratado como dado sensível pela LGPD. No mockup, usar apenas dados fictícios e pedir que colegas testadores não informem dados reais. Deixar o campo opcional, como já planejamos.

## 7. Rede neural e algoritmo de match

### 7.1 O que ela faz

A rede recebe as respostas de um perfil e devolve a probabilidade de cada tipo de perfil pedagógico. O mesmo modelo classifica alunos (como aprendem) e professores (como ensinam), então os dois ficam na mesma escala e podem ser comparados.

Tipos sugeridos: Prático (foco em atividades), Ouvinte (aprende ouvindo a explicação), Visual, Leitor (leitura e escrita) e Racional (prefere entender a lógica e resolver por conta própria). Para o tipo Racional existir, o formulário precisa de uma opção como Raciocínio lógico.

### 7.2 Como treinar sem dados reais

Não temos dados reais, então o script dataset.py gera cerca de 2.000 perfis fictícios: sorteia respostas e define o rótulo por regras de pontos combinadas pelo grupo, com um pouco de ruído (cerca de 10% de rótulos trocados). Exemplos de regras para ajustar em conjunto:

| Tipo | Pontos principais |
|---|---|
| Prático | Estilo prático (+3), ritmo rápido (+1) |
| Ouvinte | Estilo auditivo (+3), social em debate (+1) |
| Visual | Estilo visual (+3) |
| Leitor | Leitura e escrita (+3), estrutura estruturada (+1) |
| Racional | Raciocínio lógico (+3), social individual (+1) |

Os métodos de ensino do professor entram na mesma escala por uma tabela de conversão: Teoria primeiro vale Leitor e Racional, Prática guiada vale Prático, Socrático vale Racional e Ouvinte, Visual e recursos vale Visual.

### 7.3 Modelo

MLPClassifier do scikit-learn com 2 camadas escondidas pequenas (por exemplo 16 e 8 neurônios), divisão 80% treino e 20% teste. O script train.py treina, mostra a acurácia no teste e salva o modelo com joblib. O classifier.py carrega o modelo uma vez só. O resultado (rótulo e probabilidades) é gravado no perfil, para não recalcular a cada tela. Se o arquivo do modelo ainda não existir, classify() usa uma regra simples (a mesma do dataset), assim a interface funciona antes do treino.

### 7.4 Nota de compatibilidade

```
nota = 0,60 x similaridade_do_cosseno(probs_aluno, probs_professor)
     + 0,25 x cobertura_de_matérias   (matérias do aluno que o professor ensina / matérias do aluno)
     + 0,15 x encaixe_de_estilo       (quantos de ritmo, estrutura e social coincidem, de 0 a 3, dividido por 3)
```

O professor só aparece se ensinar pelo menos uma das matérias do aluno. A nota é mostrada em porcentagem, e os motivos (Por que combina) saem das coincidências mais fortes. Os pesos são um ponto de partida e podem ser ajustados.

### 7.5 Limite honesto (importante para o pôster)

A rede aprende regras que nós mesmos definimos, então a acurácia mede o quanto ela imita essas regras, não se o match realmente melhora o aprendizado. No pôster, apresentar como simulação do algoritmo. Uma versão real precisaria de dados de uso, como avaliações das aulas e taxa de alunos que continuam com o professor.

## 8. Divisão de tarefas para 4 pessoas

Quatro pessoas é um bom número: o projeto tem quatro blocos que podem andar em paralelo (banco, inteligência artificial, telas de entrada e telas de match e menu). Com três pessoas, as telas virariam um gargalo; com cinco, haveria mais gente do que trabalho independente.

### 8.1 Regras para ninguém depender de ninguém

1. Cada pessoa é dona de pastas e arquivos próprios (tabela 8.3) e só edita o que é seu.
2. Os contratos da seção 4.1 são congelados no dia 0. Mudar uma assinatura exige avisar o grupo antes.
3. Quem precisa de uma peça que ainda não existe usa o substituto (stub) do kit do dia 0 e segue em frente. Ninguém espera pelo outro.
4. Os dados de teste são os mesmos para todos (data/seed_users.json), então cada módulo pode ser testado sozinho.
5. Os módulos só se encontram em três datas de integração: 09/11, 11/11 (congelamento do protótipo) e 17/11 (congelamento da versão final).
6. Quem travar avisa no grupo no mesmo dia e pede ajuda ao seu reserva (tabela 8.3).

### 8.2 Kit do dia 0 (feito juntos na reunião de largada)

Antes de dividir, o grupo congela cinco coisas. Elas ocupam cerca de duas horas e evitam quase todos os conflitos depois:

- O formato do perfil (dicionário da seção 4.1) e os nomes das opções de cada campo.
- A classe Repo (seção 4.1) e uma versão em memória dela, a memory_repo.py, que lê data/seed_users.json.
- As assinaturas de classify() e compatibility(), com versões simples de teste (a classificação por regra e uma nota calculada sem rede).
- Os nomes das telas e as chaves do estado da sessão: login, cadastro, perfil, match e menu, e as chaves user_id, papel e tela.
- O roteador do app.py com um registro de telas (um dicionário nome da tela para função render(repo)), para cada tela ser um arquivo independente.

Esse kit já existe como esqueleto de repositório, pronto para ir ao Git (veja o README do projeto).

### 8.3 Os 4 papéis

| Papel | Arquivos e pastas só dele | Entrega principal | Por que não depende dos outros |
|---|---|---|---|
| 1. Dados e infraestrutura | pergamo/db/ (sqlite_repo, mongo_repo, seed), auth.py, config.py, data/seed_users.json, tests/test_auth.py e test_repo.py | Bancos offline e online funcionando, seed, reserva automática, atualização periódica, senhas com hash | Trabalha só contra o contrato Repo. Para ele, um perfil é apenas um dicionário. |
| 2. IA e match | pergamo/ml/, models/, tests/test_match.py | Dataset sintético, treino, classify(), compatibility(), acurácia | Usa o formato do perfil e os dados de teste. A tela já funciona com o substituto dele desde o dia 0. |
| 3. Telas de entrada e integração | app.py, ui/login.py, cadastro.py, perfil.py, components.py, .streamlit/config.toml, requirements.txt, README.md | Login, criar conta, formulário de perfil, tema da Pérgamo, roteador, integração final | Usa a memory_repo e o classify() de teste até as peças reais chegarem. |
| 4. Telas de match e menu | ui/match.py, ui/menu.py, data/atividades.json, data/agoras.json | Lista de match, detalhe do professor, decisão, menu com 3 abas, desvincular, atualização da turma | Usa a memory_repo e o compatibility() de teste. Só precisa do nome da tela e da função render(). |

Reservas (quem cobre quem se alguém travar): 1 e 2 se cobrem (lado dos dados e da lógica); 3 e 4 se cobrem (lado das telas).

### 8.4 Tarefas que cruzam os papéis

Cada pessoa escreve os testes e a seção do README sobre a própria parte. O pôster, o vídeo e o teste com usuários são divididos para ninguém ficar sobrecarregado:

| Papel | Também fica com |
|---|---|
| 1. Dados e infraestrutura | Prints finais do app, QR Code, organização do repositório e vídeo de demonstração, além da impressão do pôster. |
| 2. IA e match | Texto do pôster sobre a inteligência artificial e os resultados (acurácia no teste, com o aviso de que é simulação). |
| 3. Telas de entrada e integração | Layout e montagem do pôster, e a integração final do app. |
| 4. Telas de match e menu | Roteiro da demonstração e teste com 5 a 10 pessoas (nota de 1 a 5 de clareza e tempo para completar o fluxo). |

Todos devem conseguir explicar o projeto inteiro. Por isso, a seção 10.3 prevê um rodízio de explicação, e cada pessoa precisa entender também o contrato dos outros blocos.

## 9. Cronograma

| Período | Foco | Resultado esperado |
|---|---|---|
| Sáb 31/10 a Seg 02/11 | Largada | Reunião de 2 horas: confirmar a seção 13 e congelar o kit do dia 0 (seção 8.2). Criar repositório, quadro de tarefas e cluster. Todos instalam o ambiente. |
| Ter 03/11 a Dom 08/11 | Sprint 1 | SQLite e seed, login e cadastro, formulários de perfil, dataset e treino, esqueleto das telas. |
| Seg 09/11 a Qua 11/11 | Integração | Perfil chama a rede neural; tela de match lista professores com nota. Congelar o código na quarta para testar. |
| Qui 12/11 | Entrega do protótipo | Função central funcionando (cadastro, perfil, rede e match). |
| Sex 13/11 a Qua 18/11 | Sprint 2 | Detalhe e decisão de match, menu com 3 abas, desvincular, Mongo, atualização periódica, reserva offline, testes. |
| Qui 19/11 | Versão final | Código completo e funcionando, README pronto. |
| Sex 20/11 a Seg 30/11 | Pôster e ensaio | Teste com 5 a 10 pessoas, prints, vídeo, QR Code, pôster impresso (ideal até 27/11) e ensaio da apresentação. |
| Ter 01/12 | Amostra da A3 | Pôster na parede e demonstração. |

Escopo em três níveis, para decidir o que cortar se o tempo apertar:

- Essencial (até 12/11): login, cadastro, perfil, rede neural, lista de match com nota.
- Completo (até 19/11): detalhe, decisão, menu com 3 abas, desvincular, banco online com atualização periódica.
- Extra (só se sobrar tempo): simular o Plano Único com 3 professores, níveis de ágora, alerta de uso indevido, tema escuro.

## 10. Como trabalhar juntos

### 10.1 Configuração inicial (cada pessoa)

```
git clone <URL_DO_REPOSITORIO>
cd pergamo
python -m venv .venv
.venv\Scripts\activate          # Windows   (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python -m pergamo.db.seed       # cria o banco local com contas fictícias
python -m pergamo.ml.train      # gera o dataset sintético e treina a rede
streamlit run app.py
```

O requirements.txt deve ter versões fixas (gerar com pip freeze depois da primeira instalação que funcione para todos).

### 10.2 Regras de Git

- A branch main sempre deve rodar. Ninguém envia código quebrado direto para ela.
- Cada tarefa tem sua branch, com nome como feat/ana-tela-login ou fix/joao-seed.
- Commits pequenos e frequentes, com mensagem curta no formato feat:, fix: ou docs:.
- Pedido de mesclagem (pull request) com pelo menos uma pessoa revisando. Antes de abrir: rodar o app e o pytest.
- Antes de começar a trabalhar, atualizar com git pull. Conflito: resolver conversando com a outra pessoa, não apagando o trabalho dela.
- Nunca enviar .env, secrets, arquivos .db, a pasta .venv ou a senha do banco.
- Quem não tem experiência com Git pode usar o GitHub Desktop ou a aba de controle de versão do VS Code. O Live Share do VS Code ajuda em programação em dupla.

### 10.3 Organização do dia a dia

- Quadro de tarefas (GitHub Projects ou Trello) com colunas A fazer, Fazendo, Revisão e Feito. Cada cartão com responsável e papel.
- Duas reuniões curtas por semana (20 a 30 minutos) e um grupo de mensagens para dúvidas. Cada pessoa avisa o que fez, o que vai fazer e o que está travando.
- Cada pessoa escreve no README uma seção sobre a própria parte. Isso resolve a exigência de documentação e prepara todos para explicar o projeto.
- Rodízio de explicação: a cada semana, uma pessoa explica ao grupo uma parte que não é dela. Se usarem IA para gerar código, só entra no repositório o que o autor consegue explicar linha a linha.

## 11. Testes e roteiro de demonstração

Testes automáticos (pytest): senha com hash e verificação; criar usuário e impedir e-mail repetido; salvar e ler perfil; criar e encerrar vínculo; compatibilidade entre 0 e 1 e ordenação correta.

Checklist manual antes de cada entrega:

1. Criar conta de aluno, preencher perfil e ver a lista de professores.
2. Abrir um professor, fazer match e chegar ao menu com 3 abas.
3. Sair, entrar de novo com a mesma conta e cair direto no menu.
4. Desvincular e voltar para o match.
5. Criar conta de professor e ver, em outro navegador, o aluno aparecer na turma em poucos segundos.
6. Desligar a internet e confirmar que o app cai para o banco offline.

Roteiro da demonstração (3 a 4 minutos): apresentar o problema com a persona Miguel, criar a conta dele, mostrar a classificação da rede neural, mostrar o match com nota e motivos, fazer o vínculo e mostrar a aparição do aluno na tela do professor Renato.

## 12. Pôster: o que já temos e o que falta

O pôster precisa de título, disciplina e integrantes, problema e público, solução e tecnologias, prints do software, resultados e conclusões, e de preferência um QR Code para o repositório ou vídeo.

- Já temos: problema, público e personas, jornadas, proposta de valor e identidade visual.
- Resultados honestos para colocar: acurácia da rede no conjunto de teste (explicando que é simulação), tempo para completar o fluxo e uma nota de 1 a 5 de clareza dada por 5 a 10 pessoas que testarem o mockup.
- Prints: pegar do app final, com dados fictícios.
- Textos curtos e letras grandes, conforme as recomendações da disciplina.

## 13. Decisões a confirmar com o grupo

1. Fluxo do professor: sem tela de match, indo direto ao menu. De acordo?
2. No mockup, simular só o plano gratuito (1 professor)? Recomendado, deixando o Plano Único como extra.
3. Quem assume cada um dos 4 papéis (seção 8.3), considerando a afinidade de cada um.
4. Quem cria a conta e o cluster no MongoDB Atlas.
5. Tamanho e formato do pôster segundo a organização do evento.
6. A Proposta de 29/10 foi entregue? As tecnologias descritas nela batem com a seção 3?
7. Qualquer mudança em relação ao projeto do professor Sérgio deve ser comunicada aos dois professores.

<!--pagebreak-->

## Apêndice A. Contexto para colar na sua IA

Este roteiro serve de contexto para as IAs que cada integrante usar. Cole na conversa o texto abaixo, junto com as seções 2, 4, 5 e a seção da sua parte (6, 7 ou 8.3), e preencha a linha MINHA PARTE.

```
Você é um assistente de programação ajudando um grupo de 4 estudantes em um projeto de
faculdade (A3 de Exploração digital). Leia o contexto e siga as regras.

PROJETO: mockup em Python (Streamlit) da Pérgamo, plataforma que conecta alunos e professores
particulares por afinidade pedagógica. Fluxo: login -> criar conta -> perfil -> match (só
aluno) -> menu principal com 3 abas visuais (Turmas, Atividades, Ágoras). Bancos: SQLite
(offline, contas fictícias) e MongoDB Atlas (online). Uma rede neural simples (scikit-learn
MLPClassifier, treinada com perfis sintéticos) classifica o perfil e alimenta a nota de
compatibilidade entre aluno e professor. Tudo é simulação, com dados fictícios.

ARQUITETURA: pastas pergamo/db, pergamo/ml, pergamo/ui e app.py (roteador). Os contratos
(classe Repo, classify, compatibility e o formato do perfil) estão no roteiro e não podem
mudar sem aviso ao grupo.

MINHA PARTE: [papel + arquivos, conforme a tabela 8.3]

REGRAS:
1. Mexa apenas nos arquivos da minha parte.
2. Não altere as assinaturas dos contratos.
3. Escreva código simples, com comentários em português, que um estudante consiga explicar
   linha a linha.
4. Depois de cada trecho, explique o que ele faz, por que foi feito assim e como testar.
5. Use só dados fictícios. Nunca coloque senhas ou URIs de banco no código.
6. Python 3.11 ou superior e as versões do requirements.txt.
```

Linha MINHA PARTE sugerida para cada papel:

| Papel | Texto para colocar em MINHA PARTE |
|---|---|
| 1. Dados e infraestrutura | Implementar Repo em SQLite e MongoDB, o seed com contas fictícias, a troca automática para offline e a senha com bcrypt (pastas pergamo/db e auth.py). |
| 2. IA e match | Gerar o dataset sintético, treinar o MLPClassifier, escrever classify() e compatibility() e medir a acurácia (pasta pergamo/ml). |
| 3. Telas de entrada e integração | Roteador do app.py e telas de login, cadastro e perfil em Streamlit, com o tema da Pérgamo (app.py e ui/login, cadastro, perfil). |
| 4. Telas de match e menu | Tela de match com detalhe e decisão e o menu com 3 abas, com desvincular e atualização automática da turma (ui/match e ui/menu). |

Dicas para usar a IA sem se perder: peça sempre para ela explicar o código; teste cada trecho antes de enviar ao grupo; e, se a IA sugerir mudar um contrato, leve a ideia ao grupo em vez de aceitar sozinho.


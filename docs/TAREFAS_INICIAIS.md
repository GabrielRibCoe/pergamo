# Primeiras tarefas por papel

Crie uma issue para cada item (modelo em `.github/ISSUE_TEMPLATE/tarefa.md`) ou copie para o quadro de tarefas.
Prazos: protótipo em 12/11, versão final em 19/11.

## Todos (reunião de largada, 31/10 a 02/11)
- [ ] Ler o `docs/ROTEIRO.md` e confirmar a seção 13 (decisões)
- [ ] Instalar o ambiente e rodar `streamlit run app.py` e `pytest`
- [ ] Definir quem assume cada papel e o reserva
- [ ] Combinar os dias das duas reuniões semanais

## Papel 1 — Dados e infraestrutura
- [ ] `SqliteRepo` passando em `tests/test_contract.py` (adicionar em `FABRICAS`)
- [ ] `seed.py`: criar `data/pergamo_local.db` com `data/seed_users.json`
- [ ] Cluster do MongoDB Atlas, usuário só para o app e URI no `.env`
- [ ] `MongoRepo` passando nos mesmos testes
- [ ] `get_repo()` com troca automática para o SQLite se o Mongo falhar
- [ ] Revisar `auth.py` e o uso de senhas com hash

## Papel 2 — IA e match
- [ ] `dataset.py`: gerar ~2.000 perfis sintéticos rotulados pelas regras, com ~10% de ruído
- [ ] `train.py`: treinar o `MLPClassifier`, mostrar a acurácia e salvar em `models/perfil_model.joblib`
- [ ] `classify()` usando o modelo (com fallback por regras se o arquivo não existir)
- [ ] Ajustar os pesos e os motivos de `compatibility()`
- [ ] Testes em `tests/test_match.py` e anotar a acurácia para o pôster

## Papel 3 — Telas de entrada e integração
- [ ] Tema e identidade visual da Pérgamo (cores, título, logo)
- [ ] Formulário de perfil completo (campos das fichas e da proposta de valor)
- [ ] Mensagens de erro e validações claras em login e cadastro
- [ ] Revisar pull requests e manter `requirements.txt` e README em dia
- [ ] Integração final nas datas 09/11, 11/11 e 17/11

## Papel 4 — Telas de match e menu
- [ ] Visual dos cartões de professor e da tela de detalhe
- [ ] Mais dados fictícios em `data/atividades.json` e `data/agoras.json`
- [ ] Aba Turmas para professor e para aluno, com atualização automática a cada 3 segundos
- [ ] Roteiro da demonstração e teste com 5 a 10 pessoas

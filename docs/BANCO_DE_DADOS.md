# Guia do banco de dados (papel 1: Dados e infraestrutura)

O app tem três bancos, todos com o mesmo contrato (`pergamo/db/base.py`). A variável `PERGAMO_DB` escolhe qual usar:

| `PERGAMO_DB` | Banco | Quando usar |
|---|---|---|
| `memory` | Memória (some ao reiniciar) | Só nos testes automáticos |
| `sqlite` | Arquivo `data/pergamo_local.db` (offline) | Desenvolvimento e plano B na Amostra |
| `mongo` | MongoDB Atlas (online) | Demonstração em tempo real entre computadores |

**Reserva automática:** se o `mongo` não conectar, o app cai sozinho para o `sqlite` e mostra um aviso. Se o `sqlite` falhar, cai para a memória. O banco realmente em uso fica em `repo.modo` e o aviso em `repo.aviso`.

## 1. SQLite (offline)

Não precisa instalar nada. Na primeira execução o arquivo é criado e as contas fictícias (Miguel, Renato e os outros) são carregadas sozinhas.

```
# no arquivo .env
PERGAMO_DB=sqlite
```

Para apagar tudo e recarregar as contas fictícias: `python -m pergamo.db.seed --zerar`.
Os dados ficam salvos mesmo se o app for reiniciado, então dá para entrar em uma conta criada antes.

## 2. MongoDB Atlas (online): passo a passo

Os nomes dos menus do Atlas podem variar um pouco, mas as etapas são estas.

1. **Criar o usuário do banco.** No Atlas, abra *Database Access* e crie um usuário com senha (por exemplo `pergamo_app`). Use uma senha forte **sem** os caracteres `@ : / ?`, que complicam a URI. Dê permissão de leitura e escrita (de preferência só no banco `pergamo`).
2. **Liberar o IP.** Em *Network Access*, adicione o seu IP atual. Para a Amostra, o IP do evento é desconhecido: dá para liberar "de qualquer lugar" (`0.0.0.0/0`), mas **só com dados fictícios**, e trocando a senha do usuário depois.
3. **Copiar a URI.** Em *Database*, clique em *Connect*, escolha *Drivers* e copie a string que começa com `mongodb+srv://`. Troque `<password>` pela senha do passo 1.
4. **Colocar no `.env`** (arquivo que **não** vai para o Git):

```
PERGAMO_DB=mongo
PERGAMO_MONGO_URI=mongodb+srv://pergamo_app:SUA_SENHA@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
PERGAMO_MONGO_DB=pergamo
```

5. **Testar a conexão:** `python -m pergamo.db.testar_mongo`. Ele diz o que deu certo e, se falhar, qual é a causa mais provável.
6. **Carregar as contas fictícias:** `python -m pergamo.db.seed --banco mongo`. É seguro rodar de novo: não duplica nada.
7. **Rodar o app:** `streamlit run app.py`.
8. **Compartilhar com o grupo:** cada integrante cria o próprio `.env` com a mesma URI (enviada em canal privado, nunca no GitHub). O IP de cada um precisa estar liberado.

## 3. Demonstração de tempo real

1. Abra o app em dois navegadores (ou em dois computadores, os dois com `PERGAMO_DB=mongo`).
2. Em um, entre como professor (`renato@pergamo.test`, senha `123456`) e deixe na aba Turmas.
3. No outro, entre como aluno (`miguel@pergamo.test`), abra um professor e faça o match com o Renato.
4. Em até 3 segundos, o Miguel aparece na turma do Renato, sem recarregar a página.

## 4. Problemas comuns

| Sintoma | Causa provável | Como resolver |
|---|---|---|
| Tempo esgotado ao conectar | IP não liberado, sem internet ou cluster pausado | Libere o IP em *Network Access* e confira se o cluster está ativo |
| Usuário ou senha recusados | Credenciais do banco erradas | Use o usuário e a senha do *Database Access*, não os da conta do Atlas |
| Erro de DNS ou `mongodb+srv` | Falta o pacote `dnspython` | `pip install dnspython` |
| O app mostra "Banco: sqlite" e um aviso | O Mongo não conectou e o app usou a reserva | Rode `python -m pergamo.db.testar_mongo` |
| Contas somem ao reiniciar | O banco em uso é `memory` | Coloque `PERGAMO_DB=sqlite` (ou `mongo`) no `.env` |

## 5. Antes da Amostra (01/12)

- Entre no Atlas um ou dois dias antes: clusters gratuitos podem ser pausados por inatividade.
- Rode `python -m pergamo.db.testar_mongo` no computador da apresentação.
- Para limpar as contas de teste: `python -m pergamo.db.seed --banco mongo --zerar` (pede confirmação) e depois carregue o seed de novo.
- Deixe o plano B pronto: com `PERGAMO_DB=sqlite` o app funciona sem internet.
- Depois da Amostra, troque a senha do usuário do banco.

## 6. Mostrar o banco em uso na tela (papel 3)

No `app.py`, a barra lateral pode mostrar o banco real (e o aviso de reserva):

```python
st.caption(f"Banco: {getattr(repo, 'modo', config.DB_MODE)}")
if getattr(repo, "aviso", None):
    st.warning(repo.aviso)
```

## 7. Testes

`pytest` roda o mesmo conjunto de testes de contrato contra a memória, o SQLite e um MongoDB **falso** (`mongomock`, sem internet). Para isso, adicione ao `requirements.txt` a linha `mongomock==4.3.0`. O teste da conexão real é o `testar_mongo`.

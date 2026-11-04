# Como trabalhar neste repositório

## Regras de Git

1. A branch `main` sempre deve rodar. Ninguém envia código quebrado direto para ela.
2. Cada tarefa tem a sua branch: `feat/ana-tela-login`, `fix/joao-seed`, `docs/maria-readme`.
3. Commits pequenos e frequentes, com mensagem curta e prefixo: `feat:`, `fix:` ou `docs:`.
   Exemplo: `feat: tela de login valida senha com bcrypt`.
4. Abra um **pull request** para a `main` e peça revisão de pelo menos uma pessoa. Antes de abrir:
   rode `streamlit run app.py` e `pytest`.
5. Antes de começar a trabalhar, atualize: `git pull`. Em caso de conflito, resolva conversando com a outra pessoa.
6. Nunca envie `.env`, senhas, URI do banco, arquivos `.db` ou a pasta `.venv`.

## Fluxo no dia a dia

```
git checkout main
git pull
git checkout -b feat/seu-nome-sua-tarefa
# ...trabalha, testa...
git add .
git commit -m "feat: descrição curta"
git push -u origin feat/seu-nome-sua-tarefa
# abra o pull request no GitHub
```

Quem não tem prática com Git pode usar o GitHub Desktop ou a aba de controle de versão do VS Code.

## Combinados do grupo

- Cada pessoa só edita os arquivos do seu papel (tabela no README).
- Mudar um contrato (`db/base.py`, `classify`, `compatibility`, `constants.py`) exige avisar o grupo antes.
- Faltou uma peça de outro papel? Use o substituto do kit (banco em memória, classificação por regras) e siga em frente.
- Datas de integração: 09/11, 11/11 (congelar o protótipo) e 17/11 (congelar a versão final).
- Cada pessoa escreve no README a seção da própria parte e os testes dela.
- Se usar IA para gerar código, só entra no repositório o que você consegue explicar linha a linha.

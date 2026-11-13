"""Cria o banco offline com as contas fictícias de data/seed_users.json.
RESPONSÁVEL: papel 1 (Dados e infraestrutura).

Uso (quando o SqliteRepo estiver pronto):  python -m pergamo.db.seed
Ideia: ler o JSON, hashear a senha de teste (auth.hash_password), chamar repo.create_user,
repo.save_profile (use classify() para preencher perfil_label e perfil_probs) e repo.create_link.
O MemoryRepo (memory_repo.py) já faz isso em memória: use como referência.
"""

if __name__ == "__main__":
    print("TODO (papel 1 - Dados): implementar o seed do SQLite. Veja a docstring deste arquivo.")

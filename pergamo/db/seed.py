"""Carrega as contas fictícias de data/seed_users.json em um banco. RESPONSÁVEL: papel 1 (Dados e infraestrutura).

Uso:
    python -m pergamo.db.seed                  # SQLite offline (padrão)
    python -m pergamo.db.seed --banco mongo    # MongoDB online (usa PERGAMO_MONGO_URI do .env)
    python -m pergamo.db.seed --zerar          # apaga tudo antes (no Mongo pede confirmação)

É seguro rodar mais de uma vez: contas que já existem são puladas, e os vínculos só são criados
para as contas criadas nesta execução.
"""
import argparse
import json
from pathlib import Path

from pergamo import config
from pergamo import constants as C
from pergamo.auth import hash_password
from pergamo.config import DATA_DIR
from pergamo.ml.classifier import classify


def carregar_seed(repo, caminho: Path | str | None = None) -> dict:
    """Cria no banco as contas, perfis (já classificados pela IA) e vínculos do seed."""
    dados = json.loads(Path(caminho or DATA_DIR / "seed_users.json").read_text(encoding="utf-8"))
    senha_hash = hash_password(dados.get("senha_teste", C.SENHA_TESTE), rounds=4)  # um hash só (rápido)

    novos = set()
    for u in dados.get("usuarios", []):
        if repo.get_user_by_email(u["email"]):
            continue  # já existe: não duplica
        user_id = repo.create_user(u["email"], senha_hash, u["papel"], u["nome"])
        perfil = dict(u["perfil"])
        resultado = classify(perfil)
        perfil["perfil_label"], perfil["perfil_probs"] = resultado["label"], resultado["probs"]
        repo.save_profile(user_id, perfil)
        novos.add(u["email"].strip().lower())

    vinculos = 0
    for v in dados.get("vinculos", []):
        if v["aluno"].strip().lower() not in novos:
            continue
        aluno, professor = repo.get_user_by_email(v["aluno"]), repo.get_user_by_email(v["professor"])
        if aluno and professor and repo.get_active_link(aluno["id"]) is None:
            repo.create_link(aluno["id"], professor["id"])
            vinculos += 1
    return {"contas_criadas": len(novos), "vinculos_criados": vinculos}


def _abrir_banco(banco: str):
    if banco == "mongo":
        from pergamo.db.mongo_repo import MongoRepo

        return MongoRepo(config.MONGO_URI, config.MONGO_DB_NAME)
    from pergamo.db.sqlite_repo import SqliteRepo

    return SqliteRepo(config.SQLITE_PATH)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Carrega as contas fictícias no banco da Pérgamo.")
    ap.add_argument("--banco", choices=["sqlite", "mongo"], default="sqlite")
    ap.add_argument("--zerar", action="store_true", help="apaga todas as contas, perfis e vínculos antes")
    args = ap.parse_args()

    repo = _abrir_banco(args.banco)
    if args.zerar:
        if args.banco == "mongo" and input("Isto APAGA todas as contas do MongoDB. Digite SIM para continuar: ") != "SIM":
            raise SystemExit("Cancelado.")
        repo.limpar()
        print("Banco zerado.")
    resumo = carregar_seed(repo)
    print(f"Banco: {args.banco} | contas criadas: {resumo['contas_criadas']} | vínculos criados: {resumo['vinculos_criados']}")

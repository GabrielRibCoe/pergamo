"""Diagnóstico da conexão com o MongoDB Atlas. RESPONSÁVEL: papel 1 (Dados e infraestrutura).

Uso:  python -m pergamo.db.testar_mongo
Confere, passo a passo, se a URI do .env funciona e explica o erro mais provável se falhar.
(A URI nunca é mostrada na tela.)
"""
import sys

from pergamo import config


def main() -> int:
    if not config.MONGO_URI:
        print("[ERRO] PERGAMO_MONGO_URI está vazio. Copie .env.example para .env e cole a URI do Atlas.")
        return 1
    print("[ok] URI encontrada no .env")

    from pymongo import MongoClient
    from pymongo.errors import ConfigurationError, OperationFailure, ServerSelectionTimeoutError

    try:
        client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=8000)
        client.admin.command("ping")
    except ConfigurationError as erro:
        print(f"[ERRO] URI inválida ou DNS: {erro}")
        print("  -> Confira se copiou a URI inteira. Se for mongodb+srv, rode: pip install dnspython")
        return 1
    except OperationFailure as erro:
        print(f"[ERRO] O Atlas recusou o usuário ou a senha: {erro}")
        print("  -> Confira o usuário e a senha do banco (não é a senha da conta do Atlas).")
        print("  -> Se a senha tem caracteres especiais (@ : / ?), troque a senha ou codifique-a na URI.")
        return 1
    except ServerSelectionTimeoutError:
        print("[ERRO] Não foi possível conectar ao cluster (tempo esgotado).")
        print("  -> O mais comum: o seu IP não está liberado no Atlas (Network Access).")
        print("  -> Outras causas: sem internet, URI errada ou cluster pausado.")
        return 1
    print("[ok] Conectado ao cluster (ping respondeu)")

    from pergamo.db.mongo_repo import MongoRepo

    repo = MongoRepo(client=client, nome_banco=config.MONGO_DB_NAME)
    print(f"[ok] Banco '{config.MONGO_DB_NAME}' pronto, índices criados")
    print(f"     contas: {repo._users.count_documents({})} | perfis: {repo._profiles.count_documents({})} | "
          f"vínculos: {repo._links.count_documents({})}")
    if repo.vazio():
        print("[dica] O banco está vazio. Para carregar as contas fictícias: python -m pergamo.db.seed --banco mongo")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Senhas com hash (bcrypt). Nunca guarde senha em texto puro, nem no mockup."""
import bcrypt


def hash_password(senha: str, rounds: int = 12) -> str:
    """Devolve o hash da senha como texto. rounds menor = mais rápido (use 4 só no seed)."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(rounds=rounds)).decode("utf-8")


def verify_password(senha: str, senha_hash: str) -> bool:
    """Confere a senha digitada com o hash guardado."""
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except ValueError:
        return False

"""Configuração do app. Lê variáveis de ambiente (ou do arquivo .env).

PERGAMO_DB escolhe o banco:
    memory  -> banco em memória (padrão do kit, ótimo para desenvolver as telas)
    sqlite  -> banco offline (arquivo data/pergamo_local.db)
    mongo   -> banco online (MongoDB Atlas)
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv é opcional
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

DB_MODE = os.getenv("PERGAMO_DB", "memory").lower()
SQLITE_PATH = os.getenv("PERGAMO_SQLITE_PATH", str(DATA_DIR / "pergamo_local.db"))
MONGO_URI = os.getenv("PERGAMO_MONGO_URI", "")
MONGO_DB_NAME = os.getenv("PERGAMO_MONGO_DB", "pergamo")

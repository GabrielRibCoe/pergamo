import os
import sys
from pathlib import Path

# Os testes SEMPRE usam o banco em memória, mesmo que o seu .env aponte para SQLite ou MongoDB.
os.environ["PERGAMO_DB"] = "memory"

# Permite rodar `pytest` da raiz do projeto sem instalar o pacote
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

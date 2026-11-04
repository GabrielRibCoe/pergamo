import sys
from pathlib import Path

# Permite rodar `pytest` da raiz do projeto sem instalar o pacote
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

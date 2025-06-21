#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Añadir src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importar el módulo CLI de Streamlit
from streamlit.web import cli as stcli

if __name__ == "__main__":
    # Configurar los argumentos para el CLI de Streamlit
    sys.argv = ["streamlit", "run", str(project_root / "src" / "rag_interface.py")]
    
    # Ejecutar la aplicación Streamlit
    sys.exit(stcli.main())

"""Executa os quatro scripts da Etapa 12, na ordem correta."""
from pathlib import Path
import subprocess
import sys

PASTA = Path(__file__).resolve().parent

SCRIPTS = [
    "01_preparar_territorio.py",
    "02_preparar_projecoes_parametros.py",
    "03_preparar_servicos_indicadores.py",
    "04_preparar_indicadores_territoriais.py",
]

for script in SCRIPTS:
    print(f"\nExecutando {script}...", flush=True)
    subprocess.run([sys.executable, str(PASTA / script)], check=True, cwd=PASTA)

print("\nEtapa 12 concluida: oito CSVs gerados.")

from pathlib import Path
import subprocess
import sys

PASTA = Path(__file__).resolve().parent
SCRIPTS = [
    '01_calcular_populacao_apg.py',
    '02_calcular_projecoes.py',
    '03_calcular_perfis_demanda.py',
    '04_consolidar_indicadores.py',
    '05_validar_etapa11.py',
]

for script in SCRIPTS:
    print(f'\n>>> Executando {script} ...', flush=True)
    subprocess.run([sys.executable, str(PASTA / script)], cwd=PASTA, check=True)

print('\nTODOS OS SCRIPTS CONCLUIDOS. Consulte Arquivos Gerados/.')

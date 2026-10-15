
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Carrega as configurações do arquivo .env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Função para conectar ao PostgreSQL
def conectar():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )

# teste:
#python -c "from app.database import conectar; conn=conectar(); print('APGs:', conn.execute('SELECT COUNT(*) FROM apg').fetchone()[0]); conn.close()"
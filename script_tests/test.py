import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_acess import get_connection

conexao = get_connection()
cursor = conexao.cursor()

try:
    cursor.execute(
        """
        ALTER TABLE treinos_lista
        ADD COLUMN peso REAL NOT NULL DEFAULT 0,
        ADD COLUMN velocidade REAL NOT NULL DEFAULT 0 
        """,
    )
    conexao.commit()
except Exception:
    conexao.rollback()
    raise
finally:
    conexao.close()
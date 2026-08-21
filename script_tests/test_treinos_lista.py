import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_acess import get_connection

conexao = get_connection()

cursor = conexao.cursor()

resultado = cursor.execute(
    """
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'treinos_lista';
    """
    )
resultado = cursor.fetchall()

conexao.close()

print(resultado)
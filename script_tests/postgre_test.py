import streamlit as st
from sqlalchemy import create_engine, text
import sqlite3

TABELAS = ["cadastros", "exercicio_lista", "treinos_lista", "treinos_dia"]
PG_URL = st.secrets["DB_URL"]

def testar():
    pg_engine = create_engine(PG_URL)

    with pg_engine.begin() as conexao:
        resultado = conexao.execute(text(f"""
            SELECT * FROM exercicio_lista
        """)).fetchall()
        print(resultado)

def sqlite_test():
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()
    resultado = cursor.execute("SELECT * FROM exercicio_lista").fetchall()

    conexao.close()
    with open("exercicios_lista.txt", "w", encoding="utf-8") as f:
        for result in resultado:
            f.write(str(result) + "\n")

import sqlite3

# id que vai ser removido (duplicata) e id que vai continuar existindo
ID_DUPLICADO = 19
ID_MANTIDO = 20


def verificar_e_corrigir():
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    # 1. Conferir os dois registros, pra confirmar que são de fato duplicata
    cursor.execute("SELECT id, exercicio, tipo FROM exercicio_lista WHERE id IN (?, ?)", (ID_DUPLICADO, ID_MANTIDO))
    print("Registros comparados:")
    for linha in cursor.fetchall():
        print(" ", linha)

    # 2. Verificar quantos treinos referenciam o id duplicado
    cursor.execute("SELECT COUNT(*) FROM treinos_lista WHERE exercicio_id = ?", (ID_DUPLICADO,))
    qtd_treinos_lista = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM treinos_dia WHERE exercicio_id = ?", (ID_DUPLICADO,))
    qtd_treinos_dia = cursor.fetchone()[0]

    print(f"\nReferências ao id {ID_DUPLICADO}:")
    print(f"  treinos_lista: {qtd_treinos_lista}")
    print(f"  treinos_dia:   {qtd_treinos_dia}")

    # 3. Reatribuir as referências para o id que vai ser mantido
    if qtd_treinos_lista > 0:
        cursor.execute(
            "UPDATE treinos_lista SET exercicio_id = ? WHERE exercicio_id = ?",
            (ID_MANTIDO, ID_DUPLICADO),
        )
        print(f"\n{qtd_treinos_lista} linha(s) de treinos_lista reatribuída(s) para id {ID_MANTIDO}")

    if qtd_treinos_dia > 0:
        cursor.execute(
            "UPDATE treinos_dia SET exercicio_id = ? WHERE exercicio_id = ?",
            (ID_MANTIDO, ID_DUPLICADO),
        )
        print(f"{qtd_treinos_dia} linha(s) de treinos_dia reatribuída(s) para id {ID_MANTIDO}")

    # 4. Agora sim, apagar a duplicata
    cursor.execute("DELETE FROM exercicio_lista WHERE id = ?", (ID_DUPLICADO,))
    print(f"\nExercício id {ID_DUPLICADO} removido de exercicio_lista.")

    conexao.commit()
    conexao.close()
    print("\nConcluído e salvo no gymtrack.db.")

if __name__ == "__main__":
    sqlite_test()

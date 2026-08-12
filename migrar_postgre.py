"""
Script standalone para migrar os dados do gymtrack.db (SQLite) para o
Postgres no Neon.

Como usar:
1. Rode o app do Streamlit uma vez (com o db_acess.py já apontando pro
   Postgres) para que as tabelas sejam criadas no Neon.
2. Rode este script separadamente: python migrar_para_postgres.py
3. Confira as contagens impressas no final.

Requer: pandas, sqlalchemy, psycopg2-binary (já devem estar instalados).
"""

import sqlite3
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

# Coloque aqui a MESMA connection string que está no secrets.toml,
# já no formato postgresql+psycopg2://...
PG_URL = st.secrets["DB_URL"]

SQLITE_PATH = "gymtrack.db"  # ajuste o caminho se o arquivo não estiver na mesma pasta

# Ordem importa: tabelas referenciadas primeiro (cadastros, exercicio_lista),
# depois as que dependem delas (treinos_lista, treinos_dia).
TABELAS = ["cadastros", "exercicio_lista", "treinos_lista", "treinos_dia"]


def migrar():
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    pg_engine = create_engine(PG_URL)

    for tabela in TABELAS:
        df = pd.read_sql_query(f"SELECT * FROM {tabela}", sqlite_conn)

        if df.empty:
            print(f"{tabela}: 0 linhas (tabela vazia no SQLite, pulando)")
            continue

        df.to_sql(tabela, pg_engine, if_exists="append", index=False)
        print(f"{tabela}: {len(df)} linhas migradas")

    sqlite_conn.close()

    # Ajusta a sequence do id SERIAL de cada tabela para continuar
    # depois do maior id migrado. Sem isso, o próximo INSERT feito
    # pelo app tentaria reusar um id que já existe.
    with pg_engine.begin() as conexao:
        for tabela in TABELAS:
            conexao.execute(text(f"""
                SELECT setval(
                    pg_get_serial_sequence('{tabela}', 'id'),
                    COALESCE((SELECT MAX(id) FROM {tabela}), 1)
                )
            """))
    print("Sequences de id ajustadas para todas as tabelas.")


if __name__ == "__main__":
    migrar()
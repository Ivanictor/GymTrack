import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

def create_table_if_not_exists():
    conexao = sqlite3.connect("gymtrack.db")

    cursor = conexao.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cadastros(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha_hash TEXT NOT NULL,
        admin INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS exercicio_lista(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercicio TEXT NOT NULL,
        tipo TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS treinos_lista(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_treino TEXT NOT NULL,
        usuario_id INTEGER NOT NULL,
        exercicio_id INTEGER NOT NULL,
        repeticoes INTEGER NOT NULL,
        series INTEGER NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS treinos_dia(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_treino TEXT NOT NULL,
        usuario_id INTEGER NOT NULL,
        exercicio_id INTEGER NOT NULL,
        repeticoes INTEGER NOT NULL,
        series INTEGER NOT NULL,
        peso REAL,
        tempo_corrida INTEGER,
        velocidade REAL,
        tempo_treino INTEGER NOT NULL
        )
        """
    )
        

    conexao.commit()
    conexao.close()



def salvar_cadastro(nome, email, senha):

    create_table_if_not_exists()
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO cadastros (
            usuario,
            email,
            senha_hash
        )
        VALUES (?, ?, ?)
    """, (nome, email, generate_password_hash(senha)))
    
    conexao.commit()
    conexao.close()

def buscar_cadastro(email):

    create_table_if_not_exists()
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    registros = cursor.execute("SELECT * FROM cadastros WHERE email = ?", (email,)).fetchone()
    
    conexao.close()

    return registros

def buscar_senha(email, senha):
    create_table_if_not_exists()
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    registro = cursor.execute("SELECT senha_hash FROM cadastros WHERE email = ?", (email,)).fetchone()
    conexao.close()

    if registro is None:
            return False

    senha_hash = registro[0] 

    return check_password_hash(senha_hash, senha)

def criar_exercicio(exercicio, tipo):
    create_table_if_not_exists()

    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO exercicio_lista (
            exercicio,
            tipo
        )
        VALUES (?, ?)
    """, (exercicio, tipo))
    
    conexao.commit()
    conexao.close()

def listar_exercicios(tipo=None):
    create_table_if_not_exists()
    conexao = sqlite3.connect("gymtrack.db")

    if tipo is None:
         df = pd.read_sql_query(
              "SELECT id, exercicio, tipo FROM exercicio_lista ORDER BY exercicio", 
              conexao)

    else:

        df = pd.read_sql_query("""
            SELECT id, exercicio, tipo
            FROM exercicio_lista
            WHERE tipo = ?
            ORDER BY exercicio
        """, conexao, params=(tipo,))

    conexao.close()

    return df

def busca_id_por_exercicio(exercicio):
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    registro = cursor.execute("SELECT id FROM exercicio_lista WHERE exercicio = ?", (exercicio,)).fetchone()
    conexao.close()

    if not registro:
         raise Exception(f"Exercício {exercicio} não encontrado")

    return registro[0]

def busca_exercicio_por_id(exercicio_id):
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    registro = cursor.execute("SELECT exercicio FROM exercicio_lista WHERE id = ?", (exercicio_id,)).fetchone()
    conexao.close()

    if not registro:
        raise Exception(f"ID '{exercicio_id}' não encontrado")

    return registro[0]

def busca_tipo_por_exercicio(exercicio):
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    registro = cursor.execute("SELECT tipo FROM exercicio_lista WHERE exercicio = ?", (exercicio,)).fetchone()
    conexao.close()

    if not registro:
         raise Exception(f"Exercício {exercicio} não encontrado")

    return registro[0]

def criar_treino(nome_treino, df_treino, usuario):
    conexao = sqlite3.connect("gymtrack.db")

    df_treino = df_treino.copy()
    df_treino["nome_treino"] = nome_treino
    df_treino["usuario_id"] = usuario

    df_treino.to_sql(
        "treinos_lista",
        conexao,
        if_exists="append",
        index=False
    )

    conexao.close()

def treinos_usuario(usuario_id):
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    registros = cursor.execute("SELECT DISTINCT nome_treino FROM treinos_lista WHERE usuario_id = ?", (usuario_id,)).fetchall()
    conexao.close()
    return [registro[0] for registro in registros]

def visualizar_treino(nome_treino, usuario_id):

    conexao = sqlite3.connect("gymtrack.db")
    df_treinos_usuario = pd.read_sql_query(
        """
        SELECT
            tl.id,
            el.exercicio,
            tl.repeticoes,
            tl.series
        FROM treinos_lista tl
        JOIN exercicio_lista el
            ON tl.exercicio_id = el.id
        WHERE tl.nome_treino = ?
        AND tl.usuario_id = ?
        """,
        conexao,
        params=(nome_treino, usuario_id)
    )
    conexao.close()

    return df_treinos_usuario

def atualizar_treino(df):
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    for _, linha in df.iterrows():
        exercicio_id = busca_id_por_exercicio(linha["exercicio"])

        cursor.execute(
            """
            UPDATE treinos_lista
            SET exercicio_id = ?,
                repeticoes = ?,
                series = ?
            WHERE id = ?
            """,
            (
                exercicio_id,
                linha["repeticoes"],
                linha["series"],
                linha["id"]
            )
        )

    conexao.commit()
    conexao.close()

def exercicios_por_treino(nome_treino, usuario_id):
    conexao = sqlite3.connect("gymtrack.db")

    df = pd.read_sql_query(
        """
        SELECT
            el.exercicio,
            tl.repeticoes,
            tl.series
        FROM treinos_lista tl
        JOIN exercicio_lista el
            ON tl.exercicio_id = el.id
        WHERE tl.nome_treino = ?
        AND tl.usuario_id = ?
        """,
        conexao,
        params=(nome_treino, usuario_id)
    )

    conexao.close()

    return df

def enviar_exercicios(data_treino, df_treino, usuario, tempo):
    conexao = sqlite3.connect("gymtrack.db")

    df_treino = df_treino.copy()
    df_treino["data_treino"] = data_treino
    df_treino["usuario_id"] = usuario
    df_treino["tempo_treino"] = tempo

    df_treino.to_sql(
        "treinos_dia",
        conexao,
        if_exists="append",
        index=False
    )

    conexao.close()
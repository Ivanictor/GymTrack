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
        admin INTEGER NOT NULL DEFAULT 0,
        testo REAL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS exercicio_lista(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercicio TEXT NOT NULL UNIQUE COLLATE NOCASE,
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

def buscar_cadastro_id(usuario_id):

    create_table_if_not_exists()
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    registros = cursor.execute("SELECT * FROM cadastros WHERE id = ?", (usuario_id,)).fetchone()
    
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

    registro = cursor.execute(
        "SELECT id, exercicio FROM exercicio_lista WHERE exercicio = ? COLLATE NOCASE", 
        (exercicio,)).fetchone()

    if registro:
        conexao.close()
        return False

    else:
        cursor.execute("""
            INSERT INTO exercicio_lista (
                exercicio,
                tipo
            )
            VALUES (?, ?)
        """, (exercicio, tipo))
        
        conexao.commit()
        conexao.close()
        return True

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

def visualizar_treino_diario(usuario_id, data_treino=None, data_inicio=None, data_final=None):
    conexao = sqlite3.connect("gymtrack.db")

    query = """
    SELECT
        td.id,
        td.data_treino,
        el.exercicio,
        td.repeticoes,
        td.series,
        td.peso,
        td.tempo_corrida,
        td.velocidade,
        td.tempo_treino
    FROM treinos_dia td
    JOIN exercicio_lista el
        ON td.exercicio_id = el.id
    WHERE td.usuario_id = ?
    """
    order = "ORDER BY data_treino DESC"

    params = [usuario_id]

    if data_treino:
        query += " AND data_treino = ?"
        params.append(data_treino)

    if data_inicio:
        query += " AND data_treino >= ?"
        params.append(data_inicio)

    if data_final:
        query += " AND data_treino <= ?"
        params.append(data_final)

    query += order

    df = pd.read_sql_query(
        query,
        conexao,
        params=params
    )

    conexao.close()

    return df

def atualizar_treino_realizado(df_editado):

    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    try:
        for _, linha in df_editado.iterrows():
            exercicio_id = busca_id_por_exercicio(linha["exercicio"])

            cursor.execute(
                """
                UPDATE treinos_dia
                SET exercicio_id = ?,
                    repeticoes = ?,
                    series = ?,
                    peso = ?,
                    tempo_corrida = ?,
                    velocidade = ?,
                    tempo_treino = ?,
                    data_treino = ?
                WHERE id = ?
                """,
                (
                    exercicio_id,
                    linha["repeticoes"],
                    linha["series"],
                    linha["peso"],
                    linha["tempo_corrida"],
                    linha["velocidade"],
                    linha["tempo_treino"],
                    linha["data_treino"],
                    linha["id"],  
                ),
            )

        conexao.commit()

    finally:
        conexao.close()

def listar_usuarios():
    conexao = sqlite3.connect("gymtrack.db")
    df = pd.read_sql_query("SELECT id, usuario FROM cadastros", con=conexao)

    return df

def dados_dashboard_metricas(usuario_id, data_inicio, data_final):
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    usuario_id = int(usuario_id)

    query = """
    SELECT
        COUNT(DISTINCT data_treino),
        COALESCE(SUM(tempo_corrida), 0),
        COALESCE(SUM(tempo_corrida * velocidade), 0),
        COALESCE(SUM(tempo_treino), 0)
    FROM treinos_dia
    WHERE usuario_id = ?
    """
    params = [usuario_id]

    if data_inicio:
        query += " AND data_treino >= ?"
        params.append(data_inicio)

    if data_final:
        query += " AND data_treino <= ?"
        params.append(data_final)
    
    resultado = cursor.execute(query, params).fetchone()

    conexao.close()

    return resultado

def dados_dashboard_graphs(usuario_id, exercicio, data_inicio, data_final):
    conexao = sqlite3.connect("gymtrack.db")

    usuario_id = int(usuario_id)
    query = (
        """
        SELECT 
            td.data_treino, 
            e1.exercicio, 
            td.peso 
        FROM treinos_dia td 
        JOIN exercicio_lista e1
            ON td.exercicio_id = e1.id
        WHERE td.usuario_id = ? """)

    query_2 = (
        """
        SELECT 
            td.data_treino, 
            td.velocidade, 
            td.tempo_corrida 
        FROM treinos_dia td
        JOIN exercicio_lista e1
            ON td.exercicio_id = e1.id
        WHERE td.usuario_id = ?""")

    query_3 = (
        """
        SELECT 
            data_treino, 
            COUNT(*) AS quantidade 
        FROM treinos_dia
        WHERE usuario_id = ?
        """)

    query_4 = (
        """
        SELECT
            e1.tipo,
            COUNT(*) AS quantidade
        FROM treinos_dia td
        JOIN exercicio_lista e1
            ON td.exercicio_id = e1.id
        WHERE usuario_id = ?
        GROUP BY e1.tipo"""
    )

    params = [usuario_id]
    params_query_3 = [usuario_id]

    if data_inicio:
        query += " AND td.data_treino >= ?"
        query_2 += " AND td.data_treino >= ?"
        query_3 += " AND data_treino >= ?"
        params.append(data_inicio)
        params_query_3.append(data_inicio)

    if data_final:
        query += " AND td.data_treino <= ?"
        query_2 += " AND td.data_treino <= ?"
        query_3 += " AND data_treino <= ?"
        params.append(data_final)
        params_query_3.append(data_final)

    if exercicio:
        query += " AND e1.exercicio = ?"
        query_2 += " AND e1.exercicio = ?"
        params.append(exercicio)


    query_3 += (
                """
                GROUP BY data_treino
                ORDER BY data_treino
                """
            )

    df = pd.read_sql_query(query, conexao, params=params)
    df_speed = pd.read_sql_query(query_2, conexao, params=params)
    df_count = pd.read_sql_query(query_3, conexao, params=params_query_3)
    df_types = pd.read_sql_query(query_4, conexao, params=(usuario_id,))


    conexao.close()

    return df, df_speed, df_count, df_types

def atualizar_perfil(usuario_id, nome, email, senha, testo):
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    try:
        if senha is not None:
            cursor.execute(
                "UPDATE cadastros SET usuario = ?, email = ?, senha_hash = ?, testo = ? WHERE id = ?",
                params=(nome, email, generate_password_hash(senha), testo, usuario_id)
                )

        else:
            cursor.execute(
                "UPDATE cadastros SET usuario = ?, email = ?, testo = ? WHERE id = ?",
                params=(nome, email, testo, usuario_id)
                )

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()

def atualizar_senha(email, senha):
    conexao = sqlite3.connect("gymtrack.db")
    cursor = conexao.cursor()

    try:
        
        cursor.execute(
            "UPDATE cadastros SET senha_hash = ? WHERE email = ?",
            params=(generate_password_hash(senha), email)
            )

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()
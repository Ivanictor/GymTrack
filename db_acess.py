import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash

@st.cache_resource
def get_engine():
    return create_engine(
        st.secrets["DB_URL"],
        pool_pre_ping=True,   # evita erros de "conexão morta" após idle
        pool_size=5,
        max_overflow=10,
    )


def get_connection():
    """
    Retorna uma conexão psycopg2 "crua" tirada do pool do SQLAlchemy.
    Isso permite continuar usando cursor.execute(sql, params) com %s
    normalmente, mas reaproveitando o pool de conexões (importante em
    ambiente serverless / Streamlit Cloud).

    conexao.close() aqui NÃO fecha a conexão de verdade — devolve ela
    para o pool, que é o comportamento desejado.
    """
    return get_engine().raw_connection()


def create_table_if_not_exists():
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        # Necessário para unicidade case-insensitive (substitui COLLATE NOCASE do SQLite).

        cursor.execute("CREATE EXTENSION IF NOT EXISTS citext")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cadastros(
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
            exercicio CITEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS treinos_lista(
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
            data_treino DATE NOT NULL,
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
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


# ---------------------------------------------------------------------------
# Cadastros / Autenticação
# ---------------------------------------------------------------------------

def salvar_cadastro(nome, email, senha):
    create_table_if_not_exists()
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO cadastros (usuario, email, senha_hash)
            VALUES (%s, %s, %s)
            """,
            (nome, email, generate_password_hash(senha)),
        )
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def buscar_cadastro(email):
    create_table_if_not_exists()
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        registros = cursor.execute(
            "SELECT * FROM cadastros WHERE email = %s", (email,)
        )
        return cursor.fetchone()
    finally:
        conexao.close()


def buscar_cadastro_id(usuario_id):
    create_table_if_not_exists()
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute("SELECT * FROM cadastros WHERE id = %s", (usuario_id,))
        return cursor.fetchone()
    finally:
        conexao.close()

def query_cadastros():
    engine = get_engine()
    df = pd.read_sql_query(
                "SELECT * FROM cadastros",
                engine,
            )
    df = df.drop(columns=["senha_hash", "testo"])
    return df

def buscar_senha(email, senha):
    create_table_if_not_exists()
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute("SELECT senha_hash FROM cadastros WHERE email = %s", (email,))
        registro = cursor.fetchone()
    finally:
        conexao.close()

    if registro is None:
        return False

    senha_hash = registro[0]
    return check_password_hash(senha_hash, senha)


# ---------------------------------------------------------------------------
# Exercícios
# ---------------------------------------------------------------------------

def criar_exercicio(exercicio, tipo):
    create_table_if_not_exists()
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            "SELECT id, exercicio FROM exercicio_lista WHERE exercicio = %s",
            (exercicio,),
        )
        registro = cursor.fetchone()

        if registro:
            return False

        cursor.execute(
            """
            INSERT INTO exercicio_lista (exercicio, tipo)
            VALUES (%s, %s)
            """,
            (exercicio, tipo),
        )
        conexao.commit()
        return True
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def listar_exercicios(tipo=None):
    create_table_if_not_exists()
    engine = get_engine()

    if tipo is None:
        df = pd.read_sql_query(
            "SELECT id, exercicio, tipo FROM exercicio_lista ORDER BY exercicio",
            engine,
        )
    else:
        df = pd.read_sql_query(
            """
            SELECT id, exercicio, tipo
            FROM exercicio_lista
            WHERE tipo = %s
            ORDER BY exercicio
            """,
            engine,
            params=(tipo,),
        )

    return df


def busca_id_por_exercicio(exercicio):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute("SELECT id FROM exercicio_lista WHERE exercicio = %s", (exercicio,))
        registro = cursor.fetchone()
    finally:
        conexao.close()

    if not registro:
        raise Exception(f"Exercício {exercicio} não encontrado")

    return registro[0]


def busca_exercicio_por_id(exercicio_id):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute("SELECT exercicio FROM exercicio_lista WHERE id = %s", (exercicio_id,))
        registro = cursor.fetchone()
    finally:
        conexao.close()

    if not registro:
        raise Exception(f"ID '{exercicio_id}' não encontrado")

    return registro[0]


def busca_tipo_por_exercicio(exercicio):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute("SELECT tipo FROM exercicio_lista WHERE exercicio = %s", (exercicio,))
        registro = cursor.fetchone()
    finally:
        conexao.close()

    if not registro:
        raise Exception(f"Exercício {exercicio} não encontrado")

    return registro[0]


def excluir_exercicio(exercicio_id):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute("DELETE FROM exercicio_lista WHERE id = %s", (exercicio_id,))
        qtd = cursor.rowcount
        conexao.commit()
        return qtd
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


# ---------------------------------------------------------------------------
# Treinos (modelo / lista de exercícios do treino)
# ---------------------------------------------------------------------------

def criar_treino(nome_treino, df_treino, usuario):
    engine = get_engine()

    df_treino = df_treino.copy()
    df_treino["nome_treino"] = nome_treino
    df_treino["usuario_id"] = usuario

    df_treino.to_sql(
        "treinos_lista",
        engine,
        if_exists="append",
        index=False,
    )


def treinos_usuario(usuario_id):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            "SELECT DISTINCT nome_treino FROM treinos_lista WHERE usuario_id = %s",
            (usuario_id,),
        )
        registros = cursor.fetchall()
    finally:
        conexao.close()

    return [registro[0] for registro in registros]


def visualizar_treino(nome_treino, usuario_id):
    engine = get_engine()
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
        WHERE tl.nome_treino = %s
        AND tl.usuario_id = %s
        """,
        engine,
        params=(nome_treino, usuario_id),
    )

    return df_treinos_usuario


def atualizar_treino(df):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        for _, linha in df.iterrows():
            exercicio_id = busca_id_por_exercicio(linha["exercicio"])

            cursor.execute(
                """
                UPDATE treinos_lista
                SET exercicio_id = %s,
                    repeticoes = %s,
                    series = %s
                WHERE id = %s
                """,
                (
                    exercicio_id,
                    linha["repeticoes"],
                    linha["series"],
                    linha["id"],
                ),
            )

        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def deletar_treino(usuario_id, nome_treino):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            "DELETE FROM treinos_lista WHERE usuario_id = %s AND nome_treino = %s",
            (usuario_id, nome_treino),
        )
        quantidade_excluida = cursor.rowcount
        conexao.commit()
        return quantidade_excluida
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def exercicios_por_treino(nome_treino, usuario_id):
    engine = get_engine()

    df = pd.read_sql_query(
        """
        SELECT
            el.exercicio,
            tl.repeticoes,
            tl.series
        FROM treinos_lista tl
        JOIN exercicio_lista el
            ON tl.exercicio_id = el.id
        WHERE tl.nome_treino = %s
        AND tl.usuario_id = %s
        """,
        engine,
        params=(nome_treino, usuario_id),
    )

    return df


# ---------------------------------------------------------------------------
# Treinos realizados (dia a dia)
# ---------------------------------------------------------------------------

def enviar_exercicios(data_treino, df_treino, usuario, tempo):
    engine = get_engine()

    df_treino = df_treino.copy()
    df_treino["data_treino"] = data_treino
    df_treino["usuario_id"] = usuario
    df_treino["tempo_treino"] = tempo

    df_treino.to_sql(
        "treinos_dia",
        engine,
        if_exists="append",
        index=False,
    )


def visualizar_treino_diario(usuario_id, data_treino=None, data_inicio=None, data_final=None):
    engine = get_engine()

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
    WHERE td.usuario_id = %s
    """
    order = "ORDER BY data_treino DESC"

    params = [usuario_id]

    if data_treino:
        query += " AND data_treino = %s::date"
        params.append(data_treino)

    if data_inicio:
        query += " AND data_treino >= %s::date"
        params.append(data_inicio)

    if data_final:
        query += " AND data_treino <= %s::date"
        params.append(data_final)

    query += order

    df = pd.read_sql_query(query, engine, params=tuple(params)) #Foi iniciado como lista, termina como tupla

    return df


def atualizar_treino_realizado(df_editado):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        for _, linha in df_editado.iterrows():
            exercicio_id = busca_id_por_exercicio(linha["exercicio"])

            cursor.execute(
                """
                UPDATE treinos_dia
                SET exercicio_id = %s,
                    repeticoes = %s,
                    series = %s,
                    peso = %s,
                    tempo_corrida = %s,
                    velocidade = %s,
                    tempo_treino = %s,
                    data_treino = %s
                WHERE id = %s
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
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def excluir_treinos_realizados(ids):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.executemany(
            "DELETE FROM treinos_dia WHERE id = %s",
            [(id_,) for id_ in ids],
        )
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


# ---------------------------------------------------------------------------
# Usuários / Perfil
# ---------------------------------------------------------------------------

def listar_usuarios():
    engine = get_engine()
    df = pd.read_sql_query("SELECT id, usuario FROM cadastros", engine)
    return df


def atualizar_perfil(usuario_id, nome, email, senha, testo):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        if senha is not None:
            cursor.execute(
                """
                UPDATE cadastros
                SET usuario = %s, email = %s, senha_hash = %s, testo = %s
                WHERE id = %s
                """,
                (nome, email, generate_password_hash(senha), testo, usuario_id),
            )
        else:
            cursor.execute(
                """
                UPDATE cadastros
                SET usuario = %s, email = %s, testo = %s
                WHERE id = %s
                """,
                (nome, email, testo, usuario_id),
            )

        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def atualizar_senha(email, senha):
    conexao = get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            "UPDATE cadastros SET senha_hash = %s WHERE email = %s",
            (generate_password_hash(senha), email),
        )
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def ranking_testo():
    engine = get_engine()
    df = pd.read_sql_query(
        """
        SELECT id, usuario, testo
        FROM cadastros
        ORDER BY testo DESC
        """,
        engine,
    )
    return df


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def dados_dashboard_metricas(usuario_id, data_inicio, data_final):
    conexao = get_connection()
    cursor = conexao.cursor()

    usuario_id = int(usuario_id)

    query = """
    SELECT
        COUNT(DISTINCT data_treino),
        COALESCE(SUM(tempo_corrida), 0),
        COALESCE(SUM(tempo_corrida * velocidade / 60), 0),
        COALESCE(SUM(tempo_treino), 0)
    FROM treinos_dia
    WHERE usuario_id = %s
    """
    params = [usuario_id]

    if data_inicio:
        query += " AND data_treino >= %s::date"
        params.append(data_inicio)

    if data_final:
        query += " AND data_treino <= %s::date"
        params.append(data_final)

    try:
        cursor.execute(query, params)
        resultado = cursor.fetchone()
    finally:
        conexao.close()

    return resultado


def dados_dashboard_graphs(usuario_id, exercicio, exercicio_cardio, data_inicio, data_final):
    engine = get_engine()
    usuario_id = int(usuario_id)

    query = """
        SELECT
            td.data_treino,
            e1.exercicio,
            td.peso
        FROM treinos_dia td
        JOIN exercicio_lista e1
            ON td.exercicio_id = e1.id
        WHERE td.usuario_id = %s
        """

    query_2 = """
        SELECT
            td.data_treino,
            td.velocidade,
            td.tempo_corrida
        FROM treinos_dia td
        JOIN exercicio_lista e1
            ON td.exercicio_id = e1.id
        WHERE td.usuario_id = %s
        """

    query_3 = """
        SELECT
            data_treino,
            COUNT(*) AS quantidade
        FROM treinos_dia
        WHERE usuario_id = %s
        """

    query_4 = """
        SELECT
            e1.tipo,
            COUNT(*) AS quantidade
        FROM treinos_dia td
        JOIN exercicio_lista e1
            ON td.exercicio_id = e1.id
        WHERE usuario_id = %s
        GROUP BY e1.tipo
        """

    params = [usuario_id]
    params_query_2 = [usuario_id]
    params_query_3 = [usuario_id]

    if data_inicio:
        query += " AND td.data_treino >= %s::date"
        query_2 += " AND td.data_treino >= %s::date"
        query_3 += " AND data_treino >= %s::date"
        params.append(data_inicio)
        params_query_2.append(data_inicio)
        params_query_3.append(data_inicio)

    if data_final:
        query += " AND td.data_treino <= %s::date"
        query_2 += " AND td.data_treino <= %s::date"
        query_3 += " AND data_treino <= %s::date"
        params.append(data_final)
        params_query_2.append(data_final)
        params_query_3.append(data_final)

    if exercicio:
        query += " AND e1.exercicio = %s"
        params.append(exercicio)

    if exercicio_cardio:
        query_2 += " AND e1.exercicio = %s"
        params_query_2.append(exercicio_cardio)

    query_3 += """
        GROUP BY data_treino
        ORDER BY data_treino
        """

    df = pd.read_sql_query(query, engine, params=tuple(params))
    df_speed = pd.read_sql_query(query_2, engine, params=tuple(params_query_2))
    df_count = pd.read_sql_query(query_3, engine, params=tuple(params_query_3))
    df_types = pd.read_sql_query(query_4, engine, params=(usuario_id,))

    return df, df_speed, df_count, df_types
import streamlit as st
from datetime import date
import pandas as pd
from db_acess import visualizar_treino_diario, listar_exercicios, atualizar_treino_realizado, excluir_treinos_realizados

def data_para_br(df, coluna="data_treino"):
    df = df.copy()
    df[coluna] = pd.to_datetime(df[coluna]).dt.strftime("%d/%m/%Y")
    return df

def data_para_sql(df, coluna="data_treino"):
    df = df.copy()
    df[coluna] = pd.to_datetime(df[coluna], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")
    return df

st.title("GymTrack 🦾 - Visualização de Treinos Realizados")

usuario_id = st.session_state["id"]

st.write("Filtros")

col1_checkbox, col2_checkbox = st.columns(2)

with col1_checkbox:
    remover_filtro = st.checkbox("Mostrar todos os treinos", value=True)
with col2_checkbox:
    delete_button = st.checkbox("Mostrar botões de excluir", value=False)

if remover_filtro:
    data_treino = None
    data_inicio = None
    data_final = None
else:

    col1, col2, col3 = st.columns(3)

    with col1:
        data_treino = st.date_input(
            "Data do treino",
            max_value=date.today(),
            value=date.today(),
            format="DD/MM/YYYY"
        )

    with col2:
        data_inicio = st.date_input(
            "Data inicial",
            value=None,
            max_value=date.today(),
            format="DD/MM/YYYY"
        )

    with col3:
        data_final = st.date_input(
            "Data final",
            value=None,
            max_value=date.today(),
            format="DD/MM/YYYY"
        )

df_exercicios = listar_exercicios(tipo=None)

if df_exercicios.empty:
    st.warning("Não existem exercícios cadastrados. Cadastre exercícios antes de criar um treino.")
    st.stop()

lista_exercicios = df_exercicios["exercicio"]
lista_exercicios = list(lista_exercicios)

daily_train_df = visualizar_treino_diario(
    usuario_id,
    data_treino,
    data_inicio,
    data_final
)

daily_train_df = data_para_br(daily_train_df)

column_config={
        "id": None,  

        "data_treino": st.column_config.TextColumn(
            "Data"
        ),

        "exercicio": st.column_config.SelectboxColumn(
            "Exercício",
            options=lista_exercicios,
            required=True
        ),

        "repeticoes": st.column_config.NumberColumn(
            "Repetições",
            min_value=1,
            step=1
        ),

        "series": st.column_config.NumberColumn(
            "Séries",
            min_value=1,
            step=1
        ),

        "peso": st.column_config.NumberColumn(
            "Peso (kg)",
            format="%.1f"
        ),

        "tempo_corrida": st.column_config.NumberColumn(
            "Tempo de corrida (min)"
        ),

        "velocidade": st.column_config.NumberColumn(
            "Velocidade (km/h)",
            format="%.1f"
        ),

        "tempo_treino": st.column_config.NumberColumn(
            "Duração do treino (min)"
        ),
    }

if delete_button:
    daily_train_df.insert(0, "excluir", False)
    column_config["excluir"] = st.column_config.CheckboxColumn(
        "Excluir", 
        help="Marque os registros que deseja excluir"
        )

daily_train_df_edit = st.data_editor(
    daily_train_df,
    hide_index=True,
    column_config=column_config
)
col1, col2 = st.columns(2)

with col1:
    if st.button("Salvar mudanças"):
        try:
            if delete_button:
                daily_train_df_edit = daily_train_df_edit.drop(columns=["excluir"])
            daily_train_df_edit = data_para_sql(daily_train_df_edit)
            atualizar_treino_realizado(daily_train_df_edit)

            st.success("Mudanças salvas")

        except Exception as e:
            st.error(f"Erro ao atualizar o exercício: {e}")

with col2:
    if st.button("Excluir selecionados"):
        df_excluir = daily_train_df_edit[daily_train_df_edit["excluir"]]
        if df_excluir.empty:
            st.warning("Selecione pelo menos um registro para excluir")

        else:
            try:
                ids = df_excluir["id"].tolist()
                excluir_treinos_realizados(ids)
                st.success("Registros excluídos")
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao excluir os registros {e}")
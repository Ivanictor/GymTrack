import streamlit as st
import pandas as pd
import time
from db_acess import (criar_exercicio, 
                      listar_exercicios, 
                      criar_treino, 
                      busca_id_por_exercicio, 
                      treinos_usuario, 
                      visualizar_treino, 
                      atualizar_treino)

st.title("GymTrack 🦾 - Cadastro de Treinos")

aba_registrar_treino, aba_registrar_exercicio, aba_visualizar = st.tabs(
    ["Cadastrar treinos", "Registrar exercício", "Visualizar treinos"]
    )
with aba_registrar_exercicio:

    with st.form("cadastro_exercicio", clear_on_submit=True):
        st.header("Cadastrar exercício")

        exercicio = st.text_input("Exercício")

        tipo = st.radio("Tipo de treino", ["Superior", "Inferior", "Aeróbico"])

        enviar = st.form_submit_button("Enviar")

        if enviar:
            erros = []

            if not exercicio.strip():
                erros.append("Informe o nome do exercício")

            if tipo is None:
                erros.append("Informe o tipo do exercício")

            if erros:
                st.error("\n".join(erros))
            else:
                resultado = criar_exercicio(exercicio, tipo)

                if not resultado:
                    st.error("Exercício já criado")
                else:
                    st.success("Exercício cadastrado")
                    time.sleep(2)
                    st.rerun()


    st.markdown(
    """
    <p style="
        font-family: Arial;
        font-size: 30px;
        font-weight:bold;
    ">
        Lista de Exercícios
    </p>
    """,
    unsafe_allow_html=True,
)

    tipo = st.radio(
            "Tipo de treino", ["Superior", "Inferior", "Aeróbico"], 
            index=None)
    
    df = listar_exercicios(tipo)
    df = df.rename(columns={
        "exercicio": "Exercício",
        "tipo": "Tipo"
    })

    st.dataframe(df[["Exercício", "Tipo"]], hide_index=True)
    
with aba_registrar_treino:

    st.header("Cadastrar treinos")

    usuario = st.session_state["id"]

    nome_treino = st.text_input("Nome do treino")

    df_exercicios = listar_exercicios(tipo=None)

    if df_exercicios.empty:
        st.warning("Não existem exercícios cadastrados. Cadastre exercícios antes de criar um treino.")
        st.stop()

    lista_exercicios = df_exercicios["exercicio"]

    exercicios = []
    series_ex = []
    repeticoes = []

    quantidade = st.number_input(
        "Quantidade de exercícios",
        min_value=1,
        max_value=20,
        value=6)

    for i in range(quantidade):
        exercicios.append(
            st.selectbox(
                f"Exercício {i+1}", 
                options=lista_exercicios,
                key=f"exercicio_{i}"
            )
        )

        repeticoes.append(st.number_input(
            f"Número de repetições do exercício {i+1}",
            min_value=1,
            value=12,
            step=1,
            key=f"repeticao_{i}"
        ))

        series_ex.append(st.number_input(
            f"Número de séries do exercício {i+1}",
            min_value=1,
            value=3,
            step=1,
            key=f"serie_{i}"
        ))
        st.divider()

    
    if st.button("Enviar treino"):
        erros = []

        if not nome_treino.strip():
            erros.append("Dê um nome ao seu treino")

        if erros:
            st.error("\n".join(erros))
        else:
            df_treino = pd.DataFrame()

            for i, exercicio in enumerate(exercicios):
                exercicios[i] = busca_id_por_exercicio(exercicio)

            df_treino["exercicio_id"] = exercicios
            df_treino["repeticoes"] = repeticoes
            df_treino["series"] = series_ex

            criar_treino(nome_treino, df_treino, usuario)
            st.success("Treino cadastrado")

with aba_visualizar:
    st.header("Visualizar Treinos")

    usuario = st.session_state["id"]

    treinos = treinos_usuario(usuario)

    lista_exercicios = list(lista_exercicios)

    if not treinos:
        st.write("Não há treinos cadastrados para seu usuário")

    else:
        nome_treino = st.selectbox("Selecione o treino cadastrado que deseja visualizar", options=treinos)
        df_treinos_usuario = visualizar_treino(nome_treino, usuario)

        df_editado = st.data_editor(
            df_treinos_usuario,
            column_config={
                "id": None,
                "exercicio": st.column_config.SelectboxColumn(
                    "Exercício",
                    options=lista_exercicios,
                    required=True
                ),
                "series": st.column_config.NumberColumn(
                    "Séries",
                    min_value=1,
                    step=1,
                ),
                "repeticoes": st.column_config.NumberColumn(
                    "Repetições",
                    min_value=1,
                    step=1,
                ),
            },
            hide_index=True)

        if st.button("Salvar alterações nesse treino?"):
            atualizar_treino(df_editado)
            st.success("Treino alterado com sucesso")









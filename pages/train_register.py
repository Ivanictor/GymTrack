import streamlit as st
import pandas as pd
import time
from db_acess import (criar_exercicio, 
                      listar_exercicios, 
                      criar_treino, 
                      busca_id_por_exercicio, 
                      treinos_usuario, 
                      visualizar_treino, 
                      atualizar_treino,
                      deletar_treino,
                      excluir_exercicio)

admin = st.session_state["admin"]

st.title("GymTrack 🦾 - Cadastro de Treinos")

aba_registrar_treino, aba_registrar_exercicio, aba_visualizar = st.tabs(
    ["Cadastrar treinos", "Registrar exercício", "Visualizar treinos"]
    )

usuario_id = st.session_state["id"]
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

    with st.container(border=True):
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

    if admin == 1:
        with st.container(border=True):
                st.markdown(
                """
                <p style="
                    font-family: Arial;
                    font-size: 30px;
                    font-weight:bold;
                ">
                    Excluir exercícios
                </p>
                """,
                unsafe_allow_html=True,
            )
                df = listar_exercicios()
                exercicios_lista = df["exercicio"].tolist()

                exercicio_excluir = st.selectbox("Selecione o exercício para excluir", options=exercicios_lista)

                if st.button("Excluir"):
                    id_exercicio = busca_id_por_exercicio(exercicio_excluir)
                    qtd = excluir_exercicio(id_exercicio)
                    st.success("Exercício excluído")
                    time.sleep(1)
    
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
    pesos = []
    velocidades = []

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

        pesos.append(st.number_input(
            f"Peso do exercício {i+1} (se aeróbico, coloque 0)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key=f"peso_{i}"
        ))
        pesos.append(st.number_input(
            f"Velocidade do exercício {i+1} (se não for aeróbico, coloque 0)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key=f"velocidade_{i}"
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
            df_treino["peso"] = pesos
            df_treino["velocidade"] = velocidades

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
                "peso": st.column_config.NumberColumn(
                    "Peso (kg)",
                    min_value=0.0,
                    step=0.1,
                ),
                "velocidade": st.column_config.NumberColumn(
                    "Velocidade (km/h)",
                    min_value=0.0,
                    step=0.1,
                )
            },
            hide_index=True)
        
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Salvar alterações nesse treino?"):
                atualizar_treino(df_editado)
                st.success("Treino alterado com sucesso")
        with col2:
            if st.button("Excluir esse treino?"):
                quantidade_excluida = deletar_treino(usuario_id, nome_treino)

                if quantidade_excluida == 0:
                    st.warning("Nenhum treino foi encontrado.")
                else:
                    st.success("Treino excluído com sucesso")
        time.sleep(1)








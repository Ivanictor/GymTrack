import streamlit as st
from datetime import date
import pandas as pd
from db_acess import treinos_usuario, listar_exercicios, exercicios_por_treino, enviar_exercicios, busca_tipo_por_exercicio, busca_id_por_exercicio

st.title("GymTrack 🦾 - Lançamento do Treino do Dia")

with st.container(border=True):
    
    nome_usuario = st.session_state["nome"]
    id_usuario = st.session_state["id"]

    st.write(f"Bem vindo, {nome_usuario}. Lance aqui os exercícios que você realizou")

    data_treino = st.date_input("Data do treino", max_value=date.today(), value=date.today(), format="DD/MM/YYYY")

    tempo = st.number_input("Duração do treino (minutos)", min_value=1, step=1)

    lista_treinos = treinos_usuario(id_usuario)
    lista_treinos.append("Manual")

    df_exercicios = listar_exercicios()

    if df_exercicios.empty:
        st.warning("Cadastre exercícios antes de lançar um treino.")
        st.stop()

    lista_exercicios = df_exercicios["exercicio"].tolist()
    lista_exercicios.append("")

    treino = st.selectbox(
        "Selecione o treino cadastrado que foi realizado (caso não tenha seguido nenhum, selecione 'manual')",
        options=lista_treinos,
        index=lista_treinos.index("Manual"),
    )

    exercises = []
    sets = []
    repetitions = []
    weights = []
    speeds = []
    time_run = []

    if treino == "Manual":
        quantidade = st.number_input("Selecione a quantidade de exercícios", value=6, min_value=1, step=1)

        st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("Exercícios")

        st.markdown("<br>", unsafe_allow_html=True)

        for i in range(quantidade):
            exercises.append(
                st.selectbox(
                    f"Exercício {i+1}", 
                    options=lista_exercicios,
                    key=f"exercicio_{i}",
                    index=lista_exercicios.index("")
                )
            )

            repetitions.append(st.number_input(
                f"Número de repetições do exercício {i+1}",
                min_value=1,
                value=12,
                step=1,
                key=f"repeticao_{i}"
            ))

            sets.append(st.number_input(
                f"Número de séries do exercício {i+1}",
                min_value=1,
                value=3,
                step=1,
                key=f"serie_{i}"
            ))


            if exercises[i]:
                tipo_exercicio = busca_tipo_por_exercicio(exercises[i])
            else:
                tipo_exercicio = None

            if tipo_exercicio == "Aeróbico":
                weights.append(st.number_input(
                    f"Peso do exercício {i+1}",
                    value=0.0,
                    disabled=True,
                ))
                speeds.append(st.number_input(
                    f"Velocidade do exercício {i+1}, em km/h",
                    min_value=0.5,
                    value=6.0,
                    step=0.1
                ))
                time_run.append(st.number_input(
                    f"Tempo de exercício {i+1}, em minutos",
                    min_value=1,
                    value=15,
                    step=1
                ))
            else:
                weights.append(st.number_input(
                    f"Peso do exercício {i+1}",
                    value=1.0,
                    min_value=1.0,
                    step=0.1,
                    key=f"peso_{i}"
                ))
                speeds.append(st.number_input(
                    f"Velocidade do exercício {i+1}, em km/h",
                    value=0.0,
                    disabled=True
                ))
                time_run.append(st.number_input(
                    f"Tempo de exercício {i+1}, em minutos (necessário apenas para exercícios aeróbicos)",
                    min_value=0,
                    value=0,
                    step=1
                ))

                st.divider()
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("Exercícios")

        st.markdown("<br>", unsafe_allow_html=True)
        
        workout_df = exercicios_por_treino(treino, id_usuario)

        if workout_df.empty:
            st.warning("Esse treino não possui exercícios cadastrados.")
            st.stop()

        quantidade = len(workout_df)
        
        for i in range(quantidade):

            linha_atual = workout_df.iloc[i]
            exercises.append(
                st.selectbox(
                    f"Exercício {i+1}", 
                    options=lista_exercicios,
                    key=f"{treino}_exercicio_{i}",
                    index=lista_exercicios.index(linha_atual["exercicio"])
                )
            )

            repetitions.append(st.number_input(
                f"Número de repetições do exercício {i+1}",
                min_value=1,
                value=workout_df["repeticoes"].iloc[i],
                step=1,
                key=f"{treino}_repeticao_{i}"
            ))

            sets.append(st.number_input(
                f"Número de séries do exercício {i+1}",
                min_value=1,
                value=workout_df["series"].iloc[i],
                step=1,
                key=f"{treino}_serie_{i}"
            ))

            if exercises[i]:
                        tipo_exercicio = busca_tipo_por_exercicio(exercises[i])
            else:
                tipo_exercicio = None
            
            if tipo_exercicio == "Aeróbico":
                weights.append(st.number_input(
                    f"Peso do exercício {i+1}",
                    value=workout_df["peso"].iloc[i],
                    disabled=True,
                    key=f"{treino}_peso_{i}"
                ))
                speeds.append(st.number_input(
                    f"Velocidade do exercício {i+1}, em km/h",
                    min_value=0.5,
                    value=workout_df["velocidade".iloc[i]],
                    step=0.1,
                    key=f"{treino}_velocidade_{i}"
                ))
                time_run.append(st.number_input(
                    f"Tempo de exercício {i+1}, em minutos",
                    min_value=1,
                    value=15,
                    step=1,
                    key=f"{treino}_tempo_{i}"
                ))
            else:
                weights.append(st.number_input(
                    f"Peso do exercício {i+1}",
                    value=workout_df["peso"].iloc[i],
                    min_value=1.0,
                    step=0.1
                ))
                speeds.append(st.number_input(
                    f"Velocidade do exercício {i+1}, em km/h",
                    value=workout_df["velocidade"].iloc[i],
                    disabled=True
                ))
                time_run.append(st.number_input(
                    f"Tempo de exercício {i+1}, em minutos (necessário apenas para exercícios aeróbicos)",
                    min_value=0,
                    value=0,
                    step=1
                ))

            st.divider()

    if st.button("Enviar"):
        erros = []

        for exercise in exercises:
            if exercise == "":
                erros.append("Selecione uma atividade")
        if erros:
            st.error("\n".join(erros))
        else:
            df_envio = pd.DataFrame()

            df_envio["exercicio"] = exercises
            df_envio["exercicio_id"] = df_envio["exercicio"].apply(busca_id_por_exercicio)
            df_envio["repeticoes"] = repetitions
            df_envio["series"] = sets
            df_envio["peso"] = weights
            df_envio["velocidade"] = speeds
            df_envio["tempo_corrida"] = time_run

            df_envio = df_envio.drop(columns=["exercicio"])

            enviar_exercicios(data_treino, df_envio, id_usuario, tempo)
            st.success("Treino enviado")

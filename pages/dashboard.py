import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
from db_acess import listar_usuarios, dados_dashboard_metricas, listar_exercicios, dados_dashboard_graphs

def horas_e_minutos(tempo):
    horas = int(tempo/60)
    minutos = int(tempo%60)
    horas_decimal = tempo/60

    return horas, minutos, horas_decimal

st.title("GymTrack 🦾 - Dashboard")

usuario_id = st.session_state["id"]
usuario_admin = st.session_state["admin"]


# -------------- Filtros -------------- #

with st.sidebar:

    data_escolhida = st.radio(
        "Filtro de data", horizontal=True, options=["Manual", "Semana atual", "Mês atual", "Ano atual"], index=0)

    hoje = date.today()
    if data_escolhida == "Semana atual":

        if hoje.weekday() == 7:
            dia_inicio = hoje
        else:
            dia_inicio = hoje - timedelta(hoje.weekday() + 1)

        dia_final = hoje

    elif data_escolhida == "Mês atual":

        dia_inicio = hoje.replace(day=1)
        dia_final = hoje

    elif data_escolhida == "Ano atual":

        dia_inicio = hoje.replace(day=1, month=1)
        dia_final = hoje
    else:
        dia_inicio, dia_final = None, None

    data_inicio = st.date_input("Data de início", value=dia_inicio, max_value=date.today(), format="DD/MM/YYYY")

    data_final = st.date_input("Data de término", value=dia_final, max_value=date.today(), format="DD/MM/YYYY")

    df_exercicios = listar_exercicios(tipo=None)
    lista_exercicios = df_exercicios["exercicio"]

    exercicio = st.selectbox("Exercício", options=lista_exercicios, index=0)

    if usuario_admin == 1:
        lista_usuarios = listar_usuarios()
        usuario_escolhido = st.selectbox("Usuário", lista_usuarios["usuario"].tolist())

        usuario_id = lista_usuarios.loc[lista_usuarios["usuario"] == usuario_escolhido, "id"].iloc[0]

# ------------ Métricas ------------ #

m1, m2, m3 = st.columns([1, 1.4, 1.4])

qtd_treinos, tempo_corrida, distancia, tempo_total = dados_dashboard_metricas(usuario_id, 
                                                                                data_inicio, 
                                                                                data_final)

tempo_corrida = horas_e_minutos(tempo_corrida)
tempo_total = horas_e_minutos(tempo_total)

m1.metric("Idas à academia", qtd_treinos, border=True)
m2.metric("Tempo de cardio", f"{tempo_total[0]}h{tempo_total[1]}min", border=True)
m3.metric("Distância no cardio", f"{distancia:.1f}km", border=True)
#m4.metric("Tempo de treino", f"{tempo_total[0]}h{tempo_total[1]}min", border=True)


# ----------- Gráficos ------------ #

df_weight, df_cardio, df_count, df_types = dados_dashboard_graphs(usuario_id, exercicio, data_inicio, data_final)

df_count["data_treino"] = pd.to_datetime(df_count["data_treino"])
df_count = df_count.groupby(pd.Grouper(key="data_treino", freq="W"))["quantidade"].sum().reset_index()

df_weight["data_treino"] = pd.to_datetime(df_weight["data_treino"])
df_cardio["data_treino"] = pd.to_datetime(df_cardio["data_treino"])

df_types = df_types.rename(columns={"tipo": "Tipo", "quantidade": "Quantidade"})

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Progressão do Peso no Exercício")
        st.line_chart(df_weight, x="data_treino", y="peso", x_label="Data", y_label="Peso (kg)")

    with st.container(border=True):
        st.subheader("Quantidade de Treinos")
        st.bar_chart(df_count, x="data_treino", y="quantidade", x_label="Data", y_label="Quantidade")

with col2:
    with st.container(border=True):
        st.subheader("Progressão da Velocidade no Cardio")
        st.line_chart(df_cardio, x="data_treino", y="velocidade", x_label="Data", y_label="Velocidade (km/h)")

    with st.container(border=True):
            st.subheader("Progressão do Tempo no Cardio")
            st.line_chart(df_cardio, x="data_treino", y="tempo_corrida", x_label="Data", y_label="Tempo (min)")

with st.container(border=True):
    st.subheader("Exerícios por Tipo")
    fig = px.pie(
        df_types,
        names="Tipo",
        values="Quantidade",
        title="Distribuição dos Treinos")
    st.plotly_chart(fig)

    

    


    
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
    lista_cardio = df_exercicios.query("tipo == 'Aeróbico'")["exercicio"]

    exercicio = st.selectbox("Exercício", options=lista_exercicios, index=0)
    exercicio_cardio = st.selectbox("Exercício Cardio", options=lista_cardio, index=0)

    if usuario_admin == 1:
        lista_usuarios = listar_usuarios()
        usuario_escolhido = st.selectbox("Usuário", lista_usuarios["usuario"].tolist())

        usuario_id = lista_usuarios.loc[lista_usuarios["usuario"] == usuario_escolhido, "id"].iloc[0]

# ------------ Métricas ------------ #

m1, m2, m3, m4 = st.columns([1, 1.4, 1.4, 1.4])

qtd_treinos, tempo_corrida, distancia, tempo_total = dados_dashboard_metricas(usuario_id, 
                                                                                data_inicio, 
                                                                                data_final)

tempo_corrida = horas_e_minutos(tempo_corrida)
tempo_total = horas_e_minutos(tempo_total)

m1.metric("Idas à academia", qtd_treinos, border=True)
m2.metric("Tempo de treino", f"{tempo_total[0]}h{tempo_total[1]}min", border=True)
m3.metric("Distância no cardio", f"{distancia:.1f}km", border=True)
m4.metric("Tempo de corrida", f"{tempo_corrida[0]}h{tempo_corrida[1]}min", border=True)


# ----------- Gráficos ------------ #

df_weight, df_cardio, df_count, df_types = dados_dashboard_graphs(usuario_id, exercicio, exercicio_cardio, data_inicio, data_final)

df_count["data_treino"] = pd.to_datetime(df_count["data_treino"])

df_weight["data_treino"] = pd.to_datetime(df_weight["data_treino"])
df_cardio["data_treino"] = pd.to_datetime(df_cardio["data_treino"])

df_types = df_types.rename(columns={"tipo": "Tipo", "quantidade": "Quantidade"})

# GroupBy
df_cardio = df_cardio.groupby("data_treino", as_index=False).apply(
    lambda grupo: pd.Series({
        "velocidade": (grupo["velocidade"] * grupo["tempo_corrida"]).sum() / grupo["tempo_corrida"].sum(),
        "tempo_corrida": grupo["tempo_corrida"].sum()
    })
)

df_weight = df_weight.sort_values("data_treino")
df_weight["data_str"] = df_weight["data_treino"].dt.strftime("%d/%m/%Y")

df_weight = (
    df_weight.groupby("data_treino", as_index=False)["peso"]
    .mean() 
)
df_count = df_count.groupby(pd.Grouper(key="data_treino", freq="ME"))["quantidade"].sum().reset_index()
df_count["mes"] = df_count["data_treino"].dt.strftime("%m/%Y")
# ----- Gráfico do Peso ------ #

fig_weight = px.line(
    df_weight,
    x="data_str",
    y="peso",
    labels={
        "data_str": "Data",
        "peso": "Peso (kg)"
    }
)

fig_weight.update_traces(
    mode="lines+markers",
    marker=dict(color="#C6FF3A"),
    line=dict(color="#C6FF3A"),
    hovertemplate="Data: %{x|%d/%m/%Y}<br>Peso: %{y:.1f} kg<extra></extra>"
)

# ------- Gráfico Velocidade do cardio ----- #

fig_speed = px.line(
    df_cardio,
    x="data_treino",
    y="velocidade",
    labels={
        "data_treino": "Data",
        "velocidade": "Velocidade (km/h)",
    }
)

fig_speed.update_traces(
    mode="lines+markers",
    line=dict(color="#C6FF3A"),
    marker=dict(color="#C6FF3A"),
    hovertemplate="Data: %{x|%d/%m/%Y}<br>Velocidade: %{y:.1f} km/h<extra></extra>"
)

# ----- Gráfico Tempo no Cardio ------- #

fig_time = px.line(
    df_cardio,
    x="data_treino",
    y="tempo_corrida",
    labels={
        "data_treino": "Data",
        "tempo_corrida": "Tempo de corrida (min)",
    }
)

fig_time.update_traces(
    mode="markers",
    line=dict(color="#C6FF3A"),
    marker=dict(color="#C6FF3A"),
    hovertemplate="Data: %{x|%d/%m/%Y}<br>Tempo de corrida: %{y:.1f} min<extra></extra>"
)

# ------- Gráfico Quantidade de Treinos ------- #
fig_count = px.bar(
    df_count,
    x="mes",
    y="quantidade",
    labels={
        "mes": "Data",
        "quantidade": "Quantidade",
    }
)

fig_count.update_traces(
    marker=dict(color="#C6FF3A"),
    hovertemplate="Data: %{x|%d/%m/%Y}<br>Quantidade: %{y:.0f}<extra></extra>"
)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Progressão do Peso no Exercício")
        st.plotly_chart(fig_weight, width="stretch")

    with st.container(border=True):
        st.subheader("Quantidade de Treinos")
        st.plotly_chart(fig_count, width="stretch")

with col2:
    with st.container(border=True):
        st.subheader("Progressão da Velocidade no Cardio")
        st.plotly_chart(fig_speed, width="stretch")

    with st.container(border=True):
            st.subheader("Progressão do Tempo no Cardio")
            st.plotly_chart(fig_time, width="stretch")

with st.container(border=True):
    st.subheader("Exercícios por Tipo")
    fig = px.pie(
        df_types,
        names="Tipo",
        values="Quantidade"
        )
    fig.update_traces(
         marker=dict(
            colors=[
                "#C6FF3A",
                "#4CAF7D",
                "#7E57C2",
                "#29B6F6",
                "#FFB74D"
            ]
        ),
        hovertemplate="Tipo: %{label}<br>Quantidade: %{value:.0f}<br>Percentual: %{percent}<extra></extra>"
    )
    st.plotly_chart(fig)

    

    


    
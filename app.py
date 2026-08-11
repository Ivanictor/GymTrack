import streamlit as st
from style import aplicar_estilo

st.set_page_config(page_title="GymTrack", page_icon="🦾", layout="wide")
aplicar_estilo()

#Rotas

if "id" not in st.session_state:
    login = st.Page("pages/login.py", title="Login")
    register = st.Page("pages/register.py", title="Cadastro")
    forgot_password = st.Page("pages/forgot_password.py", title="Alterar a senha")

    pg = st.navigation([login, register, forgot_password])

else:
    daily_train = st.Page("pages/daily_train.py", title="Envio de Treinos")
    train_register = st.Page("pages/train_register.py", title="Cadastro de Treinos")
    view_train = st.Page("pages/view_train.py", title="Registro de Treinos Realizados")
    dashboard = st.Page("pages/dashboard.py", title="Dashboard")
    profile = st.Page("pages/profile.py", title="Dados de Perfil")
    testo = st.Page("pages/ranking_testo.py", title="Ranking Testo")

    pg = st.navigation([daily_train, train_register, view_train, dashboard, profile, testo])

pg.run()
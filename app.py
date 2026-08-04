import streamlit as st

#Rotas

if "id" not in st.session_state:
    login = st.Page("pages/login.py", title="Login")
    register = st.Page("pages/register.py", title="Cadastro")

    pg = st.navigation([login, register])

else:
    train_register = st.Page("pages/train_register.py", title="Registro de Treinos")
    pg = st.navigation([train_register])

pg.run()
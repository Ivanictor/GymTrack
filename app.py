import streamlit as st

#Rotas

if "id" not in st.session_state:
    login = st.Page("pages/login.py", title="Login")
    register = st.Page("pages/register.py", title="Cadastro")

    pg = st.navigation([login, register])

else:
    daily_train = st.Page("pages/daily_train.py", title="Envio de Treinos")
    train_register = st.Page("pages/train_register.py", title="Cadastro de Treinos")
    view_train = st.Page("pages/view_train.py", title="Registro de Treinos Realizados")
    
    pg = st.navigation([daily_train, train_register, view_train])

pg.run()
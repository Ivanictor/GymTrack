import streamlit as st
from db_acess import buscar_cadastro, buscar_senha
import time

st.title("GymTrack 🦾- Tela de Login")


with st.container(border=True):
    
    email = st.text_input("Email")

    senha = st.text_input("Senha", type="password")

    st.page_link("pages/register.py", label="Cadastre-se")
    st.page_link("pages/forgot_password.py", label="Esqueceu sua senha?")

    if st.button("Enviar"):

        if not email:
            st.error("Email não enviado")

        if not senha:
            st.error("Senha não enviada")

        email_registrado = buscar_cadastro(email)

        if not email_registrado:
            st.error("Email não cadastrado")

        elif not buscar_senha(email, senha):
            st.error("Senha incorreta")

        else:
            st.success("Login bem sucedido")
            st.balloons()
            time.sleep(2)

            usuario = buscar_cadastro(email)
            st.session_state.clear()

            st.session_state["id"] = usuario[0]
            st.session_state["nome"] = usuario[1]
            st.session_state["email"] = usuario[2]
            st.session_state["admin"] = usuario[4]

            st.rerun()
            st.switch_page("pages/train_register.py")

        
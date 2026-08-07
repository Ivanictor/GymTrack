import streamlit as st
from db_acess import salvar_cadastro, buscar_cadastro

st.title("GymTrack 🦾- Tela de Cadastro")

nome = st.text_input("Digite seu nome")

email = st.text_input("Digite seu email")

senha_1 = st.text_input("Digite sua senha", type="password")

senha_2 = st.text_input("Repita a senha", type="password")

if st.button("Enviar"):
    erros = []

    if not nome.strip():
        erros.append("Não informou o nome")

    if not email.strip():
       erros.append("Não informou o email")

    if "@" not in email:
        erros.append("Email inválido")

    if not senha_1.strip():
        erros.append("Não informou a senha")

    if not senha_2.strip():
        erros.append("Não repetiu a senha")

    if senha_1 != senha_2:
        erros.append("As duas senhas informadas não são iguais")

    registros_anteriores = buscar_cadastro(email)

    if registros_anteriores:
        erros.append("O email já foi cadastrado, use outro")

    if erros:
        st.error(f"Corrija as seguintes pendências:\n\n-" + "\n- ".join(erros))

    else:
        salvar_cadastro(nome, email, senha_1)
        st.success("Cadastro realizado com sucesso")
        st.switch_page("login.py")

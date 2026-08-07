import streamlit as st
import time
from db_acess import atualizar_perfil

st.title("Perfil no GymTracker 🦾")

usuario_id = st.session_state["id"]
nome = st.session_state["nome"]
email = st.session_state["email"]
admin = st.session_state["admin"]

novo_nome = st.text_input("Nome do usuário", value=nome)

novo_email = st.text_input("Email do usuário", value=email)

nova_senha = st.text_input("Senha (pode deixar em branco se não quiser alterar)", type="password")

nova_senha_2 = st.text_input("Repita a senha", type="password")

testo = st.number_input("Testosterona, em ng/dL (opcional)", min_value=0.0, step=0.01)

if admin == 1:
    st.text_input("Admin", admin, disabled=True)


st.page_link("pages/daily_train.py", label="Clique aqui se não quiser mudar nada")

col1, col2 = st.columns([0.5, 1.5])

with col1:
    if st.button("Atualizar dados"):
        erros = []
        if not novo_nome:
            erros.append("Informe o nome")

        if not novo_email:
            erros.append("Informe o email")

        if nova_senha != nova_senha_2:
            erros.append("As senhas devem ser iguais")

        if erros:
            st.error(f"Corrija as seguintes pendências:\n\n-" + "\n- ".join(erros))
        else:
            if not testo:
                testo = 0
            if not nova_senha:
                nova_senha = None
            try:
                atualizar_perfil(usuario_id, novo_nome, novo_email, nova_senha, testo)
                time.sleep(2)

            except Exception as e:
                st.error(f"Erro ao atualizar o perfil: {e}")

            else:
                st.success("Cadastro realizado com sucesso")
                st.switch_page("pages/daily_train.py")

with col2:
    if st.button("Deslogar"):
        st.session_state.clear()
        st.rerun()

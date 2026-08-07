import streamlit as st
import time
from db_acess import atualizar_senha

st.write("Esqueceu sua senha?")

email = st.text_input("Informe o email que você registrou")

nova_senha = st.text_input("Senha", type="password")

nova_senha_2 = st.text_input("Repita a senha", type="password")

st.page_link("pages/login.py", label="Clique aqui para voltar ao login")

if st.button("Enviar"):
    erros = []
    if not email:
        erros.append("Informe o email")

    if not nova_senha:
        erros.append("Informe a nova senha")

    if nova_senha != nova_senha_2:
        erros.append("As senhas devem ser iguais")

    if erros:
        st.error(f"Corrija as seguintes pendências:\n\n-" + "\n- ".join(erros))
    else:
        try:
            atualizar_senha(email, nova_senha)
            time.sleep(2)

        except Exception as e:
                    st.error(f"Erro ao alterar a senha: {e}")
        
        finally:
            st.success("Senha alterada com sucesso")
            st.switch_page("pages/login.py")
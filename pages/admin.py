import streamlit as st
from db_acess import ranking_testo

st.title("GymTrack 🦾 - Tela de Administrador")

st.subheader("Usuários cadastrados")

df = ranking_testo(testo=False)

st.dataframe(df, hide_index=True)

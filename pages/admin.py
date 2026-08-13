import streamlit as st
from db_acess import query_cadastros

st.title("GymTrack 🦾 - Tela de Administrador")

st.subheader("Usuários cadastrados")

df = query_cadastros()

st.dataframe(df)

import streamlit as st
from db_acess import buscar_todos_cadastros

st.title("GymTrack 🦾 - Tela de Administrador")

st.subheader("Usuários cadastrados")

df = buscar_todos_cadastros()

st.dataframe(df)

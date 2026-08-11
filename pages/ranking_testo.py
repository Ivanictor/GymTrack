import streamlit as st
from db_acess import ranking_testo

st.title("GymTrack 🦾 - Ranking de Testo")

df_testo = ranking_testo()
df_testo = df_testo.drop(columns=["id"])

df_testo = df_testo.rename(columns={
    "usuario": "Usuário",
    "testo": "Testo (ng/dL)"
})

df_testo["Posição"] = None

for i in range(len(df_testo)):
    df_testo.loc[i, "Posição"] = str(i+1) + "º"

df_testo = df_testo[
    ["Posição", "Usuário", "Testo (ng/dL)"]
]

st.dataframe(df_testo, hide_index=True)
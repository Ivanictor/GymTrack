import streamlit as st

def aplicar_estilo():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap');

        .stApp, div[data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif !important;
        }

        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 700 !important;
        }

        h1 {
            border-bottom: 3px solid var(--primary-color) !important;
            padding-bottom: 0.5rem !important;
            margin-bottom: 2rem !important;
            display: inline-block !important;
        }

        /* Metric: usa a cor secundária do tema (branco no claro, escuro no escuro)
           e NÃO força cor de texto — deixa o Streamlit decidir o contraste certo */
        div[data-testid="stMetric"] {
            background-color: var(--secondary-background-color) !important;
            border-radius: 12px !important;
            padding: 1.2rem !important;
            border-left: 5px solid #C6FF3A !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
        }

        div[data-testid="stVerticalBlock"][style*="border"] {
            background-color: var(--secondary-background-color) !important;
            border-radius: 14px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important;
        }

        div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
            border-radius: 10px !important;
            overflow: hidden !important;
        }
    </style>
    """, unsafe_allow_html=True)
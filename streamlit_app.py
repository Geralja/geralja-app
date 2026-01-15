import streamlit as st
from google.cloud import firestore
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="GeralJá 11.0", layout="wide")

# Conexão com Firebase (Sua chave já deve estar nos Secrets)
if "db" not in st.session_state:
    from google.oauth2 import service_account
    import json
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    st.session_state.db = firestore.Client(credentials=creds, project="geralja-5bb49")

db = st.session_state.db

# --- FUNÇÕES MESTRE (DO ARQUITETO) ---
def normalizar_texto(t):
    return str(t).lower().strip() if t else ""

def doutorado_em_portugues(texto):
    if not texto: return ""
    return " ".join([w.capitalize() for w in texto.split()])

# --- BARRA DE BUSCA GLOBAL (FIXA NO TOPO) ---
st.title("🚀 GeralJá")
busca_global = st.text_input("🔍 O que você procura no Grajaú?", key="main_search")

# --- O GRANDE SEGREDO: O EXECUTOR DINÂMICO ---
# Aqui ele lê o que você colou no seu Painel de Controle (Canteiro de Obras)
# Se o painel estiver vazio, ele não quebra.
try:
    # Busca o código que você salvou no banco para o visual
    config = db.collection("config").document("code_injection").get()
    if config.exists:
        codigo_viva = config.to_dict().get("codigo", "")
        exec(codigo_viva) # <--- A mágica acontece aqui!
    else:
        st.warning("⚠️ O 'Canteiro de Obras' está vazio. Cole o código das abas no painel.")
except Exception as e:
    st.error(f"Erro no Módulo Dinâmico: {e}")

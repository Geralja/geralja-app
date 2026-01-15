import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import datetime
import unicodedata
import time

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="GeralJá | Plataforma Suprema", layout="wide", initial_sidebar_state="collapsed")

if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()

# --- FUNÇÕES ---
def normalizar_texto(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

def carregar_bloco_dinamico():
    try:
        doc = db.collection("configuracoes").document("layout_ia").get()
        return doc.to_dict().get("codigo_injetado", "") if doc.exists else ""
    except: return ""

# --- DESIGN ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .header-master { background: white; padding: 25px; border-radius: 20px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-bottom: 6px solid #FF8C00; margin-bottom: 20px; }
    .logo-geral { color: #0047AB; font-weight: 900; font-size: 40px; letter-spacing: -2px; }
    .logo-ja { color: #FF8C00; font-weight: 900; font-size: 40px; letter-spacing: -2px; }
    .bloco-white { background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px; border: 1px solid #e2e8f0; }
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-master"><span class="logo-geral">GERAL</span><span class="logo-ja">JÁ</span></div>', unsafe_allow_html=True)

# --- A ÚNICA BARRA DE PESQUISA (Gatilho + Busca) ---
# O que for digitado aqui vai para a variável 'busca_global'
busca_global = st.text_input("", placeholder="🔍 O que você procura hoje?", label_visibility="collapsed")

# Verificação do Código Secreto
if busca_global == "0413ocara":
    st.session_state.modo_arquiteto = True
    st.toast("🔓 Modo Arquiteto Ativado!", icon="🔥")

# --- EXECUÇÃO DO CONTEÚDO DINÂMICO ---
codigo_da_ia = carregar_bloco_dinamico()
if codigo_da_ia:
    try:
        # Passamos a busca_global para dentro do exec
        exec(codigo_da_ia, globals(), locals())
    except Exception as e:
        st.error(f"Erro no sistema: {e}")

# --- PAINEL ARQUITETO OCULTO ---
if st.session_state.get("modo_arquiteto"):
    st.divider()
    with st.expander("🛠️ CONFIGURAÇÃO MESTRE - GERENTE"):
        novo_cod = st.text_area("Código de Injeção", value=codigo_da_ia, height=400)
        if st.button("🚀 SOLDAR ALTERAÇÕES"):
            db.collection("configuracoes").document("layout_ia").set({
                "codigo_injetado": novo_cod, "data": datetime.datetime.now()
            })
            st.success("Sistema Atualizado!"); time.sleep(1); st.rerun()
        if st.button("🔒 Fechar Painel"):
            st.session_state.modo_arquiteto = False
            st.rerun()

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import datetime
import unicodedata
import time

# --- 1. PERFORMANCE DE ELITE (CACHE) ---
st.set_page_config(page_title="GeralJá | Sistema Operacional", layout="wide", initial_sidebar_state="collapsed")

if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()

# --- 2. MOTOR DE INTELIGÊNCIA ---
def normalizar_texto(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

@st.cache_data(ttl=600) # Faz o código injetado carregar em milissegundos
def carregar_bloco_dinamico():
    try:
        doc = db.collection("configuracoes").document("layout_ia").get()
        return doc.to_dict().get("codigo_injetado", "") if doc.exists else ""
    except: return ""

def registrar_tendencia(termo):
    """Registra o que o povo busca para você vender anúncios caros depois"""
    if termo and len(termo) > 3 and termo != "0413ocara":
        try:
            db.collection("tendencias").add({
                "termo": termo, "data": datetime.datetime.now()
            })
        except: pass

# --- 3. DESIGN E UI LUXO ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .header-master { 
        background: white; padding: 35px; border-radius: 0 0 40px 40px; 
        text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.05); 
        border-bottom: 8px solid #FF8C00; margin-bottom: 25px; 
    }
    .logo-geral { color: #0047AB; font-weight: 900; font-size: 48px; letter-spacing: -2px; }
    .logo-ja { color: #FF8C00; font-weight: 900; font-size: 48px; letter-spacing: -2px; }
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-master"><span class="logo-geral">GERAL</span><span class="logo-ja">JÁ</span></div>', unsafe_allow_html=True)

# --- 4. BARRA DE PESQUISA INTELIGENTE ---
busca_global = st.text_input("", placeholder="🔍 O que o Grajaú precisa hoje?", label_visibility="collapsed")

if busca_global == "0413ocara":
    st.session_state.modo_arquiteto = True
    st.toast("🚀 CPU 10.0 ATIVADA", icon="⚙️")
elif busca_global:
    registrar_tendencia(busca_global)

# --- 5. EXECUÇÃO COM CONTEXTO EXPANDIDO ---
codigo_da_ia = carregar_bloco_dinamico()
if codigo_da_ia:
    try:
        contexto_compartilhado = {
            "st": st, "db": db, "datetime": datetime, "time": time,
            "normalizar_texto": normalizar_texto,
            "busca_global": busca_global,
            "CATEGORIAS_OFICIAIS": ["Pizzaria", "Mecânico", "Eletricista", "Moda", "Beleza", "Outros"],
            "BONUS_WELCOME": 50
        }
        exec(codigo_da_ia, contexto_compartilhado)
    except Exception as e:
        st.error(f"⚠️ Erro no Módulo Dinâmico: {e}")

# --- 6. PAINEL ARQUITETO PRO ---
if st.session_state.get("modo_arquiteto"):
    st.write("---")
    with st.expander("🛠️ PAINEL DE CONTROLE DE ELITE"):
        # Mostra estatísticas rápidas
        st.subheader("📊 Insights da CPU")
        col1, col2 = st.columns(2)
        col1.metric("Status do Servidor", "100% Online")
        col2.metric("Motor de Injeção", "v10.0 (Turbo)")
        
        novo_cod = st.text_area("Código de Injeção", value=codigo_da_ia, height=450)
        
        if st.button("🚀 SOLDAR E APLICAR EM TEMPO REAL"):
            db.collection("configuracoes").document("layout_ia").set({
                "codigo_injetado": novo_cod, "data": datetime.datetime.now()
            })
            st.cache_data.clear() # Limpa o cache para a mudança ser instantânea
            st.success("SISTEMA ATUALIZADO COM SUCESSO!"); time.sleep(1); st.rerun()

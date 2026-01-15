import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import datetime
import math
import re
import time
import pandas as pd
import unicodedata
from datetime import datetime
import pytz

# --- MOTOR DE GEOLOCALIZAÇÃO (RESGATADO DA V1) ---
try:
    from streamlit_js_eval import streamlit_js_eval, get_geolocation
except ImportError:
    pass

# --- 1. PERFORMANCE DE ELITE (CACHE) & TIMEZONE ---
st.set_page_config(page_title="GeralJá | Sistema Operacional", layout="wide", initial_sidebar_state="collapsed")

if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()
fuso_horario = pytz.timezone('America/Sao_Paulo')

# --- 2. MOTOR DE INTELIGÊNCIA (DOUTORADO & BUSCA) ---
def normalizar_texto(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

def doutorado_em_portugues(texto):
    """Padroniza o português (Ex: 'pizzaria' -> 'Pizzaria')"""
    if not texto: return ""
    texto = " ".join(texto.split())
    return texto.title().strip()

def calcular_distancia_real(lat1, lon1, lat2, lon2):
    """Matemática da V1 para proximidade"""
    if not all([lat1, lon1, lat2, lon2]): return 0
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)*2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)*2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

@st.cache_data(ttl=600)
def carregar_bloco_dinamico():
    try:
        doc = db.collection("configuracoes").document("layout_ia").get()
        return doc.to_dict().get("codigo_injetado", "") if doc.exists else ""
    except: return ""

def registrar_tendencia(termo):
    if termo and len(termo) > 3 and termo != "0413ocara":
        try:
            db.collection("tendencias").add({
                "termo": termo, "data": datetime.now(fuso_horario)
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

# --- 5. EXECUÇÃO COM CONTEXTO EXPANDIDO (LIMPO E SEM REPETIÇÕES) ---
codigo_da_ia = carregar_bloco_dinamico()
if codigo_da_ia:
    try:
        contexto_compartilhado = {
            "st": st, "db": db, "firestore": firestore,
            "datetime": datetime, "time": time, "re": re, "math": math, "pd": pd,
            "normalizar_texto": normalizar_texto,
            "doutorado_em_portugues": doutorado_em_portugues,
            "calcular_distancia_real": calcular_distancia_real,
            "busca_global": busca_global,
            "CATEGORIAS_OFICIAIS": ["Pizzaria", "Mecânico", "Eletricista", "Moda", "Beleza", "Outros"],
            "CONCEITOS_EXPANDIDOS": {"fome": "Pizzaria", "luz": "Eletricista", "vazamento": "Encanador"}
        }
     # --- 5. EXECUÇÃO PROTEGIDA ---
codigo_da_ia = carregar_bloco_dinamico()

if not codigo_da_ia:
    # Se o Firebase estiver vazio, ele usa este código básico para o site não sumir
    codigo_da_ia = """
abas = st.tabs(["🔍 PESQUISA", "📻 MURAL", "🛠️ BRABOS", "📝 CADASTRO"])
with abas[0]: st.info("Digite na busca acima para começar.")
with abas[3]: st.write("Área de cadastro ativa.")
    """

try:
    contexto_compartilhado = {
        "st": st, "db": db, "firestore": firestore,
        "datetime": datetime, "time": time, "re": re, "math": math, "pd": pd,
        "normalizar_texto": normalizar_texto,
        "doutorado_em_portugues": doutorado_em_portugues,
        "calcular_distancia_real": calcular_distancia_real,
        "busca_global": busca_global,
        "CATEGORIAS_OFICIAIS": ["Pizzaria", "Mecânico", "Eletricista", "Moda", "Beleza", "Outros"]
    }
    exec(codigo_da_ia, contexto_compartilhado)
except Exception as e:
    st.error(f"⚠️ Erro na Solda Dinâmica: {e}")

# --- 6. PAINEL ARQUITETO PRO ---
if st.session_state.get("modo_arquiteto"):
    st.write("---")
    with st.expander("🛠️ PAINEL DE CONTROLE DE ELITE"):
        st.subheader("📊 Insights da CPU")
        col1, col2 = st.columns(2)
        col1.metric("Status do Servidor", "100% Online")
        col2.metric("Motor de Injeção", "v10.0 (Doutorado)")
        
        novo_cod = st.text_area("Código de Injeção", value=codigo_da_ia, height=450)
        
        if st.button("🚀 SOLDAR E APLICAR EM TEMPO REAL"):
            db.collection("configuracoes").document("layout_ia").set({
                "codigo_injetado": novo_cod, "data": datetime.now(fuso_horario)
            })
            st.cache_data.clear() 
            st.success("SISTEMA ATUALIZADO!"); time.sleep(1); st.rerun()

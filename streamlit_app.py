
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

# --- MOTOR DE GEOLOCALIZAÇÃO ---
try:
    from streamlit_js_eval import streamlit_js_eval, get_geolocation
except ImportError:
    pass

# --- 1. CONFIGURAÇÃO DE ELITE ---
st.set_page_config(page_title="GeralJá | Sistema Operacional", layout="wide", initial_sidebar_state="collapsed")

if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()
fuso_horario = pytz.timezone('America/Sao_Paulo')

# --- 2. MOTOR DE INTELIGÊNCIA ---
def normalizar_texto(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

def doutorado_em_portugues(texto):
    if not texto: return ""
    return texto.strip().title()

def calcular_distancia_real(lat1, lon1, lat2, lon2):
    if not all([lat1, lon1, lat2, lon2]): return 0
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

@st.cache_data(ttl=600)
def carregar_bloco_dinamico():
    try:
        doc = db.collection("configuracoes").document("layout_ia").get()
        return doc.to_dict().get("codigo_injetado", "") if doc.exists else ""
    except: return ""

# --- 3. DESIGN LUXO ---
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

# --- 4. BUSCA GLOBAL ---
busca_global = st.text_input("", placeholder="🔍 O que o Grajaú precisa hoje?", label_visibility="collapsed")

if busca_global == "0413ocara":
    st.session_state.modo_arquiteto = True
    st.toast("🚀 CPU 10.0 ATIVADA")

# --- 5. EXECUÇÃO DO CÓDIGO DINÂMICO ---
codigo_da_ia = carregar_bloco_dinamico()

if not codigo_da_ia:
    codigo_da_ia = "st.info('Aguardando injeção de código...')"

contexto_compartilhado = {
    "st": st, "db": db, "firestore": firestore, "datetime": datetime, 
    "time": time, "math": math, "pd": pd, "normalizar_texto": normalizar_texto,
    "doutorado_em_portugues": doutorado_em_portugues, "busca_global": busca_global,
    "CATEGORIAS_OFICIAIS": ["Pizzaria", "Mecânico", "Eletricista", "Moda", "Beleza", "Outros"]
}

try:
    exec(codigo_da_ia, contexto_compartilhado)
except Exception as e:
    st.error(f"⚠️ Erro no Módulo Dinâmico: {e}")

# --- 6. PAINEL ARQUITETO PRO ---
if st.session_state.get("modo_arquiteto"):
    st.write("---")
    with st.expander("🛠️ PAINEL DE CONTROLE DE ELITE"):
        novo_cod = st.text_area("Código de Injeção", value=codigo_da_ia, height=450)
        if st.button("🚀 SOLDAR E APLICAR"):
            db.collection("configuracoes").document("layout_ia").set({
                "codigo_injetado": novo_cod, "data": datetime.now(fuso_horario)
            })
            st.cache_data.clear()
            st.success("SISTEMA ATUALIZADO!"); time.sleep(1); st.rerun()

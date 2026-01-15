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

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DE AMBIENTE E PERFORMANCE
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="GeralJá | Criando Soluções",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DESIGN SYSTEM CENTRALIZADO (GLASSMORPHISM) ---
st.markdown("""
<style>
    .block-container {
        max-width: 900px !important;
        padding-top: 2rem !important;
        margin: auto !important;
    }
    .header-container { 
        background: white; 
        padding: 40px 20px; 
        border-radius: 0 0 50px 50px; 
        text-align: center; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); 
        border-bottom: 8px solid #FF8C00; 
        margin-bottom: 25px; 
    }
    .logo-azul { color: #0047AB; font-weight: 900; font-size: 50px; letter-spacing: -2px; }
    .logo-laranja { color: #FF8C00; font-weight: 900; font-size: 50px; letter-spacing: -2px; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. CONEXÃO FIREBASE
# ------------------------------------------------------------------------------
@st.cache_resource
def conectar_banco_master():
    if not firebase_admin._apps:
        try:
            if "FIREBASE_BASE64" in st.secrets:
                b64_key = st.secrets["FIREBASE_BASE64"]
                decoded_json = base64.b64decode(b64_key).decode("utf-8")
                cred_dict = json.loads(decoded_json)
                cred = credentials.Certificate(cred_dict)
                return firebase_admin.initialize_app(cred)
            else:
                st.warning("⚠️ Configure a secret FIREBASE_BASE64.")
                return None
        except Exception as e:
            st.error(f"❌ FALHA: {e}")
            st.stop()
    return firebase_admin.get_app()

app_engine = conectar_banco_master()
db = firestore.client() if app_engine else None

# ------------------------------------------------------------------------------
# 3. COMPONENTES E FUNÇÕES
# ------------------------------------------------------------------------------
def converter_img_b64(file):
    try: return base64.b64encode(file.read()).decode()
    except: return ""

st.markdown('<div class="header-container"><span class="logo-azul">GERAL</span><span class="logo-laranja">JÁ</span><br><small style="color:#64748B; font-weight:700;">BRASIL ELITE EDITION</small></div>', unsafe_allow_html=True)

# LISTA DE ABAS ATUALIZADA
lista_abas = ["🔍 BUSCAR", "📻 COMUNIDADE", "🚀 CADASTRAR", "👤 MEU PERFIL", "👑 ADMIN"]
menu_abas = st.tabs(lista_abas)

# ==============================================================================
# ABA 1: BUSCAR (Mantida da sua V1 com melhorias de IA)
# ==============================================================================
with menu_abas[0]:
    st.write("### 🏙️ Encontre Profissionais na Zona Sul")
    # ... (Seu código original de busca via IA e ranking elite aqui)

# ==============================================================================
# ABA 2: 📻 COMUNIDADE (O NOVO FEED HÍBRIDO)
# ==============================================================================
with menu_abas[1]:
    st.markdown("### 🔥 GRAJAÚ TEM: NOTÍCIAS AO VIVO")
    
    # 1. PAINEL DE POSTAGEM (SÓ PARA VOCÊ)
    if st.session_state.get('user_id') == "11991853488": # Seu número cadastrado
        with st.expander("📝 POSTAR NO FEED (EXCLUSIVO ADMIN)"):
            with st.form("form_feed"):
                t_news = st.text_input("Título (Ex: Família procura irmãos)")
                d_news = st.text_area("Descrição Curta")
                l_news = st.text_input("Link da Matéria (Rádio/Portal)")
                if st.form_submit_button("PUBLICAR AGORA"):
                    db.collection("feed_comunidade").add({
                        "titulo": t_news, "desc": d_news, "link": l_news,
                        "tipo": "EXCLUSIVA", "data": datetime.now()
                    })
                    st.success("Postado no GeralJá! 🚀")
                    time.sleep(1)
                    st.rerun()

    st.divider()

    # 2. EXIBIÇÃO DO FEED (Busca no Firebase)
    try:
        docs = db.collection("feed_comunidade").order_by("data", direction=firestore.Query.DESCENDING).limit(10).stream()
        for doc in docs:
            item = doc.to_dict()
            st.markdown(f"""
                <div style="background: rgba(255,140,0,0.1); padding: 15px; border-left: 5px solid #FF8C00; border-radius: 12px; margin-bottom: 15px;">
                    <span style="color: #FF8C00; font-weight: bold; font-size: 12px;">⭐ EXCLUSIVA GRAJAÚ TEM</span>
                    <h4 style="margin: 5px 0; color: #0047AB;">{item['titulo']}</h4>
                    <p style="font-size: 14px; color: #64748B;">{item['desc']}</p>
                    <a href="{item['link']}" target="_blank" style="color: #FF8C00; text-decoration: none; font-weight: bold;">LER NA ÍNTEGRA →</a>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.info("O feed está sendo atualizado...")

# ==============================================================================
# ABA 3: CADASTRAR (Sua V1 Blindada)
# ==============================================================================
with menu_abas[2]:
    # (Mantenha seu código original de formulário da Aba 2 aqui)
    pass

# ==============================================================================
# ABA 4: MEU PERFIL E ABA 5: ADMIN (Mantidos da sua V1)
# ==============================================================================
# ... (Mantenha o restante do seu código original)

st.write("---")
st.markdown("<div style='text-align:center; color:gray; font-size:12px;'>v3.1 | IA Mestra Integrada</div>", unsafe_allow_html=True)

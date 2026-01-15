# ==============================================================================
# GERALJÁ: V2 TURBO - COMUNIDADE + BUSCA IA
# ==============================================================================
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

# Tenta importar bibliotecas extras
try:
    from streamlit_js_eval import streamlit_js_eval, get_geolocation
except ImportError:
    pass

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DE AMBIENTE
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="GeralJá | Criando Soluções",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DESIGN SYSTEM CENTRALIZADO ---
st.markdown("""
<style>
    .block-container { max-width: 900px !important; padding-top: 1rem !important; margin: auto !important; }
    .stApp { background-color: #f8fafc; }
    .header-container { 
        background: white; padding: 30px; border-radius: 0 0 40px 40px; 
        text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
        border-bottom: 6px solid #FF8C00; margin-bottom: 20px; 
    }
    .logo-azul { color: #0047AB; font-weight: 900; font-size: 45px; letter-spacing: -2px; }
    .logo-laranja { color: #FF8C00; font-weight: 900; font-size: 45px; letter-spacing: -2px; }
    /* Estilo dos Cards de Notícia */
    .card-noticia {
        background: white; padding: 20px; border-radius: 15px;
        border-left: 6px solid #FF8C00; margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. CONEXÃO FIREBASE (BLINDADA)
# ------------------------------------------------------------------------------
if not firebase_admin._apps:
    try:
        if "FIREBASE_BASE64" in st.secrets:
            b64_key = st.secrets["FIREBASE_BASE64"]
            decoded_json = base64.b64decode(b64_key).decode("utf-8")
            cred_dict = json.loads(decoded_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            st.error("Erro: FIREBASE_BASE64 não encontrada nas Secrets.")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")

db = firestore.client()

# --- MOTOR DE INTELIGÊNCIA GERALJÁ ---
class MotorGeralJa:
    @staticmethod
    def normalizar(texto):
        if not texto: return ""
        return "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower().strip()

# ------------------------------------------------------------------------------
# 3. INTERFACE E ABAS
# ------------------------------------------------------------------------------
st.markdown('<div class="header-container"><span class="logo-azul">GERAL</span><span class="logo-laranja">JÁ</span><br><small style="color:#64748B;">ZONA SUR • COMUNIDADE • SERVIÇOS</small></div>', unsafe_allow_html=True)

menu_abas = st.tabs(["🔍 BUSCAR", "📻 COMUNIDADE", "🚀 CADASTRAR", "👤 PAINEL", "👑 ADMIN"])

# --- ABA 1: BUSCAR (Sua Lógica da V1) ---
with menu_abas[0]:
    busca_termo = st.text_input("🤖 O que você procura hoje?", placeholder="Ex: Mecânico, Pedreiro, Pizza...")
    if busca_termo:
        st.info(f"Buscando por: {busca_termo}...")
        # Aqui o seu código de busca do Firebase da V1 deve rodar
        profissionais = db.collection("profissionais").stream()
        for p in profissionais:
            dados = p.to_dict()
            if MotorGeralJa.normalizar(busca_termo) in MotorGeralJa.normalizar(dados.get('nome', '')):
                st.write(f"✅ {dados.get('nome')}")

# --- ABA 2: COMUNIDADE (O NOVO FEED) ---
with menu_abas[1]:
    st.subheader("📻 Mural Grajaú Tem")
    
    # Postar Notícia (Admin)
    if st.session_state.get('user_id') == "11991853488" or st.checkbox("Modo Editor (Teste)"):
        with st.expander("📝 Nova Postagem"):
            t = st.text_input("Título")
            d = st.text_area("Texto curto")
            l = st.text_input("Link (opcional)")
            if st.button("Publicar"):
                db.collection("feed_comunidade").add({"titulo":t, "desc":d, "link":l, "data":datetime.now()})
                st.success("Postado!")
                st.rerun()

    # Mostrar Notícias
    docs = db.collection("feed_comunidade").order_by("data", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in docs:
        n = doc.to_dict()
        st.markdown(f"""
            <div class="card-noticia">
                <h4 style="color:#0047AB; margin:0;">{n.get('titulo')}</h4>
                <p style="color:#475569; font-size:14px;">{n.get('desc')}</p>
                <a href="{n.get('link')}" style="color:#FF8C00; font-weight:bold; text-decoration:none;">VER MAIS →</a>
            </div>
        """, unsafe_allow_html=True)

# --- ABA 3: CADASTRAR (Sua V1) ---
with menu_abas[2]:
    st.header("🚀 Cadastro de Profissional")
    with st.form("cadastro_prof"):
        nome = st.text_input("Nome da Loja/Profissional")
        zap = st.text_input("WhatsApp (apenas números)")
        senha = st.text_input("Crie uma Senha", type="password")
        if st.form_submit_button("CADASTRAR"):
            if nome and zap:
                db.collection("profissionais").document(zap).set({
                    "nome": nome, "whatsapp": zap, "senha": senha, "saldo": 50
                })
                st.success("Cadastrado com sucesso! Ganhou 50 moedas.")

# --- ABA 4: PAINEL (Login) ---
with menu_abas[3]:
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        u = st.text_input("WhatsApp")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            doc = db.collection("profissionais").document(u).get()
            if doc.exists and doc.to_dict().get('senha') == p:
                st.session_state.auth = True
                st.session_state.user_id = u
                st.rerun()
    else:
        st.write(f"Bem-vindo ao seu painel!")
        if st.button("Sair"):
            st.session_state.auth = False
            st.rerun()

# --- ABA 5: ADMIN (Sua V1) ---
with menu_abas[4]:
    chave = st.text_input("Chave Mestra", type="password")
    if chave == "suachaveaqui": # Troque pela sua chave
        st.write("Painel Administrativo Ativo")
        # Lista profissionais para editar saldo etc.

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import datetime
import unicodedata
import time

# --- CONFIGURAÇÃO DE ELITE ---
st.set_page_config(page_title="GeralJá | Plataforma Suprema", layout="wide", initial_sidebar_state="collapsed")

if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()

# --- MOTOR DE NORMALIZAÇÃO ---
def normalizar_texto(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

def carregar_bloco_dinamico():
    try:
        doc = db.collection("configuracoes").document("layout_ia").get()
        return doc.to_dict().get("codigo_injetado", "") if doc.exists else ""
    except: return ""

# --- DESIGN GLASSMORPHISM (O QUE VOCÊ GOSTOU) ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .block-container { max-width: 950px !important; padding-top: 1rem !important; margin: auto !important; }
    
    .header-master { 
        background: white; padding: 35px; border-radius: 0 0 40px 40px; 
        text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.05); 
        border-bottom: 8px solid #FF8C00; margin-bottom: 25px; 
    }
    .logo-geral { color: #0047AB; font-weight: 900; font-size: 48px; letter-spacing: -2px; }
    .logo-ja { color: #FF8C00; font-weight: 900; font-size: 48px; letter-spacing: -2px; }
    
    /* Input Estilizado */
    .stTextInput input {
        border-radius: 15px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 12px 20px !important;
        font-size: 18px !important;
    }
    
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<div class="header-master"><span class="logo-geral">GERAL</span><span class="logo-ja">JÁ</span><br><small style="color:#64748B; font-weight:700;">BRASIL ELITE EDITION</small></div>', unsafe_allow_html=True)

# --- BARRA DE PESQUISA COM SENHA OCULTA ---
# Usamos 'type="password"' para que o código 0413ocara vire bolinhas
busca_global = st.text_input("🔍 O que você procura hoje?", placeholder="Digite sua busca ou código...", type="password", label_visibility="collapsed")

# Ativação do Modo Arquiteto
if busca_global == "0413ocara":
    st.session_state.modo_arquiteto = True
    st.toast("🔓 MODO ARQUITETO ATIVADO", icon="🔥")

# --- EXECUÇÃO DO CONTEÚDO ---
codigo_da_ia = carregar_bloco_dinamico()
if codigo_da_ia:
    try:
        # Passa a busca para o código injetado
        exec(codigo_da_ia, globals(), locals())
    except Exception as e:
        st.error(f"Erro no sistema: {e}")

# --- PAINEL ARQUITETO (SÓ APARECE COM O CÓDIGO) ---
if st.session_state.get("modo_arquiteto"):
    st.write("---")
    with st.expander("🛠️ CANTEIRO DE OBRAS (ADMIN)"):
        st.caption("Modifique o código das abas e do feed abaixo:")
        novo_cod = st.text_area("Injetor de Código", value=codigo_da_ia, height=450)
        
        col_adm1, col_adm2 = st.columns(2)
        with col_adm1:
            if st.button("🚀 SOLDAR ALTERAÇÕES", use_container_width=True):
                db.collection("configuracoes").document("layout_ia").set({
                    "codigo_injetado": novo_cod, "data": datetime.datetime.now()
                })
                st.success("Sistema Atualizado!"); time.sleep(1); st.rerun()
        with col_adm2:
            if st.button("🔒 FECHAR E BLOQUEAR", use_container_width=True):
                st.session_state.modo_arquiteto = False
                st.rerun()

st.markdown('<div style="text-align:center; color:#cbd5e1; font-size:10px; margin-top:50px;">GeralJá v3.5 | Engine Elite</div>', unsafe_allow_html=True)

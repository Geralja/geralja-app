import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import datetime
import math
import re
import unicodedata
from io import BytesIO

# ==============================================================================
# 🛡️ 1. CONFIGURAÇÕES E CONSTANTES (O QUE ESTAVA FALTANDO)
# ==============================================================================
st.set_page_config(page_title="GeralJá | Plataforma Suprema", layout="wide")

# Constantes de Elite
CHAVE_ADMIN = "123" # Sua senha
BONUS_WELCOME = 50
CATEGORIAS_OFICIAIS = ["Pizzaria", "Mecânico", "Eletricista", "Moda", "Beleza", "Outros"]

# Conexão Firebase
if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()

# --- FERRAMENTAS TURBO ---
def converter_img_b64(file):
    if file:
        return base64.b64encode(file.read()).decode()
    return ""

def sanitizar(t):
    return re.sub(r'<[^>]*?>', '', t).strip() if t else ""

def enviar_alerta_admin(nome, area, zap):
    msg = f"Novo Cadastro: {nome} ({area}) - WhatsApp: {zap}"
    return f"https://wa.me/5511999999999?text={msg}" # Coloque seu zap aqui

# ==============================================================================
# 🧠 2. MOTOR DO ARQUITETO
# ==============================================================================
def carregar_bloco_dinamico():
    try:
        doc = db.collection("configuracoes").document("layout_ia").get()
        return doc.to_dict().get("codigo_injetado", "") if doc.exists else ""
    except: return ""

def painel_adm_arquiteto():
    with st.sidebar:
        st.markdown("### ⚙️ Painel de Controle")
        with st.expander("🔐 MODO ARQUITETO"):
            senha = st.text_input("Senha Master", type="password", key="master_pass")
            if senha == CHAVE_ADMIN:
                novo_cod = st.text_area("Injetor de Código", height=300, key="inj_area")
                if st.button("🚀 SOLDAR NO SITE AGORA"):
                    db.collection("configuracoes").document("layout_ia").set({"codigo_injetado": novo_cod, "data": datetime.datetime.now()})
                    st.success("Soldado!"); st.rerun()

# ==============================================================================
# 🏗️ 3. CONSTRUTOR PRINCIPAL
# ==============================================================================
def main():
    st.markdown("""<style>.stApp { background-color: #f0f2f5; } .bloco { background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; border: 1px solid #e1e4e8; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }</style>""", unsafe_allow_html=True)

    col_lateral, col_central = st.columns([1, 2.5])

    with col_lateral:
        st.markdown('<div class="bloco">### 🧭 Navegação</div>', unsafe_allow_html=True)
        painel_adm_arquiteto()

    with col_central:
        # Capa
        st.markdown('<div style="background: linear-gradient(135deg, #1d4ed8 0%, #1e3a8a 100%); border-radius: 15px; padding: 30px; color: white; margin-bottom: 20px;"><h1>GeralJá Turbo 🎯</h1></div>', unsafe_allow_html=True)

        # --- CANTEIRO DE OBRAS (ONDE VOCÊ COLA O CÓDIGO) ---
        codigo_da_ia = carregar_bloco_dinamico()
        if codigo_da_ia:
            try:
                # O site agora entende CATEGORIAS_OFICIAIS e outras variáveis aqui dentro!
                exec(codigo_da_ia)
            except Exception as e:
                st.error(f"Erro no código injetado: {e}")
        
        st.markdown('<div class="bloco">### 💎 Vitrine GeralJá</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()


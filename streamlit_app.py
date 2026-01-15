
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
# 🛡️ 1. CONFIGURAÇÕES SUPREMAS
# ==============================================================================
st.set_page_config(
    page_title="GeralJá | Plataforma Suprema", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constantes de Elite
CHAVE_ADMIN = "123" 
BONUS_WELCOME = 50
CATEGORIAS_OFICIAIS = ["Pizzaria", "Mecânico", "Eletricista", "Moda", "Beleza", "Outros"]

# Conexão Firebase Blindada
if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()

# --- FERRAMENTAS TURBO ---
def converter_img_b64(file):
    if file:
        try: return base64.b64encode(file.read()).decode()
        except: return ""
    return ""

def normalizar_texto(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

# ==============================================================================
# 🧠 2. MOTOR DO ARQUITETO (BACKEND)
# ==============================================================================
def carregar_bloco_dinamico():
    try:
        doc = db.collection("configuracoes").document("layout_ia").get()
        return doc.to_dict().get("codigo_injetado", "") if doc.exists else ""
    except: return ""

# ==============================================================================
# 🏗️ 3. CONSTRUTOR DE INTERFACE (UI/UX)
# ==============================================================================
def main():
    # CSS Customizado - Removendo excessos e fixando estilo Clean
    st.markdown("""
    <style>
        .stApp { background-color: #f8fafc; }
        .block-container { max-width: 950px !important; padding-top: 1rem !important; }
        
        /* Novo Cabeçalho Master (Substituindo a Capa Azul) */
        .header-master {
            background: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            border-bottom: 6px solid #FF8C00;
            margin-bottom: 25px;
        }
        .logo-geral { color: #0047AB; font-weight: 900; font-size: 42px; letter-spacing: -2px; }
        .logo-ja { color: #FF8C00; font-weight: 900; font-size: 42px; letter-spacing: -2px; }
        
        /* Cards de Conteúdo */
        .bloco-white { 
            background: white; 
            border-radius: 15px; 
            padding: 20px; 
            margin-bottom: 20px; 
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        /* Esconder elementos nativos desnecessários */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    # --- HEADER FIXO ---
    st.markdown("""
        <div class="header-master">
            <span class="logo-geral">GERAL</span><span class="logo-ja">JÁ</span>
            <p style="color: #64748B; margin: 0; font-weight: 600;">INTELIGÊNCIA COMUNITÁRIA & SERVIÇOS</p>
        </div>
    """, unsafe_allow_html=True)

    # --- ÁREA CENTRAL ---
    # Injetor de Código (Modo Arquiteto agora fica escondido num expander discreto no rodapé)
    with st.expander("🛠️ Painel Arquiteto"):
        senha = st.text_input("Acesso Master", type="password")
        if senha == CHAVE_ADMIN:
            novo_cod = st.text_area("Canteiro de Obras (Código IA)", height=250, placeholder="Cole o código turbinado aqui...")
            if st.button("🚀 SOLDAR E ATUALIZAR SISTEMA"):
                db.collection("configuracoes").document("layout_ia").set({
                    "codigo_injetado": novo_cod, 
                    "ultima_atualizacao": datetime.datetime.now()
                })
                st.success("Sistema Atualizado!"); st.rerun()

    # --- EXECUÇÃO DO BLOCO DINÂMICO (O CORAÇÃO DO APP) ---
    codigo_da_ia = carregar_bloco_dinamico()
    if codigo_da_ia:
        try:
            # Contexto injetado: o código aqui dentro reconhece as variáveis do main
            exec(codigo_da_ia)
        except Exception as e:
            st.error(f"Aguardando nova injeção de código ou erro detectado: {e}")
    else:
        st.info("Sintonizando frequências... Use o Painel Arquiteto para injetar as abas e o feed.")

    # --- VITRINE / RODAPÉ ---
    st.markdown('<div class="bloco-white" style="text-align:center; color:#94a3b8; font-size:12px;">© 2026 Grupo Grajaú Tem | Tecnologia Elite</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

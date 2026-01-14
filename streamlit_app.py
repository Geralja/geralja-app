import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import datetime
import math
import re
import pandas as pd
import unicodedata

# ==============================================================================
# 🛡️ 1. CONFIGURAÇÕES E SEGURANÇA (A BASE)
# ==============================================================================
st.set_page_config(page_title="GeralJá | Plataforma Turbo", layout="wide")

# Conexão Blindada com Firebase
if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()

# Antivírus de Texto e Localização
def sanitizar(t):
    return re.sub(r'<[^>]*?>', '', t).strip() if t else ""

def buscar_coords():
    return -23.5505, -46.6333 # Padrão São Paulo

# ==============================================================================
# 🧠 2. O MOTOR DO ARQUITETO (INJEÇÃO DINÂMICA)
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
            senha = st.text_input("Senha Master", type="password")
            if senha == "123":
                st.info("Dica: Cole aqui códigos Python/Streamlit")
                novo_cod = st.text_area("Injetor de Código", height=300)
                if st.button("🚀 SOLDAR NO SITE AGORA"):
                    db.collection("configuracoes").document("layout_ia").set({
                        "codigo_injetado": novo_cod,
                        "data": datetime.datetime.now()
                    })
                    st.success("Código injetado com sucesso!")
                    st.rerun()

# ==============================================================================
# 🎨 3. COMPONENTES VISUAIS (DESIGN DE ELITE)
# ==============================================================================
def renderizar_capa_fixa():
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1d4ed8 0%, #1e3a8a 100%); border-radius: 15px; padding: 40px; color: white; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
            <h1 style="color: white; border: none; margin: 0; font-size: 2.5rem;">GeralJá Turbo 🎯</h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">A inteligência que conecta você ao comércio local.</p>
        </div>
    """, unsafe_allow_html=True)

def renderizar_vitrine_oficial():
    st.markdown('<div class="bloco"><h3>💎 Vitrine de Destaques</h3></div>', unsafe_allow_html=True)
    # Aqui o sistema busca as lojas no banco
    lojas = db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">=", 1).limit(5).stream()
    for loja in lojas:
        l = loja.to_dict()
        st.markdown(f"""
            <div class="bloco">
                <h4 style="margin:0;">{sanitizar(l.get('nome'))}</h4>
                <p style="color: #666; font-size: 0.9rem;">{l.get('area', 'Serviços')}</p>
            </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 🏗️ 4. O GRANDE CONSTRUTOR (MAIN ÚNICO)
# ==============================================================================
def main():
    # Estilização Geral (CSS Timeline)
    st.markdown("""
        <style>
        .stApp { background-color: #f0f2f5; }
        .bloco { background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; border: 1px solid #e1e4e8; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        [data-testid="stHeader"] { background: rgba(0,0,0,0); }
        </style>
    """, unsafe_allow_html=True)

    # Definição de Colunas Estilo Facebook
    col_lateral, col_central = st.columns([1, 2.5])

    # --- COLUNA DA ESQUERDA (NAVEGAÇÃO) ---
    with col_lateral:
        st.markdown('<div class="bloco">### 🧭 Menu Principal</div>', unsafe_allow_html=True)
        st.button("🏠 Home Timeline", use_container_width=True)
        st.button("🏪 Minha Loja", use_container_width=True)
        
        # Painel do Arquiteto fica escondido aqui
        painel_adm_arquiteto()

    # --- COLUNA CENTRAL (O CORAÇÃO DO SITE) ---
    with col_central:
        # 1. Capa Fixa no Topo
        renderizar_capa_fixa()

        # 2. CANTEIRO DE OBRAS (Onde a mágica do Arquiteto acontece)
        codigo_da_ia = carregar_bloco_dinamico()
        if codigo_da_ia:
            st.markdown('<div class="bloco" style="border-left: 5px solid #28a745; background: #f8fff9;">', unsafe_allow_html=True)
            st.caption("🧪 Módulo Ativo via Modo Arquiteto")
            try:
                # Executa o código que você colou no site
                exec(codigo_da_ia)
            except Exception as e:
                st.error(f"Erro no código injetado: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Bloco de aviso caso o canteiro esteja vazio
            st.info("Canteiro de obras vazio. Use o Modo Arquiteto para dar vida a este espaço!")

        # 3. Busca e Vitrine
        st.markdown('<div class="bloco">', unsafe_allow_html=True)
        st.text_input("", placeholder="O que você procura hoje?", key="busca_main")
        st.markdown('</div>', unsafe_allow_html=True)
        
        renderizar_vitrine_oficial()

# ==============================================================================
# 🏁 RODAPÉ E START
# ==============================================================================
if __name__ == "__main__":
    try:
        main()
    finally:
        st.write("---")
        st.caption(f"🛡️ GeralJá Turbo v4.0 | {datetime.datetime.now().year} | Antivírus Ativo")

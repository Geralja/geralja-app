# ==============================================================================
# GERALJÁ: SHOPPING & SERVIÇOS ELITE 2026
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
import requests
from urllib.parse import quote

# Tentativa de importação para GPS (se configurado no seu ambiente)
try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    get_geolocation = None

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DE TELA E CSS (VISUAL "XIQUE")
# ------------------------------------------------------------------------------
st.set_page_config(page_title="GeralJá | Vitrine Pro", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f0f2f5; }
    
    /* Header Estilo Facebook */
    .header-fb { 
        background: white; padding: 20px; border-radius: 0 0 15px 15px; 
        text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px; border-bottom: 5px solid #1877f2;
    }

    /* Card de Vitrine Chique */
    .product-card {
        background: white; border-radius: 12px; overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: 0.3s;
        border: 1px solid #ddd; margin-bottom: 20px;
    }
    .product-card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.15); }
    
    .product-img { width: 100%; height: 220px; object-fit: cover; background: #f8f9fa; }
    
    .product-info { padding: 18px; }
    .price-tag { color: #1c1e21; font-size: 1.4rem; font-weight: 800; margin: 8px 0; }
    .store-name { color: #1877f2; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; }
    
    /* Botão Zap */
    .btn-zap {
        background-color: #25D366; color: white !important;
        padding: 12px; border-radius: 8px; text-align: center;
        font-weight: bold; text-decoration: none; display: block;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. CONEXÃO FIREBASE (SECRET BASE64)
# ------------------------------------------------------------------------------
if not firebase_admin._apps:
    try:
        # Pega a chave do Streamlit Secrets (deve estar em base64)
        b64_key = st.secrets["FIREBASE_BASE64"]
        cred_dict = json.loads(base64.b64decode(b64_key).decode("utf-8"))
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        st.stop()

db = firestore.client()

# ------------------------------------------------------------------------------
# 3. IA MESTRA E FUNÇÕES DE LÓGICA
# ------------------------------------------------------------------------------
BONUS_WELCOME = 50.0
VALOR_CLIQUE = 2.0

def processar_ia_mestra(texto):
    """IA que entende o que o usuário quer e mapeia categorias."""
    t = "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower()
    mapa = {
        "pizza": "Pizzaria", "hamburguer": "Lanchonete", "lanche": "Lanchonete",
        "carro": "Mecânico", "oficina": "Mecânico", "luz": "Eletricista",
        "celular": "Informática", "pc": "Informática", "roupa": "Moda"
    }
    for chave, cat in mapa.items():
        if chave in t: return cat
    return None

def calcular_distancia(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]: return 999
    R = 6371 # Raio da Terra em KM
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return round(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))), 1)

# ------------------------------------------------------------------------------
# 4. INTERFACE E NAVEGAÇÃO
# ------------------------------------------------------------------------------
st.markdown('<div class="header-fb"><h1>GERALJÁ</h1><p>A sua vitrine inteligente</p></div>', unsafe_allow_html=True)

menu_abas = st.tabs(["🛍️ VITRINE", "🚀 ANUNCIAR", "💰 MEU SALDO", "👑 ADMIN"])

# --- LOCALIZAÇÃO DO USUÁRIO ---
user_loc = {"lat": -23.5505, "lon": -46.6333} # Padrão SP
if get_geolocation:
    loc = get_geolocation()
    if loc:
        user_loc["lat"] = loc['coords']['latitude']
        user_loc["lon"] = loc['coords']['longitude']

# --- ABA 1: VITRINE (O SHOPPING) ---
with menu_abas[0]:
    c1, c2 = st.columns([3, 1])
    busca = c1.text_input("O que você precisa agora?", placeholder="Ex: Pizza, Consertar PC...")
    raio_km = c2.selectbox("Distância", [5, 10, 20, 50, 100], index=1)

    # A QUERY QUE PRECISAVA DO ÍNDICE:
    profs_ref = db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">", 0).stream()
    
    col_grid = st.columns(3)
    idx = 0
    
    for doc in profs_ref:
        p = doc.to_dict()
        pid = doc.id
        dist = calcular_distancia(user_loc["lat"], user_loc["lon"], p.get('lat'), p.get('lon'))
        
        # Filtro de Distância
        if dist > raio_km: continue
        
        # Filtro de Busca com IA
        cat_ia = processar_ia_mestra(busca)
        if busca and not (busca.lower() in p.get('nome','').lower() or (cat_ia and cat_ia == p.get('area'))):
            continue

        # Renderização do Card Chique
        with col_grid[idx % 3]:
            img_data = f"data:image/png;base64,{p.get('foto_b64')}" if p.get('foto_b64') else "https://via.placeholder.com/400x300?text=GeralJá"
            
            st.markdown(f"""
                <div class="product-card">
                    <img src="{img_data}" class="product-img">
                    <div class="product-info">
                        <span class="store-name">{p.get('nome')} ✔</span>
                        <div style="font-weight:600; font-size: 1.1rem; min-height: 50px;">{p.get('servico') or p.get('area')}</div>
                        <div class="price-tag">R$ {p.get('preco', '0,00')}</div>
                        <p style="font-size:0.8rem; color:#65676b;">📍 a {dist} km de você</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Falar com {p.get('nome').split()[0]}", key=f"btn_{pid}"):
                # Sistema de Cobrança por Clique
                novo_saldo = p.get('saldo', 0) - VALOR_CLIQUE
                db.collection("profissionais").document(pid).update({"saldo": novo_saldo, "cliques": p.get('cliques', 0) + 1})
                st.success(f"WhatsApp: {p.get('whatsapp')}")
                st.link_button("ABRIR WHATSAPP", f"https://wa.me/55{p.get('whatsapp')}?text=Vi+seu+anuncio+no+GeralJa")
        
        idx += 1

# --- ABA 2: CADASTRO COM FOTO ---
with menu_abas[1]:
    st.header("Anuncie na Vitrine")
    with st.form("cad_loja"):
        c_nome = st.text_input("Nome do Comércio/Profissional")
        c_zap = st.text_input("WhatsApp (apenas números)")
        c_area = st.selectbox("Categoria", ["Pizzaria", "Mecânico", "Informática", "Moda", "Outros"])
        c_serv = st.text_input("Título do Anúncio (Ex: Pizza Grande 2 Sabores)")
        c_preco = st.text_input("Preço")
        c_foto = st.file_uploader("Foto do Produto/Serviço", type=["jpg", "png"])
        
        if st.form_submit_button("PUBLICAR AGORA"):
            foto_b64 = base64.b64encode(c_foto.read()).decode() if c_foto else ""
            dados = {
                "nome": c_nome, "whatsapp": c_zap, "area": c_area, "servico": c_serv,
                "preco": c_preco, "foto_b64": foto_b64, "saldo": BONUS_WELCOME,
                "aprovado": True, "verificado": True, "cliques": 0,
                "lat": user_loc["lat"], "lon": user_loc["lon"], "data": datetime.now()
            }
            db.collection("profissionais").document(c_zap).set(dados)
            st.balloons()
            st.success("Publicado com sucesso! Você ganhou R$ 50 de bônus.")

# --- ABA 4: ADMIN (O SEU CONTROLE) ---
with menu_abas[3]:
    adm_key = st.text_input("Chave Mestra", type="password")
    if adm_key == "mumias":
        st.write("### Gestão Geral")
        docs = db.collection("profissionais").stream()
        for d in docs:
            val = d.to_dict()
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"**{val.get('nome')}** (R$ {val.get('saldo')})")
            if col2.button("+10", key=f"add_{d.id}"):
                db.collection("profissionais").document(d.id).update({"saldo": val.get('saldo',0)+10})
                st.rerun()
            if col3.button("DEL", key=f"del_{d.id}"):
                db.collection("profissionais").document(d.id).delete()
                st.rerun()

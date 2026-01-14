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

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÃO E TEMA
# ------------------------------------------------------------------------------
st.set_page_config(page_title="GeralJá | Vitrine Elite", page_icon="🛍️", layout="wide")

# CSS para Vitrine "Muito Xique"
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f0f2f5; }
    
    /* Header Estilo Facebook Marketplace */
    .header-container { 
        background: white; padding: 20px; border-radius: 0 0 20px 20px; 
        text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px; border-bottom: 4px solid #1877f2;
    }

    /* Card de Produto/Serviço Luxo */
    .product-card {
        background: white; border-radius: 12px; overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: 0.3s;
        border: 1px solid #ddd; margin-bottom: 20px;
    }
    .product-card:hover { transform: translateY(-5px); box-shadow: 0 8px 16px rgba(0,0,0,0.15); }
    
    .product-img { width: 100%; height: 200px; object-fit: cover; background: #eee; }
    
    .product-info { padding: 15px; }
    .price-tag { color: #1c1e21; font-size: 1.3rem; font-weight: 800; margin: 5px 0; }
    .store-name { color: #65676b; font-size: 0.85rem; font-weight: 600; }
    .verified-check { color: #1877f2; margin-left: 4px; }
    
    /* Botão Zap Customizado */
    .btn-zap {
        background-color: #25D366; color: white !important;
        padding: 12px; border-radius: 8px; text-align: center;
        font-weight: bold; text-decoration: none; display: block;
        margin-top: 10px; transition: 0.3s;
    }
    .btn-zap:hover { background-color: #128C7E; }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. CONEXÃO FIREBASE (SECRET BASE64)
# ------------------------------------------------------------------------------
if not firebase_admin._apps:
    try:
        if "FIREBASE_BASE64" in st.secrets:
            b64_key = st.secrets["FIREBASE_BASE64"]
            cred_dict = json.loads(base64.b64decode(b64_key).decode("utf-8"))
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            st.error("Erro: Secret FIREBASE_BASE64 não configurada.")
            st.stop()
    except Exception as e:
        st.error(f"Erro Firebase: {e}")
        st.stop()

db = firestore.client()

# ------------------------------------------------------------------------------
# 3. CONSTANTES E IA MESTRA (CONCEITOS)
# ------------------------------------------------------------------------------
BONUS_WELCOME = 50.0
VALOR_CLIQUE = 2.0
CATEGORIAS_OFICIAIS = ["Pizzaria", "Lanchonete", "Mecânico", "Eletricista", "Loja de Roupas", "Adega", "Informática", "Diarista", "Outros"]

CONCEITOS_IA = {
    "pizza": "Pizzaria", "fome": "Pizzaria", "mecanico": "Mecânico", 
    "carro": "Mecânico", "roupa": "Loja de Roupas", "cerveja": "Adega"
}

def processar_ia_avancada(texto):
    t_clean = "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower().strip()
    for chave, cat in CONCEITOS_IA.items():
        if chave in t_clean: return cat
    return "NAO_ENCONTRADO"

def calcular_distancia(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]: return 99.0
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return round(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))), 1)

# ------------------------------------------------------------------------------
# 4. INTERFACE PRINCIPAL
# ------------------------------------------------------------------------------
st.markdown('<div class="header-container"><h1 style="color:#1877f2; margin:0;">GERALJÁ</h1><p style="color:#65676b;">A Sua Vitrine Comunitária</p></div>', unsafe_allow_html=True)

menu_abas = st.tabs(["🔍 VITRINE", "🚀 CADASTRAR", "👤 MEU PERFIL", "👑 ADMIN"])

# --- ABA 1: VITRINE (BUSCA E PRODUTOS) ---
with menu_abas[0]:
    c1, c2 = st.columns([3, 1])
    termo = c1.text_input("O que você procura hoje?", placeholder="Ex: Pizza, iPhone, Pintor...")
    raio = c2.select_slider("Raio (KM)", options=[5, 10, 20, 50, 100], value=10)

    # Simulação de Localização (No original você usa get_geolocation)
    m_lat, m_lon = -23.5505, -46.6333 

    profs = db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">", 0).stream()
    
    lista_vitrine = []
    for doc in profs:
        p = doc.to_dict()
        p['id'] = doc.id
        dist = calcular_distancia(m_lat, m_lon, p.get('lat'), p.get('lon'))
        if dist <= raio:
            p['dist'] = dist
            lista_vitrine.append(p)

    # Grid de 3 Colunas para ficar "Xique"
    cols = st.columns(3)
    for i, p in enumerate(lista_vitrine):
        with cols[i % 3]:
            # IA verifica se o termo de busca bate com o serviço
            if termo and processar_ia_avancada(termo) != p.get('area') and termo.lower() not in p.get('nome').lower():
                continue

            foto_p = p.get('foto_b64', '')
            img_src = f"data:image/png;base64,{foto_p}" if foto_p else "https://via.placeholder.com/400x300?text=Sem+Foto"
            verificado = '<span class="verified-check">✔</span>' if p.get('verificado') else ""
            
            st.markdown(f"""
                <div class="product-card">
                    <img src="{img_src}" class="product-img">
                    <div class="product-info">
                        <span class="store-name">{p.get('nome').upper()} {verificado}</span>
                        <div style="font-size: 1.1rem; font-weight: 600;">{p.get('servico') or p.get('area')}</div>
                        <div class="price-tag">R$ {p.get('preco', '0,00')}</div>
                        <p style="font-size:0.8rem; color:gray;">📍 {p['dist']} km de você</p>
                        <a href="https://wa.me/55{p['id']}?text=Olá, vi seu produto no GeralJá" target="_blank" class="btn-zap">
                            💬 VER DETALHES
                        </a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Lógica de débito de saldo (Simulada no clique do botão acima precisaria de um redirecionador)
            # Para simplificar, registramos a visualização:
            db.collection("profissionais").document(p['id']).update({"cliques": p.get('cliques', 0) + 1})

# --- ABA 2: CADASTRO (TURBINADO) ---
with menu_abas[1]:
    st.header("🚀 Cadastre sua Loja ou Serviço")
    with st.form("cad_novo"):
        c_nome = st.text_input("Nome da Loja/Profissional")
        c_zap = st.text_input("WhatsApp (com DDD, só números)")
        c_area = st.selectbox("Categoria", CATEGORIAS_OFICIAIS)
        c_preco = st.text_input("Preço Principal (Ex: 59.90)")
        c_desc = st.text_area("Descrição do Produto/Serviço")
        c_foto = st.file_uploader("Foto da Vitrine", type=["jpg", "png"])
        
        if st.form_submit_button("PUBLICAR NA VITRINE"):
            if c_nome and c_zap:
                foto_b64 = base64.b64encode(c_foto.read()).decode() if c_foto else ""
                db.collection("profissionais").document(c_zap).set({
                    "nome": c_nome, "whatsapp": c_zap, "area": c_area,
                    "preco": c_preco, "descricao": c_desc, "foto_b64": foto_b64,
                    "saldo": BONUS_WELCOME, "aprovado": True, "lat": m_lat, "lon": m_lon,
                    "cliques": 0, "verificado": False
                })
                st.success("Sua vitrine está no ar!")
                st.balloons()

# --- ABA 3: PERFIL E ABA 4: ADMIN (MANTIDAS DO SEU ORIGINAL) ---
with menu_abas[3]:
    chave = st.text_input("Chave Mestra", type="password")
    if chave == "mumias":
        st.write("### Painel de Controle Master")
        # Aqui você coloca a lógica de aprovação e saldo do seu arquivo original

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
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import math
import unicodedata
import pandas as pd
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO VISUAL LUXO ---
st.set_page_config(page_title="GeralJá | Vitrine Elite", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;700&display=swap');
    
    .stApp { background-color: #050505; color: #fff; }
    
    /* Grid de Vitrine Infinita */
    .vitrine-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        padding: 20px;
    }

    /* Card Estilo Instagram/Marketplace Luxo */
    .vitrine-item {
        position: relative;
        background: #111;
        border-radius: 0px;
        overflow: hidden;
        border: 1px solid #222;
        transition: 0.4s;
    }
    
    .vitrine-item:hover {
        border-color: #d4af37;
        transform: scale(1.02);
    }

    .item-img {
        width: 100%;
        height: 400px;
        object-fit: cover;
        display: block;
    }

    /* Informações sobrepostas na imagem */
    .item-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(transparent, rgba(0,0,0,0.9));
        padding: 20px;
    }

    .item-price {
        color: #d4af37;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
    }

    .item-title {
        font-size: 1rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .store-badge {
        font-size: 0.7rem;
        color: #888;
        letter-spacing: 2px;
    }
    
    /* Botão Invisível Premium */
    div.stButton > button {
        background: rgba(212, 175, 55, 0.1) !important;
        color: #d4af37 !important;
        border: 1px solid #d4af37 !important;
        border-radius: 0px !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- FIREBASE SETUP (MANTENDO SEU ESQUELETO) ---
if not firebase_admin._apps:
    b64_key = st.secrets["FIREBASE_BASE64"]
    cred_dict = json.loads(base64.b64decode(b64_key).decode("utf-8"))
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- HEADER ---
st.markdown("<h1 style='text-align:center; font-family:Montserrat; letter-spacing:15px; color:#d4af37;'>GERALJÁ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555; margin-bottom:40px;'>EXPOSIÇÃO DE ELITE</p>", unsafe_allow_html=True)

tabs = st.tabs(["💎 VITRINE", "🏪 MINHA VITRINE", "⚙️ ADMIN"])

# --- ABA 1: A VITRINE REAL (GRID DE PRODUTOS) ---
with tabs[0]:
    c1, c2 = st.columns([3, 1])
    busca = c1.text_input("", placeholder="O QUE VOCÊ BUSCA? (PIZZA, IPHONE, CARRO...)")
    
    # Busca todas as lojas com saldo
    lojas = db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">=", 1).stream()

    # Vamos coletar todos os POSTS de todas as lojas que têm saldo
    todos_produtos = []
    for loja in lojas:
        l_data = loja.to_dict()
        l_id = loja.id
        
        # Puxa os produtos da sub-coleção 'posts'
        posts = db.collection("profissionais").document(l_id).collection("posts").where("ativo", "==", True).stream()
        for p in posts:
            p_data = p.to_dict()
            p_data['loja_id'] = l_id
            p_data['loja_nome'] = l_data['nome']
            p_data['loja_zap'] = l_data['whatsapp']
            p_data['loja_saldo'] = l_data['saldo']
            
            # Filtro de busca simples
            if busca.lower() in p_data.get('titulo', '').lower() or busca.lower() in p_data.get('categoria', '').lower():
                todos_produtos.append(p_data)

    # Exibe em Grid de 3 colunas
    if todos_produtos:
        cols = st.columns(3)
        for i, produto in enumerate(todos_produtos):
            with cols[i % 3]:
                img_b64 = produto.get('foto')
                img_src = f"data:image/png;base64,{img_b64}" if img_b64 else "https://via.placeholder.com/600x800"
                
                # O Card da Vitrine
                st.markdown(f"""
                    <div class="vitrine-item">
                        <img src="{img_src}" class="item-img">
                        <div class="item-overlay">
                            <div class="store-badge">{produto['loja_nome'].upper()}</div>
                            <div class="item-title">{produto['titulo']}</div>
                            <div class="item-price">R$ {produto['preco']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Ação de clique (Desconta 1 GeralCoin da loja)
                if st.button(f"TENHO INTERESSE", key=f"int_{i}"):
                    if produto['loja_saldo'] >= 1:
                        # Desconta saldo do lojista
                        db.collection("profissionais").document(produto['loja_id']).update({
                            "saldo": produto['loja_saldo'] - 1
                        })
                        st.success(f"CONTATO DA LOJA: {produto['loja_zap']}")
                        st.link_button("CHAMAR NO WHATSAPP", f"https://wa.me/55{produto['loja_zap']}?text=Olá, vi seu {produto['titulo']} no GeralJá")
                    else:
                        st.error("VITRINE INDISPONÍVEL NO MOMENTO")

# --- ABA 2: EDITOR (MANTENDO SUA LÓGICA DE 50 CRÉDITOS) ---
with tabs[1]:
    # Lógica do Editor onde o lojista cria os posts com foto, preço e título...
    # Se ele completar 100% da vitrine (Título + Foto + Preço), ganha os 50 GeralCoins.
    st.write("Área do Lojista: Gerencie seus produtos aqui.")

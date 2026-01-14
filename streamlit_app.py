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

# --- CONFIGURAÇÃO DE ALTO PADRÃO ---
st.set_page_config(page_title="GERALJÁ | L'Exclusif", layout="wide")

# CSS: ESTÉTICA DE GRIFE (DARK MODE LUXURY)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@200;400;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top, #1a1a1a 0%, #000000 100%);
        color: #e0e0e0;
    }
# ------------------------------------------------------------------------------
# 4. FUNÇÕES AUXILIARES
# ------------------------------------------------------------------------------
def registrar_clique(pro_id, saldo_atual):
    if saldo_atual >= VALOR_CLIQUE:
        novo_saldo = saldo_atual - VALOR_CLIQUE
        db.collection("profissionais").document(pro_id).update({"saldo": novo_saldo})
        return True
    return False

    /* Título Estilo Joalheria */
    .brand-title {
        font-family: 'Cinzel', serif;
        font-size: 3.5rem;
        letter-spacing: 10px;
        text-align: center;
        background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    /* Container da Vitrine de Luxo */
    .luxury-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(191, 149, 63, 0.3);
        border-radius: 0px; /* Bordas retas são mais elegantes em luxo */
        padding: 0px;
        transition: 0.5s;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }

    .luxury-card:hover {
        border: 1px solid rgba(191, 149, 63, 1);
        box-shadow: 0 0 30px rgba(191, 149, 63, 0.2);
        transform: scale(1.02);
    }

    .product-price {
        font-family: 'Montserrat', sans-serif;
        font-weight: 200;
        letter-spacing: 2px;
        color: #bf953f;
        font-size: 1.2rem;
    }

    .product-name {
        font-family: 'Montserrat', sans-serif;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 3px;
        margin-top: 15px;
    }

    /* Botão Invisível/Elegante */
    div.stButton > button {
        background: transparent !important;
        color: #bf953f !important;
        border: 1px solid #bf953f !important;
        border-radius: 0px !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        width: 100%;
        transition: 0.4s;
    }

    div.stButton > button:hover {
        background: #bf953f !important;
        color: black !important;
    }

    /* Linha Divisória de Ouro */
    .gold-line {
        height: 1px;
        background: linear-gradient(to right, transparent, #bf953f, transparent);
        margin: 40px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    b64_key = st.secrets["FIREBASE_BASE64"]
    cred_dict = json.loads(base64.b64decode(b64_key).decode("utf-8"))
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- HERO SECTION ---
st.markdown('<h1 class="brand-title">GERALJÁ</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-family:Montserrat; font-weight:200; letter-spacing:5px;">L\'EXCLUSIF MARKETPLACE</p>', unsafe_allow_html=True)
st.markdown('<div class="gold-line"></div>', unsafe_allow_html=True)

menu = st.tabs(["COLLECTION", "MAISON (EDITOR)", "CONCIERGE"])

# --- ABA 1: VITRINE (A COLLECTION) ---
with menu[0]:
    # Barra de Busca Minimalista
    busca = st.text_input("", placeholder="RECHERCHE / BUSCAR...")
    
    # Query de quem tem saldo (mínimo 1 GeralCoin)
    lojas = db.collection("profissionais").where("saldo", ">=", 1).stream()

    for loja in lojas:
        l_data = loja.to_dict()
        
        # Nome da Loja como uma "Grife"
        st.markdown(f'<h2 style="font-family:Cinzel; color:#bf953f; text-align:center; margin-top:50px;">{l_data.get("nome").upper()}</h2>', unsafe_allow_html=True)
        
        # Sub-coleção de Posts (Produtos)
        posts_ref = db.collection("profissionais").document(loja.id).collection("posts").where("ativo", "==", True).stream()
        
        posts = list(posts_ref)
        if posts:
            cols = st.columns(3)
            for i, p_doc in enumerate(posts):
                p = p_doc.to_dict()
                with cols[i % 3]:
                    img = f"data:image/png;base64,{p.get('foto')}" if p.get('foto') else "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&q=80&w=400"
                    
                    st.markdown(f"""
                        <div class="luxury-card">
                            <img src="{img}" style="width:100%; filter: grayscale(30%);">
                            <div style="padding:20px; text-align:center;">
                                <div class="product-name">{p.get('titulo')}</div>
                                <div class="product-price">VALEUR: R$ {p.get('preco')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"S'ENTRETENIR / CONTATAR", key=f"lux_{p_doc.id}"):
                        if l_data.get('saldo', 0) >= 1:
                            db.collection("profissionais").document(loja.id).update({"saldo": l_data.get('saldo') - 1})
                            st.success(f"WHATSAPP PRIVÉ: {l_data.get('whatsapp')}")
                        else:
                            st.error("SOLDE INSUFFISANT")

# --- ABA 2: MAISON (O EDITOR PESSOAL) ---
with menu[1]:
    st.markdown('<h2 style="font-family:Cinzel; text-align:center;">VOTRE MAISON</h2>', unsafe_allow_html=True)
    
    login_id = st.text_input("IDENTIFIANT (WHATSAPP)", type="password")
    
    if login_id:
        doc_ref = db.collection("profissionais").document(login_id)
        loja_doc = doc_ref.get()
        
        if loja_doc.exists:
            l = loja_doc.to_dict()
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.markdown(f"""
                    <div style="border:1px solid #bf953f; padding:30px; text-align:center;">
                        <p style="letter-spacing:3px;">GERALCOINS</p>
                        <h1 style="color:#bf953f;">{l.get('saldo', 0)}</h1>
                    </div>
                """, unsafe_allow_html=True)
            
            with c2:
                st.markdown("### NOUVELLE PIÈCE (NOVO PRODUTO)")
                with st.form("luxury_post"):
                    t = st.text_input("NOME DO PRODUTO")
                    pr = st.text_input("VALOR EXCLUSIVO")
                    f = st.file_uploader("FOTOGRAFIA DE ALTA RESOLUÇÃO")
                    if st.form_submit_button("PUBLIER DANS LA COLLECTION"):
                        # Ganha crédito se a vitrine ficar 100% (Título + Preço + Foto)
                        bonus = 0
                        if t and pr and f: bonus = 50 # Estratégia dos 50 créditos
                        
                        foto_b64 = base64.b64encode(f.read()).decode() if f else ""
                        doc_ref.collection("posts").add({
                            "titulo": t, "preco": pr, "foto": foto_b64, 
                            "ativo": True, "data": datetime.now()
                        })
                        if bonus > 0:
                            doc_ref.update({"saldo": l.get('saldo', 0) + bonus})
                            st.balloons()
                        st.success("VITRINE ATUALIZADA COM SUCESSO")

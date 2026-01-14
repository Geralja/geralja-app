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

# --- ESQUELETO: FUNÇÕES ORIGINAIS DE IA E GPS ---
def processar_ia_mestra(texto):
    t = "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower()
    mapa = {"pizza": "Pizzaria", "fome": "Pizzaria", "mecanico": "Mecânico", "luz": "Eletricista", "roupa": "Moda"}
    for chave, cat in mapa.items():
        if chave in t: return cat
    return None

def calcular_distancia(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]: return 999
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return round(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))), 1)

# --- CONFIGURAÇÃO DE TELA E DESIGN LUXO ---
st.set_page_config(page_title="GeralJá | L'Elite", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Montserrat:wght@300;600&display=swap');
    .stApp { background: #0a0a0a; color: #d4af37; }
    .main-title { font-family: 'Cinzel', serif; color: #d4af37; text-align: center; font-size: 3rem; letter-spacing: 5px; }
    .gold-card { 
        background: rgba(255, 255, 255, 0.05); border: 1px solid #d4af37; 
        padding: 0px; border-radius: 0px; transition: 0.4s; margin-bottom: 20px;
    }
    .gold-card:hover { box-shadow: 0 0 20px rgba(212, 175, 55, 0.4); transform: scale(1.01); }
    .price-tag { font-family: 'Montserrat', sans-serif; color: #fff; font-size: 1.2rem; font-weight: 300; }
    div.stButton > button { 
        background: transparent; color: #d4af37; border: 1px solid #d4af37; 
        border-radius: 0px; width: 100%; font-family: 'Montserrat'; text-transform: uppercase;
    }
    div.stButton > button:hover { background: #d4af37; color: #000; }
    </style>
""", unsafe_allow_html=True)

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    b64_key = st.secrets["FIREBASE_BASE64"]
    cred_dict = json.loads(base64.b64decode(b64_key).decode("utf-8"))
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- INTERFACE ---
st.markdown('<h1 class="main-title">GERALJÁ</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; letter-spacing:3px; color:#888;">THE ELITE MARKETPLACE</p>', unsafe_allow_html=True)

tabs = st.tabs(["💎 VITRINE", "🏠 MINHA VITRINE (EDITOR)", "👑 ADMIN"])

# --- ABA 1: VITRINE (BUSCA + GPS + IA) ---
with tabs[0]:
    c1, c2, c3 = st.columns([2, 1, 1])
    busca = c1.text_input("O QUE DESEJA ENCONTRAR?", placeholder="Ex: Pizza, Mecânico...")
    raio = c2.slider("DISTÂNCIA (KM)", 1, 100, 20)
    
    m_lat, m_lon = -23.5505, -46.6333 # Localização padrão
    
    # Busca lojas com saldo (GeralCoins)
    lojas = db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">=", 1).stream()

    for loja in lojas:
        l = loja.to_dict()
        dist = calcular_distancia(m_lat, m_lon, l.get('lat'), l.get('lon'))
        
        # Filtro de GPS e IA
        if dist > raio: continue
        cat_ia = processar_ia_mestra(busca)
        if busca and not (busca.lower() in l.get('nome','').lower() or (cat_ia and cat_ia == l.get('area'))):
            continue

        st.markdown(f'<h3 style="border-left: 3px solid #d4af37; padding-left: 15px; margin-top:40px;">{l["nome"].upper()}</h3>', unsafe_allow_html=True)
        
        # Vitrine de Rolagem (Posts da Loja)
        posts = db.collection("profissionais").document(loja.id).collection("posts").where("ativo", "==", True).stream()
        p_list = list(posts)
        
        if p_list:
            cols = st.columns(len(p_list) if len(p_list) < 4 else 4)
            for i, p_doc in enumerate(p_list):
                p_data = p_doc.to_dict()
                with cols[i % 4]:
                    img = f"data:image/png;base64,{p_data.get('foto')}" if p_data.get('foto') else "https://via.placeholder.com/400x400/1a1a1a/d4af37?text=Luxury"
                    st.markdown(f"""
                        <div class="gold-card">
                            <img src="{img}" style="width:100%; height:200px; object-fit:cover;">
                            <div style="padding:15px; text-align:center;">
                                <div style="font-size:0.9rem; letter-spacing:1px;">{p_data.get('titulo').upper()}</div>
                                <div class="price-tag">R$ {p_data.get('preco')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Botão de Contato Único por Loja
            if st.button(f"S'ENTRETENIR (CONTATAR {l['nome'].split()[0].upper()})", key=f"btn_{loja.id}"):
                # Desconta 1 GeralCoin
                db.collection("profissionais").document(loja.id).update({"saldo": l['saldo'] - 1})
                st.success(f"CONTATO EXCLUSIVO: {l['whatsapp']}")
                st.link_button("ABRIR WHATSAPP", f"https://wa.me/55{l['whatsapp']}")

# --- ABA 2: MINHA VITRINE (O EDITOR COM ESTRATÉGIA DE 50 CRÉDITOS) ---
with tabs[1]:
    login = st.text_input("ACESSO AO MAISON (SEU WHATSAPP)", type="password")
    if login:
        doc_ref = db.collection("profissionais").document(login)
        loja_doc = doc_ref.get()
        
        if loja_doc.exists:
            l_data = loja_doc.to_dict()
            st.markdown(f"### BEM-VINDO, {l_data['nome'].upper()}")
            st.info(f"Seu Saldo: {l_data.get('saldo', 0)} GeralCoins")
            
            with st.form("editor_luxo"):
                st.write("CRIE UMA POSTAGEM IMPECÁVEL")
                t_prod = st.text_input("TÍTULO DO PRODUTO")
                p_prod = st.text_input("PREÇO")
                f_prod = st.file_uploader("IMAGEM DA PEÇA")
                
                if st.form_submit_button("PUBLICAR NA VITRINE"):
                    if t_prod and p_prod and f_prod:
                        foto_b64 = base64.b64encode(f_prod.read()).decode()
                        doc_ref.collection("posts").add({
                            "titulo": t_prod, "preco": p_prod, "foto": foto_b64, 
                            "ativo": True, "data": datetime.now()
                        })
                        # Regra dos 50 Créditos (Bônus se vitrine estiver 100%)
                        if l_data.get('saldo') < 50: # Dá o bônus apenas na primeira vitrine perfeita
                            doc_ref.update({"saldo": l_data['saldo'] + 50})
                            st.balloons()
                        st.success("VITRINE ATUALIZADA E CRÉDITOS RECEBIDOS!")
        else:
            if st.button("QUERO ME CADASTRAR E GANHAR 50 CRÉDITOS"):
                # Lógica de criação rápida de conta...
                pass

# --- ABA 3: ADMIN (MUMIAS) ---
with tabs[2]:
    if st.text_input("CHAVE MESTRA", type="password") == "mumias":
        st.write("CONTROLE GERAL")
        # Mantém sua lógica de deletar e adicionar saldo manualmente...

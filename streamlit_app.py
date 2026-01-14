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

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="GeralJá | Vitrine Hub", layout="wide")

# CSS PREMIUM: Cores Profissionais e Efeito de Rolagem
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .vitrine-scroll {
        display: flex;
        overflow-x: auto;
        gap: 15px;
        padding: 10px 0;
        scrollbar-width: thin;
    }
    .post-card {
        min-width: 250px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    .coin-badge {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: #000;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
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

# --- HEADER ---
st.markdown("<div style='text-align:center'><h1>⚡ GERALJÁ</h1><p>Vitrine Social & Marketplace</p></div>", unsafe_allow_html=True)

menu = st.tabs(["🔍 BUSCAR", "🏪 MINHA VITRINE", "👑 ADMIN"])

# ------------------------------------------------------------------------------
# ABA 1: BUSCA (VITRINE DE ROLAGEM)
# ------------------------------------------------------------------------------
with menu[0]:
    busca = st.text_input("Encontre uma loja ou produto...", placeholder="Ex: Adega do Jhow")
    
    if busca:
        # Se buscar por uma loja específica, mostra o feed dela
        lojas = db.collection("profissionais").where("nome", "==", busca).stream()
    else:
        # Feed geral (quem tem saldo)
        lojas = db.collection("profissionais").where("saldo", ">=", 1).stream()

    for loja in lojas:
        l_data = loja.to_dict()
        st.markdown(f"### {l_data.get('nome')} ✔️")
        
        # VITRINE DE ROLAGEM (Simulação com colunas ou HTML)
        posts_ref = db.collection("profissionais").document(loja.id).collection("posts").where("ativo", "==", True).stream()
        
        posts = list(posts_ref)
        if posts:
            cols = st.columns(len(posts) if len(posts) < 4 else 4)
            for i, p_doc in enumerate(posts):
                p = p_doc.to_dict()
                with cols[i % 4]:
                    img = f"data:image/png;base64,{p.get('foto')}" if p.get('foto') else "https://via.placeholder.com/300"
                    st.markdown(f"""
                        <div class="post-card">
                            <img src="{img}" style="width:100%; border-radius:15px 15px 0 0;">
                            <div style="padding:10px;">
                                <small>{p.get('categoria')}</small>
                                <div style="font-weight:bold;">{p.get('titulo')}</div>
                                <div style="color:#1877f2; font-size:1.2rem;">R$ {p.get('preco')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Botão de Ação Único por Loja
            if st.button(f"📞 Contatar {l_data.get('nome')}", key=f"contact_{loja.id}"):
                if l_data.get('saldo', 0) >= 1:
                    db.collection("profissionais").document(loja.id).update({"saldo": l_data.get('saldo') - 1})
                    st.success(f"WhatsApp: {l_data.get('whatsapp')}")
                else:
                    st.error("Loja temporariamente sem GeralCoins para atendimento.")

# ------------------------------------------------------------------------------
# ABA 2: MINHA VITRINE (O EDITOR DO LOJISTA)
# ------------------------------------------------------------------------------
with menu[1]:
    st.subheader("🏪 Painel do Lojista")
    id_loja = st.text_input("Seu WhatsApp (Login)", type="password")
    
    if id_loja:
        doc_ref = db.collection("profissionais").document(id_loja)
        loja_doc = doc_ref.get()
        
        if loja_doc.exists:
            l = loja_doc.to_dict()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"""
                    <div style="background:white; padding:20px; border-radius:15px; border-left: 5px solid #FFD700">
                        <p>Meu Saldo</p>
                        <h2>{l.get('saldo', 0)} <span style="font-size:1rem">GeralCoins</span></h2>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("🚀 Turbinar Vitrine"):
                    st.info(f"PIX para recarga: {st.secrets.get('PIX', '11991853488')}")

            with col2:
                st.markdown("### 📸 Novo Post (Produto/Serviço)")
                with st.expander("Criar Postagem Chique"):
                    with st.form("novo_post"):
                        t_post = st.text_input("Título do Produto")
                        p_post = st.text_input("Preço")
                        cat_post = st.selectbox("Categoria", ["Promoção", "Lançamento", "Mais Vendido"])
                        f_post = st.file_uploader("Foto do Produto")
                        
                        if st.form_submit_button("Publicar na Vitrine"):
                            foto_b64 = base64.b64encode(f_post.read()).decode() if f_post else ""
                            # Adiciona o post na sub-coleção da loja
                            doc_ref.collection("posts").add({
                                "titulo": t_post,
                                "preco": p_post,
                                "categoria": cat_post,
                                "foto": foto_b64,
                                "ativo": True,
                                "data": datetime.now()
                            })
                            st.success("Postagem ativada!")
        else:
            # Fluxo de Primeiro Cadastro
            st.warning("Loja não encontrada. Cadastre-se agora!")
            with st.form("primeiro_cad"):
                n_loja = st.text_input("Nome da Loja")
                z_loja = st.text_input("WhatsApp (Será seu Login)")
                if st.form_submit_button("Criar Minha Vitrine Grátis"):
                    # Ganha 50 GeralCoins ao cadastrar
                    doc_ref = db.collection("profissionais").document(z_loja)
                    doc_ref.set({
                        "nome": n_loja,
                        "whatsapp": z_loja,
                        "saldo": 50, # Bônus inicial!
                        "aprovado": True
                    })
                    st.balloons()
                    st.rerun()

# ------------------------------------------------------------------------------
# ABA 3: ADMIN (MUMIAS)
# ------------------------------------------------------------------------------
with menu[2]:
    if st.text_input("Mestra", type="password") == "mumias":
        st.write("Gerenciamento de GeralCoins")
        # Lista todas as lojas para o admin dar créditos ou deletar

# --- GERALJÁ | TESTADOR DE ELITE (BUSCA CORRIGIDA) ---
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import math
import re
import time
import pandas as pd
import unicodedata
from datetime import datetime
import pytz

# 1. AMBIENTE
st.set_page_config(page_title="GeralJá | Laboratório 2.0", layout="wide", page_icon="🧪")

# 2. CONEXÃO FIREBASE
if not firebase_admin._apps:
    try:
        fb_base64 = st.secrets["firebase"]["base64"] 
        fb_dict = json.loads(base64.b64decode(fb_base64).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except Exception as e:
        st.error(f"Erro na conexão Firebase: {e}")

db = firestore.client()
fuso_horario = pytz.timezone('America/Sao_Paulo')

# 3. CARREGAMENTO INICIAL
if 'codigo_mestre' not in st.session_state:
    try:
        doc = db.collection("configuracoes").document("layout_ia").get()
        st.session_state.codigo_mestre = doc.to_dict().get("codigo_injetado", "") if doc.exists else ""
    except:
        st.session_state.codigo_mestre = "# Erro ao carregar."

# --- INTERFACE ---
st.title("🧪 Laboratório GeralJá")
st.caption("Gênia da Web - Busca em tempo real ativada")

# 4. COLUNAS LADO A LADO
col_editor, col_preview = st.columns([1, 1])

with col_editor:
    st.subheader("📝 Editor de Código")
    
    # BUSCA (Agora vinculada ao session_state)
    with st.expander("🔍 PESQUISAR LINHA NO EDITOR", expanded=True):
        busca_termo = st.text_input("Digite o código que deseja encontrar:")
        if busca_termo:
            # Ele pesquisa no conteúdo que está no editor agora
            linhas_atuais = st.session_state.codigo_mestre.split('\n')
            encontrou = False
            for i, texto_linha in enumerate(linhas_atuais):
                if busca_termo.lower() in texto_linha.lower():
                    st.warning(f"📍 Linha {i+1}: `{texto_linha.strip()}`")
                    encontrou = True
            if not encontrou:
                st.error("Termo não localizado no código abaixo.")

    # EDITOR (O segredo está no on_change para atualizar a busca)
    def atualizar_codigo():
        st.session_state.codigo_mestre = st.session_state.new_code

    code_test = st.text_area(
        "Rascunho de Teste", 
        value=st.session_state.codigo_mestre, 
        height=500, 
        key="new_code", 
        on_change=atualizar_codigo
    )
    
    col_btn1, col_btn2 = st.columns(2)
    btn_testar = col_btn1.button("🔍 EXECUTAR TESTE LOCAL", use_container_width=True)
    btn_publicar = col_btn2.button("🚀 PUBLICAR NO SITE", type="primary", use_container_width=True)

with col_preview:
    st.subheader("📱 Preview")
    st.markdown("---")
    
    contexto = {
        "st": st, "db": db, "firestore": firestore, "datetime": datetime, 
        "time": time, "math": math, "pd": pd, "base64": base64,
        "CATEGORIAS_OFICIAIS": ["Pedreiro", "Locutor", "Eletricista", "Mecânico"]
    }

    if btn_testar:
        try:
            exec(st.session_state.codigo_mestre, contexto)
        except Exception as e:
            st.error(f"❌ ERRO: {e}")

# 5. PUBLICAÇÃO
if btn_publicar:
    try:
        db.collection("configuracoes").document("layout_ia").set({
            "codigo_injetado": st.session_state.codigo_mestre,
            "data_atualizacao": datetime.now(fuso_horario),
            "status": "producao"
        })
        st.balloons()
        st.success("✅ PUBLICADO!")
    except Exception as e:
        st.error(f"Erro: {e}")

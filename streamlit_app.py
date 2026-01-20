# --- GERALJÁ | TESTADOR DE ELITE (VERSÃO BLINDADA) ---
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
if 'first_run' not in st.session_state:
    st.set_page_config(page_title="GeralJá | Laboratório 2.0", layout="wide", page_icon="🧪")
    st.session_state.first_run = True

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

# 3. CARREGAMENTO INICIAL DO CÓDIGO
if 'codigo_mestre' not in st.session_state:
    try:
        doc = db.collection("configuracoes").document("layout_ia").get()
        st.session_state.codigo_mestre = doc.to_dict().get("codigo_injetado", "") if doc.exists else ""
    except:
        st.session_state.codigo_mestre = "# Erro ao carregar."

# --- INTERFACE ---
st.title("🧪 Laboratório GeralJá")
st.caption("Gênia da Web - Resolvido conflito de IDs")

# 4. COLUNAS
col_editor, col_preview = st.columns([1, 1])

with col_editor:
    st.subheader("📝 Editor de Código")
    
    # BUSCA COM KEY ÚNICA (Resolve o erro do multiple text_input)
    with st.expander("🔍 PESQUISAR LINHA NO EDITOR", expanded=False):
        busca_termo = st.text_input("Localizar termo:", key="lab_search_input") # KEY ADICIONADA
        if busca_termo:
            linhas_atuais = st.session_state.codigo_mestre.split('\n')
            for i, texto_linha in enumerate(linhas_atuais):
                if busca_termo.lower() in texto_linha.lower():
                    st.info(f"📍 Linha {i+1}: `{texto_linha.strip()[:50]}...`")

    # Função para salvar mudança no editor
    def atualizar_codigo():
        st.session_state.codigo_mestre = st.session_state.editor_key

    # EDITOR COM KEY ÚNICA
    code_test = st.text_area(
        "Rascunho de Teste", 
        value=st.session_state.codigo_mestre, 
        height=500, 
        key="editor_key", 
        on_change=atualizar_codigo
    )
    
    col_btn1, col_btn2 = st.columns(2)
    btn_testar = col_btn1.button("🔍 EXECUTAR TESTE LOCAL", use_container_width=True, key="lab_btn_test")
    btn_publicar = col_btn2.button("🚀 PUBLICAR NO SITE", type="primary", use_container_width=True, key="lab_btn_pub")

with col_preview:
    st.subheader("📱 Preview")
    st.markdown("---")
    
    # Contexto para o EXEC
    contexto = {
        "st": st, "db": db, "firestore": firestore, "datetime": datetime, 
        "time": time, "math": math, "pd": pd, "base64": base64,
        "CATEGORIAS_OFICIAIS": ["Pedreiro", "Locutor", "Eletricista", "Mecânico"]
    }

    # Só executa se o código não estiver vazio
    if st.session_state.codigo_mestre:
        try:
            # Roda o código. Se o seu código tiver text_input sem key, 
            # o erro agora será APENAS dentro do preview, sem travar o editor.
            exec(st.session_state.codigo_mestre, contexto)
        except Exception as e:
            st.error(f"❌ ERRO NO PREVIEW: {e}")

# 5. PUBLICAÇÃO
if btn_publicar:
    try:
        db.collection("configuracoes").document("layout_ia").set({
            "codigo_injetado": st.session_state.codigo_mestre,
            "data_atualizacao": datetime.now(fuso_horario),
            "status": "producao"
        })
        st.balloons()
        st.success("✅ PUBLICADO COM SUCESSO!")
    except Exception as e:
        st.error(f"Erro ao publicar: {e}")

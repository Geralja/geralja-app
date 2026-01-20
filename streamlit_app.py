# --- GERALJÁ | TESTADOR DE ELITE (VERSÃO SINCRONIZADA) ---
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

# 1. AMBIENTE IGUAL AO SITE OFICIAL
st.set_page_config(page_title="GeralJá | Laboratório de Testes", layout="wide", page_icon="🧪")

# 2. CONEXÃO SEGURA
if not firebase_admin._apps:
    try:
        fb_base64 = st.secrets["firebase"]["base64"] 
        fb_dict = json.loads(base64.b64decode(fb_base64).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except Exception as e:
        st.error(f"Erro na conexão Firebase: {e}")

db = firestore.client()
fuso_horario = pytz.timezone('America/Sao_Paulo')

# 3. FUNÇÕES CORE
def normalizar_texto(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

def doutorado_em_portugues(texto):
    if not texto: return ""
    return texto.strip().title()

# 4. BUSCA DE CÓDIGO (Para não perder o fio da meada)
try:
    doc_atual = db.collection("configuracoes").document("layout_ia").get()
    codigo_atual = doc_atual.to_dict().get("codigo_injetado", "") if doc_atual.exists else ""
except:
    codigo_atual = "# Escreva seu código..."

# --- NOVO: BUSCADOR DE CÓDIGO (GPS DO DESENVOLVEDOR) ---
st.title("🧪 Laboratório GeralJá")
st.caption("Gênia da Web - Sincronizado com o Site Oficial")

with st.expander("🔍 LOCALIZAR CÓDIGO / EVITAR ERROS", expanded=False):
    busca = st.text_input("O que você quer achar no código? (Ex: 'st.rerun', 'btn_salvar')")
    if busca:
        linhas_cod = codigo_atual.split('\n')
        for i, linha in enumerate(linhas_cod):
            if busca.lower() in linha.lower():
                st.code(f"Linha {i+1}: {linha.strip()}")

st.markdown("---")

# 5. INTERFACE IDENTICA AO ORIGINAL
col_editor, col_preview = st.columns([1, 1])

with col_editor:
    st.subheader("📝 Editor de Código")
    
    # Área de edição exatamente como você gosta
    code_test = st.text_area("Rascunho de Teste", value=codigo_atual, height=500)
    
    # Validação silenciosa na barra lateral para não poluir o visual
    try:
        compile(code_test, '<string>', 'exec')
    except Exception as e:
        st.sidebar.error(f"⚠️ Erro detectado: {e}")

    col_btn1, col_btn2 = st.columns(2)
    btn_testar = col_btn1.button("🔍 EXECUTAR TESTE LOCAL", use_container_width=True)
    btn_publicar = col_btn2.button("🚀 PUBLICAR NO SITE", type="primary", use_container_width=True)

with col_preview:
    st.subheader("📱 Preview")
    st.markdown("---")
    
    # Contexto idêntico ao que o site espera
    contexto_compartilhado = {
        "st": st, 
        "db": db, 
        "firestore": firestore, 
        "datetime": datetime, 
        "time": time, 
        "math": math, 
        "pd": pd, 
        "base64": base64,
        "normalizar_texto": normalizar_texto,
        "doutorado_em_portugues": doutorado_em_portugues,
        "CATEGORIAS_OFICIAIS": ["Pedreiro", "Locutor", "Locutor porta de loja", "Eletricista", "Mecânico"]
    }

    if btn_testar or (code_test and not btn_publicar):
        try:
            exec(code_test, contexto_compartilhado)
        except Exception as e:
            st.error(f"❌ ERRO NO SEU CÓDIGO: {e}")

# 6. LÓGICA DE PUBLICAÇÃO (MANTIDA)
if btn_publicar:
    try:
        db.collection("configuracoes").document("layout_ia").set({
            "codigo_injetado": code_test,
            "data_atualizacao": datetime.now(fuso_horario),
            "status": "producao"
        })
        st.balloons()
        st.success("✅ CÓDIGO ENVIADO PARA O SITE OFICIAL!")
    except Exception as e:
        st.error(f"Erro ao publicar: {e}")

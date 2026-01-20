# --- GERALJÁ | TESTADOR DE ELITE (SANDBOX) ---
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import math
import re
import time
import pandas as pd
import unicodedata # Adicionado: estava faltando!
from datetime import datetime
import pytz

# 1. AMBIENTE DE SIMULAÇÃO
st.set_page_config(page_title="GeralJá | Laboratório de Testes", layout="wide", page_icon="🧪")

# 2. CONEXÃO SEGURA (CORRIGIDA)
if not firebase_admin._apps:
    try:
        # Usando o nome correto da secret que você definiu no seu secrets.toml
        # Se no arquivo estiver [firebase] base64 = "...", use a linha abaixo:
        fb_base64 = st.secrets["firebase"]["base64"] 
        fb_dict = json.loads(base64.b64decode(fb_base64).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except Exception as e:
        st.error(f"Erro na conexão Firebase: {e}")

db = firestore.client()
fuso_horario = pytz.timezone('America/Sao_Paulo')

# 3. FUNÇÕES CORE (Sincronizadas)
def normalizar_texto(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

def doutorado_em_portugues(texto):
    if not texto: return ""
    return texto.strip().title()

# 4. INTERFACE DO LABORATÓRIO
st.title("🧪 Laboratório GeralJá")
st.caption("Gênia da Web - Modo Desenvolvedor Ativo")

col_editor, col_preview = st.columns([1, 1])

with col_editor:
    st.subheader("📝 Editor de Código")
    
    # Tenta buscar o código que já está rodando no site oficial
    try:
        doc_atual = db.collection("configuracoes").document("layout_ia").get()
        codigo_atual = doc_atual.to_dict().get("codigo_injetado", "") if doc_atual.exists else ""
    except:
        codigo_atual = "# Escreva seu código Python aqui..."

    # Área de edição
    code_test = st.text_area("Rascunho de Teste", value=codigo_atual, height=500)
    
    col_btn1, col_btn2 = st.columns(2)
    btn_testar = col_btn1.button("🔍 EXECUTAR TESTE LOCAL", use_container_width=True)
    btn_publicar = col_btn2.button("🚀 PUBLICAR NO SITE", type="primary", use_container_width=True)

with col_preview:
    st.subheader("📱 Preview")
    st.markdown("---")
    
    # O contexto que o exec() vai enxergar
    contexto_compartilhado = {
        "st": st, 
        "db": db, 
        "firestore": firestore, 
        "datetime": datetime, 
        "time": time, 
        "math": math, 
        "pd": pd, 
        "normalizar_texto": normalizar_texto,
        "doutorado_em_portugues": doutorado_em_portugues,
        "CATEGORIAS_OFICIAIS": ["Pedreiro", "Locutor", "Locutor porta de loja", "Eletricista", "Mecânico"]
    }

    if btn_testar or code_test:
        try:
            # RODA O CÓDIGO INJETADO
            exec(code_test, contexto_compartilhado)
        except Exception as e:
            st.error(f"❌ ERRO NO SEU CÓDIGO: {e}")

# 5. LÓGICA DE PUBLICAÇÃO
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

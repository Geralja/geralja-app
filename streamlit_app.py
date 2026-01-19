
# --- GERALJÁ | TESTADOR DE ELITE (SANDBOX) ---
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64, json, datetime, math, re, time, pandas as pd, unicodedata, pytz
from datetime import datetime
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONEXÃO SEGURA COM O COFRE ---
if not firebase_admin._apps:
    # Puxa os dados do st.secrets que você acabou de salvar
    fb_conf = st.secrets["firebase"]
    
    # Inicializa o Firebase usando as chaves do cofre
    # Nota: Para Firestore em Python, o ideal é usar a Service Account (JSON), 
    # mas se estiver usando via REST ou outra integração, os dados acima ajudam.
    
    # Se você for usar o SDK de Admin (recomendado para Firestore), 
    # o ideal é gerar o JSON na aba "Service Accounts" do Firebase como te falei antes.

# 1. AMBIENTE DE SIMULAÇÃO
st.set_page_config(page_title="GeralJá | Laboratório de Testes", layout="wide")

# 2. CONEXÃO (Mesma do Principal para garantir paridade)
if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()
fuso_horario = pytz.timezone('America/Sao_Paulo')

# 3. FUNÇÕES CORE (Copiadas do Principal para paridade total)
def normalizar_texto(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

def doutorado_em_portugues(texto):
    if not texto: return ""
    return texto.strip().title()

# 4. INTERFACE DO LABORATÓRIO
st.title("🧪 Laboratório GeralJá")
st.info("O código escrito aqui simula o comportamento do módulo dinâmico do site oficial.")

col_editor, col_preview = st.columns([1, 1])

with col_editor:
    st.subheader("📝 Editor de Código")
    # Busca o código atual do banco para começar o teste a partir dele
    doc_atual = db.collection("configuracoes").document("layout_ia").get()
    codigo_atual = doc_atual.to_dict().get("codigo_injetado", "") if doc_atual.exists else ""
    
    # Campo para editar o novo código de teste
    code_test = st.text_area("Rascunho de Teste", value=codigo_atual, height=500, help="Escreva o código aqui para testar ao lado.")
    
    btn_testar = st.button("🔍 EXECUTAR TESTE LOCAL")
    btn_publicar = st.button("🚀 PUBLICAR NO SITE OFICIAL", type="primary")

with col_preview:
    st.subheader("📱 Visualização em Tempo Real")
    st.markdown("---")
    
    # Contexto que a Genia definiu para o exec()
    contexto_compartilhado = {
        "st": st, "db": db, "firestore": firestore, "datetime": datetime, 
        "time": time, "math": math, "pd": pd, "normalizar_texto": normalizar_texto,
        "doutorado_em_portugues": doutorado_em_portugues, "busca_global": "", # Simulado
        "CATEGORIAS_OFICIAIS": ["Pizzaria", "Mecânico", "Eletricista", "Moda", "Beleza", "Outros"]
    }

    if btn_testar or code_test:
        try:
            # RODA O CÓDIGO APENAS NESTA COLUNA
            exec(code_test, contexto_compartilhado)
        except Exception as e:
            st.error(f"❌ ERRO NO TESTE: {e}")

# 5. LÓGICA DE PUBLICAÇÃO (A SOLDA FINAL)
if btn_publicar:
    try:
        db.collection("configuracoes").document("layout_ia").set({
            "codigo_injetado": code_test,
            "data_atualizacao": datetime.now(fuso_horario),
            "status": "producao"
        })
        st.success("✅ CÓDIGO SOLDADO COM SUCESSO NO SITE PRINCIPAL!")
        st.balloons()
        time.sleep(2)
    except Exception as e:
        st.error(f"Erro ao publicar: {e}")

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

# --- MOTOR DE GEOLOCALIZAÇÃO (RESGATADO DA V1) ---
try:
    from streamlit_js_eval import streamlit_js_eval, get_geolocation
except ImportError:
    pass

# --- 1. PERFORMANCE DE ELITE (CACHE) & TIMEZONE ---
st.set_page_config(page_title="GeralJá | Sistema Operacional", layout="wide", initial_sidebar_state="collapsed")

if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()
fuso_horario = pytz.timezone('America/Sao_Paulo')

# --- 2. MOTOR DE INTELIGÊNCIA (DOUTORADO & BUSCA) ---
def normalizar_texto(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

def doutorado_em_portugues(texto):
    """Padroniza o português (Ex: 'pizzaria' -> 'Pizzaria')"""
    if not texto: return ""
    texto = " ".join(texto.split())
    return texto.title().strip()

def calcular_distancia_real(lat1, lon1, lat2, lon2):
    """Matemática da V1 para proximidade"""
    if not all([lat1, lon1, lat2, lon2]): return 0
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

@st.cache_data(ttl=600)
def carregar_bloco_dinamico():
    try:
        doc = db.collection("configuracoes").document("layout_ia").get()
        return doc.to_dict().get("codigo_injetado", "") if doc.exists else ""
    except: return ""

def registrar_tendencia(termo):
    if termo and len(termo) > 3 and termo != "0413ocara":
        try:
            db.collection("tendencias").add({
                "termo": termo, "data": datetime.now(fuso_horario)
            })
        except: pass

# --- 3. DESIGN E UI LUXO ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .header-master { 
        background: white; padding: 35px; border-radius: 0 0 40px 40px; 
        text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.05); 
        border-bottom: 8px solid #FF8C00; margin-bottom: 25px; 
    }
    .logo-geral { color: #0047AB; font-weight: 900; font-size: 48px; letter-spacing: -2px; }
    .logo-ja { color: #FF8C00; font-weight: 900; font-size: 48px; letter-spacing: -2px; }
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-master"><span class="logo-geral">GERAL</span><span class="logo-ja">JÁ</span></div>', unsafe_allow_html=True)

# --- 4. BARRA DE PESQUISA INTELIGENTE ---
busca_global = st.text_input("", placeholder="🔍 O que o Grajaú precisa hoje?", label_visibility="collapsed")

if busca_global == "0413ocara":
    st.session_state.modo_arquiteto = True
    st.toast("🚀 CPU 10.0 ATIVADA", icon="⚙️")
elif busca_global:
    registrar_tendencia(busca_global)

# --- 5. EXECUÇÃO COM CONTEXTO EXPANDIDO (LIMPO E SEM REPETIÇÕES) ---
codigo_da_ia = carregar_bloco_dinamico()
if codigo_da_ia:
    try:
        contexto_compartilhado = {
            "st": st, "db": db, "firestore": firestore,
            "datetime": datetime, "time": time, "re": re, "math": math, "pd": pd,
            "normalizar_texto": normalizar_texto,
            "doutorado_em_portugues": doutorado_em_portugues,
            "calcular_distancia_real": calcular_distancia_real,
            "busca_global": busca_global,
            "CATEGORIAS_OFICIAIS": ["Pizzaria", "Mecânico", "Eletricista", "Moda", "Beleza", "Outros"],
            "CONCEITOS_EXPANDIDOS": {"fome": "Pizzaria", "luz": "Eletricista", "vazamento": "Encanador"}
        }
        exec(codigo_da_ia, contexto_compartilhado)
    except Exception as e:
        st.error(f"⚠️ Erro no Módulo Dinâmico: {e}")

# --- 6. PAINEL ARQUITETO PRO ---
if st.session_state.get("modo_arquiteto"):
    st.write("---")
    with st.expander("🛠️ PAINEL DE CONTROLE DE ELITE"):
        st.subheader("📊 Insights da CPU")
        col1, col2 = st.columns(2)
        col1.metric("Status do Servidor", "100% Online")
        col2.metric("Motor de Injeção", "v10.0 (Doutorado)")
        
        novo_cod = st.text_area("Código de Injeção", value=codigo_da_ia, height=450)
        
        if st.button("🚀 SOLDAR E APLICAR EM TEMPO REAL"):
            db.collection("configuracoes").document("layout_ia").set({
                "codigo_injetado": novo_cod, "data": datetime.now(fuso_horario)
            })
            st.cache_data.clear() 
            st.success("SISTEMA ATUALIZADO!"); time.sleep(1); st.rerun()
            # ==============================================================================
# 🔍 ABA #1: O MOTOR UNIFICADO (V1 + V2) - BUSCA ESTILO GOOGLE
# ==============================================================================

with menu[0]:
    # 1. Identificação da Busca
    if busca_global and busca_global != "0413ocara":
        st.markdown(f"### 🔎 Resultados para: *'{busca_global}'*")
    else:
        st.markdown("### 🔎 Explore o Grajaú")

    # 2. Filtros de Refino
    with st.expander("⚙️ Refinar Busca (Distância e Categorias)"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_cat = st.multiselect("Categorias Específicas", CATEGORIAS_OFICIAIS)
        with col_f2:
            raio_km = st.slider("Distância Máxima (KM)", 1, 50, 10)
    
    st.divider()

    # 3. MOTOR DE BUSCA HÍBRIDO (Lê V1 e V2)
    try:
        # Puxamos todos os profissionais para fazer a filtragem inteligente
        # Nota: Assim que o índice de 'saldo' terminar, voltamos a usar o order_by
        docs = db.collection("profissionais").stream()
        
        encontrados = 0
        termo = normalizar_texto(busca_global)
        
        for idx, d in enumerate(docs):
            p = d.to_dict()
            
            # --- PONTE DE COMPATIBILIDADE (V1 -> V2) ---
            nome_original = p.get('nome', 'Profissional')
            # Na V1 o campo era 'area', na V2 é 'categoria' 
            cat_p = p.get('categoria') if p.get('categoria') else p.get('area', 'Geral')
            # Na V1 era 'aprovado', na V2 é 'status' 
            esta_ativo = p.get('status') == "Ativo" or p.get('aprovado') == True
            desc_p = p.get('servico') if p.get('servico') else p.get('descricao', '')
            
            if esta_ativo:
                # Lógica de Busca Estilo Google (Nome, Descrição ou Categoria)
                texto_alvo = normalizar_texto(f"{nome_original} {desc_p} {cat_p}")
                
                if not busca_global or busca_global == "0413ocara" or termo in texto_alvo:
                    # Filtro de Categoria da Aba
                    if not filtro_cat or cat_p in filtro_cat:
                        encontrados += 1
                        nome_formatado = doutorado_em_portugues(nome_original)
                        
                        with st.container():
                            st.markdown(f"""
                            <div class="card-brabo-pesquisa">
                                <div style="display: flex; justify-content: space-between;">
                                    <b style="font-size: 20px; color: #0047AB;">{nome_formatado} {"☑️" if p.get('verificado') else ""}</b>
                                    <span class="badge-categoria">{cat_p}</span>
                                </div>
                                <p class="result-info">{desc_p[:150]}...</p>
                                <div style="font-size: 12px; color: #FF8C00;">🔥 {p.get('saldo', 0)} pontos de reputação</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            c1, c2 = st.columns(2)
                            # Usa o ID do documento (Zap) para o link [cite: 48, 62]
                            zap_link = p.get('whatsapp') if p.get('whatsapp') else d.id
                            c1.link_button("🟢 ZAP DIRETO", f"https://wa.me/55{zap_link}", key=f"q_zap_{idx}")
                            if c2.button(f"👀 Ver Detalhes", key=f"q_det_{idx}"):
                                st.toast(f"Carregando vitrine de {nome_formatado}...")

        if encontrados == 0:
            st.info("Nenhum profissional encontrado. Tente buscar por outro termo!")

    except Exception as e:
        st.error(f"Erro na integração: {e}")

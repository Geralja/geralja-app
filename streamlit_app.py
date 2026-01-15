# ==============================================================================
# GERALJÁ: ELITE EDITION - ROBUSTEZ TOTAL + FEED COMUNIDADE
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

# --- COMPONENTES DE GEOLOCALIZAÇÃO ---
try:
    from streamlit_js_eval import streamlit_js_eval, get_geolocation
except ImportError:
    pass

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DE AMBIENTE E PERFORMANCE
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="GeralJá | Criando Soluções",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS DE ALTA PERFORMANCE (UI LUXO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="viewerBadge"] { font-family: 'Inter', sans-serif; }
    .block-container { max-width: 1000px !important; padding-top: 1rem !important; margin: auto !important; }
    .header-container { 
        background: white; padding: 40px 20px; border-radius: 0 0 50px 50px; 
        text-align: center; box-shadow: 0 15px 40px rgba(0,0,0,0.08); 
        border-bottom: 8px solid #FF8C00; margin-bottom: 25px; 
    }
    .logo-azul { color: #0047AB; font-weight: 900; font-size: 50px; letter-spacing: -3px; }
    .logo-laranja { color: #FF8C00; font-weight: 900; font-size: 50px; letter-spacing: -3px; }
    .card-elite {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05); border: 1px solid #f1f5f9;
        margin-bottom: 20px; transition: 0.3s;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        background: #f1f5f9; border-radius: 10px; padding: 10px 20px; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background: #FF8C00 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. CORE: CONEXÃO FIREBASE & INTELIGÊNCIA
# ------------------------------------------------------------------------------
@st.cache_resource
def init_db():
    if not firebase_admin._apps:
        try:
            b64_key = st.secrets["FIREBASE_BASE64"]
            cred_dict = json.loads(base64.b64decode(b64_key).decode("utf-8"))
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Erro Crítico Firebase: {e}")
    return firestore.client()

db = init_db()

class MotorGeralJa:
    @staticmethod
    def normalizar(t):
        if not t: return ""
        return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

# ------------------------------------------------------------------------------
# 3. INTERFACE PRINCIPAL
# ------------------------------------------------------------------------------
st.markdown('<div class="header-container"><span class="logo-azul">GERAL</span><span class="logo-laranja">JÁ</span><br><small style="color:#64748B; font-weight:bold;">A MAIOR VITRINE DA ZONA SUR</small></div>', unsafe_allow_html=True)

menu_abas = st.tabs(["🔍 BUSCA IA", "📻 COMUNIDADE", "🚀 CADASTRAR", "👤 MEU PERFIL", "⚙️ ADMIN"])

# ==============================================================================
# ABA 1: BUSCA IA (ROBUSTEZ TOTAL V1)
# ==============================================================================
with menu_abas[0]:
    col_search, col_loc = st.columns([4, 1])
    with col_search:
        busca = st.text_input("O que você precisa no Grajaú?", placeholder="Ex: Pedreiro, Pizza, Advogado...")
    with col_loc:
        if st.button("📍 Perto de mim"):
            st.toast("Buscando localização...")

    # Categorias Rápidas
    st.write("---")
    cats = ["🛠️ Serviços", "🍕 Alimentação", "⚖️ Jurídico", "🩺 Saúde", "🚗 Automotivo"]
    cat_sel = st.pills("Categorias", cats)

    # Lógica de Ranking e Busca (Sua V1 completa)
    prof_ref = db.collection("profissionais")
    query = prof_ref.stream()
    
    resultados = []
    for doc in query:
        p = doc.to_dict()
        pid = doc.id
        p['id'] = pid
        match = False
        
        termo = MotorGeralJa.normalizar(busca)
        if termo in MotorGeralJa.normalizar(p.get('nome','')) or termo in MotorGeralJa.normalizar(p.get('servico','')):
            match = True
        
        if match:
            # Cálculo de Pontuação Elite
            score = p.get('saldo', 0) * 2 + p.get('avaliacao', 0) * 10
            p['score'] = score
            resultados.append(p)
    
    # Ordenar por Score (Elite primeiro)
    resultados = sorted(resultados, key=lambda x: x['score'], reverse=True)

    if resultados:
        for r in resultados:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 3, 1])
                with c1:
                    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70)
                with c2:
                    st.subheader(r.get('nome'))
                    st.caption(f"📍 {r.get('bairro', 'Grajaú')} • ⭐ {r.get('avaliacao', 5.0)}")
                    st.write(r.get('servico', 'Serviço Geral'))
                with c3:
                    zap_link = f"https://wa.me/55{r.get('whatsapp')}?text=Vi+no+GeralJa"
                    st.link_button("ZAP", zap_link, use_container_width=True)
    elif busca:
        st.warning("Nenhum profissional encontrado com esse termo.")

# ==============================================================================
# ABA 2: COMUNIDADE (FEED DINÂMICO)
# ==============================================================================
with menu_abas[1]:
    st.markdown("### 📻 Mural Grajaú Tem")
    
    # Sistema de Postagem Admin
    if st.session_state.get('user_id') == "11991853488":
        with st.expander("📝 PUBLICAR NO FEED"):
            with st.form("feed_form"):
                titulo = st.text_input("Título")
                desc = st.text_area("Descrição")
                link = st.text_input("Link da Matéria")
                if st.form_submit_button("Postar"):
                    db.collection("feed_comunidade").add({
                        "titulo": titulo, "desc": desc, "link": link,
                        "data": datetime.now(), "autor": "Bonynho"
                    })
                    st.success("Publicado com sucesso!")
                    st.rerun()

    # Exibição das Notícias
    noticias = db.collection("feed_comunidade").order_by("data", direction=firestore.Query.DESCENDING).limit(15).stream()
    for n in noticias:
        item = n.to_dict()
        st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 15px; border-left: 6px solid #FF8C00; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 15px;">
                <h4 style="color: #0047AB; margin: 0;">{item.get('titulo')}</h4>
                <p style="color: #64748B; margin: 10px 0;">{item.get('desc')}</p>
                <a href="{item.get('link')}" target="_blank" style="color: #FF8C00; font-weight: bold; text-decoration: none;">VER NO PORTAL →</a>
            </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 3: CADASTRAR (ROBUSTEZ V1)
# ==============================================================================
with menu_abas[2]:
    st.markdown("### 🚀 Faça parte da maior rede da Zona Sul")
    with st.form("cad_form"):
        c_nome = st.text_input("Nome Profissional/Loja")
        c_zap = st.text_input("WhatsApp (com DDD)")
        c_serv = st.text_area("O que você faz? (Serviços)")
        c_senha = st.text_input("Senha", type="password")
        if st.form_submit_button("CRIAR MEU PERFIL ELITE"):
            if c_nome and c_zap:
                db.collection("profissionais").document(c_zap).set({
                    "nome": c_nome, "whatsapp": c_zap, "servico": c_serv,
                    "senha": c_senha, "saldo": 50, "avaliacao": 5.0, "data_cad": datetime.now()
                })
                st.success("Bem-vindo! Você recebeu 50 moedas de bônus! 🎁")

# ==============================================================================
# ABA 4: PAINEL / LOGIN
# ==============================================================================
with menu_abas[3]:
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.subheader("🔑 Acesso ao Painel")
        u = st.text_input("WhatsApp", key="login_u")
        p = st.text_input("Senha", type="password", key="login_p")
        if st.button("Entrar no Painel"):
            doc = db.collection("profissionais").document(u).get()
            if doc.exists and doc.to_dict().get('senha') == p:
                st.session_state.auth = True
                st.session_state.user_id = u
                st.rerun()
            else:
                st.error("Dados incorretos.")
    else:
        # Conteúdo do Painel do Profissional
        p_doc = db.collection("profissionais").document(st.session_state.user_id).get().to_dict()
        st.write(f"### Olá, {p_doc.get('nome')}!")
        st.metric("Seu Saldo", f"{p_doc.get('saldo')} moedas")
        if st.button("Sair"):
            st.session_state.auth = False
            st.rerun()

# ==============================================================================
# ABA 5: ADMIN (CONTROLE TOTAL V1)
# ==============================================================================
with menu_abas[4]:
    st.subheader("👑 Controle Mestre")
    adm_pass = st.text_input("Chave Mestra", type="password")
    if adm_pass == "suachave": # Coloque sua chave
        profs = db.collection("profissionais").stream()
        for p_doc in profs:
            d = p_doc.to_dict()
            with st.expander(f"👤 {d.get('nome')} ({p_doc.id})"):
                st.write(f"Saldo: {d.get('saldo')}")
                if st.button(f"➕ Add Saldo ({p_doc.id})"):
                    db.collection("profissionais").document(p_doc.id).update({"saldo": d.get('saldo') + 10})
                    st.rerun()

st.markdown("<br><center><small>v3.2 Elite • Grajaú Tem Engine</small></center>", unsafe_allow_html=True)

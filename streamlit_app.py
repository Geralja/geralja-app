import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json
import datetime
import pandas as pd
from datetime import datetime
import pytz

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÕES E CONSTANTES
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="GeralJá | Premium Pro",
    page_icon="⚡",
    layout="wide"
)

PIX_OFICIAL = "11991853488"
BONUS_WELCOME = 50.0  # Saldo inicial gratuito
VALOR_CLIQUE = 2.00   # Quanto custa cada clique para o profissional

# ------------------------------------------------------------------------------
# 2. ESTILIZAÇÃO MODERNA (CSS)
# ------------------------------------------------------------------------------
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        border-radius: 20px;
        transition: all 0.3s ease;
        background: linear-gradient(45deg, #00b4d8, #0077b6);
        color: white;
        border: none;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
    .card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .card:hover { border-color: #00b4d8; }
    .status-online { color: #00ff88; font-weight: bold; }
    .price-tag { background: #2a2a2a; padding: 5px 10px; border-radius: 10px; color: #ffcc00; }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. FIREBASE SETUP
# ------------------------------------------------------------------------------
if not firebase_admin._apps:
    try:
        # Tenta carregar dos Secrets do Streamlit
        fb_dict = json.loads(st.secrets["firebase"]["text"])
        cred = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro ao conectar Firebase: {e}")

db = firestore.client()

# ------------------------------------------------------------------------------
# 4. FUNÇÕES AUXILIARES
# ------------------------------------------------------------------------------
def registrar_clique(pro_id, saldo_atual):
    if saldo_atual >= VALOR_CLIQUE:
        novo_saldo = saldo_atual - VALOR_CLIQUE
        db.collection("profissionais").document(pro_id).update({"saldo": novo_saldo})
        return True
    return False

# ------------------------------------------------------------------------------
# 5. INTERFACE PRINCIPAL
# ------------------------------------------------------------------------------
st.title("⚡ GeralJá Pro")
st.caption("A plataforma mais rápida para encontrar profissionais qualificados.")

abas = st.tabs(["🔍 Encontrar Profissional", "💼 Para Profissionais", "⚙️ Admin"])

# --- ABA 1: BUSCA ---
with abas[0]:
    col1, col2 = st.columns([2, 1])
    with col1:
        busca = st.text_input("O que você precisa hoje?", placeholder="Ex: Eletricista, Limpeza, Design...")
    with col2:
        categoria = st.selectbox("Categoria", ["Todas", "Reparos", "Limpeza", "Tecnologia", "Saúde"])

    # Lógica de Busca no Firebase
    pros_ref = db.collection("profissionais")
    query = pros_ref.where("saldo", ">", 0).stream() # Só mostra quem tem saldo

    cols = st.columns(3)
    idx = 0
    for doc in query:
        p = doc.to_dict()
        p['id'] = doc.id
        
        # Filtro simples de texto
        if busca.lower() in p.get('nome', '').lower() or busca.lower() in p.get('servico', '').lower():
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="card">
                    <h4>{p.get('nome')}</h4>
                    <p style='font-size: 0.8em; color: #888;'>{p.get('servico')}</p>
                    <span class="price-tag">⭐ {p.get('rating', '5.0')}</span>
                    <p class="status-online">● Disponível Agora</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📞 Ver Contato", key=p['id']):
                    if registrar_clique(p['id'], p.get('saldo', 0)):
                        st.success(f"WhatsApp: {p.get('whatsapp')}")
                        st.info("Diga que viu no GeralJá!")
                    else:
                        st.warning("Este profissional está temporariamente indisponível.")
            idx += 1

# --- ABA 2: CADASTRO ---
with abas[1]:
    st.header("Seja um parceiro")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome Completo")
        zap = st.text_input("WhatsApp (com DDD)")
        servico = st.text_input("Sua Especialidade")
        
        if st.form_submit_button("Cadastrar e Ganhar Bônus"):
            novo_pro = {
                "nome": nome,
                "whatsapp": zap,
                "servico": servico,
                "saldo": BONUS_WELCOME,
                "data_adesao": datetime.now(pytz.timezone('America/Sao_Paulo')),
                "rating": 5.0
            }
            db.collection("profissionais").add(novo_pro)
            st.balloons()
            st.success(f"Bem-vindo! Você ganhou R$ {BONUS_WELCOME} de saldo inicial!")

# --- ABA 3: ADMIN ---
with abas[2]:
    chave = st.text_input("Chave Mestra", type="password")
    if chave == st.secrets.get("ADMIN_KEY", "admin123"):
        st.write("### Gestão de Saldo")
        # Lista simples para o admin gerenciar
        pros = db.collection("profissionais").stream()
        for doc in pros:
            p = doc.to_dict()
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"{p.get('nome')} | Saldo: R$ {p.get('saldo')}")
            if col_b.button("+R$10", key=f"add_{doc.id}"):
                db.collection("profissionais").document(doc.id).update({"saldo": p.get('saldo', 0) + 10})
                st.rerun()

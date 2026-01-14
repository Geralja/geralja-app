import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import datetime
import pandas as pd
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO DE AMBIENTE ---
st.set_page_config(
    page_title="GeralJá | Social Marketplace",
    page_icon="⚡",
    layout="wide"
)

# Constantes que estavam faltando
PIX_OFICIAL = "11991853488"
BONUS_WELCOME = 50.0
VALOR_CLIQUE = 2.00

# --- ESTILIZAÇÃO INTERFACE FACEBOOK (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    .fb-card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        border: 1px solid #ddd;
    }
    .pro-name { color: #1c1e21; font-weight: bold; font-size: 1.2rem; }
    .verified-badge { color: #1877f2; margin-left: 5px; }
    .service-tag { 
        background: #e7f3ff; color: #1877f2; 
        padding: 4px 10px; border-radius: 5px; 
        font-size: 0.85rem; font-weight: 600;
    }
    /* Estilização dos Botões */
    div.stButton > button {
        width: 100%;
        background-color: #1877f2;
        color: white;
        border-radius: 6px;
        border: none;
        height: 45px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #166fe5;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO FIREBASE ---
if not firebase_admin._apps:
    try:
        fb_dict = json.loads(st.secrets["firebase"]["text"])
        cred = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(cred)
    except:
        st.error("Erro: Configure o Secret 'firebase' no Streamlit Cloud.")

db = firestore.client()

# --- HEADER ---
st.markdown("""
    <div style="background: white; padding: 10px; border-bottom: 1px solid #ddd; margin-bottom: 20px; text-align: center;">
        <h1 style="color: #1877f2; margin: 0;">GeralJá</h1>
        <p style="color: #65676b;">Encontre soluções na sua comunidade</p>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
abas = st.tabs(["🏠 Feed de Serviços", "➕ Cadastrar-se", "📈 Painel Pro", "🛡️ Admin"])

# ------------------------------------------------------------------------------
# ABA 1: FEED (BUSCA)
# ------------------------------------------------------------------------------
with abas[0]:
    col_l, col_c, col_r = st.columns([1, 2, 1])
    
    with col_l:
        st.markdown("### Filtros")
        busca = st.text_input("🔍 O que procura?", placeholder="Ex: Pintor, Advogado...")
        categoria = st.selectbox("Categoria", ["Todas", "Manutenção", "Estética", "Educação", "Outros"])

    with col_c:
        pros_ref = db.collection("profissionais").where("saldo", ">", 0).stream()
        
        encontrados = 0
        for doc in pros_ref:
            p = doc.to_dict()
            pid = doc.id
            
            # Lógica de Busca Simples
            if busca.lower() in p.get('nome', '').lower() or busca.lower() in p.get('servico', '').lower():
                encontrados += 1
                nome_completo = p.get('nome', 'Profissional')
                servico = p.get('servico') or "Serviços Gerais"
                primeiro_nome = nome_completo.split()[0]
                
                # Card Estilo Facebook
                st.markdown(f"""
                <div class="fb-card">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="width: 45px; height: 45px; background: #ccd0d5; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 12px;">
                            {nome_completo[0].upper()}
                        </div>
                        <div>
                            <span class="pro-name">{nome_completo}</span> <span class="verified-badge">✔</span><br>
                            <small style="color: #65676b;">Ativo agora • São Paulo</small>
                        </div>
                    </div>
                    <div style="margin: 15px 0;">
                        <span class="service-tag">{servico}</span>
                    </div>
                    <p style="color: #1c1e21; font-size: 0.95rem;">Especialista pronto para atender sua solicitação. Clique abaixo para negociar.</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Enviar mensagem para {primeiro_nome}", key=f"btn_{pid}"):
                    if p.get('saldo', 0) >= VALOR_CLIQUE:
                        novo_saldo = p.get('saldo') - VALOR_CLIQUE
                        db.collection("profissionais").document(pid).update({"saldo": novo_saldo})
                        st.success(f"Contato: {p.get('whatsapp')}")
                        st.link_button("Abrir WhatsApp", f"https://wa.me/{p.get('whatsapp')}")
                    else:
                        st.warning("Este profissional atingiu o limite de contatos.")

        if encontrados == 0:
            st.info("Nenhum profissional encontrado com esse termo.")

    with col_r:
        st.markdown("### Sugestões")
        st.info("💡 Profissionais com selo ✔ têm prioridade no atendimento.")

# ------------------------------------------------------------------------------
# ABA 2: CADASTRO
# ------------------------------------------------------------------------------
with abas[1]:
    st.markdown("## Comece a receber clientes hoje!")
    with st.form("reg_pro"):
        nome_c = st.text_input("Seu Nome")
        zap_c = st.text_input("WhatsApp (com DDD)")
        serv_c = st.text_input("O que você faz?")
        
        if st.form_submit_button("Criar meu Perfil Pro"):
            if nome_c and zap_c:
                novo = {
                    "nome": nome_c,
                    "whatsapp": zap_c,
                    "servico": serv_c,
                    "saldo": BONUS_WELCOME,
                    "data": datetime.now(pytz.timezone('America/Sao_Paulo')),
                    "verificado": True
                }
                db.collection("profissionais").add(novo)
                st.balloons()
                st.success("Cadastro realizado! Você ganhou R$ 50 de bônus.")

# ------------------------------------------------------------------------------
# ABA 3 e 4: PAINEL E ADMIN (Resumidos para funcionalidade)
# ------------------------------------------------------------------------------
with abas[2]:
    st.write("Consulte seu saldo enviando seu nome na busca.")

with abas[3]:
    pwd = st.text_input("Chave Mestra", type="password")
    if pwd == "admin123":
        st.write("Gerenciamento de Profissionais")
        # Aqui você pode listar todos e deletar ou adicionar saldo

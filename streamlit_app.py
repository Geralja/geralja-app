import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="GeralJá Social", layout="wide")

# --- CSS ESTILO FACEBOOK / SOCIAL APP ---
st.markdown("""
    <style>
    /* Fundo suave de rede social */
    .stApp { background-color: #f0f2f5; }
    
    /* Card estilo Post do Facebook */
    .fb-card {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        border: 1px solid #ddd;
    }
    
    .pro-name {
        color: #1c1e21;
        font-weight: bold;
        font-size: 1.1rem;
        text-decoration: none;
    }
    
    .verified-badge {
        color: #1877f2;
        font-size: 0.9rem;
        margin-left: 5px;
    }
    
    .category-pill {
        background: #e4e6eb;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #050505;
        display: inline-block;
        margin-right: 5px;
    }

    /* Botão estilo 'Enviar Mensagem' */
    div.stButton > button {
        width: 100%;
        background-color: #e4e6eb;
        color: #050505;
        border: none;
        font-weight: 600;
        transition: 0.2s;
    }
    
    div.stButton > button:hover {
        background-color: #d8dadf;
    }

    /* Estilo para o topo azul */
    .header-fb {
        background-color: #ffffff;
        padding: 10px 20px;
        border-bottom: 1px solid #ddd;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO FIREBASE (Mesma lógica anterior) ---
if not firebase_admin._apps:
    fb_dict = json.loads(st.secrets["firebase"]["text"])
    cred = credentials.Certificate(fb_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- HEADER TIPO BARRA DE NAVEGAÇÃO ---
st.markdown("""
    <div class="header-fb">
        <h2 style='color: #1877f2; margin:0;'>GeralJá <span style='font-size: 0.8rem; color: #65676b;'>Comunidade</span></h2>
    </div>
""", unsafe_allow_html=True)

# --- STORIES / CATEGORIAS ---
st.write("### Categorias")
cat_cols = st.columns(6)
categorias = ["🏠 Reformas", "🧹 Limpeza", "💻 Tech", "🎨 Design", "🚗 Mecânico", "⚖️ Jurídico"]
for i, cat in enumerate(categorias):
    cat_cols[i].markdown(f"<div class='category-pill'>{cat}</div>", unsafe_allow_html=True)

st.divider()

# --- LAYOUT PRINCIPAL (3 Colunas: Filtros | Feed | Perfil) ---
col_left, col_feed, col_right = st.columns([1, 2, 1])

with col_left:
    st.markdown("#### Filtros")
    st.text_input("🔍 Buscar no feed", placeholder="Ex: Eletricista...")
    st.checkbox("Apenas Verificados")
    st.checkbox("Mais Próximos")

with col_feed:
    # Lógica de puxar dados
    pros_ref = db.collection("profissionais").where("saldo", ">", 0).stream()
    
    for doc in pros_ref:
        p = doc.to_dict()
        pid = doc.id
        
        # HTML do Card
        st.markdown(f"""
            <div class="fb-card">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 40px; height: 40px; background: #1877f2; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 10px;">
                        {p.get('nome')[0].upper()}
                    </div>
                    <div>
                        <span class="pro-name">{p.get('nome')}</span>
                        <span class="verified-badge">✔ Verificado</span><br>
                        <small style="color: #65676b;">Publicado em: 14 jan 2026</small>
                    </div>
                </div>
                <p style="color: #050505;">{p.get('servico')}</p>
                <hr style="border: 0.5px solid #eee;">
            </div>
        """, unsafe_allow_html=True)
        
        # Botão de Interação
        if st.button(f"💬 Entrar em contato com {p.get('nome').split()[0]}", key=pid):
            # Lógica de cobrança de saldo
            novo_saldo = p.get('saldo', 0) - 2.0
            db.collection("profissionais").document(pid).update({"saldo": novo_saldo})
            st.success(f"WhatsApp: {p.get('whatsapp')}")

with col_right:
    st.markdown("#### Seu Perfil")
    with st.container():
        st.markdown("""
            <div class="fb-card" style="text-align: center;">
                <p><b>R$ 50,00</b><br><small>Saldo de Impulsionamento</small></p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("➕ Recarregar"):
            st.info("PIX: " + st.secrets.get("PIX", "11991853488"))

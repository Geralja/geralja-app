import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import math
import unicodedata
from datetime import datetime
from streamlit_js_eval import get_geolocation

# 1. CONFIGURAÇÃO DE TELA (FIXO ✅)
st.set_page_config(page_title="GeralJá | Sistema de Elite", layout="wide")

# ==============================================================================
# 🔒 BLOCO 0: INFRAESTRUTURA E SEGURANÇA (A ORIGEM - FIXO ✅)
# ==============================================================================
if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()

# ==============================================================================
# 🧠 BLOCO 1: O MOTOR DE INTELIGÊNCIA (O CÉREBRO - FIXO ✅)
# ==============================================================================
def ia_mestra_processar(texto):
    if not texto: return None
    t = "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower()
    mapa = {"pizza": "Pizzaria", "fome": "Pizzaria", "carro": "Mecânico", "luz": "Eletricista", "roupa": "Moda"}
    for chave, cat in mapa.items():
        if chave in t: return cat
    return None

def calcular_distancia_real(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]: return 999
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return round(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))), 1)

# ==============================================================================
# 💎 BLOCO 2: DESIGN DE VITRINE (Aprovado como Revista ✅)
# ==============================================================================
def renderizar_vitrine_luxo(busca, lat_u, lon_u):
    cat_ia = ia_mestra_processar(busca)
    st.markdown("""
        <style>
        .card-luxo { background: white; border-radius: 25px; border: 1px solid #eee; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); overflow: hidden; }
        .img-luxo { width: 100%; height: 380px; object-fit: cover; }
        .info-luxo { padding: 25px; }
        .price-luxo { font-size: 1.5rem; font-weight: 800; color: #1a1a1a; }
        .loja-tag { font-size: 0.7rem; letter-spacing: 2px; color: #888; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    lojas = db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">=", 1).stream()

    for loja in lojas:
        l_id, l_data = loja.id, loja.to_dict()
        if busca and not (busca.lower() in l_data.get('nome','').lower() or cat_ia == l_data.get('area')):
            continue

        posts = db.collection("profissionais").document(l_id).collection("posts").where("ativo", "==", True).stream()
        for p_doc in posts:
            p = p_doc.to_dict()
            st.markdown(f"""
                <div class="card-luxo">
                    <img src="data:image/png;base64,{p.get('foto')}" class="img-luxo">
                    <div class="info-luxo">
                        <div class="loja-tag">{l_data.get('nome').upper()}</div>
                        <h2 style="margin: 10px 0;">{p.get('titulo')}</h2>
                        <div class="price-luxo">R$ {p.get('preco')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"SOLICITAR ATENDIMENTO", key=f"btn_{p_doc.id}"):
                db.collection("profissionais").document(l_id).update({"saldo": l_data['saldo'] - 1})
                st.success(f"CONCIERGE LIBERADO: {l_data.get('whatsapp')}")
                st.link_button("ABRIR WHATSAPP", f"https://wa.me/55{l_data.get('whatsapp')}")

# ==============================================================================
# 🛠️ BLOCO EM TESTE: CONSTRUTOR DE FUNÇÕES
# ==============================================================================
def main():
    # Localização em tempo real (Sua função potente)
    loc = get_geolocation()
    lat = loc['coords']['latitude'] if loc else -23.5505
    lon = loc['coords']['longitude'] if loc else -46.6333

    menu = st.tabs(["💎 VITRINE", "🏪 MEU ESPAÇO", "👑 ADMIN"])

    with menu[0]:
        st.markdown("<h1 style='text-align:center;'>GERALJÁ</h1>", unsafe_allow_html=True)
        busca = st.text_input("", placeholder="Busque o que você precisa...")
        renderizar_vitrine_luxo(busca, lat, lon)

    with menu[1]:
        st.info("Aqui instalaremos o Bloco do Lojista (50 créditos)")

# ==============================================================================
# 🧹 O VARREDOR (RODAPÉ FINALIZADOR - FIXO ✅)
# ==============================================================================
def finalizar_e_alinhar_layout():
    st.write("---")
    st.markdown("""
        <div style="text-align: center; opacity: 0.7; font-size: 0.8rem; padding: 20px;">
            <p>🎯 <b>GeralJá</b> - Sistema de Inteligência Local</p>
            <p>v2.0 | © 2026 Todos os direitos reservados</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    finalizar_e_alinhar_layout()

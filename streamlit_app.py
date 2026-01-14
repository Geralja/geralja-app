import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import math
import unicodedata
from datetime import datetime
from streamlit_js_eval import get_geolocation

# ==============================================================================
# 🧱 BLOCO 0: IGNIÇÃO E BANCO DE DADOS (FIXO ✅)
# ==============================================================================
if not firebase_admin._apps:
    try:
        # Puxa sua chave do Streamlit Secrets
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except Exception as e:
        st.error(f"Erro na conexão: {e}")

db = firestore.client()

# ==============================================================================
# 🧱 BLOCO 1: O CÉREBRO (IA E GPS) - (FIXO ✅)
# ==============================================================================

def ia_mestra_processar(texto):
    if not texto: return None
    t = "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower()
    mapa = {"pizza": "Pizzaria", "hamburguer": "Lanchonete", "mecanico": "Mecânico", "luz": "Eletricista", "roupa": "Moda"}
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
# 🧱 BLOCO 2: DESIGN DE VITRINE "REVISTA DE LUXO" - (APROVADO ✅)
# ==============================================================================

def renderizar_vitrine_luxo(busca, lat_u, lon_u):
    cat_ia = ia_mestra_processar(busca)
    
    # CSS de Elite
    st.markdown("""
        <style>
        .card-luxo { background: #fff; border-radius: 25px; border: 1px solid #eee; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); overflow: hidden; }
        .img-luxo { width: 100%; height: 400px; object-fit: cover; }
        .info-luxo { padding: 25px; }
        .price-luxo { font-size: 1.5rem; font-weight: 800; color: #000; }
        </style>
    """, unsafe_allow_html=True)

    # Busca no seu Banco de Dados Real
    lojas = db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">=", 1).stream()

    for loja in lojas:
        l_id = loja.id
        l_data = loja.to_dict()
        dist = calcular_distancia_real(lat_u, lon_u, l_data.get('lat'), l_data.get('lon'))
        
        # Filtro de Busca
        if busca and not (busca.lower() in l_data.get('nome','').lower() or cat_ia == l_data.get('area')):
            continue

        # Puxa os Posts de cada Loja
        posts = db.collection("profissionais").document(l_id).collection("posts").where("ativo", "==", True).stream()
        for p_doc in posts:
            p = p_doc.to_dict()
            st.markdown(f"""
                <div class="card-luxo">
                    <img src="data:image/png;base64,{p.get('foto')}" class="img-luxo">
                    <div class="info-luxo">
                        <small>{l_data.get('nome').upper()} • {dist}km</small>
                        <h2>{p.get('titulo')}</h2>
                        <div class="price-luxo">R$ {p.get('preco')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"FALAR COM {l_data.get('nome').upper()}", key=f"btn_{p_doc.id}"):
                # Cobrança de 1 crédito
                db.collection("profissionais").document(l_id).update({"saldo": l_data['saldo'] - 1})
                st.success(f"Contato: {l_data.get('whatsapp')}")

# ==============================================================================
# 🏗️ CONSTRUTOR PRINCIPAL (CANTEIRO DE OBRAS)
# ==============================================================================

def main():
    st.set_page_config(page_title="GeralJá | Elite", layout="wide")
    
    # LOCALIZAÇÃO GPS
    loc = get_geolocation()
    lat = loc['coords']['latitude'] if loc else -23.5505
    lon = loc['coords']['longitude'] if loc else -46.6333

    tab1, tab2 = st.tabs(["🔍 EXPLORAR VITRINE", "🏪 MINHA MAISON"])

    with tab1:
        termo = st.text_input("", placeholder="O que você deseja buscar hoje?")
        renderizar_vitrine_luxo(termo, lat, lon)

    with tab2:
        st.write("Bloco do Editor em Construção...")

# ==============================================================================
# 🏁 RODAPÉ E VARREDOR (FIXO NA ORIGEM ✅)
# ==============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erro no Motor Principal: {e}")
    
    st.write("---")
    st.markdown("<div style='text-align:center; opacity:0.5;'>GeralJá Core System v2.0</div>", unsafe_allow_html=True)

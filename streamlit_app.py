import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import datetime
import math
import re
import pandas as pd
import unicodedata

# 1. CONFIGURAÇÃO DE TELA (FIXO ✅)
st.set_page_config(page_title="GeralJá | Timeline Elite", layout="wide")

# ==============================================================================
# 🛡️ BLOCO DE SEGURANÇA E IMPORTAÇÕES (FIXO ✅)
# ==============================================================================
try:
    from streamlit_js_eval import get_geolocation
    GPS_DISPONIVEL = True
except (ImportError, ModuleNotFoundError):
    GPS_DISPONIVEL = False

def sanitizar_texto_luxo(texto):
    if not texto: return ""
    limpo = re.sub(r'<[^>]*?>', '', texto)
    if limpo.isupper() and len(limpo) > 10:
        limpo = limpo.capitalize()
    return limpo.strip()

def buscar_localizacao_segura():
    if GPS_DISPONIVEL:
        try:
            loc = get_geolocation()
            if loc and 'coords' in loc:
                return loc['coords']['latitude'], loc['coords']['longitude']
        except: pass
    return -23.5505, -46.6333 

# ==============================================================================
# 🔒 BLOCO 0: CONEXÃO FIREBASE (FIXO ✅)
# ==============================================================================
if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except: pass
db = firestore.client()

# ==============================================================================
# 🧠 BLOCO 1: MOTOR DE INTELIGÊNCIA (FIXO ✅)
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
# 💎 BLOCO 2: VITRINE DE LUXO (DINÂMICA DE DESTAQUE ✅)
# ==============================================================================
def renderizar_vitrine_luxo(busca, lat_u, lon_u):
    cat_ia = ia_mestra_processar(busca)
    
    # CSS dos Cards na Timeline
    st.markdown("""
        <style>
        .card-luxo { background: white; border-radius: 15px; border: 1px solid #e1e4e8; margin-bottom: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); overflow: hidden; }
        .img-luxo { width: 100%; height: 320px; object-fit: cover; }
        .info-luxo { padding: 20px; }
        .price-luxo { font-size: 1.4rem; font-weight: 800; color: #1a1a1a; }
        </style>
    """, unsafe_allow_html=True)

    lojas = db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">=", 1).stream()

    for loja in lojas:
        l_id, l_data = loja.id, loja.to_dict()
        nome_limpo = sanitizar_texto_luxo(l_data.get('nome', 'Loja'))
        dist = calcular_distancia_real(lat_u, lon_u, l_data.get('lat'), l_data.get('lon'))
        
        termo = busca.lower() if busca else ""
        is_busca_loja = termo and termo in nome_limpo.lower()
        is_busca_geral = not termo or (cat_ia == l_data.get('area'))

        if is_busca_loja:
            posts = db.collection("profissionais").document(l_id).collection("posts").where("ativo", "==", True).stream()
        elif is_busca_geral:
            posts = db.collection("profissionais").document(l_id).collection("posts").where("destaque", "==", True).limit(1).stream()
        else: continue

        for p_doc in posts:
            p = p_doc.to_dict()
            st.markdown(f"""
                <div class="card-luxo">
                    <img src="data:image/png;base64,{p.get('foto')}" class="img-luxo">
                    <div class="info-luxo">
                        <small style="color:#65676b; font-weight:bold;">{nome_limpo.upper()} • {dist}km</small>
                        <h3 style="margin: 5px 0;">{sanitizar_texto_luxo(p.get('titulo'))}</h3>
                        <div class="price-luxo">R$ {p.get('preco')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"SOLICITAR ATENDIMENTO", key=f"btn_{p_doc.id}", use_container_width=True):
                db.collection("profissionais").document(l_id).update({"saldo": l_data['saldo'] - 1})
                st.success(f"CONCIERGE LIBERADO: {l_data.get('whatsapp')}")
                st.link_button("ABRIR WHATSAPP", f"https://wa.me/55{l_data.get('whatsapp')}", use_container_width=True)

# ==============================================================================
# 🏗️ CONSTRUTOR PRINCIPAL (MODULAR E ELÁSTICO)
# ==============================================================================
def main():
    lat, lon = buscar_localizacao_segura()

    # Estilização da Timeline (Fundo cinza, blocos brancos)
    st.markdown("""
        <style>
        .bloco-modular { background-color: #ffffff; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #f0f2f5; }
        .stApp { background-color: #f0f2f5; }
        </style>
    """, unsafe_allow_html=True)

    col_lateral, col_central = st.columns([1, 2.5])

    # 📦 BLOCO LATERAL
    with col_lateral:
        st.markdown('<div class="bloco-modular">', unsafe_allow_html=True)
        st.markdown("### 🧭 Explorar")
        st.button("🏠 Home Feed", use_container_width=True)
        st.button("🏪 Minha Maison", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="bloco-modular">', unsafe_allow_html=True)
        st.caption("🛡️ STATUS DE SEGURANÇA")
        st.success("Antivírus Ativo")
        st.markdown('</div>', unsafe_allow_html=True)

    # 📦 BLOCO CENTRAL (Timeline)
    with col_central:
        
        # 🚀 1. CANTEIRO DE OBRAS (Prioridade Máxima - Espaço Elástico)
        st.markdown('<div class="bloco-modular" style="border-left: 5px solid #007bff;">', unsafe_allow_html=True)
        st.markdown("### 🧪 BLOCO EM TESTE")
        # --- O NOVO BLOCO ENTRA AQUI ---
        st.info("O espaço está reservado. O próximo módulo que testarmos aparecerá neste bloco azul.")
        # -------------------------------
        st.markdown('</div>', unsafe_allow_html=True)

        # 💎 2. VITRINE OFICIAL
        st.markdown('<div class="bloco-modular">', unsafe_allow_html=True)
        busca = st.text_input("", placeholder="Busque por produtos ou lojas...", key="busca_timeline")
        st.markdown('</div>', unsafe_allow_html=True)
        
        renderizar_vitrine_luxo(busca, lat, lon)

# ==============================================================================
# 🏁 RODAPÉ FINALIZADOR
# ==============================================================================
def rodape_inteligente():
    st.write("---")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<small>🟢 SISTEMA PROTEGIDO</small>", unsafe_allow_html=True)
    with c2: st.markdown("<div style='text-align:center;'><small>🛡️ ANTIVÍRUS ATIVO</small></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div style='text-align:right;'><small>v2.0 | {datetime.datetime.now().year}</small></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    finally:
        rodape_inteligente()

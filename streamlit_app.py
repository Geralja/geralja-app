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
st.set_page_config(page_title="GeralJá | Sistema de Elite", layout="wide")

# ==============================================================================
# 🛡️ BLOCO DE SEGURANÇA E IMPORTAÇÕES (FIXO ✅)
# ==============================================================================
try:
    from streamlit_js_eval import get_geolocation
    GPS_DISPONIVEL = True
except (ImportError, ModuleNotFoundError):
    GPS_DISPONIVEL = False

# Sanitização (Antivírus de texto)
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
    return -23.5505, -46.6333 # SP Padrão

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
                        <div class="loja-tag">{nome_limpo.upper()} • {dist}km</div>
                        <h2 style="margin: 10px 0;">{sanitizar_texto_luxo(p.get('titulo'))}</h2>
                        <div class="price-luxo">R$ {p.get('preco')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"SOLICITAR ATENDIMENTO", key=f"btn_{p_doc.id}"):
                db.collection("profissionais").document(l_id).update({"saldo": l_data['saldo'] - 1})
                st.success(f"CONCIERGE LIBERADO: {l_data.get('whatsapp')}")
                st.link_button("ABRIR WHATSAPP", f"https://wa.me/55{l_data.get('whatsapp')}")

# ==============================================================================
# 🏗️ CONSTRUTOR PRINCIPAL (ESPAÇO ELÁSTICO)
# ==============================================================================
def main():
    # 1. PEÇAS FIXAS DE FUNDAÇÃO (GPS e IA)
    lat, lon = buscar_localizacao_segura()
    
    # 2. 🚀 ÁREA DE TESTE (PRIORIDADE MÁXIMA)
    # Tudo o que estiver nesta caixa aparece PRIMEIRO para sua avaliação.
    st.markdown("### 🧪 BLOCO EM TESTE")
    with st.container():
        # EXEMPLO: Se estivéssemos testando o novo Editor de 50 Créditos:
        # modulo_editor_lojista_TESTE() 
        st.info("Aguardando novo bloco para teste... O espaço está reservado aqui no topo.")
    
    st.write("---") # Divisor visual entre Teste e Fixo

    # 3. 🏠 CONTEÚDO FIXO (CEDENDO ESPAÇO)
    # Este conteúdo "desce" para dar lugar ao teste acima.
    abas = st.tabs(["💎 VITRINE OFICIAL", "🏪 CONFIGURAÇÕES"])
    
    with abas[0]:
        st.markdown("<h1 style='text-align:center;'>GERALJÁ</h1>", unsafe_allow_html=True)
        busca = st.text_input("", placeholder="Busque por loja ou produto...", key="busca_fixa")
        renderizar_vitrine_luxo(busca, lat, lon)
    
    with abas[1]:
        st.write("Configurações do sistema.")

# ==============================================================================
# 🏁 O RESTO DO CÓDIGO (BANCO, IA, RODAPÉ) SEGUE IGUAL
# ==============================================================================
# ==============================================================================
# 🏁 RODAPÉ E FINALIZAÇÃO
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

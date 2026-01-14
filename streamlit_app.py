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
def renderizar_vitrine_luxo(busca, lat_u, lon_u):
    cat_ia = ia_mestra_processar(busca)
    
    # Buscamos as lojas que têm saldo
    lojas = db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">=", 1).stream()

    for loja in lojas:
        l_id, l_data = loja.id, loja.to_dict()
        nome_loja = l_data.get('nome', '').lower()
        termo_busca = busca.lower() if busca else ""

        # REGRA DE EXIBIÇÃO:
        # 1. Se o usuário digitou o nome EXATO da loja ou parte dele
        is_busca_loja = termo_busca and termo_busca in nome_loja
        
        # 2. Se é apenas uma busca por categoria (IA) ou busca vazia
        is_busca_geral = not termo_busca or (cat_ia == l_data.get('area'))

        if is_busca_loja:
            # MOSTRA TUDO: Busca todos os posts ativos daquela loja específica
            posts = db.collection("profissionais").document(l_id).collection("posts").where("ativo", "==", True).stream()
        elif is_busca_geral:
            # MOSTRA DESTAQUE: Busca apenas o post marcado como 'destaque' para a vitrine geral
            posts = db.collection("profissionais").document(l_id).collection("posts").where("destaque", "==", True).limit(1).stream()
        else:
            continue

        for p_doc in posts:
            p = p_doc.to_dict()
            # [AQUI VAI O SEU CSS DO CARD DE LUXO QUE JÁ ENVIAMOS]
            st.markdown(f"""
                <div class="card-luxo">
                    <img src="data:image/png;base64,{p.get('foto')}" class="img-luxo">
                    <div class="info-luxo">
                        <div class="loja-tag">{l_data.get('nome').upper()}</div>
                        <h2>{p.get('titulo')}</h2>
                        <div class="price-luxo">R$ {p.get('preco')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            # ... (Botão de contato e cobrança de 1 crédito segue igual)

def modulo_editor_lojista(l_id, l_data):
    st.subheader("📸 Gerenciar Minha Vitrine")
    
    # 1. LISTAR POSTS PARA ESCOLHER O DESTAQUE
    posts_ref = db.collection("profissionais").document(l_id).collection("posts").stream()
    meus_posts = {p.id: p.to_dict().get('titulo') for p in posts_ref}
    
    if meus_posts:
        selecionado = st.selectbox("Qual post deve aparecer na Vitrine Geral?", 
                                    options=list(meus_posts.keys()), 
                                    format_func=lambda x: meus_posts[x])
        
        if st.button("Fixar como Destaque"):
            # Primeiro: Tira o destaque de todos
            for p_id in meus_posts.keys():
                db.collection("profissionais").document(l_id).collection("posts").document(p_id).update({"destaque": False})
            # Segundo: Coloca o destaque no selecionado
            db.collection("profissionais").document(l_id).collection("posts").document(selecionado).update({"destaque": True})
            st.success("Post fixado na vitrine principal!")
    
    # 2. REGRA DOS 50 CRÉDITOS
    if not l_data.get('ganhou_bonus') and len(meus_posts) >= 1:
        if st.button("Minha Vitrine está 100% Perfeita! (Ganhar 50 GeralCoins)"):
            db.collection("profissionais").document(l_id).update({
                "saldo": l_data.get('saldo', 0) + 50,
                "ganhou_bonus": True
            })
            st.balloons()
            st.rerun()
            

# ==============================================================================
# 🏁 BLOCO 4: RODAPÉ INTELIGENTE COM AUTO-CORREÇÃO E SEGURANÇA (FIXO ✅)
# ==============================================================================

import re

# 1. FUNÇÃO ANTIVÍRUS E AUTO-CORREÇÃO (O "Limpador")
def sanitizar_texto_luxo(texto):
    """Bloqueia poluição visual e scripts maliciosos"""
    if not texto: return ""
    # Antivírus: Remove qualquer tentativa de código <script> ou HTML
    limpo = re.sub(r'<[^>]*?>', '', texto)
    # Auto-Correção: Se o lojista escreveu TUDO EM MAIÚSCULO, nós suavizamos
    if limpo.isupper() and len(limpo) > 10:
        limpo = limpo.capitalize()
    return limpo.strip()

# 2. FUNÇÃO DO RODAPÉ INTELIGENTE
def rodape_inteligente():
    st.write("---")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("<small>🟢 SISTEMA PROTEGIDO</small>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='text-align:center;'><small>🛡️ ANTIVÍRUS DE DADOS ATIVO</small></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div style='text-align:right;'><small>v2.0 | {datetime.now().year}</small></div>", unsafe_allow_html=True)

    # O "Varredor" Original do seu arquivo (Estilizado)
    st.markdown("""
        <style>
            .main .block-container { padding-bottom: 5rem !important; }
            .footer-clean { text-align: center; padding: 20px; opacity: 0.6; font-size: 0.8rem; }
        </style>
        <div class="footer-clean">
            <p>🎯 <b>GeralJá</b> - Sistema de Inteligência Local</p>
            <p>Conectando com segurança e elegância.</p>
        </div>
    """, unsafe_allow_html=True)

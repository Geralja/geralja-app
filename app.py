# ==============================================================================
# GERALJÁ 2.0 - SISTEMA TURBINADO (REDE SOCIAL + COMERCIAL)
# ==============================================================================
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import math
import re
import time
from datetime import datetime
from PIL import Image
import io

# --- TENTA IMPORTAR GPS (Indispensável para o Piloto) ---
try:
    from streamlit_js_eval import get_geolocation
except:
    pass

# ==============================================================================
# 1. MOTOR IA MESTRE: FUNÇÕES SEPARADAS
# ==============================================================================
class IAMestre:
    @staticmethod
    def otimizar_imagem(file):
        """Transforma fotos pesadas em JPEG leve de alta qualidade"""
        if file is None: return None
        try:
            img = Image.open(file)
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.thumbnail((800, 800))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=60, optimize=True)
            return base64.b64encode(buffer.getvalue()).decode()
        except: return None

    @staticmethod
    def limpar_id(texto):
        """Limpa o WhatsApp para virar ID único"""
        return re.sub(r'\D', '', str(texto or ""))

    @staticmethod
    def calc_distancia(lat1, lon1, lat2, lon2):
        """Cálculo de Proximidade (Haversine)"""
        if not all([lat1, lon1, lat2, lon2]): return 999
        R = 6371 
        dLat, dLon = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

    @staticmethod
    def renderizar_post(foto_b64, legenda, nome_prof, data, zap):
        """Visual de Post de Rede Social Comercial"""
        st.markdown(f"""
            <div style="border-radius: 15px; background: white; padding: 15px; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); border: 1px solid #eee;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 40px; height: 40px; background: #FFD700; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px; color: white;">
                        {nome_prof[0].upper()}
                    </div>
                    <div>
                        <b>{nome_prof}</b><br>
                        <small style="color: #888;">{data}</small>
                    </div>
                </div>
                <img src="data:image/jpeg;base64,{foto_b64}" style="width: 100%; border-radius: 10px; max-height: 350px; object-fit: cover;">
                <p style="margin-top: 10px; color: #333;">{legenda}</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"💬 Orçamento com {nome_prof}", key=f"btn_{zap}_{time.time()}"):
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=https://wa.me/55{zap}">', unsafe_allow_html=True)

# ==============================================================================
# 2. CONEXÃO FIREBASE (SEGURA)
# ==============================================================================
st.set_page_config(page_title="GeralJá IA", layout="wide", page_icon="🚀")

if not firebase_admin._apps:
    try:
        cred_info = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
    except:
        st.error("Erro nos Secrets! Verifique o 'textkey'.")

db = firestore.client()

# ==============================================================================
# 3. INTERFACE E ABAS (ORGANIZAÇÃO POR LINHAS)
# ==============================================================================
menu = st.tabs(["📱 FEED SOCIAL", "🔍 BUSCA GPS", "📢 CADASTRAR", "👤 MEU PERFIL", "⚙️ ADMIN"])

# ------------------------------------------------------------------------------
# ABA 1: FEED SOCIAL (A NOVA IDEIA)
# ------------------------------------------------------------------------------
with menu[0]:
    st.subheader("🔥 Mural de Realizações")
    posts = db.collection("postagens").order_by("data", direction=firestore.Query.DESCENDING).limit(15).stream()
    
    col_feed1, col_feed2 = st.columns(2)
    for i, p in enumerate(posts):
        dados = p.to_dict()
        with (col_feed1 if i % 2 == 0 else col_feed2):
            IAMestre.renderizar_post(dados['foto'], dados['legenda'], dados['nome_prof'], dados['data'], dados['zap_prof'])

# ------------------------------------------------------------------------------
# ABA 2: BUSCA GPS (PROFISSIONAIS PERTO)
# ------------------------------------------------------------------------------
with menu[1]:
    st.subheader("📍 Profissionais na sua região")
    loc = get_geolocation()
    if loc:
        lat_c, lon_c = loc['coords']['latitude'], loc['coords']['longitude']
        profs = db.collection("profissionais").stream()
        for p in profs:
            d = p.to_dict()
            dist = IAMestre.calc_distancia(lat_c, lon_c, d.get('lat'), d.get('lon'))
            if dist < 50: # Raio de 50km
                with st.container(border=True):
                    st.write(f"**{d['nome']}** - {d['area']} (a {dist:.1f} km)")
                    st.link_button("Ver Perfil/WhatsApp", f"https://wa.me/55{d['telefone']}")
    else:
        st.warning("Ative o GPS para buscar.")

# ------------------------------------------------------------------------------
# ABA 3: CADASTRAR
# ------------------------------------------------------------------------------
with menu[2]:
    with st.form("cad_pro"):
        st.subheader("🚀 Criar Conta Comercial")
        c1, c2 = st.columns(2)
        n_nome = c1.text_input("Nome/Empresa")
        n_zap = c1.text_input("WhatsApp")
        n_pass = c2.text_input("Senha", type="password")
        n_area = c2.selectbox("Área", ["Pintor", "Eletricista", "Encanador", "Diarista", "Mecânico"])
        
        if st.form_submit_button("CRIAR MINHA VITRINE"):
            loc_p = get_geolocation()
            uid = IAMestre.limpar_id(n_zap)
            if loc_p and uid:
                db.collection("profissionais").document(uid).set({
                    "nome": n_nome, "telefone": uid, "senha": n_pass, "area": n_area,
                    "lat": loc_p['coords']['latitude'], "lon": loc_p['coords']['longitude'],
                    "saldo": 0
                })
                st.success("Cadastrado! Faça login no 'Meu Perfil'.")

# ------------------------------------------------------------------------------
# ABA 4: MEU PERFIL (POSTAR NA REDE SOCIAL)
# ------------------------------------------------------------------------------
with menu[3]:
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.subheader("🔑 Entrar no Painel")
        l_zap = st.text_input("WhatsApp", key="login_zap")
        l_pas = st.text_input("Senha", type="password")
        if st.button("ACESSAR"):
            uid = IAMestre.limpar_id(l_zap)
            doc = db.collection("profissionais").document(uid).get()
            if doc.exists and str(doc.to_dict().get('senha')) == l_pas:
                st.session_state.auth, st.session_state.u_id = True, uid
                st.session_state.u_nome = doc.to_dict().get('nome')
                st.rerun()
    else:
        st.write(f"Olá, **{st.session_state.u_nome}**!")
        with st.expander("📸 POSTAR NOVO TRABALHO (MURAL)"):
            f_post = st.file_uploader("Foto do Serviço", type=['jpg','png','jpeg'])
            leg_post = st.text_area("O que foi feito?")
            if st.button("Publicar Agora"):
                if f_post and leg_post:
                    img_b64 = IAMestre.otimizar_imagem(f_post)
                    db.collection("postagens").add({
                        "zap_prof": st.session_state.u_id,
                        "nome_prof": st.session_state.u_nome,
                        "foto": img_b64, "legenda": leg_post,
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    st.success("Postado!")
                    time.sleep(1)
                    st.rerun()
        if st.button("Sair"):
            st.session_state.auth = False
            st.rerun()

# ------------------------------------------------------------------------------
# ABA 5: ADMIN
# ------------------------------------------------------------------------------
with menu[4]:
    if st.text_input("Chave Mestra", type="password") == "admin123":
        st.write("Painel Admin Ativo")
)

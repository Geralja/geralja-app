# ==============================================================================
# GERALJÁ 2.0 - VERSÃO ESTÁVEL (REDE SOCIAL + GPS)
# ==========================================================
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json, base64, io, re, time, math
from datetime import datetime
from PIL import Image

# 1. TENTA ATIVAR O GPS LOGO NO INÍCIO
try:
    from streamlit_js_eval import get_geolocation
    loc = get_geolocation()
except:
    loc = None

# 2. CONEXÃO COM FIREBASE (Usa os Secrets que já estão funcionando)
if not firebase_admin._apps:
    try:
        cred_info = json.loads(st.secrets["textkey"])
        firebase_admin.initialize_app(credentials.Certificate(cred_info))
    except:
        st.error("Erro nos Secrets! Verifique o painel do Streamlit.")

db = firestore.client()

# ==========================================================
# 3. MOTOR IA MESTRE: FUNÇÕES SEPARADAS POR LINHAS
# ==========================================================

def otimizar_imagem(file):
    """IA que deixa a foto leve para o mural carregar rápido"""
    if file is None: return None
    img = Image.open(file)
    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
    img.thumbnail((700, 700))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=60)
    return base64.b64encode(buffer.getvalue()).decode()

# ----------------------------------------------------------

def calcular_distancia(lat1, lon1, lat2, lon2):
    """Calcula a distância entre cliente e profissional"""
    if not all([lat1, lon1, lat2, lon2]): return 999
    R = 6371 
    dLat, dLon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# ==========================================================
# 4. INTERFACE DO APLICATIVO (ABAS)
# ==========================================================
st.title("🚀 GeralJá - Mural de Serviços")

aba_feed, aba_busca, aba_cadastro, aba_perfil = st.tabs([
    "🔥 FEED SOCIAL", "🔍 BUSCAR GPS", "📢 CADASTRAR", "👤 MEU PERFIL"
])

# --- ABA 1: FEED SOCIAL (A VITRINE) ---
with aba_feed:
    st.subheader("Trabalhos Recentes")
    # Busca os posts mais novos do banco
    posts = db.collection("postagens").order_by("data", direction=firestore.Query.DESCENDING).limit(10).stream()
    
    for p in posts:
        d = p.to_dict()
        with st.container(border=True):
            st.markdown(f"**{d['nome_prof']}** • <small>{d['data']}</small>", unsafe_allow_html=True)
            st.image(f"data:image/jpeg;base64,{d['foto']}", use_container_width=True)
            st.write(d['legenda'])
            st.link_button(f"Pedir Orçamento para {d['nome_prof']}", f"https://wa.me/55{d['zap_prof']}")

# --- ABA 2: BUSCAR GPS ---
with aba_busca:
    st.subheader("Profissionais Perto de Você")
    if loc:
        lat_c, lon_c = loc['coords']['latitude'], loc['coords']['longitude']
        profs = db.collection("profissionais").stream()
        for p in profs:
            d = p.to_dict()
            dist = calcular_distancia(lat_c, lon_c, d.get('lat'), d.get('lon'))
            if dist < 50:
                with st.container(border=True):
                    st.write(f"**{d['nome']}** - {d.get('area')} (a {dist:.1f} km)")
                    st.link_button("Chamar no WhatsApp", f"https://wa.me/55{d['telefone']}")
    else:
        st.info("Ative o GPS para ver a distância dos profissionais.")

# --- ABA 3: CADASTRAR ---
with aba_cadastro:
    with st.form("cad"):
        st.subheader("Crie sua Conta Comercial")
        nome = st.text_input("Nome/Empresa")
        zap = st.text_input("WhatsApp")
        area = st.selectbox("Área", ["Pintor", "Eletricista", "Encanador", "Limpeza", "Outros"])
        senha = st.text_input("Crie uma Senha", type="password")
        if st.form_submit_button("CRIAR MEU PERFIL"):
            if loc and nome and zap:
                uid = re.sub(r'\D', '', zap)
                db.collection("profissionais").document(uid).set({
                    "nome": nome, "telefone": uid, "area": area, "senha": senha,
                    "lat": loc['coords']['latitude'], "lon": loc['coords']['longitude']
                })
                st.success("✅ Perfil criado! Vá em 'Meu Perfil' para postar.")
            else:
                st.error("Erro: Ative o GPS para cadastrar seu local de atendimento.")

# --- ABA 4: MEU PERFIL (SISTEMA DE POSTAGEM) ---
with aba_perfil:
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.write("### Login")
        l_zap = st.text_input("WhatsApp", key="login_z")
        l_pas = st.text_input("Senha", type="password", key="login_s")
        if st.button("Entrar no Meu Painel"):
            uid = re.sub(r'\D', '', l_zap)
            doc = db.collection("profissionais").document(uid).get()
            if doc.exists and str(doc.to_dict().get('senha')) == l_pas:
                st.session_state.auth, st.session_state.u_id = True, uid
                st.session_state.u_nome = doc.to_dict().get('nome')
                st.rerun()
    else:
        st.write(f"### Olá, {st.session_state.u_nome}!")
        with st.expander("📸 POSTAR NOVO TRABALHO"):
            nova_foto = st.file_uploader("Foto do Serviço", type=['jpg','png','jpeg'])
            legenda = st.text_area("O que foi feito?")
            if st.button("PUBLICAR NO FEED"):
                if nova_foto and legenda:
                    img_b64 = otimizar_imagem(nova_foto)
                    db.collection("postagens").add({
                        "zap_prof": st.session_state.u_id,
                        "nome_prof": st.session_state.u_nome,
                        "foto": img_b64, "legenda": legenda,
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    st.success("🔥 Postado no Mural!")
                    time.sleep(1); st.rerun()
        if st.button("Sair"):
            st.session_state.auth = False; st.rerun()

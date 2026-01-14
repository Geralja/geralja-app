# ==============================================================================
# GERALJÁ 2.0 - REDE SOCIAL COMERCIAL (ESTÁVEL)
# ==============================================================================
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json, base64, io, re, time, math
from datetime import datetime
from PIL import Image

# ------------------------------------------------------------------------------
# [1] CONFIGURAÇÃO DA PÁGINA E GPS
# ------------------------------------------------------------------------------
st.set_page_config(page_title="GeralJá Social", layout="wide", page_icon="🚀")

# Tenta capturar localização logo no início
try:
    from streamlit_js_eval import get_geolocation
    loc = get_geolocation()
except:
    loc = None

# ------------------------------------------------------------------------------
# [2] CONEXÃO COM FIREBASE (SEGURA)
# ------------------------------------------------------------------------------
if not firebase_admin._apps:
    try:
        cred_info = json.loads(st.secrets["textkey"])
        firebase_admin.initialize_app(credentials.Certificate(cred_info))
    except:
        st.error("Erro nos Secrets! Verifique o 'textkey' no painel do Streamlit.")

db = firestore.client()

# ------------------------------------------------------------------------------
# [3] MOTOR IA MESTRE - TRATAMENTO DE IMAGENS E DADOS
# ------------------------------------------------------------------------------
class IAMestre:
    @staticmethod
    def otimizar_foto(file):
        """ IA que comprime a foto para não travar o app """
        if file is None: return None
        img = Image.open(file)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.thumbnail((700, 700)) # Tamanho ideal para celular
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60)
        return base64.b64encode(buf.getvalue()).decode()

    @staticmethod
    def calc_distancia(lat1, lon1, lat2, lon2):
        """ Calcula quem é o profissional mais próximo """
        if not all([lat1, lon1, lat2, lon2]): return 999
        R = 6371 
        dLat, dLon = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# ------------------------------------------------------------------------------
# [4] INTERFACE PRINCIPAL - ABAS DO APLICATIVO
# ------------------------------------------------------------------------------
st.title("🚀 GeralJá - Mural de Serviços")

menu = st.tabs(["🔥 FEED SOCIAL", "🔍 BUSCA GPS", "📢 CADASTRAR", "👤 MEU PERFIL"])

# --- ABA 1: FEED SOCIAL (A VITRINE) ---
with menu[0]:
    st.subheader("Trabalhos Postados Recentemente")
    posts = db.collection("postagens").order_by("data", direction=firestore.Query.DESCENDING).limit(15).stream()
    
    col_a, col_b = st.columns(2)
    for i, p in enumerate(posts):
        d = p.to_dict()
        with (col_a if i % 2 == 0 else col_b):
            st.markdown(f"""
                <div style="border:1px solid #ddd; border-radius:15px; padding:15px; background:white; margin-bottom:20px;">
                    <b style="font-size:16px;">{d['nome_prof']}</b> • <small>{d['data']}</small>
                    <img src="data:image/jpeg;base64,{d['foto']}" style="width:100%; border-radius:10px; margin-top:10px;">
                    <p style="margin-top:10px;">{d['legenda']}</p>
                </div>
            """, unsafe_allow_html=True)
            st.link_button(f"Falar com {d['nome_prof']}", f"https://wa.me/55{d['zap_prof']}")

# --- ABA 2: BUSCA GPS ---
with menu[1]:
    st.subheader("Profissionais Perto de Você")
    if loc:
        lat_c, lon_c = loc['coords']['latitude'], loc['coords']['longitude']
        profs = db.collection("profissionais").stream()
        for p in profs:
            d = p.to_dict()
            dist = IAMestre.calc_distancia(lat_c, lon_c, d.get('lat'), d.get('lon'))
            if dist < 50:
                with st.container(border=True):
                    st.write(f"**{d['nome']}** - a {dist:.1f} km")
                    st.link_button("Ver no WhatsApp", f"https://wa.me/55{d['telefone']}")
    else:
        st.info("Ative o GPS no seu navegador para ver a distância.")

# --- ABA 3: CADASTRAR ---
with menu[2]:
    with st.form("registro_prof"):
        st.write("Crie seu Perfil Profissional")
        n = st.text_input("Nome/Empresa")
        z = st.text_input("WhatsApp (ex: 11999999999)")
        s = st.text_input("Crie uma Senha", type="password")
        if st.form_submit_button("CRIAR MINHA VITRINE"):
            if loc and n and z:
                uid = re.sub(r'\D', '', z)
                db.collection("profissionais").document(uid).set({
                    "nome": n, "telefone": uid, "senha": s,
                    "lat": loc['coords']['latitude'], "lon": loc['coords']['longitude']
                })
                st.success("Cadastrado com sucesso!")
            else:
                st.error("Erro: Ative o GPS para cadastrar seu local de atendimento.")

# --- ABA 4: MEU PERFIL (POSTAR) ---
with menu[3]:
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.write("### Login")
        log_z = st.text_input("WhatsApp", key="log_z")
        log_s = st.text_input("Senha", type="password", key="log_s")
        if st.button("Acessar Meu Painel"):
            uid = re.sub(r'\D', '', log_z)
            doc = db.collection("profissionais").document(uid).get()
            if doc.exists and str(doc.to_dict().get('senha')) == log_s:
                st.session_state.auth, st.session_state.u_id = True, uid
                st.session_state.u_nome = doc.to_dict().get('nome')
                st.rerun()
    else:
        st.write(f"Olá, **{st.session_state.u_nome}**!")
        with st.expander("📸 POSTAR NOVO SERVIÇO NO FEED"):
            f = st.file_uploader("Foto do Trabalho", type=['jpg','png','jpeg'])
            l = st.text_area("O que você fez?")
            if st.button("PUBLICAR AGORA"):
                if f and l:
                    img_b64 = IAMestre.otimizar_foto(f)
                    db.collection("postagens").add({
                        "zap_prof": st.session_state.u_id,
                        "nome_prof": st.session_state.u_nome,
                        "foto": img_b64, "legenda": l,
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    st.success("Postagem realizada!")
                    time.sleep(1); st.rerun()
        if st.button("Sair"):
            st.session_state.auth = False; st.rerun()

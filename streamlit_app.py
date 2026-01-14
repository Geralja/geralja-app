import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json, base64, io, re
from datetime import datetime
from PIL import Image

# 1. CONFIGURAÇÃO INICIAL
st.set_page_config(page_title="GeralJá", layout="wide")

# 2. CONEXÃO FIREBASE
if not firebase_admin._apps:
    try:
        cred_info = json.loads(st.secrets["textkey"])
        db_cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(db_cred)
    except Exception as e:
        st.error(f"Erro de Configuração: {e}")
        st.stop()

db = firestore.client()

# 3. GPS (Instalado no topo)
try:
    from streamlit_js_eval import get_geolocation
    loc = get_geolocation()
except:
    loc = None

# 4. INTERFACE
st.title("🚀 GeralJá Social")
abas = st.tabs(["🔥 FEED", "📢 CADASTRAR", "👤 PERFIL"])

with abas[0]:
    st.subheader("Mural de Serviços")
    try:
        posts = db.collection("postagens").order_by("data", direction=firestore.Query.DESCENDING).limit(10).stream()
        for p in posts:
            d = p.to_dict()
            st.markdown(f"### {d['nome_prof']}")
            st.image(f"data:image/jpeg;base64,{d['foto']}", use_container_width=True)
            st.write(d['legenda'])
            st.link_button("WhatsApp", f"https://wa.me/55{d['zap_prof']}")
            st.divider()
    except:
        st.write("Ainda não há postagens no feed.")

with abas[1]:
    with st.form("cad"):
        st.write("Criar Perfil")
        nome = st.text_input("Nome")
        zap = st.text_input("WhatsApp")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("CADASTRAR"):
            uid = re.sub(r'\D', '', zap)
            lat = loc['coords']['latitude'] if loc else 0
            lon = loc['coords']['longitude'] if loc else 0
            db.collection("profissionais").document(uid).set({
                "nome": nome, "senha": senha, "zap": uid, "lat": lat, "lon": lon
            })
            st.success("Cadastrado!")

with abas[2]:
    st.write("Área do Profissional")
    # Lógica de login e postagem aqui...

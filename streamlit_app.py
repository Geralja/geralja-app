# ==============================================================================
# GERALJÁ 2.0 - REDE SOCIAL COMERCIAL (ESTÁVEL)
# ==============================================================================
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import re
import time
import math
import io
import base64
from datetime import datetime
from PIL import Image

# ------------------------------------------------------------------------------
# [FUNÇÃO] INICIALIZAÇÃO DO FIREBASE
# ------------------------------------------------------------------------------
if not firebase_admin._apps:
    try:
        cred_info = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro nos Secrets: {e}")
        st.stop()

db = firestore.client()

# ------------------------------------------------------------------------------
# [FUNÇÃO] IA MESTRE - PROCESSAMENTO DE IMAGEM E ESTÉTICA
# ------------------------------------------------------------------------------
class IAMestre:
    @staticmethod
    def otimizar_imagem(file):
        if file is None: return None
        try:
            img = Image.open(file)
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.thumbnail((700, 700))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=60, optimize=True)
            return base64.b64encode(buffer.getvalue()).decode()
        except: return None

    @staticmethod
    def renderizar_post_social(foto_b64, legenda, nome_prof, data, zap):
        """Design de Post para o Feed Social"""
        st.markdown(f"""
            <div style="border-radius: 20px; background: white; padding: 15px; margin-bottom: 25px; border: 1px solid #eee; box-shadow: 0px 5px 15px rgba(0,0,0,0.05);">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <div style="width: 40px; height: 40px; background: #FFD700; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px;">
                        {nome_prof[0].upper()}
                    </div>
                    <div>
                        <b style="font-size: 16px;">{nome_prof}</b><br>
                        <small style="color: #888;">{data}</small>
                    </div>
                </div>
                <img src="data:image/jpeg;base64,{foto_b64}" style="width: 100%; border-radius: 15px; max-height: 400px; object-fit: cover;">
                <p style="margin-top: 15px; color: #333; font-size: 15px;">{legenda}</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"Pedir Orçamento: {nome_prof}", key=f"btn_{zap}_{time.time()}"):
            st.link_button("Abrir WhatsApp", f"https://wa.me/55{zap}")

# ------------------------------------------------------------------------------
# [COMPONENTE] GPS (LOCALIZAÇÃO ÚNICA NA SIDEBAR PARA EVITAR ERRO DE NODE)
# ------------------------------------------------------------------------------
with st.sidebar:
    st.title("📍 GeralJá Local")
    from streamlit_js_eval import get_geolocation
    loc = get_geolocation()
    if loc:
        st.success("Localização capturada!")
    else:
        st.info("Aguardando GPS...")

# ------------------------------------------------------------------------------
# [INTERFACE] ABAS PRINCIPAIS
# ------------------------------------------------------------------------------
st.title("🚀 Rede Social GeralJá")
abas = st.tabs(["🔥 FEED COMERCIAL", "🔍 BUSCAR", "📢 CADASTRAR", "👤 MEU PERFIL"])

# --- ABA 1: FEED SOCIAL ---
with abas[0]:
    posts = db.collection("postagens").order_by("data", direction=firestore.Query.DESCENDING).limit(10).stream()
    for p in posts:
        d = p.to_dict()
        IAMestre.renderizar_post_social(d['foto'], d['legenda'], d['nome_prof'], d['data'], d['zap_prof'])

# --- ABA 2: BUSCAR (FILTRO GPS) ---
with abas[1]:
    st.subheader("Profissionais Perto")
    if loc:
        st.write("Filtro por proximidade ativo!")
        # Lógica de distância aqui
    else:
        st.warning("Ative o GPS para filtrar por distância.")

# --- ABA 3: CADASTRAR ---
with abas[2]:
    with st.form("cad_pro"):
        nome = st.text_input("Nome Profissional")
        zap = st.text_input("WhatsApp (Apenas números)")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("CRIAR MINHA CONTA"):
            if loc and nome and zap:
                uid = re.sub(r'\D', '', zap)
                db.collection("profissionais").document(uid).set({
                    "nome": nome, "telefone": uid, "senha": senha,
                    "lat": loc['coords']['latitude'], "lon": loc['coords']['longitude'], "saldo": 0
                })
                st.success("Cadastro Realizado!")

# --- ABA 4: MEU PERFIL (POSTAR NO FEED) ---
with abas[3]:
    if 'auth' not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        l_zap = st.text_input("WhatsApp")
        l_pas = st.text_input("Senha", type="password")
        if st.button("Entrar no Painel"):
            uid = re.sub(r'\D', '', l_zap)
            doc = db.collection("profissionais").document(uid).get()
            if doc.exists and str(doc.to_dict().get('senha')) == l_pas:
                st.session_state.auth, st.session_state.u_id = True, uid
                st.session_state.u_nome = doc.to_dict().get('nome')
                st.rerun()
    else:
        st.write(f"### Olá, {st.session_state.u_nome}!")
        with st.expander("📸 Publicar no Mural Comercial"):
            f_u = st.file_uploader("Foto do seu serviço", type=['jpg','png','jpeg'])
            l_u = st.text_area("O que você fez neste serviço?")
            if st.button("POSTAR NO FEED"):
                if f_u and l_u:
                    img_b64 = IAMestre.otimizar_imagem(f_u)
                    db.collection("postagens").add({
                        "zap_prof": st.session_state.u_id,
                        "nome_prof": st.session_state.u_nome,
                        "foto": img_b64, "legenda": l_u,
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    st.success("Postagem realizada com sucesso!")
        if st.button("Sair"):
            st.session_state.auth = False
            st.rerun()

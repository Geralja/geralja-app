# ==============================================================================
# GERALJÁ 2.0: REDE SOCIAL COMERCIAL DE SERVIÇOS
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

# --- TENTA IMPORTAR GPS ---
try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    pass

# ==============================================================================
# 1. MOTOR IA MESTRE (Lógica de Otimização e Estética)
# ==============================================================================
class IAMestre:
    @staticmethod
    def otimizar_imagem(file):
        """Comprime fotos para serem leves e rápidas no feed"""
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
        return re.sub(r'\D', '', str(texto or ""))

    @staticmethod
    def calc_distancia(lat1, lon1, lat2, lon2):
        if not all([lat1, lon1, lat2, lon2]): return 999
        R = 6371 
        dLat, dLon = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

    @staticmethod
    def renderizar_post(foto_b64, legenda, nome_prof, data):
        """Cria o visual de post de rede social de luxo"""
        st.markdown(f"""
            <div style="border-radius: 20px; background: white; padding: 15px; margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(0,0,0,0.08); border: 1px solid #f0f0f0;">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <div style="width: 45px; height: 45px; background: linear-gradient(45deg, #FFD700, #FFA500); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        {nome_prof[0].upper()}
                    </div>
                    <div>
                        <b style="color: #1E293B; font-size: 16px;">{nome_prof}</b><br>
                        <small style="color: #94A3B8;">{data}</small>
                    </div>
                </div>
                <img src="data:image/jpeg;base64,{foto_b64}" style="width: 100%; border-radius: 15px; object-fit: cover; max-height: 400px;">
                <p style="margin-top: 12px; color: #334155; font-size: 15px; line-height: 1.5;">{legenda}</p>
                <div style="border-top: 1px solid #f1f5f9; padding-top: 10px; margin-top: 10px;">
                     <span style="color: #FFD700;">★</span> <small style="color: #64748B;">Destaque GeralJá</small>
                </div>
            </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 2. CONFIGURAÇÃO E CONEXÃO FIREBASE
# ==============================================================================
st.set_page_config(page_title="GeralJá | Social Business", layout="wide", page_icon="🚀")

if not firebase_admin._apps:
    try:
        cred_info = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error("⚠️ Erro nos Secrets do Streamlit!")

db = firestore.client()

# ==============================================================================
# 3. INTERFACE PRINCIPAL (ABAS)
# ==============================================================================
menu = st.tabs(["🔥 FEED & BUSCA", "📢 CADASTRAR", "👤 MEU PERFIL", "⚙️ ADMIN"])

# ------------------------------------------------------------------------------
# ABA 1: FEED & BUSCA (A Rede Social)
# ------------------------------------------------------------------------------
with menu[0]:
    st.subheader("📱 Feed de Serviços")
    loc_cliente = get_geolocation()
    
    col_search, col_rad = st.columns([3, 1])
    termo = col_search.text_input("O que você precisa hoje?", placeholder="Ex: Reforma de banheiro, Pintura...")
    raio = col_rad.select_slider("Raio de distância (km)", options=[1, 5, 10, 20, 50, 100], value=20)

    # Lógica de exibição de POSTS (O Diferencial Comercial)
    st.markdown("---")
    posts_ref = db.collection("postagens").order_by("data", direction=firestore.Query.DESCENDING).limit(20).stream()
    
    col_f1, col_f2 = st.columns(2) # Layout em duas colunas estilo Pinterest
    
    for i, post in enumerate(posts_ref):
        p_data = post.to_dict()
        with (col_f1 if i % 2 == 0 else col_f2):
            IAMestre.renderizar_post(p_data['foto'], p_data['legenda'], p_data['nome_prof'], p_data['data'])
            if st.button(f"Pedir Orçamento: {p_data['nome_prof']}", key=f"btn_p_{post.id}"):
                st.link_button("Ir para WhatsApp", f"https://wa.me/55{p_data['zap_prof']}")

# ------------------------------------------------------------------------------
# ABA 2: CADASTRAR (Entrada de Novos Usuários)
# ------------------------------------------------------------------------------
with menu[1]:
    st.subheader("📢 Torne-se um Profissional de Elite")
    loc_pro = get_geolocation()
    
    with st.form("registro_social"):
        c1, c2 = st.columns(2)
        nome_reg = c1.text_input("Nome ou Empresa")
        zap_reg = c1.text_input("WhatsApp (Login)")
        area_reg = c2.selectbox("Categoria", ["Eletricista", "Pintor", "Limpeza", "Mecânico", "Obras", "Outros"])
        pass_reg = c2.text_input("Senha de Acesso", type="password")
        
        if st.form_submit_button("🚀 CRIAR MINHA REDE COMERCIAL"):
            uid = IAMestre.limpar_id(zap_reg)
            if loc_pro and uid:
                with st.spinner("IA criando perfil..."):
                    db.collection("profissionais").document(uid).set({
                        "nome": nome_reg, "telefone": uid, "area": area_reg, "senha": pass_reg,
                        "lat": loc_pro['coords']['latitude'], "lon": loc_pro['coords']['longitude'],
                        "saldo": 10, "cliques": 0
                    })
                    st.success("Perfil criado! Agora faça login para postar no Feed.")
            else:
                st.error("Ative o GPS para ser encontrado por clientes!")

# ------------------------------------------------------------------------------
# ABA 3: MEU PERFIL (Postagens e Gestão)
# ------------------------------------------------------------------------------
with menu[2]:
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        c_log1, c_log2 = st.columns(2)
        l_zap = c_log1.text_input("WhatsApp", key="login_u")
        l_pas = c_log1.text_input("Senha", type="password", key="login_p")
        if c_log1.button("Acessar Painel"):
            uid = IAMestre.limpar_id(l_zap)
            doc = db.collection("profissionais").document(uid).get()
            if doc.exists and str(doc.to_dict().get('senha')) == l_pas:
                st.session_state.auth = True
                st.session_state.u_id = uid
                st.session_state.u_nome = doc.to_dict().get('nome')
                st.rerun()
    else:
        st.header(f"Bem-vindo, {st.session_state.u_nome}!")
        
        # --- FUNÇÃO DE POSTAGEM (REDE SOCIAL) ---
        with st.container(border=True):
            st.subheader("📸 Poste um novo Trabalho")
            nova_foto = st.file_uploader("Foto do Serviço Realizado", type=['jpg', 'jpeg', 'png'])
            legenda_post = st.text_area("Descreva o que foi feito (ex: Pintura finalizada no centro)")
            
            if st.button("🚀 PUBLICAR NO FEED"):
                if nova_foto and legenda_post:
                    with st.spinner("IA processando post..."):
                        img_b64 = IAMestre.otimizar_imagem(nova_foto)
                        dados_post = {
                            "zap_prof": st.session_state.u_id,
                            "nome_prof": st.session_state.u_nome,
                            "foto": img_b64,
                            "legenda": legenda_post,
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                        }
                        db.collection("postagens").add(dados_post)
                        st.success("🔥 Postado com sucesso! Seus clientes já podem ver.")
                        time.sleep(1)
                        st.rerun()

        if st.button("🚪 Sair"):
            st.session_state.auth = False
            st.rerun()

# ------------------------------------------------------------------------------
# ABA 4: ADMIN
# ------------------------------------------------------------------------------
with menu[3]:
    adm_pass = st.text_input("Chave Mestra", type="password")
    if adm_pass == "admin123":
        st.write("### Painel Administrativo GeralJá")
        # Aqui você pode adicionar funções de controle de usuários

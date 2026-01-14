import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64, json, math, re, time, io
from datetime import datetime
from PIL import Image

# Tenta importar o componente de localização
try:
    from streamlit_js_eval import get_geolocation
except:
    pass

# --- CONFIGURAÇÃO E CONEXÃO ---
st.set_page_config(page_title="GeralJá IA", layout="wide", page_icon="🚀")

# [IMPORTANTE] Localização no topo para estabilidade
loc = get_geolocation()

if not firebase_admin._apps:
    try:
        cred_info = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
    except:
        st.error("Erro nos Secrets! Verifique o 'textkey'.")

db = firestore.client()

# --- MOTOR IA MESTRE ---
class IAMestre:
    @staticmethod
    def otimizar_imagem(file):
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
    def renderizar_post(foto_b64, legenda, nome_prof, data, zap, post_id):
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
        if st.button(f"💬 Orçamento com {nome_prof}", key=f"btn_{post_id}"):
            st.link_button("Abrir Conversa", f"https://wa.me/55{zap}")

# --- INTERFACE ---
menu = st.tabs(["📱 FEED SOCIAL", "🔍 BUSCA GPS", "📢 CADASTRAR", "👤 MEU PERFIL", "⚙️ ADMIN"])

with menu[0]:
    st.subheader("🔥 Mural de Realizações")
    posts = db.collection("postagens").order_by("data", direction=firestore.Query.DESCENDING).limit(15).stream()
    col1, col2 = st.columns(2)
    for i, p in enumerate(posts):
        d = p.to_dict()
        with (col1 if i % 2 == 0 else col2):
            IAMestre.renderizar_post(d['foto'], d['legenda'], d['nome_prof'], d['data'], d['zap_prof'], p.id)

with menu[1]:
    st.subheader("📍 Profissionais Perto")
    if loc:
        lat_c, lon_c = loc['coords']['latitude'], loc['coords']['longitude']
        profs = db.collection("profissionais").stream()
        for p in profs:
            d = p.to_dict()
            dist = IAMestre.calc_distancia(lat_c, lon_c, d.get('lat'), d.get('lon'))
            if dist < 50:
                with st.container(border=True):
                    st.write(f"**{d['nome']}** - {d['area']} (a {dist:.1f} km)")
                    st.link_button("Chamar no Zap", f"https://wa.me/55{d['telefone']}")
    else: st.warning("Ative o GPS.")

with menu[2]:
    with st.form("cad_pro"):
        st.subheader("🚀 Criar Conta")
        c1, c2 = st.columns(2)
        n_nome = c1.text_input("Nome")
        n_zap = c1.text_input("WhatsApp")
        n_pass = c2.text_input("Senha", type="password")
        n_area = c2.selectbox("Área", ["Pintor", "Eletricista", "Encanador", "Limpeza"])
        if st.form_submit_button("CADASTRAR"):
            uid = IAMestre.limpar_id(n_zap)
            if loc and uid:
                db.collection("profissionais").document(uid).set({
                    "nome": n_nome, "telefone": uid, "senha": n_pass, "area": n_area,
                    "lat": loc['coords']['latitude'], "lon": loc['coords']['longitude'], "saldo": 0
                })
                st.success("Sucesso!")

with menu[3]:
    if 'auth' not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        l_zap = st.text_input("Zap")
        l_pas = st.text_input("Senha", type="password")
        if st.button("ACESSAR"):
            uid = IAMestre.limpar_id(l_zap)
            doc = db.collection("profissionais").document(uid).get()
            if doc.exists and str(doc.to_dict().get('senha')) == l_pas:
                st.session_state.auth, st.session_state.u_id = True, uid
                st.session_state.u_nome = doc.to_dict().get('nome')
                st.rerun()
    else:
        st.write(f"Olá, {st.session_state.u_nome}")
        with st.expander("📸 NOVO POST"):
            f = st.file_uploader("Foto")
            l = st.text_area("Legenda")
            if st.button("Publicar"):
                img_b64 = IAMestre.otimizar_imagem(f)
                db.collection("postagens").add({
                    "zap_prof": st.session_state.u_id, "nome_prof": st.session_state.u_nome,
                    "foto": img_b64, "legenda": l, "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                st.success("Postado!")
                time.sleep(1); st.rerun()

with menu[4]:
    if st.text_input("Admin", type="password") == "admin123":
        st.write("Acesso Liberado.")

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64, json, math, re, time, io
from datetime import datetime
from PIL import Image

# --- CONFIGURAÇÃO E GPS ---
st.set_page_config(page_title="GeralJá v2", page_icon="🚀", layout="wide")

try:
    from streamlit_js_eval import get_geolocation
    loc = get_geolocation()
except:
    loc = None

# --- CONEXÃO FIREBASE (VIA BASE64) ---
if not firebase_admin._apps:
    try:
        encoded_json = st.secrets["FIREBASE_BASE64"]
        decoded_json = base64.b64decode(encoded_json).decode("utf-8")
        cred = credentials.Certificate(json.loads(decoded_json))
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        st.stop()

db = firestore.client()

# --- MOTOR IA MESTRE ---
class IAMestre:
    @staticmethod
    def otimizar_foto(file):
        img = Image.open(file)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.thumbnail((800, 800))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60)
        return base64.b64encode(buf.getvalue()).decode()

    @staticmethod
    def calc_distancia(lat1, lon1, lat2, lon2):
        if not all([lat1, lon1, lat2, lon2]): return 999
        R = 6371 
        dLat, dLon = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# --- INTERFACE ---
st.title("🚀 GeralJá - Mural & Busca")

menu = st.tabs(["🔥 FEED & BUSCA", "📢 CADASTRAR", "👤 MEU PERFIL", "⚙️ ADMIN"])

# --- ABA 1: FEED & BUSCA ---
with menu[0]:
    st.subheader("Profissionais e Trabalhos")
    busca = st.text_input("Filtrar por serviço (ex: Pintor, Eletricista)", "")
    
    if loc:
        lat_u, lon_u = loc['coords']['latitude'], loc['coords']['longitude']
        profs = db.collection("profissionais").stream()
        lista = []
        for p in profs:
            d = p.to_dict()
            d['id'] = p.id
            d['dist'] = IAMestre.calc_distancia(lat_u, lon_u, d.get('lat'), d.get('lon'))
            if busca.lower() in d.get('area', '').lower() or busca == "":
                lista.append(d)
        
        # Ranking: Saldo maior aparece primeiro, depois menor distância
        lista = sorted(lista, key=lambda x: (x.get('saldo', 0), -x['dist']), reverse=True)

        for p in lista:
            with st.container(border=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    # Busca último post desse profissional
                    posts = db.collection("postagens").where("zap_prof", "==", p['id']).order_by("data", direction=firestore.Query.DESCENDING).limit(1).get()
                    if posts:
                        st.image(f"data:image/jpeg;base64,{posts[0].to_dict()['foto']}", use_container_width=True)
                    else:
                        st.write("📸 *Sem fotos postadas*")
                with col2:
                    st.markdown(f"### {p['nome']}")
                    st.write(f"💼 **Área:** {p.get('area', 'Geral')}")
                    st.write(f"📍 **Distância:** {p['dist']:.1f} km")
                    st.link_button("Chamar no WhatsApp", f"https://wa.me/55{p['telefone']}")

# --- ABA 2: CADASTRAR ---
with menu[1]:
    with st.form("cad_form"):
        st.write("### Criar Conta Comercial")
        n = st.text_input("Nome Profissional/Empresa")
        z = st.text_input("WhatsApp (só números)")
        a = st.selectbox("Especialidade", ["Pintor", "Eletricista", "Encanador", "Limpeza", "Mecânico", "Pedreiro"])
        s = st.text_input("Senha", type="password")
        if st.form_submit_button("CADASTRAR"):
            if loc and n and z:
                uid = re.sub(r'\D', '', z)
                db.collection("profissionais").document(uid).set({
                    "nome": n, "telefone": uid, "area": a, "senha": s,
                    "lat": loc['coords']['latitude'], "lon": loc['coords']['longitude'], "saldo": 0
                })
                st.success("✅ Cadastrado! Vá em 'Meu Perfil' para postar fotos.")
            else: st.warning("Ative o GPS para cadastrar.")

# --- ABA 3: MEU PERFIL (POSTAGEM) ---
with menu[2]:
    if 'auth' not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        z_log = st.text_input("Seu WhatsApp")
        s_log = st.text_input("Sua Senha", type="password")
        if st.button("Acessar Painel"):
            uid = re.sub(r'\D', '', z_log)
            doc = db.collection("profissionais").document(uid).get()
            if doc.exists and str(doc.to_dict().get('senha')) == s_log:
                st.session_state.auth, st.session_state.u_id = True, uid
                st.session_state.u_nome = doc.to_dict().get('nome')
                st.rerun()
    else:
        st.write(f"Olá, {st.session_state.u_nome}!")
        with st.expander("📸 PUBLICAR NOVO TRABALHO"):
            f = st.file_uploader("Escolha a foto")
            t = st.text_area("Descrição do que foi feito")
            if st.button("PUBLICAR"):
                if f and t:
                    b64 = IAMestre.otimizar_foto(f)
                    db.collection("postagens").add({
                        "zap_prof": st.session_state.u_id, "nome_prof": st.session_state.u_nome,
                        "foto": b64, "legenda": t, "data": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    st.success("Postado com sucesso!")
                    time.sleep(1); st.rerun()
        if st.button("Sair"): st.session_state.auth = False; st.rerun()

# --- ABA 4: ADMIN ---
with menu[3]:
    if st.text_input("Chave Mestra", type="password") == "admin123":
        st.write("Painel Administrativo")
        profs = db.collection("profissionais").stream()
        for p_doc in profs:
            pd = p_doc.to_dict()
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{pd['nome']}** (Saldo: {pd.get('saldo', 0)})")
            if c2.button("➕ SALDO", key=p_doc.id):
                db.collection("profissionais").document(p_doc.id).update({"saldo": pd.get('saldo', 0) + 10})
                st.rerun()

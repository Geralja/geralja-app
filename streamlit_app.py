import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64, json, math, re, time, io
from datetime import datetime
from PIL import Image

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÃO E GPS (Início do Arquivo)
# ------------------------------------------------------------------------------
st.set_page_config(page_title="GeralJá v2", page_icon="🚀", layout="wide")

try:
    from streamlit_js_eval import get_geolocation
    loc = get_geolocation()
except:
    loc = None

# ------------------------------------------------------------------------------
# 2. CONEXÃO FIREBASE (Método Base64 da sua v1)
# ------------------------------------------------------------------------------
if not firebase_admin._apps:
    try:
        encoded_json = st.secrets["FIREBASE_BASE64"]
        decoded_json = base64.b64decode(encoded_json).decode("utf-8")
        cred_dict = json.loads(decoded_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro na conexão Firebase: {e}")
        st.stop()

db = firestore.client()

# ------------------------------------------------------------------------------
# 3. MOTOR IA MESTRE (Processamento)
# ------------------------------------------------------------------------------
class IAMestre:
    @staticmethod
    def otimizar_imagem(file):
        """ Reduz o peso da foto para o app voar """
        img = Image.open(file)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.thumbnail((800, 800))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=60)
        return base64.b64encode(buffer.getvalue()).decode()

    @staticmethod
    def calc_distancia(lat1, lon1, lat2, lon2):
        if not all([lat1, lon1, lat2, lon2]): return 999
        R = 6371 
        dLat, dLon = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# ------------------------------------------------------------------------------
# 4. INTERFACE PRINCIPAL
# ------------------------------------------------------------------------------
st.title("🚀 GeralJá v2 - Rede Social de Serviços")

abas = st.tabs(["🔥 FEED & BUSCA", "📢 CADASTRAR", "👤 MEU PAINEL", "⚙️ ADMIN"])

# --- ABA 1: FEED E BUSCA (A Grande Novidade) ---
with abas[0]:
    st.subheader("Trabalhos e Profissionais")
    
    # Filtro de Busca Rápida
    busca = st.text_input("O que você procura? (Ex: Pintor, Limpeza)", placeholder="Busque por área...")
    
    if loc:
        lat_u, lon_u = loc['coords']['latitude'], loc['coords']['longitude']
        
        # Puxa profissionais e posts
        profs = db.collection("profissionais").stream()
        lista_profs = []
        for p in profs:
            d = p.to_dict()
            d['id'] = p.id
            d['dist'] = IAMestre.calc_distancia(lat_u, lon_u, d.get('lat'), d.get('lon'))
            if busca.lower() in d.get('area', '').lower() or busca == "":
                lista_profs.append(d)
        
        # Ordena por saldo (quem paga aparece antes) e distância
        lista_profs = sorted(lista_profs, key=lambda x: (x.get('saldo', 0), -x['dist']), reverse=True)

        for p in lista_profs:
            with st.container(border=True):
                c1, c2 = st.columns([1, 3])
                with c1:
                    # Tenta pegar o último post desse profissional
                    post = db.collection("postagens").where("zap_prof", "==", p['id']).order_by("data", direction=firestore.Query.DESCENDING).limit(1).get()
                    if post:
                        st.image(f"data:image/jpeg;base64,{post[0].to_dict()['foto']}", use_container_width=True)
                    else:
                        st.write("📸 Sem foto recente")
                with c2:
                    st.write(f"### {p['nome']}")
                    st.write(f"📍 A **{p['dist']:.1f} km** | ⭐ {p.get('area', 'Geral')}")
                    st.link_button(f"Falar no WhatsApp", f"https://wa.me/55{p['telefone']}")

# --- ABA 2: CADASTRAR ---
with abas[1]:
    with st.form("registro"):
        st.subheader("Entrar para o Time GeralJá")
        n = st.text_input("Nome Profissional")
        z = st.text_input("WhatsApp (só números)")
        a = st.selectbox("Especialidade", ["Pintor", "Eletricista", "Encanador", "Limpeza", "Mecânico", "Outros"])
        s = st.text_input("Senha de Acesso", type="password")
        if st.form_submit_button("CADASTRAR AGORA"):
            if loc and n and z:
                uid = re.sub(r'\D', '', z)
                db.collection("profissionais").document(uid).set({
                    "nome": n, "telefone": uid, "area": a, "senha": s,
                    "lat": loc['coords']['latitude'], "lon": loc['coords']['longitude'], "saldo": 0
                })
                st.success("✅ Conta criada! Faça login no seu painel.")
            else:
                st.warning("⚠️ Ative o GPS para concluir o cadastro.")

# --- ABA 3: MEU PAINEL (Onde a mágica acontece) ---
with abas[2]:
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.subheader("Acesse seu Perfil")
        l_z = st.text_input("WhatsApp", key="l_z")
        l_s = st.text_input("Senha", type="password", key="l_s")
        if st.button("LOGAR"):
            uid = re.sub(r'\D', '', l_z)
            doc = db.collection("profissionais").document(uid).get()
            if doc.exists and str(doc.to_dict().get('senha')) == l_s:
                st.session_state.auth, st.session_state.u_id = True, uid
                st.session_state.u_nome = doc.to_dict().get('nome')
                st.rerun()
            else: st.error("Dados incorretos!")
    else:
        st.write(f"### Olá, {st.session_state.u_nome}!")
        with st.expander("📸 POSTAR FOTO DO SEU TRABALHO"):
            img = st.file_uploader("Escolha a foto")
            txt = st.text_area("Legenda do serviço")
            if st.button("PUBLICAR NO MURAL"):
                if img and txt:
                    b64 = IAMestre.otimizar_imagem(img)
                    db.collection("postagens").add({
                        "zap_prof": st.session_state.u_id, "nome_prof": st.session_state.u_nome,
                        "foto": b64, "legenda": txt, "data": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    st.success("🔥 Postado!")
                    time.sleep(1); st.rerun()
        if st.button("Sair"):
            st.session_state.auth = False; st.rerun()

# --- ABA 4: ADMIN ---
with abas[3]:
    if st.text_input("Chave Admin", type="password") == "admin123":
        st.subheader("Gestão de Saldo")
        ps = db.collection("profissionais").stream()
        for p_doc in ps:
            pd = p_doc.to_dict()
            col1, col2 = st.columns([2, 1])
            col1.write(f"{pd['nome']} (Saldo: {pd.get('saldo', 0)})")
            if col2.button("➕ 10", key=p_doc.id):
                db.collection("profissionais").document(p_doc.id).update({"saldo": pd.get('saldo', 0) + 10})
                st.rerun()

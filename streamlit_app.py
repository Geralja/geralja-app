import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import re
import time
import json
import math
from PIL import Image
import io

# Tenta importar o GPS, se falhar, o app avisa
try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    pass

# ==============================================================================
# 1. MOTOR IA MESTRE (Otimização de Fotos e IDs)
# ==============================================================================
class IAMestre:
    @staticmethod
    def otimizar_imagem(file):
        """Reduz a foto para não travar o banco de dados (Max 1MB)"""
        if file is None: return None
        try:
            img = Image.open(file)
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.thumbnail((700, 700)) # Resolução ideal
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=60, optimize=True)
            return base64.b64encode(buffer.getvalue()).decode()
        except: return None

    @staticmethod
    def limpar_id(texto):
        return re.sub(r'\D', '', str(texto or ""))

    @staticmethod
    def calc_distancia(lat1, lon1, lat2, lon2):
        """Cálculo de distância em KM"""
        if not all([lat1, lon1, lat2, lon2]): return 999
        R = 6371 
        dLat, dLon = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# ==============================================================================
# 2. CONEXÃO FIREBASE (Protegida por Secrets)
# ==============================================================================
st.set_page_config(page_title="GeralJá v2.0", layout="wide", page_icon="🚀")

if not firebase_admin._apps:
    try:
        cred_info = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error("⚠️ Configure o 'textkey' nos Secrets do Streamlit.")

db = firestore.client()

# ==============================================================================
# 3. INTERFACE EM ABAS
# ==============================================================================
st.title("🚀 GeralJá - Inteligência em Serviços")
abas = st.tabs(["🔍 BUSCAR", "📢 CADASTRAR", "👤 MEU PERFIL", "⚙️ ADMIN"])

# --- ABA 1: BUSCAR ---
with abas[0]:
    st.subheader("Encontre Profissionais")
    loc_cliente = get_geolocation() # Pede GPS do cliente
    
    col_b1, col_b2 = st.columns([3, 1])
    busca_term = col_b1.text_input("O que você procura?", placeholder="Ex: Eletricista...")
    raio_km = col_b2.slider("Raio (KM)", 1, 100, 20)

    if loc_cliente:
        lat_c, lon_c = loc_cliente['coords']['latitude'], loc_cliente['coords']['longitude']
        profs = db.collection("profissionais").stream()
        lista_rank = []

        for p in profs:
            d = p.to_dict()
            dist = IAMestre.calc_distancia(lat_c, lon_c, d.get('lat'), d.get('lon'))
            if dist <= raio_km:
                d['dist_p'] = round(dist, 1)
                # Ranking: Saldo (Moedas) faz subir, Distância faz descer
                d['score'] = (d.get('saldo', 0) * 10) - dist
                lista_rank.append(d)

        lista_rank = sorted(lista_rank, key=lambda x: x['score'], reverse=True)

        for item in lista_rank:
            with st.container(border=True):
                c1, c2 = st.columns([1, 4])
                with c1:
                    if item.get('f1'): st.image(f"data:image/jpeg;base64,{item['f1']}")
                with c2:
                    st.write(f"### {item['nome']}")
                    st.caption(f"📍 {item['dist_p']} km de você • {item['area']}")
                    st.write(item.get('descricao', '')[:150])
                    st.link_button(f"Falar com {item['nome']}", f"https://wa.me/55{item['telefone']}")
    else:
        st.info("📍 Por favor, ative o GPS para ver quem está perto de você.")

# --- ABA 2: CADASTRAR (4 FOTOS + GPS) ---
with abas[1]:
    st.subheader("Criar seu Perfil Profissional")
    loc_cad = get_geolocation() # Pede GPS do profissional
    
    with st.form("cad_prof"):
        c1, c2 = st.columns(2)
        n_nome = c1.text_input("Nome/Empresa")
        n_zap = c1.text_input("WhatsApp")
        n_area = c2.selectbox("Área", ["Eletricista", "Encanador", "Limpeza", "Outros"])
        n_pass = c2.text_input("Senha", type="password")
        n_desc = st.text_area("Sua Descrição")
        
        st.write("📷 **Fotos da sua Vitrine**")
        f_c1, f_c2 = st.columns(2)
        u1 = f_c1.file_uploader("Foto 1", type=['jpg','png'])
        u2 = f_c1.file_uploader("Foto 2", type=['jpg','png'])
        u3 = f_c2.file_uploader("Foto 3", type=['jpg','png'])
        u4 = f_c2.file_uploader("Foto 4", type=['jpg','png'])

        if st.form_submit_button("CRIAR VITRINE"):
            uid = IAMestre.limpar_id(n_zap)
            if not loc_cad: st.error("Erro: GPS desligado!")
            elif not uid or not n_pass: st.warning("Preencha WhatsApp e Senha!")
            else:
                with st.spinner("IA Mestre salvando..."):
                    dados = {
                        "nome": n_nome, "telefone": uid, "area": n_area, "senha": n_pass,
                        "descricao": n_desc, "saldo": 0,
                        "lat": loc_cad['coords']['latitude'], "lon": loc_cad['coords']['longitude'],
                        "f1": IAMestre.otimizar_imagem(u1), "f2": IAMestre.otimizar_imagem(u2),
                        "f3": IAMestre.otimizar_imagem(u3), "f4": IAMestre.otimizar_imagem(u4),
                    }
                    db.collection("profissionais").document(uid).set(dados)
                    st.success("✅ Cadastrado com sucesso!")

# --- ABA 3 E 4 (LOGS E ADMIN) ---
with abas[2]: # Perfil
    st.write("Em breve: Painel de Edição")

with abas[3]: # Admin
    adm_pw = st.text_input("Admin", type="password")
    if adm_pw == "admin123":
        st.write("Controle de Moedas Ativo")

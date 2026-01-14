import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import math
import re
import time
from PIL import Image
import io

# --- TENTA IMPORTAR GPS (Requisito para Turbinar) ---
try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    pass

# ==============================================================================
# 1. MOTOR IA MESTRE (Otimização de Imagem e Dados)
# ==============================================================================
class IAMestre:
    @staticmethod
    def otimizar_imagem(file):
        """Turbina o carregamento: reduz fotos para JPEG leve e alta qualidade"""
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
    def limpar_id(texto):
        return re.sub(r'\D', '', str(texto or ""))

    @staticmethod
    def calcular_distancia(lat1, lon1, lat2, lon2):
        """Cálculo matemático real de proximidade"""
        if not all([lat1, lon1, lat2, lon2]): return 999
        R = 6371 # Raio da Terra em KM
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# ==============================================================================
# 2. CONEXÃO FIREBASE E CONFIGURAÇÕES
# ==============================================================================
st.set_page_config(page_title="GeralJá IA", layout="wide", page_icon="🇧🇷")

if not firebase_admin._apps:
    try:
        cred_info = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error("⚠️ Conecte o Firebase nos Secrets.")

db = firestore.client()
CATEGORIAS = ["Eletricista", "Encanador", "Diarista", "Pintor", "Mecânico", "Pedreiro", "Outros"]

# ==============================================================================
# 3. INTERFACE PRINCIPAL (TURBINADA)
# ==============================================================================
st.title("🚀 GeralJá - Criando Soluções")
menu = st.tabs(["🔍 BUSCAR", "📢 CADASTRAR", "👤 MEU PERFIL", "⚙️ ADMIN"])

# ------------------------------------------------------------------------------
# ABA 1: BUSCAR (Inteligência por GPS e Saldo)
# ------------------------------------------------------------------------------
with menu[0]:
    st.markdown("### 🔍 Profissionais Perto de Você")
    loc_cliente = get_geolocation() if 'streamlit_js_eval' in globals() else None
    
    col_s1, col_s2 = st.columns([3, 1])
    busca = col_s1.text_input("O que você precisa?", placeholder="Ex: Pintor rápido...")
    raio = col_s2.slider("Raio (km)", 1, 100, 15)

    if loc_cliente:
        lat_c = loc_cliente['coords']['latitude']
        lon_c = loc_cliente['coords']['longitude']
        
        # Busca no Banco
        profs = db.collection("profissionais").stream()
        lista_ranking = []

        for p in profs:
            d = p.to_dict()
            dist = IAMestre.calcular_distancia(lat_c, lon_c, d.get('lat'), d.get('lon'))
            
            if dist <= raio:
                d['dist_real'] = round(dist, 1)
                # O PULO DO GATO: Score = (Saldo * 5) - (Distância)
                # Isso faz quem paga aparecer no topo, mas prioriza quem está perto
                d['score'] = (d.get('saldo', 0) * 5) - dist
                lista_ranking.append(d)

        lista_ranking = sorted(lista_ranking, key=lambda x: x['score'], reverse=True)

        for item in lista_ranking:
            with st.container(border=True):
                c_img, c_txt = st.columns([1, 4])
                with c_img:
                    if item.get('f1'):
                        st.image(f"data:image/jpeg;base64,{item['f1']}", use_container_width=True)
                with c_txt:
                    st.subheader(f"{item['nome']}")
                    st.caption(f"📍 {item['dist_real']} km de distância • {item['area']}")
                    st.write(item.get('descricao', '')[:120] + "...")
                    if st.button(f"Falar com {item['nome']}", key=f"chat_{item['telefone']}"):
                        # Incrementa clique e abre zap
                        db.collection("profissionais").document(item['telefone']).update({"cliques": firestore.Increment(1)})
                        st.markdown(f'<meta http-equiv="refresh" content="0;URL=https://wa.me/55{item["telefone"]}">', unsafe_allow_html=True)
    else:
        st.warning("📍 Ative o GPS para ver os melhores profissionais da sua região.")

# ------------------------------------------------------------------------------
# ABA 2: CADASTRAR (Captura GPS e 4 Fotos)
# ------------------------------------------------------------------------------
with menu[1]:
    st.subheader("📢 Divulgue seu trabalho")
    st.info("📍 Sua localização será capturada para clientes te acharem.")
    loc_cad = get_geolocation()
    
    with st.form("form_novo_parceiro"):
        c1, c2 = st.columns(2)
        n_nome = c1.text_input("Nome/Empresa")
        n_zap = c1.text_input("WhatsApp (Seu Login)")
        n_area = c2.selectbox("Especialidade", CATEGORIAS)
        n_pass = c2.text_input("Crie uma Senha", type="password")
        n_desc = st.text_area("Descrição do seu Serviço")
        
        st.write("📸 **Sua Vitrine (Até 4 fotos)**")
        fc1, fc2 = st.columns(2)
        up1 = fc1.file_uploader("Foto 1 (Destaque)", type=['jpg','png','jpeg'])
        up2 = fc1.file_uploader("Foto 2", type=['jpg','png','jpeg'])
        up3 = fc2.file_uploader("Foto 3", type=['jpg','png','jpeg'])
        up4 = fc2.file_uploader("Foto 4", type=['jpg','png','jpeg'])
        
        if st.form_submit_button("🚀 CRIAR MINHA VITRINE"):
            uid = IAMestre.limpar_id(n_zap)
            if not loc_cad: st.error("Ative o GPS para cadastrar!")
            elif not uid or not n_pass: st.warning("WhatsApp e Senha obrigatórios!")
            else:
                with st.spinner("IA Mestre processando fotos..."):
                    dados = {
                        "nome": n_nome.upper(),
                        "telefone": uid,
                        "area": n_area,
                        "senha": n_pass,
                        "descricao": n_desc,
                        "lat": loc_cad['coords']['latitude'],
                        "lon": loc_cad['coords']['longitude'],
                        "saldo": 0, "cliques": 0,
                        "f1": IAMestre.otimizar_imagem(up1), "f2": IAMestre.otimizar_imagem(up2),
                        "f3": IAMestre.otimizar_imagem(up3), "f4": IAMestre.otimizar_imagem(up4),
                    }
                    db.collection("profissionais").document(uid).set(dados)
                    st.success("✅ Perfil criado! Faça login na aba 'Meu Perfil'.")

# ------------------------------------------------------------------------------
# ABA 3: MEU PERFIL (Visualização e Edição)
# ------------------------------------------------------------------------------
with menu[2]:
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        with st.container(border=True):
            st.subheader("🔑 Login do Parceiro")
            l_zap = st.text_input("WhatsApp", key="l_zap")
            l_pw = st.text_input("Senha", type="password", key="l_pw")
            if st.button("ENTRAR"):
                u_id = IAMestre.limpar_id(l_zap)
                doc = db.collection("profissionais").document(u_id).get()
                if doc.exists and str(doc.to_dict().get('senha')) == l_pw:
                    st.session_state.auth = True
                    st.session_state.u_id = u_id
                    st.rerun()
                else: st.error("Acesso Negado.")
    else:
        # Área Logada
        d = db.collection("profissionais").document(st.session_state.u_id).get().to_dict()
        st.header(f"Olá, {d.get('nome')}!")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Meu Saldo", f"{d.get('saldo')} 🪙")
        col_m2.metric("Cliques Recebidos", d.get('cliques'))
        col_m3.metric("Status", "Ativo")

        if st.button("🚪 SAIR"):
            st.session_state.auth = False
            st.rerun()

# ------------------------------------------------------------------------------
# ABA 4: ADMIN (Controle Geral)
# ------------------------------------------------------------------------------
with menu[3]:
    st.subheader("⚙️ Painel de Controle")
    adm_pw = st.text_input("Chave Mestra", type="password")
    if adm_pw == "admin123":
        profs_all = db.collection("profissionais").stream()
        for p in profs_all:
            dados_p = p.to_dict()
            with st.expander(f"{dados_p.get('nome')} - {dados_p.get('saldo')} 🪙"):
                if st.button(f"Dar 50 Moedas para {dados_p.get('nome')}", key=f"coin_{dados_p.get('telefone')}"):
                    db.collection("profissionais").document(dados_p.get('telefone')).update({"saldo": firestore.Increment(50)})
                    st.rerun()

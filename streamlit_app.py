import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64, json, math, re, time, io
from datetime import datetime
from PIL import Image
import requests  # Faltava este!
# ... outros imports ...

PIX_OFICIAL = "11991853488"
BONUS_WELCOME = 50 # Faltava este!
# ... restante das constantes ...
# ==============================================================================
# 1. CONFIGURAÇÃO DE AMBIENTE (Baseado na sua v1)
# ==============================================================================
st.set_page_config(
    page_title="GeralJá | Criando Soluções",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Tenta capturar GPS (streamlit-js-eval)
try:
    from streamlit_js_eval import get_geolocation
    loc = get_geolocation()
except:
    loc = None

# ==============================================================================
# 2. CONEXÃO FIREBASE (Método Base64 que funciona no seu link)
# ==============================================================================
if not firebase_admin._apps:
    try:
        encoded_json = st.secrets["FIREBASE_BASE64"]
        decoded_json = base64.b64decode(encoded_json).decode("utf-8")
        cred_dict = json.loads(decoded_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro de conexão Firebase: {e}")
        st.stop()

db = firestore.client()

# ==============================================================================
# 3. MOTOR DE INTELIGÊNCIA E UTILITÁRIOS
# ==============================================================================
class GeralJaEngine:
    @staticmethod
    def otimizar_foto(file):
        """ Compacta a imagem para não estourar o banco de dados """
        img = Image.open(file)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.thumbnail((800, 800))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60)
        return base64.b64encode(buf.getvalue()).decode()

    @staticmethod
    def calcular_distancia(lat1, lon1, lat2, lon2):
        """ Cálculo de Haversine para proximidade """
        if not all([lat1, lon1, lat2, lon2]): return 999
        R = 6371 
        dLat, dLon = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# ==============================================================================
# 4. INTERFACE PRINCIPAL (SISTEMA DE ABAS)
# ==============================================================================
st.title("🚀 GeralJá v2.0")

menu = st.tabs(["🔥 FEED & BUSCA", "📢 CADASTRAR", "👤 MEU PERFIL", "⚙️ ADMIN", "⭐ FEEDBACK"])

# --- ABA 1: FEED & BUSCA ---
with menu[0]:
    st.subheader("Encontre Profissionais e Veja Trabalhos")
    busca_termo = st.text_input("🔍 O que você precisa?", placeholder="Ex: Pintor, Elétrica, Limpeza...")
    
    if loc:
        u_lat = loc['coords']['latitude']
        u_lon = loc['coords']['longitude']
        
        # Puxa profissionais
        profs_ref = db.collection("profissionais").stream()
        lista_final = []
        
        for p in profs_ref:
            dados = p.to_dict()
            dados['id'] = p.id
            dados['distancia'] = GeralJaEngine.calcular_distancia(u_lat, u_lon, dados.get('lat'), dados.get('lon'))
            
            # Filtro de busca
            if busca_termo.lower() in dados.get('area', '').lower() or busca_termo.lower() in dados.get('nome', '').lower() or busca_termo == "":
                lista_final.append(dados)
        
        # RANKING: 1º Saldo (Destaque Pago), 2º Menor Distância
        lista_final = sorted(lista_final, key=lambda x: (x.get('saldo', 0), -x['distancia']), reverse=True)

        for prof in lista_final:
            with st.container(border=True):
                col_foto, col_info = st.columns([1, 2])
                
                with col_foto:
                    # BUSCA FOTO (Correção Anti-Erro de Índice)
                    posts_ref = db.collection("postagens").where("zap_prof", "==", prof['id']).limit(3).get()
                    if posts_ref:
                        # Ordena no Python para evitar erro de Index do Firebase
                        posts_ordenados = sorted([doc.to_dict() for doc in posts_ref], key=lambda x: x.get('data', ''), reverse=True)
                        st.image(f"data:image/jpeg;base64,{posts_ordenados[0]['foto']}", use_container_width=True)
                    else:
                        st.info("📸 Sem fotos")
                
                with col_info:
                    st.subheader(prof['nome'])
                    st.write(f"💼 **Especialidade:** {prof.get('area', 'Geral')}")
                    st.write(f"📍 **Distância:** {prof['distancia']:.1f} km")
                    if prof.get('saldo', 0) > 0:
                        st.caption("⭐ PROFISSIONAL EM DESTAQUE")
                    st.link_button(f"Falar com {prof['nome']}", f"https://wa.me/55{prof['telefone']}")

    else:
        st.warning("📍 Por favor, autorize o GPS para ver os profissionais próximos.")

# --- ABA 2: CADASTRAR ---
with menu[1]:
    st.header("Anuncie seus Serviços")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome ou Nome da Empresa")
        whats = st.text_input("WhatsApp (com DDD, apenas números)")
        area = st.selectbox("Sua Área Principal", ["Pintor", "Eletricista", "Encanador", "Limpeza", "Mecânico", "Pedreiro", "Outros"])
        senha = st.text_input("Crie uma Senha", type="password")
        
        if st.form_submit_button("CRIAR MEU PERFIL"):
            if loc and nome and whats:
                uid = re.sub(r'\D', '', whats)
                db.collection("profissionais").document(uid).set({
                    "nome": nome, "telefone": uid, "area": area, "senha": senha,
                    "lat": loc['coords']['latitude'], "lon": loc['coords']['longitude'], "saldo": 0
                })
                st.success("✅ Perfil criado! Agora faça login em 'Meu Perfil' para postar fotos.")
            else:
                st.error("⚠️ Erro: Nome e WhatsApp são obrigatórios e o GPS deve estar ativo.")

# --- ABA 3: MEU PERFIL (SISTEMA DE POSTAGEM) ---
with menu[2]:
    if 'logado' not in st.session_state: st.session_state.logado = False
    
    if not st.session_state.logado:
        st.subheader("Acesso ao Painel")
        login_z = st.text_input("Seu WhatsApp cadastrado")
        login_s = st.text_input("Sua Senha", type="password")
        if st.button("ENTRAR"):
            uid = re.sub(r'\D', '', login_z)
            doc_p = db.collection("profissionais").document(uid).get()
            if doc_p.exists and str(doc_p.to_dict().get('senha')) == login_s:
                st.session_state.logado = True
                st.session_state.u_id = uid
                st.session_state.u_nome = doc_p.to_dict().get('nome')
                st.rerun()
            else:
                st.error("WhatsApp ou Senha incorretos.")
    else:
        st.write(f"### Bem-vindo, {st.session_state.u_nome}!")
        with st.expander("📸 POSTAR NOVO TRABALHO (MURAL)"):
            arquivo = st.file_uploader("Selecione uma foto do seu serviço", type=['jpg','png','jpeg'])
            texto = st.text_area("Descreva o que foi feito nesse trabalho")
            if st.button("PUBLICAR NO FEED"):
                if arquivo and texto:
                    with st.spinner("Otimizando imagem..."):
                        img_b64 = GeralJaEngine.otimizar_foto(arquivo)
                        db.collection("postagens").add({
                            "zap_prof": st.session_state.u_id,
                            "nome_prof": st.session_state.u_nome,
                            "foto": img_b64,
                            "legenda": texto,
                            "data": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                    st.success("🔥 Trabalho publicado com sucesso!")
                    time.sleep(1)
                    st.rerun()
        
        if st.button("Sair do Painel"):
            st.session_state.logado = False
            st.rerun()

# --- ABA 4: ADMIN (CONTROLE DE SALDO) ---
with menu[3]:
    adm_key = st.text_input("Chave Mestra", type="password")
    if adm_key == "admin123":
        st.subheader("Gerenciar Destaques")
        profs_adm = db.collection("profissionais").stream()
        for p_adm in profs_adm:
            p_data = p_adm.to_dict()
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{p_data['nome']}** (Saldo: {p_data.get('saldo', 0)})")
            if c2.button("➕ ADICIONAR 10", key=f"add_{p_adm.id}"):
                db.collection("profissionais").document(p_adm.id).update({"saldo": p_data.get('saldo', 0) + 10})
                st.rerun()

# --- ABA 5: FEEDBACK ---
with menu[4]:
    st.write("Dúvidas ou sugestões? Envie para nós!")
    st.text_area("Sua mensagem")
    if st.button("Enviar"):
        st.toast("Mensagem enviada!")

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import re
import time
import json
from PIL import Image
import io

# ==============================================================================
# 1. FUNÇÕES IA MESTRE (Otimização e Segurança)
# ==============================================================================
class IAMestre:
    @staticmethod
    def otimizar_imagem(file):
        """Reduz a imagem para não estourar o limite de 1MB do Firestore"""
        if file is None: return None
        try:
            img = Image.open(file)
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.thumbnail((800, 800)) # Resolução ideal
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=60, optimize=True)
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            st.error(f"Erro na Imagem: {e}")
            return None

    @staticmethod
    def limpar_id(texto):
        return re.sub(r'\D', '', str(texto or ""))

# ==============================================================================
# 2. CONEXÃO FIREBASE (Protegida)
# ==============================================================================
if not firebase_admin._apps:
    try:
        # Puxa dos Secrets do Streamlit (Configurações > Secrets)
        # O nome da chave deve ser "textkey"
        cred_info = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error("⚠️ Erro de Conexão. Verifique os Secrets do Streamlit.")

db = firestore.client()

# ==============================================================================
# 3. INTERFACE E ABAS
# ==============================================================================
st.set_page_config(page_title="GeralJá IA", layout="wide", page_icon="🚀")
st.title("🚀 GeralJá - Versão Piloto")

# Estilo para os Cards
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6; border-radius: 10px 10px 0 0; padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)

abas = st.tabs(["🔍 BUSCAR", "📢 CADASTRAR", "👤 MEU PERFIL", "⚙️ ADMIN"])

# ------------------------------------------------------------------------------
# ABA: CADASTRAR (PILOTO COM 4 FOTOS)
# ------------------------------------------------------------------------------
with abas[1]:
    st.subheader("📝 Criar sua Vitrine de Profissional")
    with st.form("form_cadastro_ia"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Profissional/Empresa")
        zap = c1.text_input("WhatsApp (Seu login)")
        area = c2.selectbox("Especialidade", ["Eletricista", "Encanador", "Diarista", "Pintor", "Mecânico", "Outros"])
        senha = c2.text_input("Senha", type="password")
        
        desc = st.text_area("Descrição dos seus serviços")
        
        st.write("📸 **Portfólio (Até 4 fotos)**")
        f_col1, f_col2 = st.columns(2)
        u1 = f_col1.file_uploader("Foto 1 (Principal)", type=['jpg','png','jpeg'])
        u2 = f_col1.file_uploader("Foto 2", type=['jpg','png','jpeg'])
        u3 = f_col2.file_uploader("Foto 3", type=['jpg','png','jpeg'])
        u4 = f_col2.file_uploader("Foto 4", type=['jpg','png','jpeg'])

        if st.form_submit_button("🚀 FINALIZAR CADASTRO"):
            uid = IAMestre.limpar_id(zap)
            if not uid or not senha or not nome:
                st.warning("⚠️ Preencha Nome, WhatsApp e Senha!")
            else:
                with st.spinner("IA Mestre processando fotos e salvando..."):
                    dados = {
                        "nome": nome.upper(),
                        "telefone": uid,
                        "area": area,
                        "senha": senha,
                        "descricao": desc,
                        "saldo": 0,
                        "cliques": 0,
                        "f1": IAMestre.otimizar_imagem(u1),
                        "f2": IAMestre.otimizar_imagem(u2),
                        "f3": IAMestre.otimizar_imagem(u3),
                        "f4": IAMestre.otimizar_imagem(u4),
                        "data_criacao": firestore.SERVER_TIMESTAMP
                    }
                    db.collection("profissionais").document(uid).set(dados)
                    st.success(f"✅ Sucesso! Profissional {nome} cadastrado.")
                    st.balloons()

# Os outros blocos serão turbinados assim que o cadastro estiver OK

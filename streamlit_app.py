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
# 1. FUNÇÕES DE ELITE (IA MESTRE)
# ==============================================================================
class IAMestre:
    @staticmethod
    def otimizar_imagem(file):
        """Comprime a imagem para caber no limite de 1MB do Firestore"""
        if file is None: return None
        try:
            img = Image.open(file)
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.thumbnail((800, 800)) # Resolução ideal para mobile
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=60, optimize=True)
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            st.error(f"Erro IA Imagem: {e}")
            return None

    @staticmethod
    def limpar_id(texto):
        """Transforma WhatsApp em ID limpo"""
        return re.sub(r'\D', '', str(texto or ""))

# ==============================================================================
# 2. CONFIGURAÇÃO E CONEXÃO
# ==============================================================================
st.set_page_config(page_title="GeralJá IA", layout="wide", page_icon="🚀")

if not firebase_admin._apps:
    try:
        # Puxa dos Secrets do Streamlit
        cred_info = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")

db = firestore.client()

# ==============================================================================
# 3. ESTRUTURA DE ABAS
# ==============================================================================
st.title("🚀 GeralJá v2.0")
st.markdown("---")

abas = st.tabs(["🔍 BUSCAR", "📢 CADASTRAR", "👤 MEU PERFIL", "⚙️ ADMIN"])

# --- ABA: CADASTRAR (PILOTO) ---
with abas[1]:
    st.subheader("🚀 Junte-se ao time de Elite")
    with st.form("novo_cadastro"):
        col1, col2 = st.columns(2)
        c_nome = col1.text_input("Nome Profissional")
        c_zap = col1.text_input("WhatsApp (Será seu login)")
        c_area = col2.selectbox("Sua Especialidade", ["Eletricista", "Encanador", "Diarista", "Mecânico", "Outros"])
        c_senha = col2.text_input("Crie uma Senha", type="password")
        
        st.write("📸 **Suas Melhores Fotos (Máximo 4)**")
        f_col1, f_col2 = st.columns(2)
        up1 = f_col1.file_uploader("Foto Principal", type=['jpg','png','jpeg'])
        up2 = f_col1.file_uploader("Foto 2", type=['jpg','png','jpeg'])
        up3 = f_col2.file_uploader("Foto 3", type=['jpg','png','jpeg'])
        up4 = f_col2.file_uploader("Foto 4", type=['jpg','png','jpeg'])

        if st.form_submit_button("CRIAR MINHA VITRINE"):
            id_limpo = IAMestre.limpar_id(c_zap)
            if not id_limpo or not c_senha:
                st.warning("Preencha WhatsApp e Senha!")
            else:
                with st.spinner("IA Mestre processando fotos..."):
                    dados = {
                        "nome": c_nome,
                        "telefone": id_limpo,
                        "area": c_area,
                        "senha": c_senha,
                        "saldo": 0,
                        "cliques": 0,
                        "f1": IAMestre.otimizar_imagem(up1),
                        "f2": IAMestre.otimizar_imagem(up2),
                        "f3": IAMestre.otimizar_imagem(up3),
                        "f4": IAMestre.otimizar_imagem(up4),
                    }
                    db.collection("profissionais").document(id_limpo).set(dados)
                    st.success("✅ Perfil Criado! Vá na aba 'Meu Perfil' para entrar.")

# Os outros blocos (Busca, Perfil, Admin) ficam vazios por enquanto 
# para você testar se esse salvamento já funciona.

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import math
import unicodedata
from streamlit_js_eval import get_geolocation

# ==========================================================
# 0. CONEXÃO E ESTRUTURA DE DADOS (FIXO ✅)
# ==========================================================
if not firebase_admin._apps:
    try:
        fb_dict = json.loads(base64.b64decode(st.secrets["FIREBASE_BASE64"]).decode())
        firebase_admin.initialize_app(credentials.Certificate(fb_dict))
    except Exception as e:
        st.error(f"Erro na ignição do Banco: {e}")
db = firestore.client()

# ==========================================================
# 1. MOTOR DE BUSCA DO BANCO (ESQUELETO DO TEU ARQUIVO) - FIXO ✅
# ==========================================================

def buscar_lojas_ativas():
    """Puxa do teu banco apenas quem está aprovado e tem saldo"""
    # Usando a coleção 'profissionais' que já tens no banco
    return db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">=", 1).stream()

def buscar_posts_da_loja(id_loja):
    """Puxa os produtos (posts) da sub-coleção que criamos"""
    return db.collection("profissionais").document(id_loja).collection("posts").where("ativo", "==", True).stream()

def ia_mestra_processar(texto):
    """IA original para mapear categorias do teu banco"""
    if not texto: return None
    t = "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower()
    mapa = {
        "pizza": "Pizzaria", "fome": "Pizzaria", "carro": "Mecânico", 
        "luz": "Eletricista", "roupa": "Moda", "celular": "Informática"
    }
    for chave, cat in mapa.items():
        if chave in t: return cat
    return None

# ==========================================================
# 2. ÁREA DE TESTE: CONSTRUTOR DE VITRINE LUXO 🛠️
# ==========================================================

def main():
    # Carregamos o seu CSS de tema claro/escuro original aqui para manter o visual
    st.markdown("<h1 style='text-align:center;'>GERALJÁ | BANCO ATIVO</h1>", unsafe_allow_html=True)
    
    # 1. LOCALIZAÇÃO (Ponto crucial do teu banco para calcular KM)
    loc = get_geolocation()
    u_lat = loc['coords']['latitude'] if loc else -23.5505
    u_lon = loc['coords']['longitude'] if loc else -46.6333

    # 2. BUSCA NO BANCO
    busca = st.text_input("Encontre no Banco GeralJá...")
    cat_ia = ia_mestra_processar(busca)
    
    # LISTAGEM REAL DOS DADOS QUE JÁ TENS
    lojas = buscar_lojas_ativas()
    
    st.write("---")
    st.write("### 💎 TESTE DE DESIGN DE VITRINE (DADOS REAIS)")
    
    # Aqui vamos testar como exibir os dados que vieram do banco
    for loja in lojas:
        dados = loja.to_dict()
        # Se a IA detetou algo ou se o nome bate, mostramos:
        if not busca or (cat_ia == dados.get('area')) or (busca.lower() in dados.get('nome','').lower()):
            with st.expander(f"🏪 {dados.get('nome')} - Saldo: {dados.get('saldo')} GeralCoins"):
                st.write(f"Categoria: {dados.get('area')}")
                # Aqui o sistema vai ler os 'posts' que o lojista cadastrou
                posts = buscar_posts_da_loja(loja.id)
                for p in posts:
                    st.json(p.to_dict()) # Teste bruto dos dados por enquanto

# ==========================================================
# 3. FINALIZADOR (VARREDOR ORIGINAL) ✅
# ==========================================================
if __name__ == "__main__":
    main()
    # Puxa o seu rodapé finalizador aqui
    st.markdown("<div style='text-align:center; padding:20px; opacity:0.5;'>🎯 GeralJá | Banco de Dados Conectado</div>", unsafe_allow_html=True)

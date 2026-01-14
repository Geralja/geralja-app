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

def bloco_vitrine_TESTE(busca, categoria_ia, lat_user, lon_user):
    """
    TESTE: Interface de Alto Padrão em Blocos.
    O foco aqui é o PRODUTO. O nome da loja é o detalhe.
    """
    # 1. CSS DE DESIGN MODERNO (Limpo e Imersivo)
    st.markdown("""
        <style>
        .card-elite {
            background: #fff;
            border-radius: 20px;
            border: 1px solid #f0f0f0;
            margin-bottom: 30px;
            transition: 0.4s;
            box-shadow: 0 10px 20px rgba(0,0,0,0.03);
        }
        .card-elite:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }
        .img-vitrine {
            width: 100%;
            height: 350px;
            object-fit: cover;
            border-radius: 20px 20px 0 0;
        }
        .info-vitrine {
            padding: 20px;
            text-align: left;
        }
        .loja-tag {
            font-size: 0.7rem;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 700;
        }
        .preco-elite {
            color: #1a1a1a;
            font-size: 1.4rem;
            font-weight: 800;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. BUSCA NO BANCO REAL (Usando o motor fixo do Bloco 1)
    lojas = db.collection("profissionais").where("aprovado", "==", True).where("saldo", ">=", 1).stream()

    for loja in lojas:
        l_data = loja.to_dict()
        l_id = loja.id
        
        # Filtro de IA e Nome (O seu esqueleto potente)
        if busca and not (busca.lower() in l_data.get('nome','').lower() or categoria_ia == l_data.get('area')):
            continue
            
        # Puxa os Posts (Produtos) de cada loja
        posts = db.collection("profissionais").document(l_id).collection("posts").where("ativo", "==", True).stream()
        
        for p_doc in posts:
            p = p_doc.to_dict()
            
            # Montagem do Card de Luxo
            col1, col2, col3 = st.columns([1, 6, 1]) # Centraliza o bloco na tela
            with col2:
                img_src = f"data:image/png;base64,{p.get('foto')}" if p.get('foto') else "https://via.placeholder.com/600x400"
                
                st.markdown(f"""
                    <div class="card-elite">
                        <img src="{img_src}" class="img-vitrine">
                        <div class="info-vitrine">
                            <span class="loja-tag">{l_data.get('nome')}</span>
                            <h3 style="margin: 5px 0; color:#000;">{p.get('titulo')}</h3>
                            <div class="preco-elite">R$ {p.get('preco')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # BOTÃO DE AÇÃO (Onde o 1 crédito é cobrado)
                if st.button(f"S'ENTRETENIR / CONTATAR {l_data.get('nome').upper()}", key=f"btn_{p_doc.id}"):
                    # Executa a função fixa de cobrança
                    if l_data['saldo'] >= 1:
                        db.collection("profissionais").document(l_id).update({"saldo": l_data['saldo'] - 1})
                        st.success(f"WHATSAPP: {l_data.get('whatsapp')}")
                        st.link_button("ABRIR WHATSAPP", f"https://wa.me/55{l_data.get('whatsapp')}")
                    else:
                        st.error("Loja indisponível no momento.")
                
                st.write("") # Espaçador

# ==========================================================
# 3. FINALIZADOR (VARREDOR ORIGINAL) ✅
# ==========================================================
if __name__ == "__main__":
    main()
    # Puxa o seu rodapé finalizador aqui
    st.markdown("<div style='text-align:center; padding:20px; opacity:0.5;'>🎯 GeralJá | Banco de Dados Conectado</div>", unsafe_allow_html=True)

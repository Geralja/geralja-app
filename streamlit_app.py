import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import datetime
import pandas as pd
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO DE AMBIENTE ---
st.set_page_config(
    page_title="GeralJá | Social Marketplace",
    page_icon="⚡",
    layout="wide"
)

# Constantes que estavam faltando
PIX_OFICIAL = "11991853488"
BONUS_WELCOME = 50.0
VALOR_CLIQUE = 2.00

# --- NOVO ESTILO CSS PARA VITRINE CHIQUE ---
st.markdown("""
    <style>
    .vitrine-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
    }
    .product-card {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        width: 300px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
        border: 1px solid #f0f0f0;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
    }
    .product-image {
        width: 100%;
        height: 200px;
        background: #f8f9fa; /* Cor de fundo se não tiver imagem */
        display: flex;
        align-items: center;
        justify-content: center;
        color: #adb5bd;
    }
    .product-info {
        padding: 15px;
    }
    .product-price {
        color: #1a1a1a;
        font-size: 1.4rem;
        font-weight: 800;
        margin: 5px 0;
    }
    .product-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #444;
        margin-bottom: 5px;
    }
    .merchant-badge {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #1877f2;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DA VITRINE (DENTRO DA ABA 1) ---
with abas[0]:
    st.markdown("<h2 style='text-align: center; color: #1a1a1a;'>🛍️ Vitrine de Ofertas</h2>", unsafe_allow_html=True)
    
    # Barra de busca estilizada
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        busca = st.text_input("🔍 O que você deseja comprar hoje?", placeholder="Ex: iPhone, Pizza, Cadeira...")

    # Grid de Produtos
    cols_vitrine = st.columns(3)
    pros_ref = db.collection("profissionais").where("saldo", ">", 0).stream()

    for i, doc in enumerate(pros_ref):
        p = doc.to_dict()
        pid = doc.id
        
        # Dados do Produto/Comerciante
        nome_loja = p.get('nome', 'Loja Parceira')
        produto_nome = p.get('servico', 'Produto Premium') # Aqui o comerciante coloca o nome do produto
        preco = p.get('preco', 'Consulte') # Adicionei campo de preço
        
        # Layout em Colunas (3 por linha)
        with cols_vitrine[i % 3]:
            st.markdown(f"""
                <div class="product-card">
                    <div class="product-image">
                        <img src="https://via.placeholder.com/300x200?text={produto_nome.replace(' ', '+')}" style="width:100%">
                    </div>
                    <div class="product-info">
                        <span class="merchant-badge">⭐ {nome_loja}</span>
                        <div class="product-title">{produto_nome}</div>
                        <div class="product-price">R$ {preco}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botão de Compra/Contato Integrado
            if st.button(f"🛍️ Tenho Interesse", key=f"buy_{pid}", use_container_width=True):
                if p.get('saldo', 0) >= 2.0:
                    novo_saldo = p.get('saldo') - 2.0
                    db.collection("profissionais").document(pid).update({"saldo": novo_saldo})
                    st.success(f"Fale com a loja: {p.get('whatsapp')}")
                    st.link_button("Chamar no WhatsApp", f"https://wa.me/{p.get('whatsapp')}?text=Vi+seu+produto+{produto_nome}+no+GeralJá")

# --- INICIALIZAÇÃO FIREBASE ---
if not firebase_admin._apps:
    try:
        fb_dict = json.loads(st.secrets["firebase"]["text"])
        cred = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(cred)
    except:
        st.error("Erro: Configure o Secret 'firebase' no Streamlit Cloud.")

db = firestore.client()

# --- HEADER ---
st.markdown("""
    <div style="background: white; padding: 10px; border-bottom: 1px solid #ddd; margin-bottom: 20px; text-align: center;">
        <h1 style="color: #1877f2; margin: 0;">GeralJá</h1>
        <p style="color: #65676b;">Encontre soluções na sua comunidade</p>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
abas = st.tabs(["🏠 Feed de Serviços", "➕ Cadastrar-se", "📈 Painel Pro", "🛡️ Admin"])

# ------------------------------------------------------------------------------
# ABA 1: FEED (BUSCA)
# ------------------------------------------------------------------------------
with abas[0]:
    col_l, col_c, col_r = st.columns([1, 2, 1])
    
    with col_l:
        st.markdown("### Filtros")
        busca = st.text_input("🔍 O que procura?", placeholder="Ex: Pintor, Advogado...")
        categoria = st.selectbox("Categoria", ["Todas", "Manutenção", "Estética", "Educação", "Outros"])

    with col_c:
        pros_ref = db.collection("profissionais").where("saldo", ">", 0).stream()
        
        encontrados = 0
        for doc in pros_ref:
            p = doc.to_dict()
            pid = doc.id
            
            # Lógica de Busca Simples
            if busca.lower() in p.get('nome', '').lower() or busca.lower() in p.get('servico', '').lower():
                encontrados += 1
                nome_completo = p.get('nome', 'Profissional')
                servico = p.get('servico') or "Serviços Gerais"
                primeiro_nome = nome_completo.split()[0]
                
                # Card Estilo Facebook
                st.markdown(f"""
                <div class="fb-card">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="width: 45px; height: 45px; background: #ccd0d5; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 12px;">
                            {nome_completo[0].upper()}
                        </div>
                        <div>
                            <span class="pro-name">{nome_completo}</span> <span class="verified-badge">✔</span><br>
                            <small style="color: #65676b;">Ativo agora • São Paulo</small>
                        </div>
                    </div>
                    <div style="margin: 15px 0;">
                        <span class="service-tag">{servico}</span>
                    </div>
                    <p style="color: #1c1e21; font-size: 0.95rem;">Especialista pronto para atender sua solicitação. Clique abaixo para negociar.</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Enviar mensagem para {primeiro_nome}", key=f"btn_{pid}"):
                    if p.get('saldo', 0) >= VALOR_CLIQUE:
                        novo_saldo = p.get('saldo') - VALOR_CLIQUE
                        db.collection("profissionais").document(pid).update({"saldo": novo_saldo})
                        st.success(f"Contato: {p.get('whatsapp')}")
                        st.link_button("Abrir WhatsApp", f"https://wa.me/{p.get('whatsapp')}")
                    else:
                        st.warning("Este profissional atingiu o limite de contatos.")

        if encontrados == 0:
            st.info("Nenhum profissional encontrado com esse termo.")

    with col_r:
        st.markdown("### Sugestões")
        st.info("💡 Profissionais com selo ✔ têm prioridade no atendimento.")

# ------------------------------------------------------------------------------
# ABA 2: CADASTRO
# ------------------------------------------------------------------------------
with abas[1]:
    st.markdown("## Comece a receber clientes hoje!")
    with st.form("reg_pro"):
        nome_c = st.text_input("Seu Nome")
        zap_c = st.text_input("WhatsApp (com DDD)")
        serv_c = st.text_input("O que você faz?")
        
        if st.form_submit_button("Criar meu Perfil Pro"):
            if nome_c and zap_c:
                novo = {
                    "nome": nome_c,
                    "whatsapp": zap_c,
                    "servico": serv_c,
                    "saldo": BONUS_WELCOME,
                    "data": datetime.now(pytz.timezone('America/Sao_Paulo')),
                    "verificado": True
                }
                db.collection("profissionais").add(novo)
                st.balloons()
                st.success("Cadastro realizado! Você ganhou R$ 50 de bônus.")

# ------------------------------------------------------------------------------
# ABA 3 e 4: PAINEL E ADMIN (Resumidos para funcionalidade)
# ------------------------------------------------------------------------------
with abas[2]:
    st.write("Consulte seu saldo enviando seu nome na busca.")

with abas[3]:
    pwd = st.text_input("Chave Mestra", type="password")
    if pwd == "admin123":
        st.write("Gerenciamento de Profissionais")
        # Aqui você pode listar todos e deletar ou adicionar saldo

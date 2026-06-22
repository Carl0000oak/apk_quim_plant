import streamlit as st
from complant.main import carregar_banco, buscar_compostos, listar_categorias

st.set_page_config(page_title="🌿 COMPLANT", layout="wide")

st.title("🌿 COMPLANT - Análise Fitoquímica")

# Carregar banco
if st.button("📥 Carregar Base de Dados"):
    carregar_banco()
    st.success("✅ Base carregada!")

# Buscar composto
termo = st.text_input("🔍 Buscar composto:")
if termo:
    resultados = buscar_compostos(termo)
    if resultados:
        st.write(f"✅ {len(resultados)} resultados:")
        for r in resultados[:10]:
            st.write(f"  • {r['nome']} ({r['categoria']})")
    else:
        st.warning("Nenhum composto encontrado")
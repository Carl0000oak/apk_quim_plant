"""
🧪 TESTE RÁPIDO - COMPLANT
"""

from complant.main import carregar_banco, buscar_compostos, listar_categorias, analisar_planta

print("🧪 TESTANDO COMPLANT")
print("=" * 50)

# 1. Carregar banco
print("\n1️⃣ Carregando banco de dados...")
carregar_banco()

# 2. Listar categorias
print("\n2️⃣ Categorias disponíveis:")
categorias = listar_categorias()
for cat in categorias[:5]:
    print(f"  • {cat}")

# 3. Buscar composto
print("\n3️⃣ Buscando 'quinine':")
resultados = buscar_compostos("quinine")
for r in resultados[:5]:
    print(f"  • {r['nome']} ({r['categoria']})")

# 4. Analisar planta
print("\n4️⃣ Analisando planta...")
analisar_planta("Lippia alba", max_artigos=5)

print("\n✅ Teste concluído!")

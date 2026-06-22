print("🧪 TESTANDO COMPLANT")
print("=" * 50)

print("\n1️⃣ Testando import...")
from complant.main import carregar_banco, buscar_compostos, listar_categorias, analisar_planta, buscar_plantas_por_composto
print("✅ Import OK")

print("\n2️⃣ Testando carregamento...")
carregar_banco()
print("✅ Carregamento OK")

print("\n3️⃣ Testando categorias...")
categorias = listar_categorias()
print(f"✅ {len(categorias)} categorias encontradas")
for cat in categorias[:3]:
    print(f"  • {cat}")

print("\n4️⃣ Testando busca por PLANTA...")
analisar_planta("Lippia alba", max_artigos=3)

print("\n5️⃣ Testando busca por COMPOSTO...")
buscar_plantas_por_composto("quercetin", max_artigos=5)

print("\n✅ TODOS OS TESTES PASSARAM!")

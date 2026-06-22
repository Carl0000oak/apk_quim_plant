print("🧪 TESTANDO COMPLANT")
print("="*50)

# 1. Testar import
print("\n1️⃣ Testando import...")
from complant.main import carregar_banco, buscar_compostos, listar_categorias
print("✅ Import OK")

# 2. Testar carregamento
print("\n2️⃣ Testando carregamento...")
carregar_banco()
print("✅ Carregamento OK")

# 3. Testar categorias
print("\n3️⃣ Testando categorias...")
categorias = listar_categorias()
print(f"✅ {len(categorias)} categorias encontradas")
for cat in categorias[:3]:
    print(f"  • {cat}")

# 4. Testar busca
print("\n4️⃣ Testando busca...")
resultados = buscar_compostos("quinine")
print(f"✅ {len(resultados)} resultados para 'quinine'")
for r in resultados[:3]:
    print(f"  • {r['nome']} ({r['categoria']})")

print("\n✅ TODOS OS TESTES PASSARAM!")

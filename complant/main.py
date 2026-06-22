from .db_manager import DatabaseManager

db = DatabaseManager()

def carregar_banco():
    return db.baixar()

def buscar_compostos(termo):
    return db.buscar(termo)

def listar_categorias():
    return db.get_categorias()

def compostos_por_categoria(categoria):
    return db.get_categoria(categoria)

def analisar_planta(nome_planta, max_artigos=5):
    print(f"🔍 Analisando: {nome_planta}")
    if not carregar_banco():
        return None
    
    # Buscar compostos
    todos = db.get_all()
    print(f"✅ {len(todos)} compostos disponiveis")
    
    # Simular busca
    resultados = db.buscar(nome_planta[:3])
    if resultados:
        print(f"Encontrados {len(resultados)} compostos")
        for r in resultados[:5]:
            print(f"  • {r['nome']} ({r['categoria']})")
    return resultados

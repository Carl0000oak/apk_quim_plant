"""
🌿 COMPLANT - Módulo Principal
"""

from .db_manager import DatabaseManager
from .search.wikipedia import buscar_foto_wikipedia
from .search.pubmed import buscar_pubmed

# Banco de dados global
db = DatabaseManager()

def carregar_banco():
    """Carrega o banco de dados"""
    return db.baixar()

def buscar_compostos(termo):
    """Busca compostos por nome"""
    return db.buscar(termo)

def listar_categorias():
    """Lista todas as categorias"""
    return db.get_categorias()

def compostos_por_categoria(categoria):
    """Retorna compostos de uma categoria"""
    return db.get_categoria(categoria)

def analisar_planta(nome_planta, max_artigos=10):
    """
    Analisa uma planta e retorna compostos encontrados
    """
    print(f"\n🔍 Analisando: {nome_planta}")
    print("=" * 50)
    
    # 1. Carregar banco de dados
    if not carregar_banco():
        return None
    
    # 2. Buscar artigos no PubMed
    artigos = buscar_pubmed(nome_planta, max_artigos)
    if not artigos:
        print("❌ Nenhum artigo encontrado")
        return None
    
    # 3. Buscar foto da planta
    buscar_foto_wikipedia(nome_planta)
    
    # 4. Extrair compostos dos artigos
    compostos_encontrados = {}
    for artigo in artigos:
        texto = f"{artigo.get('titulo', '')} {artigo.get('resumo', '')}".lower()
        for categoria in db.get_categorias():
            for composto in db.get_categoria(categoria):
                if composto in texto:
                    if composto not in compostos_encontrados:
                        compostos_encontrados[composto] = {
                            'categoria': categoria,
                            'artigos': []
                        }
                    compostos_encontrados[composto]['artigos'].append(artigo.get('pmid'))
    
    # 5. Resultados
    print(f"\n✅ Encontrados {len(compostos_encontrados)} compostos")
    
    for composto, info in compostos_encontrados.items():
        print(f"  • {composto} ({info['categoria']}) - {len(info['artigos'])} artigos")
    
    return compostos_encontrados

def main():
    """Interface principal"""
    print("🌿 COMPLANT - Análise Fitoquímica")
    print("=" * 50)
    
    # Carregar banco de dados
    carregar_banco()
    
    while True:
        print("\n📋 MENU:")
        print("  1. Analisar planta")
        print("  2. Buscar composto")
        print("  3. Listar categorias")
        print("  4. Ver estatísticas")
        print("  5. Sair")
        
        opcao = input("\nEscolha: ").strip()
        
        if opcao == '1':
            planta = input("🌱 Nome da planta: ").strip()
            if planta:
                analisar_planta(planta)
        
        elif opcao == '2':
            termo = input("🔍 Nome do composto: ").strip()
            if termo:
                resultados = buscar_compostos(termo)
                if resultados:
                    print(f"\n✅ Encontrados {len(resultados)} compostos:")
                    for r in resultados[:10]:
                        print(f"  • {r['nome']} ({r['categoria']})")
                else:
                    print("❌ Nenhum composto encontrado")
        
        elif opcao == '3':
            categorias = listar_categorias()
            print("\n📂 Categorias:")
            for cat in categorias:
                print(f"  • {cat}")
        
        elif opcao == '4':
            stats = db.stats()
            print("\n📊 Estatísticas:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        elif opcao == '5':
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()
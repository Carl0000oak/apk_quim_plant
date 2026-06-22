from .db_manager import DatabaseManager
from .search.pubmed import buscar_pubmed
import requests
import json

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
    print(f"\n🔍 ANALISANDO PLANTA: {nome_planta}")
    print("=" * 50)
    
    if not carregar_banco():
        return None
    
    # Buscar artigos
    artigos = buscar_pubmed(nome_planta, max_artigos)
    if not artigos:
        print("❌ Nenhum artigo encontrado")
        return None
    
    # Buscar compostos nos artigos
    compostos_encontrados = {}
    for artigo in artigos:
        texto = f"{artigo.get('titulo', '')} {artigo.get('resumo', '')}".lower()
        for categoria in db.get_categorias():
            for composto in db.get_categoria(categoria):
                if composto in texto:
                    if composto not in compostos_encontrados:
                        compostos_encontrados[composto] = {
                            'categoria': categoria,
                            'freq': 0
                        }
                    compostos_encontrados[composto]['freq'] += 1
    
    print(f"\n✅ Encontrados {len(compostos_encontrados)} compostos:")
    for composto, info in sorted(compostos_encontrados.items(), key=lambda x: x[1]['freq'], reverse=True):
        print(f"  • {composto} ({info['categoria']}) - {info['freq']} artigos")
    
    return compostos_encontrados

def buscar_plantas_por_composto(composto, max_artigos=10):
    print(f"\n🧪 BUSCANDO PLANTAS COM: {composto}")
    print("=" * 50)
    
    if not carregar_banco():
        return None
    
    # Buscar artigos sobre o composto
    artigos = buscar_pubmed(composto, max_artigos)
    if not artigos:
        print("❌ Nenhum artigo encontrado")
        return None
    
    # Lista de plantas para buscar
    plantas_comuns = [
        'lippia', 'mentha', 'rosmarinus', 'camellia', 'hypericum',
        'aloe', 'curcuma', 'zingiber', 'lavandula', 'thymus',
        'ocimum', 'salvia', 'melissa', 'matricaria', 'calendula',
        'eucalyptus', 'cinnamomum', 'pinus', 'abies', 'picea'
    ]
    
    plantas_encontradas = {}
    
    for artigo in artigos:
        texto = f"{artigo.get('titulo', '')} {artigo.get('resumo', '')}".lower()
        for planta in plantas_comuns:
            if planta in texto:
                if planta not in plantas_encontradas:
                    plantas_encontradas[planta] = []
                plantas_encontradas[planta].append(artigo.get('pmid'))
    
    if not plantas_encontradas:
        print(f"❌ Nenhuma planta encontrada com {composto}")
        return None
    
    print(f"\n✅ Encontradas {len(plantas_encontradas)} plantas com {composto}:")
    for planta, artigos_lista in sorted(plantas_encontradas.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  🌿 {planta.title()} - {len(artigos_lista)} artigos")
    
    return plantas_encontradas

def main():
    print("🌿 COMPLANT - Análise Fitoquímica")
    print("=" * 50)
    
    carregar_banco()
    
    while True:
        print("\n📋 MENU:")
        print("  1. 🔍 Buscar por PLANTA (ex: Lippia alba)")
        print("  2. 🔍 Buscar por COMPOSTO (ex: quercetin)")
        print("  3. 📂 Listar categorias")
        print("  4. 📊 Ver estatísticas")
        print("  5. 🚪 Sair")
        
        opcao = input("\nEscolha: ").strip()
        
        if opcao == '1':
            planta = input("🌱 Nome da planta: ").strip()
            if planta:
                analisar_planta(planta)
            else:
                print("❌ Digite um nome válido")
        
        elif opcao == '2':
            composto = input("🧪 Nome do composto: ").strip()
            if composto:
                buscar_plantas_por_composto(composto)
            else:
                print("❌ Digite um nome válido")
        
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
            print("❌ Opção inválida. Digite 1, 2, 3, 4 ou 5")

if __name__ == "__main__":
    main()

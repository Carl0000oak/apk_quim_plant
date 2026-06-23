"""
🌿 COMPLANT - Módulo Principal
"""

from .db_manager import db
from .search.pubmed import buscar_pubmed
from .search.wikipedia import buscar_foto_wikipedia
from collections import Counter, defaultdict

# ============================================
# BASE DE DADOS
# ============================================

VALID_COMPOUNDS = []

def carregar_banco():
    """Carrega TODOS os dados"""
    global VALID_COMPOUNDS
    if db.baixar():
        VALID_COMPOUNDS = db.get_all()
        print(f"📚 {len(VALID_COMPOUNDS)} compostos disponíveis")
        return True
    return False

def buscar_compostos(termo):
    return db.buscar(termo)

def listar_categorias():
    return db.get_categorias()

def compostos_por_categoria(categoria):
    return db.get_categoria(categoria)

def get_funcoes(composto):
    return db.get_funcoes(composto)

# ============================================
# ANALISAR PLANTA
# ============================================

def analisar_planta(nome_planta, max_artigos=15):  # ← MUDOU PARA 15
    print(f"\n🔍 ANALISANDO PLANTA: {nome_planta}")
    print("=" * 50)
    
    if not carregar_banco():
        return None
    
    artigos = buscar_pubmed(nome_planta, max_artigos)  # ← USA 15
    if not artigos:
        print("❌ Nenhum artigo encontrado")
        return None
    
    print(f"📄 {len(artigos)} artigos analisados")
    
    # Extrair compostos
    compostos = {}
    for artigo in artigos:
        texto = f"{artigo.get('titulo', '')} {artigo.get('resumo', '')} {artigo.get('texto_completo', '')}".lower()
        pmid = artigo.get('pmid', '')
        
        for comp in VALID_COMPOUNDS:
            comp_lower = comp.lower()
            comp_norm = db.normalizar_composto(comp)
            
            if comp_lower in texto or comp_norm in texto:
                if comp not in compostos:
                    compostos[comp] = {'freq': 0, 'categoria': 'MISCELLANEOUS', 'artigos': []}
                compostos[comp]['freq'] += 1
                compostos[comp]['artigos'].append(pmid)
                
                for cat, comps in db.data.get('categories', {}).items():
                    if comp in comps:
                        compostos[comp]['categoria'] = cat
                        break
    
    if not compostos:
        print("❌ Nenhum composto encontrado")
        return None
    
    # Organizar resultados
    resultados = []
    for comp, info in compostos.items():
        funcoes = db.get_funcoes(comp)
        resultados.append({
            'compound': comp,
            'freq': info['freq'],
            'family': info['categoria'],
            'category': info['categoria'],
            'articles': len(info['artigos']),
            'agriculture': funcoes.get('agriculture', ['-']),
            'health': funcoes.get('health', ['-']),
            'food': funcoes.get('food', ['-'])
        })
    
    resultados = sorted(resultados, key=lambda x: x['freq'], reverse=True)
    
    print(f"\n✅ Encontrados {len(resultados)} compostos:")
    for item in resultados[:20]:
        print(f"  • {item['compound']} ({item['family']}) - {item['freq']} artigos")
    
    return resultados

# ============================================
# BUSCAR PLANTAS POR COMPOSTO
# ============================================

def buscar_plantas_por_composto(composto, max_artigos=5):
    print(f"\n🧪 BUSCANDO PLANTAS COM: {composto}")
    print("=" * 50)
    
    if not carregar_banco():
        return None
    
    artigos = buscar_pubmed(composto, max_artigos)
    if not artigos:
        print("❌ Nenhum artigo encontrado")
        return None
    
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

# ============================================
# MENU PRINCIPAL
# ============================================

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
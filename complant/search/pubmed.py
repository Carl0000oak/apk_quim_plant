"""
🔍 BUSCADOR DE ARTIGOS - PUBMED
"""

import requests
import time
from urllib.parse import quote

def buscar_pubmed(planta, max_artigos=10):
    """
    Busca artigos no PubMed sobre a planta
    """
    print(f"🔍 Buscando artigos para: {planta}")
    
    termos = [
        f'"{planta}" AND ("phytochemical" OR "compound")',
        f'"{planta}" AND ("essential oil" OR "extract")',
    ]
    
    pmids = set()
    
    for termo in termos:
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={quote(termo)}&retmax={max_artigos}&retmode=json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                ids = data.get('esearchresult', {}).get('idlist', [])
                pmids.update(ids[:5])
                print(f"  ✅ {len(ids)} artigos")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ Erro: {e}")
            continue
    
    if not pmids:
        print("❌ Nenhum artigo encontrado")
        return []
    
    print(f"📚 {len(pmids)} artigos encontrados")
    
    artigos = []
    
    for pmid in list(pmids)[:max_artigos]:
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('result', {}).get(pmid, {})
                
                artigos.append({
                    'pmid': pmid,
                    'titulo': result.get('title', ''),
                    'resumo': result.get('abstract', ''),
                    'link': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ⚠️ Erro: {e}")
            continue
    
    print(f"✅ {len(artigos)} artigos confirmados")
    return artigos

if __name__ == "__main__":
    artigos = buscar_pubmed("Lippia alba")
    for artigo in artigos[:3]:
        print(f"\n📄 {artigo['titulo']}")
"""
🔍 BUSCADOR DE ARTIGOS - PUBMED (COM TEXTO COMPLETO)
"""

import requests
import time
from urllib.parse import quote
from bs4 import BeautifulSoup

def buscar_pubmed(planta, max_artigos=15):  # ← MUDOU PARA 15
    print(f"🔍 Buscando artigos para: {planta}")
    print("-"*60)
    
    termos = [
        f'"{planta}" AND ("phytochemical" OR "compound" OR "essential oil")',
        f'"{planta}" AND ("flavonoid" OR "terpene" OR "phenolic")',
        f'"{planta}" AND ("GC-MS" OR "HPLC" OR "analysis")',
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
                print(f"  ✅ {termo[:50]}...: {len(ids)} artigos")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ Erro na busca: {e}")
            continue
    
    
    if not pmids:
        print("❌ Nenhum artigo encontrado")
        return []
    
    print(f"\n📚 {len(pmids)} artigos encontrados")
    
    artigos = []
    
    for i, pmid in enumerate(list(pmids)[:max_artigos]):
        try:
            print(f"\n  📄 Processando artigo {i+1}/{min(len(pmids), max_artigos)} (PMID: {pmid})...")
            
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                continue
                
            data = response.json()
            result = data.get('result', {}).get(pmid, {})
            titulo = result.get('title', '')
            resumo = result.get('abstract', '')
            
            planta_lower = planta.lower()
            if planta_lower not in titulo.lower() and planta_lower not in resumo.lower():
                print(f"    ⚠️ Planta não mencionada no título/resumo")
                continue
            
            print(f"    ✅ Planta confirmada")
            
            texto_completo = ""
            pmcid = ""
            
            try:
                url_pmc = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id={pmid}&linkname=pubmed_pmc&retmode=json"
                resp_pmc = requests.get(url_pmc, timeout=10)
                
                if resp_pmc.status_code == 200:
                    dados_pmc = resp_pmc.json()
                    links = dados_pmc.get('linksets', [])
                    if links and links[0].get('linksetdbs'):
                        pmc_ids = links[0]['linksetdbs'][0].get('links', [])
                        if pmc_ids:
                            pmcid = pmc_ids[0]
                            print(f"    📄 PMC ID: {pmcid}")
                            
                            url_xml = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid}&retmode=xml"
                            resp_xml = requests.get(url_xml, timeout=30)
                            
                            if resp_xml.status_code == 200:
                                soup = BeautifulSoup(resp_xml.text, 'html.parser')
                                for tag in soup.find_all(['p', 'abstract', 'title', 'sec']):
                                    if tag.text:
                                        texto_completo += tag.text + " "
                                texto_completo = texto_completo[:30000]
                                print(f"    📄 Texto completo: {len(texto_completo)} caracteres")
            except Exception as e:
                print(f"    ⚠️ Erro no download do PMC: {e}")
            
            if not texto_completo:
                texto_completo = f"{titulo} {resumo}"
                print(f"    📄 Usando apenas título + resumo ({len(texto_completo)} caracteres)")
            
            artigos.append({
                'pmid': pmid,
                'pmcid': pmcid,
                'titulo': titulo,
                'resumo': resumo,
                'texto_completo': texto_completo,
                'link': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    ⚠️ Erro: {e}")
            continue
    
    print(f"\n✅ {len(artigos)} artigos confirmados")
    return artigos
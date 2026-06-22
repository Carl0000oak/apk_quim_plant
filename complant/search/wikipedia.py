"""
🌿 BUSCADOR DE IMAGENS - WIKIPEDIA
"""

import requests
from IPython.display import Image, display
from urllib.parse import quote

def buscar_foto_wikipedia(nome_planta):
    """
    Busca e exibe foto da planta usando Wikipedia
    """
    print(f"🔍 Buscando foto de: {nome_planta}")
    
    wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={quote(nome_planta)}&prop=pageimages&format=json&pithumbsize=500"
    
    try:
        response = requests.get(wiki_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page_data in pages.items():
                if 'thumbnail' in page_data:
                    img_url = page_data['thumbnail']['source']
                    print(f"✅ Foto encontrada!")
                    print(f"📷 {img_url}")
                    return img_url
                else:
                    print(f"❌ Nenhuma foto encontrada para: {nome_planta}")
                    return None
        else:
            print(f"❌ Erro ao acessar Wikipedia")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

if __name__ == "__main__":
    buscar_foto_wikipedia("Lippia alba")


import requests
from urllib.parse import quote

def buscar_foto_wikipedia(nome_planta):
    """
    Busca e retorna a URL da imagem da planta na Wikipedia
    """
    print(f"🔍 Buscando foto de: {nome_planta}")
    
    try:
        # Buscar na Wikipedia
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={quote(nome_planta)}&prop=pageimages&format=json&pithumbsize=500"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page_data in pages.items():
                if 'thumbnail' in page_data:
                    img_url = page_data['thumbnail']['source']
                    print(f"✅ Foto encontrada!")
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



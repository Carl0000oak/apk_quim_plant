import requests
import json

class DatabaseManager:
    def __init__(self):
        self.url = "https://raw.githubusercontent.com/Carl0000oak/apk_quim_plant/main/complant/data/compounds.json"
        self.data = None
        self.version = "0.0"
        self.total = 0
    
    def baixar(self):
        print("📥 Baixando base de dados...")
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            self.data = response.json()
            self.version = self.data.get('version', '1.0.0')
            self.total = self.data.get('total', 0)
            print(f"✅ Baixado! {self.total} compostos")
            return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def get_categoria(self, categoria):
        if not self.data:
            return []
        return self.data.get('categories', {}).get(categoria, [])
    
    def get_all(self):
        if not self.data:
            return []
        return self.data.get('all', [])
    
    def get_categorias(self):
        if not self.data:
            return []
        return list(self.data.get('categories', {}).keys())
    
    def buscar(self, termo):
        if not self.data:
            return []
        termo = termo.lower()
        resultados = []
        for categoria, compostos in self.data.get('categories', {}).items():
            for composto in compostos:
                if termo in composto.lower():
                    resultados.append({
                        'nome': composto,
                        'categoria': categoria
                    })
        return resultados
    
    def stats(self):
        if not self.data:
            return {}
        categorias = self.data.get('categories', {})
        total = sum(len(c) for c in categorias.values())
        return {
            'total': total,
            'categorias': len(categorias),
            'versao': self.version,
            'por_categoria': {k: len(v) for k, v in categorias.items()}
        }

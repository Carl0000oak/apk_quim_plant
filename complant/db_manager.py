"""
📦 GERENCIADOR DE BANCO DE DADOS
Baixa e gerencia os compostos do GitHub
"""

import requests
import json
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        self.url = "https://raw.githubusercontent.com/Carl0000oak/apk_quim_plant/main/complant/data/compounds.json"
        self.cache_file = "complant/data/compounds_cache.json"
        self.data = None
        self.version = "0.0"
        self.total = 0
    
    def baixar(self):
        """Baixa o JSON do GitHub"""
        print("📥 Baixando base de dados do GitHub...")
        
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            
            self.data = response.json()
            self.version = self.data.get('version', '1.0.0')
            self.total = self.data.get('total', 0)
            
            print(f"✅ Baixado! {self.total} compostos (versão {self.version})")
            
            # Salvar cache
            self._salvar_cache()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao baixar: {e}")
            
            # Tentar carregar do cache
            if self._carregar_cache():
                print("📂 Usando dados em cache")
                return True
            
            print("❌ Sem dados disponíveis")
            return False
    
    def _salvar_cache(self):
        """Salva os dados em cache local"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def _carregar_cache(self):
        """Carrega dados do cache local"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                    self.version = self.data.get('version', '1.0.0')
                    self.total = self.data.get('total', 0)
                return True
        except:
            pass
        return False
    
    def get_categoria(self, categoria):
        """Retorna os compostos de uma categoria específica"""
        if not self.data:
            return []
        return self.data.get('categories', {}).get(categoria, [])
    
    def get_all(self):
        """Retorna todos os compostos"""
        if not self.data:
            return []
        return self.data.get('all', [])
    
    def get_categorias(self):
        """Retorna todas as categorias"""
        if not self.data:
            return []
        return list(self.data.get('categories', {}).keys())
    
    def buscar(self, termo):
        """Busca compostos por nome"""
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
        """Estatísticas da base"""
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

# Teste rápido
if __name__ == "__main__":
    db = DatabaseManager()
    db.baixar()
    
    print("\n📊 ESTATÍSTICAS:")
    stats = db.stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
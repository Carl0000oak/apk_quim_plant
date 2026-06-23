"""
📦 GERENCIADOR DE BANCO DE DADOS
Gerencia compostos, funções e sinônimos
"""

import requests
import json
import os

class DatabaseManager:
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/Carl0000oak/apk_quim_plant/main/complant/data/"
        self.compounds_url = self.base_url + "compounds.json"
        self.functions_url = self.base_url + "functions.json"
        self.synonyms_url = self.base_url + "synonyms.json"
        
        self.data = None
        self.functions = {}
        self.synonyms = {}
        self.synonym_rules = {}
        self.version = "0.0"
        self.total = 0
    
    def baixar(self):
        """Baixa todos os dados do GitHub"""
        print("📥 Baixando base de dados...")
        
        # 1. Baixar compostos
        if not self._baixar_compostos():
            return False
        
        # 2. Baixar funções
        self._baixar_funcoes()
        
        # 3. Baixar sinônimos
        self._baixar_sinonimos()
        
        return True
    
    def _baixar_compostos(self):
        """Baixa o arquivo de compostos"""
        try:
            response = requests.get(self.compounds_url, timeout=10)
            response.raise_for_status()
            self.data = response.json()
            self.version = self.data.get('version', '1.0.0')
            self.total = self.data.get('total', 0)
            print(f"✅ Compostos: {self.total} (versão {self.version})")
            self._salvar_cache("compounds_cache.json", self.data)
            return True
        except Exception as e:
            print(f"❌ Erro ao baixar compostos: {e}")
            if self._carregar_cache("compounds_cache.json"):
                return True
            return False
    
    def _baixar_funcoes(self):
        """Baixa o arquivo de funções e extrai do formato correto"""
        try:
            response = requests.get(self.functions_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # ==========================================
                # EXTRAIR FUNÇÕES DO FORMATO DO SEU JSON
                # ==========================================
                functions = {}
                
                # 1. Funções por categoria (functions_by_category)
                for categoria, funcoes in data.get('functions_by_category', {}).items():
                    # Aplica as funções da categoria a todos os compostos da categoria
                    for composto in self.data.get('categories', {}).get(categoria.upper(), []):
                        if composto not in functions:
                            functions[composto] = {
                                'agriculture': [],
                                'health': [],
                                'food': []
                            }
                        functions[composto]['agriculture'].extend(funcoes.get('agriculture', []))
                        functions[composto]['health'].extend(funcoes.get('health', []))
                        functions[composto]['food'].extend(funcoes.get('food', []))
                
                # 2. Funções específicas (specific_compounds)
                for composto, funcoes in data.get('specific_compounds', {}).items():
                    composto_normalizado = composto.lower()
                    if composto_normalizado not in functions:
                        functions[composto_normalizado] = {
                            'agriculture': [],
                            'health': [],
                            'food': []
                        }
                    functions[composto_normalizado]['agriculture'].extend(funcoes.get('agriculture', []))
                    functions[composto_normalizado]['health'].extend(funcoes.get('health', []))
                    functions[composto_normalizado]['food'].extend(funcoes.get('food', []))
                
                # 3. Remover duplicatas
                for composto in functions:
                    functions[composto]['agriculture'] = list(set(functions[composto]['agriculture']))
                    functions[composto]['health'] = list(set(functions[composto]['health']))
                    functions[composto]['food'] = list(set(functions[composto]['food']))
                
                self.functions = functions
                print(f"✅ Funções: {len(self.functions)} compostos")
                self._salvar_cache("functions_cache.json", data)
            else:
                print("ℹ️ Arquivo functions.json não encontrado")
        except Exception as e:
            print(f"ℹ️ Erro ao baixar functions.json: {e}")
    
    def _baixar_sinonimos(self):
        """Baixa o arquivo de sinônimos"""
        try:
            response = requests.get(self.synonyms_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.synonyms = data.get('synonyms', {})
                self.synonym_rules = data.get('synonym_rules', {})
                print(f"✅ Sinônimos: {len(self.synonyms)} compostos")
                self._salvar_cache("synonyms_cache.json", data)
            else:
                print("ℹ️ Arquivo synonyms.json não encontrado")
        except:
            print("ℹ️ Erro ao baixar synonyms.json")
    
    def _salvar_cache(self, nome_arquivo, dados):
        try:
            os.makedirs("complant/data", exist_ok=True)
            with open(f"complant/data/{nome_arquivo}", 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def _carregar_cache(self, nome_arquivo):
        try:
            if os.path.exists(f"complant/data/{nome_arquivo}"):
                with open(f"complant/data/{nome_arquivo}", 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    if nome_arquivo == "compounds_cache.json":
                        self.data = dados
                        self.version = dados.get('version', '1.0.0')
                        self.total = dados.get('total', 0)
                    elif nome_arquivo == "functions_cache.json":
                        # Recarregar funções do cache
                        self._baixar_funcoes()
                    elif nome_arquivo == "synonyms_cache.json":
                        self.synonyms = dados.get('synonyms', {})
                        self.synonym_rules = dados.get('synonym_rules', {})
                return True
        except:
            pass
        return False
    
    def normalizar_composto(self, nome):
        """Normaliza o nome do composto usando sinônimos"""
        nome_lower = nome.lower()
        
        # Verificar sinônimos específicos
        if nome_lower in self.synonyms:
            # Retorna o nome canônico (primeiro da lista)
            if isinstance(self.synonyms[nome_lower], dict):
                return nome_lower
            return nome_lower
        
        # Verificar regras de substituição
        if self.synonym_rules:
            # Substituir letras gregas
            greek = self.synonym_rules.get('greek_letters', {})
            for grego, substitutos in greek.items():
                for sub in substitutos:
                    if sub in nome_lower:
                        return nome_lower.replace(sub, grego)
        
        return nome_lower
    
    def get_categoria(self, categoria):
        if not self.data:
            return []
        return self.data.get('categories', {}).get(categoria, [])
    
    def get_all(self):
        if not self.data:
            return []
        todos = []
        for categoria, compostos in self.data.get('categories', {}).items():
            todos.extend(compostos)
        return todos
    
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
                # Usar normalização
                comp_norm = self.normalizar_composto(composto)
                if termo in comp_norm or termo in composto.lower():
                    resultados.append({
                        'nome': composto,
                        'categoria': categoria,
                        'funcoes': self.functions.get(composto, {})
                    })
        return resultados
    
    def get_funcoes(self, composto):
        """Retorna as funções de um composto"""
        return self.functions.get(composto, {})
    
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

# Instância global
db = DatabaseManager()
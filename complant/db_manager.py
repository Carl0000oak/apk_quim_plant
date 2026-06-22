import requests
import json

class DatabaseManager:
    def __init__(self):
        self.url = "https://raw.githubusercontent.com/Carl0000oak/apk_quim_plant/main/complant/data/compounds.json"
        self.data = None
    
    def baixar(self):
        try:
            response = requests.get(self.url, timeout=10)
            self.data = response.json()
            return True
        except:
            return False
    
    def get_categorias(self):
        if not self.data:
            return []
        return list(self.data.get('categories', {}).keys())

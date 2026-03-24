import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GitHubClient:
    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
        else:
            logging.warning("No se encontró GITHUB_TOKEN. El límite de peticiones será muy estricto.")

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _handle_rate_limit(self, response):
        """Revisa si nos quedamos sin peticiones y pausa el programa si es necesario."""
        if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
            reset_time = int(response.headers['X-RateLimit-Reset'])
            current_time = int(time.time())
            sleep_time = max(reset_time - current_time, 0) + 5 # 5 segundos de margen
            
            logging.warning(f"Límite de API alcanzado. Durmiendo por {sleep_time} segundos...")
            time.sleep(sleep_time)
            return True # Indica que hubo un rate limit
        return False

    def _make_request(self, url, params=None):
        """Hace la petición HTTP y maneja errores y rate limits automáticamente."""
        while True:
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            
            if self._handle_rate_limit(response):
                continue # Si hubo rate limit y ya dormimos, reintentamos la misma URL
                
            logging.error(f"Error {response.status_code} al consultar {url}: {response.text}")
            return None

    def get_top_repositories(self, language, page=1, per_page=10):
        url = "https://api.github.com/search/repositories"
        params = {
            "q": f"language:{language}",
            "sort": "stars",
            "order": "desc",
            "page": page,
            "per_page": per_page
        }
        logging.info(f"Buscando top repositorios para {language} (Página {page})...")
        return self._make_request(url, params=params)

    def get_repository_tree(self, owner, repo, default_branch="main"):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}"
        params = {"recursive": 1}
        logging.info(f"Obteniendo árbol de archivos para {owner}/{repo}...")
        
        data = self._make_request(url, params=params)
        if data and "tree" in data:
            return data["tree"]
        return []

    def download_raw_file(self, raw_url):
        """Descarga el contenido en texto plano de un archivo."""
        while True:
            response = self.session.get(raw_url)
            
            if response.status_code == 200:
                return response.text
                
            if self._handle_rate_limit(response):
                continue
                
            return None
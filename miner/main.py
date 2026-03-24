import time
import logging
from github_client import GitHubClient
from code_parser import extract_python_methods, extract_java_methods
from text_processor import extract_words
from publisher import WordPublisher

logging.basicConfig(level=logging.INFO, format='%(message)s')
publisher = WordPublisher()

def run_miner():
    client = GitHubClient()
    languages = ["python", "java"]
    page = 1
    
    while True:
        for lang in languages:
            logging.info(f"\n{'='*40}\nBuscando repositorios de {lang.upper()} (Página {page})\n{'='*40}")
            
            # se traen los repos más populares
            repos_data = client.get_top_repositories(lang, page=page, per_page=2) # Usamos 2 para probar rápido
            
            if not repos_data or "items" not in repos_data:
                logging.warning("No se pudieron obtener los repositorios. Reintentando en breve...")
                time.sleep(10)
                continue
                
            for repo in repos_data["items"]:
                owner = repo["owner"]["login"]
                repo_name = repo["name"]
                branch = repo.get("default_branch", "main")
                
                logging.info(f"\n[+] Procesando Repo: {owner}/{repo_name}")
                
                # se obtiene el árbol de archivos
                tree = client.get_repository_tree(owner, repo_name, branch)
                if not tree:
                    continue
                    
                # se filtran los archivos que nos interesan (.py o .java)
                ext = ".py" if lang == "python" else ".java"
                files_to_process = [f for f in tree if f["path"].endswith(ext) and f["type"] == "blob"]
                
                logging.info(f"    Encontrados {len(files_to_process)} archivos {ext}")
                
                # se limita a procesar los primeros 5 archivos del repo
                for file_info in files_to_process[:5]:
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{file_info['path']}"
                    
                    # se descarga el código fuente completo
                    source_code = client.download_raw_file(raw_url)
                    if not source_code:
                        continue
                        
                    # se extraen los identificadores
                    if lang == "python":
                        method_names = extract_python_methods(source_code)
                    else:
                        method_names = extract_java_methods(source_code)
                        
                    # se limpian y preparan las palabras
                    for name in method_names:
                        clean_words = extract_words(name)
                        
                        if clean_words:
                           publisher.publish(clean_words, lang)
                            
        page += 1
        logging.info("\nPasando a la siguiente página de popularidad en 5 segundos...")
        time.sleep(5)

if __name__ == "__main__":
    try:
        run_miner()
    except KeyboardInterrupt:
        logging.info("\nMiner detenido por el usuario.")
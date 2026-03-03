import requests
import time
import csv
import random
import concurrent.futures
from bs4 import BeautifulSoup

# Configurações globais
# O User-Agent é essencial para evitar bloqueios do IMDB
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
}

# Número máximo de threads para processamento paralelo
MAX_THREADS = 15

def extract_movie_details(movie_url):
    """
    Extrai detalhes de um filme específico a partir de sua URL no IMDB.
    """
    try:
        # Pequeno delay aleatório para simular comportamento humano e evitar rate limit
        time.sleep(random.uniform(0.1, 0.3))
        
        response = requests.get(movie_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extração do Título (usando seletores baseados na estrutura atual do IMDB)
        title_tag = soup.find('span', {'data-testid': 'hero__primary-text'})
        title = title_tag.get_text().strip() if title_tag else "N/A"
        
        # Extração do Ano/Data
        # O IMDB agrupa ano, classificação indicativa e duração em uma lista
        meta_tags = soup.find('ul', {'class': 'ipc-inline-list ipc-inline-list--show-dividers sc-d8941411-2 iJqZxw baseAlt'})
        year = "N/A"
        if meta_tags:
            items = meta_tags.find_all('li')
            if items:
                year = items[0].get_text().strip()
        
        # Extração da Nota (Rating)
        rating_tag = soup.find('span', {'class': 'sc-bde20123-1 cCByYl'})
        rating = rating_tag.get_text().strip() if rating_tag else "N/A"
        
        # Extração da Sinopse (Plot)
        plot_tag = soup.find('span', {'data-testid': 'plot-xs_to_m'})
        plot = plot_tag.get_text().strip() if plot_tag else "N/A"
        
        print(f"Processado: {title} ({year}) - Nota: {rating}")
        return [title, year, rating, plot]
        
    except Exception as e:
        print(f"Erro ao processar {movie_url}: {e}")
        return None

def main():
    print("Iniciando extração de filmes populares do IMDB...")
    start_time = time.time()
    
    # URL dos filmes mais populares
    base_url = 'https://www.imdb.com'
    popular_url = f'{base_url}/chart/moviemeter/'
    
    try:
        response = requests.get(popular_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Localiza os links dos filmes na lista
        # A estrutura do IMDB usa data-testid para facilitar a localização
        movie_tags = soup.find_all('a', {'class': 'ipc-title-link-wrapper'})
        
        # Limitamos a 50 filmes para demonstração rápida e eficiente
        movie_links = [base_url + tag['href'].split('?')[0] for tag in movie_tags[:50]]
        
        print(f"Encontrados {len(movie_links)} filmes. Iniciando processamento com {MAX_THREADS} threads...")
        
        # Execução Multithreading
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            # Mapeia a função de extração para a lista de links
            future_to_url = {executor.submit(extract_movie_details, url): url for url in movie_links}
            for future in concurrent.futures.as_completed(future_to_url):
                data = future.result()
                if data:
                    results.append(data)
        
        # Salvando os resultados em CSV
        with open('exercicio_ebac_movies.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Título', 'Ano', 'Nota', 'Sinopse'])
            writer.writerows(results)
            
        end_time = time.time()
        print(f"\nTarefa concluída com sucesso!")
        print(f"Total de filmes salvos: {len(results)}")
        print(f"Tempo total de execução: {end_time - start_time:.2f} segundos")
        
    except Exception as e:
        print(f"Erro na execução principal: {e}")

if __name__ == "__main__":
    main()

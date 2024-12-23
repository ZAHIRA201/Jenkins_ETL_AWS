import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import requests

# Fonction pour scrapper PubMed
def scrape_pubmed():
    itemfull = []
    for i in range(1, 320):  # Nombre de pages à parcourir
        url = "https://pubmed.ncbi.nlm.nih.gov/?term=drone&page=" + str(i)
        p = requests.get(url)
        soup = BeautifulSoup(p.content, 'html.parser')
        content = soup.find_all('div', class_='docsum-wrap')
        for item in content:
            title = item.find('a', class_='docsum-title')
            author = item.find('span', class_='docsum-authors full-authors')
            citation = item.find('div', class_='docsum-citation full-citation')
            pmid = item.find('span', class_='docsum-pmid')
            abstract = item.find("div", class_="full-view-snippet")
            url_article = 'https://pubmed.ncbi.nlm.nih.gov/' + str(pmid.text) + '/'
            itemfull.append({
                'Source': 'PubMed',
                'Title': title.text.strip(),
                'Author': author.text.strip(),
                'ID': pmid.text.strip(),
                'Abstract': abstract.text.strip(),
                'URL': url_article.strip()
            })
    return itemfull

# Fonction pour scrapper Google Patent
def scrape_google_patent():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    base_url = "https://patents.google.com/?q=(drone)&num=100&oq=drone&page="
    num_pages = 300

    patent_results = []

    for page in range(1, num_pages + 1):
        url = base_url + str(page)
        driver.get(url)
        time.sleep(5)  # Attendez que la page se charge complètement

        soup = BeautifulSoup(driver.page_source, "html.parser")

        for el in soup.select("search-result-item"):
            title = el.select_one("h3").get_text()
            link = "https://patents.google.com/" + el.select_one("state-modifier")['data-result']
            image_url = el.select_one('img')['src']
            metadata = ' '.join(el.select_one('h4.metadata').get_text().split())
            date = el.select_one('h4.dates').get_text().strip()
            snippet = el.select_one('span#htmlContent').get_text()

            # Extraction de l'auteur
            author = el.select_one('span.item-assignee').get_text().strip() if el.select_one(
                'span.item-assignee') else ''

            # Extraction de l'URL du brevet
            patent_url = el.select_one('a.style-scope.patent-result')['href'] if el.select_one(
                'a.style-scope.patent-result') else ''

            # Extraction de l'inventeur
            inventor_element = el.select_one('state-modifier')
            inventor = inventor_element['data-inventor'] if inventor_element and 'data-inventor' in inventor_element.attrs else ''

            # Extraction de l'abstract
            abstract_element = el.select_one('section#abstract')
            abstract = abstract_element.find('div', class_='abstract').text.strip() if abstract_element else ''

            # Extraction de l'ID du brevet
            patent_id = el.select_one('h2#pubnum').text.strip() if el.select_one('h2#pubnum') else ''

            # Ajoutez 'PatentID', 'PatentAuthor', 'Inventor' et 'Abstract' à patent_results
            patent_results.append({
                'Source': 'Google Patent',
                'Title': title,
                'URL': link,
                'Image': image_url,
                'Metadata': metadata,
                'Date': date,
                'Snippet': snippet,
                'ID': patent_id,  # ID du brevet de Google Patent
                'Author': author,  # Inventeur du brevet de Google Patent
                'Abstract': abstract  # Abstract du brevet de Google Patent
            })

    driver.quit()

    return patent_results




# Charger les données de Patent Scope depuis le fichier CSV
patent_scope_data = pd.read_csv("C:/Users/chaym/Desktop/S4/Big Data/big_data_project/drones_data.csv")

# Appel des fonctions pour scrapper les deux sources
pubmed_data = scrape_pubmed()
google_patent_data = scrape_google_patent()

# Ajouter une colonne 'Source' avec la valeur statique 'Patent Scope'
patent_scope_data = patent_scope_data.assign(Source='Patent Scope')

# Charger les données de Patent Scope depuis le fichier CSV
patent_scope_data = pd.read_csv("C:/Users/chaym/Desktop/S4/Big Data/big_data_project/drones_data.csv")

# Appel des fonctions pour scrapper les deux sources
pubmed_data = scrape_pubmed()
google_patent_data = scrape_google_patent()

# Renommer les colonnes de Patent Scope pour les harmoniser avec les autres sources
patent_scope_data = patent_scope_data.rename(columns={
    'abstract': 'Abstract',
    'basic_patent_date': 'Date',
    'inventor': 'Author',
    'publication_number': 'ID',
    'title_original': 'Title'
})

# Ajouter la colonne 'Source'
patent_scope_data['Source'] = 'Patent Scope'

# Sélectionner les colonnes spécifiées dans l'ordre désiré
patent_scope_data = patent_scope_data[['Source','Abstract', 'Date', 'cited_patents', 'dwpi_family_kind', 'dwpi_family_members_count', 'first_claim', 'Author', 'ID', 'related_application_numbers', 'Title']]


# Concaténer les données
combined_data = pd.concat([pd.DataFrame(pubmed_data), pd.DataFrame(google_patent_data), patent_scope_data], ignore_index=True)


# Spécifier toutes les colonnes possibles
all_columns = ['Source', 'Title', 'Author', 'ID', 'Abstract', 'URL', 'Image', 'Metadata', 'Date', 'Snippet',
            'cited_patents','dwpi_family_kind','dwpi_family_members_count','first_claim',
            'related_application_numbers']

# Remplacer les valeurs manquantes par une chaîne vide
combined_data = combined_data.reindex(columns=all_columns, fill_value='')

# Enregistrer les données dans un fichier CSV
combined_data.to_csv('combined_data2.csv', index=False)

print('Data saved to CSV file: combined_data2.csv')
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import spacy
from langdetect import detect
import uuid # Importer le module uuid pour la génération de noms de fichiers uniques
import random as rd

# Liste des User Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]

def extraire_mots_cles_fr(requete):
    """
    Fonction pour extraire les mots-clés à partir de la requête de l'utilisateur en français.
    
    Arguments :
        - requete : La requête de l'utilisateur
        
    Returns :
        - mots_cles_format : Les mots-clés formatés sous forme de chaîne de caractères
    """
    nlp = spacy.load("fr_core_news_sm")
    requete_utilisateur = requete.lower()
    doc = nlp(requete_utilisateur)
    mots_cles = []
    for token in doc:
        if (token.pos_ == "NOUN" and token.dep_ not in ["ROOT","obj"]) or \
           (token.pos_ == "ADV" ) or \
           (token.pos_ == "PRON" and token.dep_ != "dep") or \
           (token.dep_ == "ROOT" and token.pos_ not in ["NOUN","VERB"]) or \
           (token.pos_ == "ADJ" ) or \
           (token.pos_ == "PROPN" and token.dep_ in ["nmod","punct"]):
            if not token.is_stop and not token.is_punct and token.text.lower() not in ['article', 'articles']:
                mots_cles.append(token.text)
    mots_cles_format = ' '.join(mots_cles)
    return mots_cles_format

def extraire_mots_cles_en(requete):
    """
    Fonction pour extraire les mots-clés à partir de la requête de l'utilisateur en anglais.
    
    Arguments :
        - requete : La requête de l'utilisateur
        
    Returns :
        - mots_cles_format : Les mots-clés formatés sous forme de chaîne de caractères
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(requete)
    mots_cles = []
    for token in doc:
        if (token.pos_ == "NOUN" ) or  (token.dep_ == "punct") or \
           (token.pos_ == "ADV") or (token.dep_ == "pobj") or \
           (token.pos_ == "PROPN" and token.dep_ != "dep") or \
           (token.pos_ == "ADJ" ) :
            if not token.is_stop and not token.is_punct and token.text.lower() not in ['article', 'articles']:
                mots_cles.append(token.text)
    mots_cles_format = ' '.join(mots_cles)
    return mots_cles_format

def detect_language(text):
    """
    Fonction pour détecter la langue d'un texte donné.
    
    Arguments :
        - text : Le texte à analyser
        
    Returns :
        - 'français' si la langue détectée est le français, sinon 'anglais'
    """
    lang = detect(text)
    if lang == 'fr':
        return 'français'
    else:
        return 'anglais'

def format_mot(motcle):
    """
    Fonction pour formater un mot-clé pour une utilisation dans une URL de recherche.
    
    Arguments :
        - motcle : Le mot-clé à formater
        
    Returns :
        - format_motcle : Le mot-clé formaté pour une URL de recherche
    """
    if ' ' in motcle:
        format_motcle = motcle.replace(' ', '+')
    else:
        format_motcle = motcle
    return format_motcle

def download_pdf_and_save(pdf_url, folder_name):
    """
    Fonction pour télécharger un fichier PDF depuis un URL et l'enregistrer dans un dossier spécifié.
    
    Arguments :
        - pdf_url : L'URL du fichier PDF à télécharger
        - folder_name : Le nom du dossier dans lequel enregistrer le fichier PDF
        
    Returns :
        - file_path : Le chemin du fichier enregistré
    """
    try:
        headers = {"User-Agent": rd.choice(user_agents)}
        response = requests.get(pdf_url, headers=headers, stream=True)
        response.raise_for_status()
        file_name = f"article_{uuid.uuid4()}.pdf"
        file_path = os.path.join(folder_name, file_name)
        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement du PDF {pdf_url}: {str(e)}")
        return None

def main():
    """
    Fonction principale du programme.
    """
    requete_utilisateur = input('Veuillez saisir votre requête : ')

    langue = detect_language(requete_utilisateur)

    if langue == 'français':
        mots_cles_format = extraire_mots_cles_fr(requete_utilisateur)
        print("Langue détectée ==> Français")
    else:
        mots_cles_format = extraire_mots_cles_en(requete_utilisateur)
        print("Langue détectée ==> Anglais")

    search_query = format_mot(mots_cles_format)

    num_pages = int(input("Entrez le nombre de pages à parcourir : "))
    folder_name = f"{search_query.replace('+', '-')}-{num_pages}"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    num_articles = 0  # Compteur d'articles téléchargés avec succès

    for page_num in range(1, num_pages+1):
        print(f"Page {page_num}")
        page_url = f"https://www.semanticscholar.org/search?q={search_query}&sort=relevance&page={page_num}"
        driver.get(page_url)
        time.sleep(5) 

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        pdf_links = soup.select('a[href$=".pdf"]')

        for link in pdf_links:
            pdf_url = link["href"]
            #print("Téléchargement du PDF:", pdf_url)
            file_path = download_pdf_and_save(pdf_url, folder_name)
            if file_path:
                num_articles += 1
                #print(f"Enregistré sous: {file_path}")

    driver.quit()

    print(f"Nombre total d'articles téléchargés avec succès : {num_articles}")

if __name__ == "__main__":
    main()

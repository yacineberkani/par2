from bs4 import BeautifulSoup
import requests
import urllib.request, urllib.parse, urllib.error
import re
import ssl
import json
import calendar
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy


def extraire_mots_cles(requete):

    nlp = spacy.load("fr_core_news_sm")
    
    requete_utilisateur = requete.lower()

    doc = nlp(requete_utilisateur)

    mots_cles = []
    for token in doc:

        if (token.pos_ == "NOUN" and token.dep_ not in ["ROOT"]) or \
           (token.pos_ == "ADV" and token.dep_ != "advmod") or \
           (token.pos_ == "PRON" and token.dep_ != "dep") or \
           (token.dep_ == "ROOT" and token.pos_ not in ["NOUN","VERB"]) or \
           token.pos_ == "ADJ" or \
           (token.pos_ == "PROPN" and token.dep_ in ["nmod","punct"]):

            if not token.is_stop and not token.is_punct:
                mots_cles.append(token.text)
    

    mots_cles = [mot for mot in mots_cles if mot.lower() != 'article']
    mots_cles_format = ' '.join(mots_cles)
    
    return mots_cles_format

def format_mot(motcle):
    if ' ' in motcle:
        format_motcle = motcle.replace(' ', '+')
    else:
        format_motcle = motcle
    return format_motcle

def strip_brackets(s): 
    no_brackets = "" 
    dont_want = ['[', ']']
    for char in s: 
        if char not in dont_want:
            no_brackets += char
    return no_brackets 

def get_bibliography(soup):
    article = soup.find('article')
    journal = soup.find('journal')
    listauteur = article.find('authorlist')
    auteur = ""
    if listauteur:
        initials = listauteur.find_all('initials')
        lastnames = listauteur.find_all('lastname')
        for i in range(len(lastnames)):
            if i < len(initials):
                initial = initials[i].text
                auteur += initial
                auteur += '. '
            else:
                auteur += ' '
            nom = lastnames[i].text
            auteur += nom
            if i == len(lastnames) - 2:
                auteur += ' and '
            elif i != len(lastnames) - 1:
                auteur += ', '
        auteur += ", "

    titreArticle = ''
    if article.find('articletitle'):
            titreArticle = '"'
            titre_str = article.find('articletitle').text
            titre_str = strip_brackets(titre_str)
            titreArticle  += titre_str
            if titreArticle [-1] == '.':
                titreArticle  += ''
            else:
                titreArticle  += '.'           
    titreJournal = ''
    if journal.find('title'):
        titreJournal = journal.find('title').text
        titreJournal += ' '
     
    JournalIssue = journal.find('journalissue')
    month = JournalIssue.find('month')
    date = ''
    if month:
        month = JournalIssue.find('month').text
        if len(month)<3:
            month_int = int(str(month))
            month = calendar.month_abbr[month_int]
        year = JournalIssue.find('year').text
        date = '('
        date += month
        date += '. '
        date += year
        date += '). '
    elif JournalIssue.find('year'):
        date = '('
        date += JournalIssue.find('year').text
        date += '). '      
    else: ''

    if soup.find('articleid'):
        doi_pii = article.find_all('elocationid')
        doi_pii_str = ""
        if len(doi_pii)>1:
            if 'doi' in str(doi_pii[0]):
                doi_pii = doi_pii[0].text
                doi_pii_str += "DOI "
                doi_pii_str += doi_pii
                doi_pii_str += "."
            elif 'doi' in str(doi_pii[1]):
                doi_pii = doi_pii[1].text
                doi_pii_str += "DOI "
                doi_pii_str += doi_pii
                doi_pii_str += "."
        elif len(doi_pii) == 1:
            if 'doi' in str(doi_pii[0]):
                doi_pii = doi_pii[0].text
                doi_pii_str += "DOI "
                doi_pii_str += doi_pii
                doi_pii_str += "."
            elif 'pii' in str(doi_pii[0]):
                doi_pii = doi_pii[0].text
                doi_pii_str += "PII "
                doi_pii_str += doi_pii
                doi_pii_str += "."
    
    resume = ''
    if article.find('abstracttext'):
        resume = article.find('abstracttext').text
    
    result = []
    result.append(auteur)
    result.append(titreArticle)
    result.append(titreJournal)
    result.append(date)
    result.append(doi_pii_str)
    result.append(resume)

    return result

def get_pubmed_ids(url, num):
    pageweb = urllib.request.urlopen(url).read()
    dict_page = json.loads(pageweb)
    return dict_page["esearchresult"]["idlist"]

def get_article_data(pubmed_ids):
    articles_data = []
    for link in pubmed_ids:
        url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=idlist"
        url = url.replace('idlist', link)
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        article = get_bibliography(soup)
        lien = f"https://www.ncbi.nlm.nih.gov/pubmed/{link}"
        article.append(lien) 
        articles_data.append(article)
    return articles_data

def calculate_similarity(keyword, article_titles):
    keyword_vector = [keyword]
    corpus = keyword_vector + article_titles
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
    keyword_tfidf_vector = tfidf_matrix[0]
    article_titles_tfidf_matrix = tfidf_matrix[1:]
    cosine_similarities = cosine_similarity(keyword_tfidf_vector, article_titles_tfidf_matrix)
    return cosine_similarities.flatten()

def main():
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=NUM&sort=relevance&term=KEYWORD"
    mot_cle = str(input('Veuillez saisir votre requête : '))
    motcle  = extraire_mots_cles(mot_cle)
    num = int(input('Nombre de résultats souhaitez : '))
    url = url.replace('NUM', str(num))
    url = url.replace('KEYWORD', format_mot(motcle))

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    pubmed_ids = get_pubmed_ids(url, num)
    articles_data = get_article_data(pubmed_ids)
    df = pd.DataFrame(articles_data)
    df.columns = ['Auteur', 'Nom_Article', 'Journal', 'Date', 'DOI', 'Résume', 'lien']
    
    
    similarity_scores = calculate_similarity(motcle, df['Nom_Article'].tolist())
    df['Similarité_Cosinus'] = similarity_scores

    file_name = motcle.replace(' ', '_') + '_' + str(num) + '.csv'
    df.to_csv(file_name)

    print("Fichier CSV enregistré avec succès.")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 21:12:04 2023

@author: corentin
"""


#use https://geekflare.com/global-news-api/
#https://geekflare.com/best-stock-market-api/

#https://alpaca.markets/docs/market-data/news/#content-related-queries

import requests

# Adresse de l'API de Reuters
url = 'https://api.reuters.com/articles'

# Clé d'API Reuters
api_key = 'YOUR_API_KEY'

# En-têtes de la requête HTTP
headers = {
    'X-Api-Key': api_key
}

# Paramètres de la requête
params = {
    'limit': 10,  # Nombre maximum d'articles à récupérer
    'sort_by': 'latest'  # Trier les articles par date de publication
}

# Envoyer la requête à l'API
response = requests.get(url, headers=headers, params=params)

# Vérifier que la réponse est correcte
if response.status_code == 200:
    # Récupérer les articles de la réponse
    articles = response.json()['articles']
    
    # Ouvrir le fichier .txt en mode écriture
    with open('articles.txt', 'w') as f:
        # Pour chaque article
        for article in articles:
            # Récupérer le titre, l'auteur, la date et le corps de l'article
            title = article['title']
            author = article['author']
            date = article['published_at']
            body = article['body']
            
            # Écrire le titre, l'auteur, la date et le corps de l'article dans le fichier
            f.write(f"Title: {title}\n")
            f.write(f"Author: {author}\n")
            f.write(f"Date: {date}\n")
            f.write(f"Body:\n{body}\n")
else:
    print("Une erreur s'est produite lors de la récupération des articles.")
    
    
from newsapi import NewsApiClient

# Init
newsapi = NewsApiClient(api_key='da52d31a65a84f2296c46f88038d6c41')

# /v2/top-headlines
top_headlines = newsapi.get_top_headlines(q='Crypto',
                                          #sources='bbc-news,the-verge',
                                          )
                                          #country='us
                                          
                                          
top_h = newsapi.get_top_headlines()

# /v2/everything
all_articles = newsapi.get_everything(q='bitcoin',
                                      #sources='bbc-news,the-verge',
                                      #domains='bbc.co.uk,techcrunch.com',
                                      from_param='2022-12-09',
                                      to='2022-12-12',
                                      language='en',
                                      sort_by='relevancy',
                                      page=2)

# /v2/top-headlines/sources
sources = newsapi.get_sources()


from newsdataapi import NewsDataApiClient

# API key authorization, Initialize the client with your API key

api = NewsDataApiClient(apikey="pub_15487c95330fc171fb1e49b8a924454dc5a80")

# You can pass empty or with request parameters {ex. (country = "us")}

response = api.news_api( q= "crypto")





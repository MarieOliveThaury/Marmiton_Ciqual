import requests
from bs4 import BeautifulSoup
import lxml
import re
import numpy as np

def find_all_recipes(search : str): 
#returns a list with all the url of the recipes corresponding to the research
    
    #making the research compatible with an url  : 
    key_word = search.lower().replace(' ', '-')
    first_url = "https://www.marmiton.org/recettes/recherche.aspx?aqt=" + key_word
    
    #going to the first proposals (i.e. the first proposal page) for key_word : 
    current_page = BeautifulSoup(requests.get(first_url).text) 
    
    #1 : getting all the urls for the proposal pages : 
    list_url = [first_url]
    for url in list_url :
        current_page = BeautifulSoup(requests.get(url).text)
        found_pages = current_page.findAll('a', {'class' : 'SHRD__sc-1ymbfjb-1 MTkAM'})
        for page in found_pages : 
            new_url = "https://www.marmiton.org" + page.get('href')
            if new_url not in list_url : 
                list_url.append(new_url)
    
    #2 : getting all the urls for the recipe pages : 
    list_recipes_url = []
    for url in list_url : 
        current_page = BeautifulSoup(requests.get(url).text)
        found_recipes = current_page.findAll('a', {'class' : 'MRTN__sc-1gofnyi-2 gACiYG'})
        for recipe in found_recipes:
            href = recipe.get('href')
            if href[0:17] == '/recettes/recette' : 
            #sometimes, marmiton proposes albums, or videos without recipes instead of recipes
                new_url = "https://www.marmiton.org" + href
                list_recipes_url.append(new_url)
                
    return list_recipes_url
    
            
                
    
    
    
    
    
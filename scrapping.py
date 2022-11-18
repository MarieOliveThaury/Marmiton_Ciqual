import requests
from bs4 import BeautifulSoup
import lxml
import re
import numpy as np

def find_all_dishes(search : str): 
#returns a list with all the url of the recipes corresponding to the research
    
    #making the research compatible with an url  : 
    key_word = search.lower().replace(' ', '-')
    first_url = "https://www.marmiton.org/recettes/recherche.aspx?aqt=" + key_word
    
    #going to the first proposals (i.e. the first proposal page) for key_word : 
    current_page = BeautifulSoup(requests.get(first_url).text) 
    
    #1 : getting all the urls for the proposal pages : 
    list_url = [first_url]
    for url in list_url :
        current_page = BeautifulSoup(requests.get(url).text, features="lxml")
        found_pages = current_page.findAll('a', {'class' : 'SHRD__sc-1ymbfjb-1 MTkAM'})
        #all the links that appear on the current page to go to other pages 
        for page in found_pages : 
            new_url = "https://www.marmiton.org" + page.get('href')
            if new_url not in list_url : 
                list_url.append(new_url)
    
    #2 : getting all the urls for the recipe pages : 
    list_dishes_url = []
    for url in list_url : 
        current_page = BeautifulSoup(requests.get(url).text)
        found_dishes = current_page.findAll('a', {'class' : 'MRTN__sc-1gofnyi-2 gACiYG'})
        #all the recipes found on the current page 
        for dish in found_dishes:
            href = dish.get('href')
            if href[0:17] == '/recettes/recette' : 
            #sometimes, marmiton proposes albums, or videos without recipes instead of recipes
                new_url = "https://www.marmiton.org" + href
                list_dishes_url.append(new_url)
                
    return list_dishes_url
    
    
def find_recipe(dish_url : str): 
    
    soup = BeautifulSoup(requests.get(dish_url).text))
    ingredients_table = soup.find('div', {'class' : 'MuiGrid-root RCP__sc-vgpd2s-6 ghZzUe MuiGrid-container MuiGrid-spacing-xs-2'})
    
    #1 : for the ingredients 
    ingredients1 = ingredients_table.findAll('span', {'class' : 'RCP__sc-8cqrvd-3 itCXhd'})
    ingredients2 = ingredients_table.findAll('span', {'class' : 'RCP__sc-8cqrvd-3 cDbUWZ'})
    ingredients = ingredients1 + ingredients2
    ingredients_names = []
    for ingredient in ingredients:
        ingredient_name = ingredient.string
        ingredients_names.append(ingredient_name)
    
    #2: for the quantites
    qte = ingredients_table.findAll('span', {'class' : 'SHRD__sc-10plygc-0 epviYI'})
    qtes = []
    for q in qte:
        string = q.text.replace("\xa0", "")
        qtes.append(string)
        
    #3: creating a dictionnary for the recipe : 
    recipe = {}
    for i in range (len(ingredients_names)) :
        recipe[ingredients_names[i]] = qtes[i]
    
    return recipe 
            
                
    
    
    
    
    
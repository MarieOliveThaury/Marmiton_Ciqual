import requests
from bs4 import BeautifulSoup
import lxml
import re
import numpy as np
from tqdm.auto import tqdm

def find_all_dishes(search : str): 
#returns a list with all the url of the recipes corresponding to the research
    
    #making the research compatible with an url  : 
    key_word = search.lower().replace(' ', '-')
    first_url = "https://www.marmiton.org/recettes/recherche.aspx?aqt=" + key_word
    
    #going to the first proposals (i.e. the first proposal page) for key_word : 
    current_page = BeautifulSoup(requests.get(first_url).text, features="lxml") 
    
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
        current_page = BeautifulSoup(requests.get(url).text, features="lxml")
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
#returns a list corresponding to the url containing : 
#1) the name of the recipe 
#2) a dictionnary with the recipe 
    
    soup = BeautifulSoup(requests.get(dish_url).text,features="lxml")
    
    #0 : for the title of the recipe : 
    recipe_title = soup.find('h1', {'class' : 'SHRD__sc-10plygc-0 itJBWW'})
    recipe_title = recipe_title.get_text(separator="") 
    
    
    #1 : for the ingredients
    
    ingredients_cells = soup.findAll('div', {'class' : 'MuiGrid-root MuiGrid-item MuiGrid-grid-xs-3 MuiGrid-grid-sm-3'})
    ingredients_names = []
    for cell in ingredients_cells:
        ingredient = cell.findAll('span', {'class' : 'RCP__sc-8cqrvd-3 itCXhd'})
        if len(ingredient) == 0:
            ingredient = cell.findAll('span', {'class' : 'RCP__sc-8cqrvd-3 cDbUWZ'})
        ingredients_names.append(ingredient[0].string)
    
    #2: for the quantites
    qte = soup.findAll('span', {'class' : 'SHRD__sc-10plygc-0 epviYI'})
    qtes = []
    for q in qte:
        string = q.text.replace("\xa0", "")
        qtes.append(string)
        
    #3: creating a dictionnary for the recipe : 
    recipe = {}
    for i in range (len(ingredients_names)) :
        recipe[ingredients_names[i]] = qtes[i]
    
    #4 : for the number of people : 
    nb_people = soup.find('span', {'class' : 'SHRD__sc-w4kph7-4 knYsyq'})
    nb_people = nb_people.get_text(separator="")
    
    return recipe_title, recipe, nb_people
            
def find_all_recipes(search : str) : 
#returns a dictionnary with all the the recipes corresponding to the research
    
    list_dishes_url = find_all_dishes(search)
    all_recipes = {}
    for dish in tqdm(list_dishes_url) : 
        all_recipes[find_recipe(dish)[0]] = {'recette' : find_recipe(dish)[1], 'nombre de personnes' : find_recipe(dish)[2]}
        #we should add other features like the mark, the nb of people, the number of opinions...
    
    return all_recipes
        
                
    
    
    
    
    
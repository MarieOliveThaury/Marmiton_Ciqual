import requests
from bs4 import BeautifulSoup
import html.parser
import re
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from tools.data_tools import * 
from tools.conversion_tools import *


def find_all_dishes(search : str, N : int): 
    """
    Args:
        search (str) : raw text corresponding to the user's search 
        N (int) : how many recipe proposals the algorithm returns 

    Returns:
        list_dishes_url (list) : list with the urls of the N recipes 
    """
    
    #making the research compatible with an url  : 
    key_word = search.lower().replace(' ', '-')
    first_url = "https://www.marmiton.org/recettes/recherche.aspx?aqt=" + key_word
    
    #going to the first proposals (i.e. the first proposal page) for key_word : 
    current_page = BeautifulSoup(requests.get(first_url).text, features="html.parser") 
    
    #1 : getting all the urls for the proposal pages : 
    list_url = [first_url]
    n = 12 #on average, a proposal page contains 12 recipes
    for url in list_url :
        if n < N :
            current_page = BeautifulSoup(requests.get(url).text, features="html.parser")
            found_pages = current_page.findAll('a', {'class' : 'SHRD__sc-1ymbfjb-1 MTkAM'})
            #all the links that appear on the current page to go to other pages 
            for page in found_pages : 
                new_url = "https://www.marmiton.org" + page.get('href')
                if new_url not in list_url : 
                    list_url.append(new_url)
            n += 12
    
    #2 : getting all the urls for the recipe pages : 
    list_dishes_url = []
    for url in list_url : 
        current_page = BeautifulSoup(requests.get(url).text, features="html.parser")
        found_dishes = current_page.findAll('a', {'class' : 'MRTN__sc-1gofnyi-2 gACiYG'})
        #all the recipes found on the current page
        for dish in found_dishes:
            href = dish.get('href')
            if href[0:17] == '/recettes/recette' : 
            #sometimes, marmiton proposes albums, or videos without recipes instead of recipes
                new_url = "https://www.marmiton.org" + href
                if len(list_dishes_url) < N:
                    list_dishes_url.append(new_url)
                
    return list_dishes_url
    
    
def find_recipe(dish_url : str): 
    """
    Args:
        dish_url (str) : text corresponding to a url of a marmiton's recipe 

    Returns : a list with : 
        recipe_title (str) : name of the recipe 
        recipe (dict) : dictionary whose keys are the ingredients and values are the quantities 
        nb_people (float) : number of people 
    """
    
    soup = BeautifulSoup(requests.get(dish_url).text,features="html.parser")
    
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
    nb_people = soup.find('span', {'class' : 'SHRD__sc-w4kph7-4 knYsyq'}) or soup.find('span', {'class' : 'SHRD__sc-w4kph7-4 hYSrSW'}) or '4' 
    #by default, we say that the recipe is for 4 persons 
    if nb_people != '4' : 
        nb_people = nb_people.get_text(separator="")
    nb_people = float(nb_people)
    
    return recipe_title, recipe, nb_people
            
def find_all_recipes(search : str, N : int) : 
    """
    Args:
        search (str) : raw text corresponding to the user's search 
        N (int) : how many recipe proposals the algorithm returns 

    Returns :
        full_df (pandas DataFrame) : a table with the name of the recipe, the recipe and the number of people for the N marmiton's proposed recipes for the user's search
    """
    
    print("Etape 1 : récupération des recettes que vous propose Marmiton pour : ", search)
    
    list_dishes_url = find_all_dishes(search, N)
    all_recipes = {}
    for dish in tqdm(list_dishes_url) : 
        all_recipes[find_recipe(dish)[0]] = {'lien' : dish,'recette' : find_recipe(dish)[1], 'nombre de personnes' : find_recipe(dish)[2]}
        #we should add other features like the mark, the nb of people, the number of opinions...
        
    recipes_names = list(all_recipes.keys())
    conversion(all_recipes)
    df_recipes = []
    for i in range(len(recipes_names)):
        dict_recipe = all_recipes[recipes_names[i]]
        ingredients = list(dict_recipe['recette'].keys())
        qtes = list(dict_recipe['recette'].values())
    
        dict_iq = {'Ingrédient' : ingredients, 'Quantités' : qtes}
        df = pd.DataFrame(dict_iq)
        df['Nom recette'] = recipes_names[i]
    
        df_recipes.append(df)
    
    full_df = pd.concat(df_recipes, axis=0, ignore_index=True)
    full_df = full_df.reindex(columns=['Nom recette', 'Ingrédient', 'Quantités'])
    full_df = full_df.rename(columns = {'Ingrédients' : 'Ingrédient', 'Quantités' : 'Quantité'})
    full_df['Ingrédient'] = full_df['Ingrédient'].apply(lambda x: no_accent_and_sg(x))
    
    print("Les recettes proposées par Marmiton ont été récupérées !\n") 
    
    return full_df
        
                
print("scraping_marmiton importé ! ")
    
    
    
    

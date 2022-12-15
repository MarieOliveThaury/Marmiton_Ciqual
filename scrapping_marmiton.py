import requests
from bs4 import BeautifulSoup
import html.parser
import re
import numpy as np
from tqdm.auto import tqdm
import pandas as pd

corres = open("Poids.txt", "r")
poids=corres.readlines()
dicopoids={}
for ligne in poids:
    dicopoids[str(''.join(z for z in ligne if not z.isdigit()).replace(" \n", "").lower())]=int("".join(re.findall('\d',str(ligne))))

corres2 = open("Quantificateurs.txt", "r")
quantif=corres2.readlines()
dicoquantif={}
for ligne in quantif:
    dicoquantif[str(''.join(z for z in ligne if not z.isdigit()).replace(" \n", "").lower())]=int("".join(re.findall('\d',str(ligne))))

def convert(dico):
    for x,y in dico.items():
        
            
                for k,v in y['recette'].items():
                    if type(v)==str:
                        if v != '':
                            if '⁄' in v:
                                if '1⁄4' in v:
                                    n=0.25
                                if '1⁄3' in v:
                                    n=0.33
                                if '1⁄2' in v:
                                    n=0.5
                                for a,b in dicopoids.items():
                                    if a in k:
                                        y['recette'].update({k:str(b*n)+"g"})
                                for a,b in dicoquantif.items():
                                    if l in ['.'+a,a,a+'s','.'+a+'s','⁄'+a,'⁄'+a+'s'] :
                                        y['recette'].update({k:str(b*n)+"g"})       
                            
                
                            else:
                                n=float(("".join(re.findall('\d',str(v)))))
                
                                l=str(''.join(z for z in v if not z.isdigit()))
                
                                if l not in ['g','.g']:    
                                    for a,b in dicopoids.items():
                                        if a in k:
                                            y['recette'].update({k:str(b*n)+"g"})
                                    for a,b in dicoquantif.items():
                                        if l in ['.'+a,a,a+'s','.'+a+'s','⁄'+a,'⁄'+a+'s'] :
                                            y['recette'].update({k:str(b*n)+"g"})       
                                        
                        elif v=="": #on définit une valeur standardisé pour les éléments manquants. Ces élements sont souvent utilisés en des quantités limitées.
                            y['recette'].update({k:str(2*int(y['nombre de personnes']))+"g"})
                
def keskimank(dico):
    for x,y in dico.items():
                for k,v in y['recette'].items():
                    l=str(''.join(z for z in v if not z.isdigit()))
                    if l not in ['.g','g']:

                        print(k,v)
def bouchetrou(dico):
    for x,y in dico.items():
                element=[]
                for k,v in y['recette'].items():
                    v=str(v)
                    l=str(''.join(z for z in v if not z.isdigit()))
                    if l not in ['.g','g']:
                        element=element+[k]
                        
                for a in element:
                    del y['recette'][a]

def usable(dico):
    for x,y in dico.items():
        for k,v in y['recette'].items():
                n=float(str(v).replace('g',''))
                y['recette'].update({k:float(n)})
                
def parpersonne(dico):
    for x,y in dico.items():
        for k,v in y['recette'].items():
                
                y['recette'].update({k:v/y['nombre de personnes']})
    

                
def conversion(dico):
    convert(dico)
    bouchetrou(dico)
    usable(dico)
    parpersonne(dico)
    
    

def find_all_dishes(search : str, nb_of_recipes : int): 
#returns a list with all the url of the recipes corresponding to the research
    
    #making the research compatible with an url  : 
    key_word = search.lower().replace(' ', '-')
    first_url = "https://www.marmiton.org/recettes/recherche.aspx?aqt=" + key_word
    
    #going to the first proposals (i.e. the first proposal page) for key_word : 
    current_page = BeautifulSoup(requests.get(first_url).text, features="html.parser") 
    
    #1 : getting all the urls for the proposal pages : 
    list_url = [first_url]
    for url in list_url :
        current_page = BeautifulSoup(requests.get(url).text, features="html.parser")
        found_pages = current_page.findAll('a', {'class' : 'SHRD__sc-1ymbfjb-1 MTkAM'})
        #all the links that appear on the current page to go to other pages 
        for page in found_pages : 
            new_url = "https://www.marmiton.org" + page.get('href')
            if new_url not in list_url : 
                list_url.append(new_url)
    
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
                if len(list_dishes_url) < nb_of_recipes:
                    list_dishes_url.append(new_url)
                
    return list_dishes_url
    
    
def find_recipe(dish_url : str): 
#returns a list corresponding to the url containing : 
#1) the name of the recipe 
#2) a dictionnary with the recipe 
    
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
            
def find_all_recipes(search : str, nb_of_recipes : int) : 
#returns a dataframe with all the the recipes corresponding to the research
    
    list_dishes_url = find_all_dishes(search, nb_of_recipes)
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
    
        dict_iq = {'Ingrédients' : ingredients, 'Quantités' : qtes}
        df = pd.DataFrame(dict_iq)
        df['Nom recette'] = recipes_names[i]
    
        df_recipes.append(df)
    
    full_df = pd.concat(df_recipes, axis=0, ignore_index=True)
    
    return full_df
        
                
    
    
    
    
    

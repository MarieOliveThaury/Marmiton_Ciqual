import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm.auto import tqdm
#from IPython.display import Image


def Pl_to_Sg(pluriel : str):
    
#Fonction qui met un mot au pluriel au singulier
#Attention, elle fonctionne pour le lexique de la nourriture mais n'est pas généralisable !

    #On s'occupe d'abord d'une liste d'exceptions
    #Aliments finissant par -ou et qui prennent un -x au pluriel
    except_ou = ['choux']
    #Aliments finissant par un -s même au singulier
    except_sg_s = ['anchois', 'brebis', 'jus', 'pois', 'radis']
    #Aliments qui s'emploient toujours au pluriel, qui n'existent pas vraiment au singulier...
    except_pl = ['rillettes']
    #Aliments en -al qui prennent un pluriel en -aux
    al_aux = ['chevaux', 'végétaux']

    #Désormais on traite tous les cas possibles
    if pluriel in except_pl:
        return pluriel
    elif pluriel in except_ou:
        return pluriel[:-1]
    elif pluriel[-3:] == 'aux':
        if pluriel[-4:] == 'eaux':
            return pluriel[:-1]
        else:
            if pluriel in al_aux:
                return pluriel[:-2] + 'l'
            else:
                return pluriel[:-1]
    elif pluriel[-1:] == 's':
        if pluriel in except_sg_s:
            return pluriel
        else:
            return pluriel[:-1]
    else:
        print(pluriel, 'n\'est pas référencé. Erreur possible.')
        return pluriel
    
#Problème : cette fonction ne marche que pour des mots isolés
#Gérer le cas des groupes nominaux


def get_nutrition_ingredient(ingredient : str) : 
    
    #gets the nutrition for one ingredient
    
    research_bar = driver.find_element("xpath", "//input[@id='champ-recherche']")
    research_bar.clear()
    research_bar.send_keys(Pl_to_Sg(ingredient))

    search_button = driver.find_element("xpath", "//a[@id='loupe']")
    search_button.click()

    nutrition = driver.find_elements("xpath", "//td")

    list_nutrition = [] 
    n = 0 
    for quality in nutrition :
        texte = quality.text
        if n%5 == 0 and texte != "":  #we have to add the fact that only select 5 or 6 criterias and avoid to take them all
            list_nutrition.append(texte)
        if n%5 == 1 and texte != "" : 
            if "<" in texte : 
                texte = "0"
            list_nutrition.append(float(texte.replace(',','.')))
        n += 1 

    return list_nutrition

def get_nutrition_recipe(recipe : dict) : 
    
    #gets the nutrition for all the ingredients of a recipe 
    #returns a dictionnary 
    
    chromedriver_autoinstaller.install() 
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome("chromedriver", options=chrome_options)
    
    driver.get('https://ciqual.anses.fr/')
    switch_to_french = driver.find_element(By.XPATH, "//a[@id='fr-switch']")
    driver.execute_script("arguments[0].click();", switch_to_french)
    
    ingredients = recipe.keys()
    
    dic_nutrition = {}
    for ingredient in range(tqdm(len(ingredients))) : 
        dic_nutrition(ingredient) = get_nutrition_ingredient(ingredient) 
    
    return dic_nutrition 

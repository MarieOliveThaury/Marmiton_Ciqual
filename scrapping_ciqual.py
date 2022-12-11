import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm.auto import tqdm
from IPython.display import Image
import time
import pandas as pd

#setting the driver 
chromedriver_autoinstaller.install() 
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')


#getting ciqual data : 

ciqual = "https://minio.lab.sspcloud.fr/mthaury/Ciqual.xls"

ciqual = pd.read_excel(ciqual)

ciqual.drop(['alim_grp_code', 'alim_ssgrp_code', 'alim_ssssgrp_code',
       'alim_grp_nom_fr', 'alim_ssgrp_nom_fr', 'alim_ssssgrp_nom_fr',
       'alim_code', 'alim_nom_sci',
       'Energie, Règlement UE N° 1169/2011 (kcal/100 g)',
       'Energie, N x facteur Jones, avec fibres  (kJ/100 g)',
       'Energie, N x facteur Jones, avec fibres  (kcal/100 g)',
       'Eau (g/100 g)', 'Protéines, N x facteur de Jones (g/100 g)', 'Fructose (g/100 g)',
       'Galactose (g/100 g)', 'Glucose (g/100 g)', 'Lactose (g/100 g)',
       'Maltose (g/100 g)', 'Saccharose (g/100 g)', 'Amidon (g/100 g)',
       'Fibres alimentaires (g/100 g)', 'Polyols totaux (g/100 g)',
       'Cendres (g/100 g)', 'Alcool (g/100 g)', 'Acides organiques (g/100 g)', 'AG monoinsaturés (g/100 g)',
       'AG polyinsaturés (g/100 g)', 'AG 4:0, butyrique (g/100 g)',
       'AG 6:0, caproïque (g/100 g)', 'AG 8:0, caprylique (g/100 g)',
       'AG 10:0, caprique (g/100 g)', 'AG 12:0, laurique (g/100 g)',
       'AG 14:0, myristique (g/100 g)', 'AG 16:0, palmitique (g/100 g)',
       'AG 18:0, stéarique (g/100 g)', 'AG 18:1 9c (n-9), oléique (g/100 g)',
       'AG 18:2 9c,12c (n-6), linoléique (g/100 g)',
       'AG 18:3 c9,c12,c15 (n-3), alpha-linolénique (g/100 g)',
       'AG 20:4 5c,8c,11c,14c (n-6), arachidonique (g/100 g)',
       'AG 20:5 5c,8c,11c,14c,17c (n-3) EPA (g/100 g)',
       'AG 22:6 4c,7c,10c,13c,16c,19c (n-3) DHA (g/100 g)',
       'Cholestérol (mg/100 g)','Calcium (mg/100 g)', 'Chlorure (mg/100 g)', 'Cuivre (mg/100 g)',
       'Fer (mg/100 g)', 'Iode (µg/100 g)', 'Magnésium (mg/100 g)',
       'Manganèse (mg/100 g)', 'Phosphore (mg/100 g)', 'Potassium (mg/100 g)',
       'Sélénium (µg/100 g)', 'Sodium (mg/100 g)', 'Zinc (mg/100 g)',
       'Rétinol (µg/100 g)', 'Beta-Carotène (µg/100 g)',
       'Vitamine D (µg/100 g)', 'Vitamine E (mg/100 g)',
       'Vitamine K1 (µg/100 g)', 'Vitamine K2 (µg/100 g)',
       'Vitamine C (mg/100 g)', 'Vitamine B1 ou Thiamine (mg/100 g)',
       'Vitamine B2 ou Riboflavine (mg/100 g)',
       'Vitamine B3 ou PP ou Niacine (mg/100 g)',
       'Vitamine B5 ou Acide pantothénique (mg/100 g)',
       'Vitamine B6 (mg/100 g)', 'Vitamine B9 ou Folates totaux (µg/100 g)',
       'Vitamine B12 (µg/100 g)'], axis = 1, inplace = True)

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
        #print(pluriel, 'n\'est pas référencé. Erreur possible.')
        return pluriel
    
#Problème : cette fonction ne marche que pour des mots isolés
#Gérer le cas des groupes nominaux

def clean(texte) : 
    if ("<" in texte) or (texte.isalpha()) or (texte =="-"): 
        texte = "0"
    return float(texte.replace(',', '.'))


###################################################################################
# la fonction ne gère pas encore le cas où ciqual ne trouve pas de correspondance #
###################################################################################


def get_nutrition_recipe(recipe : dict) : 
    
    # get the start time
    #st = time.time()
    
    #gets the nutrition for all the ingredients of a recipe 
    #returns a dataframe
    driver = webdriver.Chrome("chromedriver", options=chrome_options)
    
    driver.get('https://ciqual.anses.fr/')
    switch_to_french = driver.find_element(By.XPATH, "//a[@id='fr-switch']")
    driver.execute_script("arguments[0].click();", switch_to_french)
    
    ingredients = list(recipe.keys())
    print(ingredients) 
    
    df_nutrition = pd.DataFrame([]) 
    for i in tqdm(range(len(ingredients))) : 
        research_bar = driver.find_element("xpath", "//input[@id='champ-recherche']")
        research_bar.clear()
        time.sleep(1)
        research_bar.send_keys(Pl_to_Sg(ingredients[i]))
        time.sleep(1)
    
        search_button = driver.find_element("xpath", "//a[@id='loupe']")
        search_button.click()
        time.sleep(1)

        nutrition = driver.find_elements("xpath", "//div[@class='titre-fiche']") 
        
        correspondance = (nutrition[0]).text
        
        no_correspondance = pd.DataFrame({'alim_nom_fr' : ['Pas de correspondance dans Ciqual'], 
              'Energie, Règlement UE N° 1169/2011 (kJ/100 g)':['0'], 
              'Protéines, N x 6.25 (g/100 g)':['0'], 'Glucides (g/100 g)':['0'], 
              'Lipides (g/100 g)' : ['0'], 'Sucres (g/100 g)' : ['0'],
              'AG saturés (g/100 g)' : ['0'], 'Sel chlorure de sodium (g/100 g)' : ['0']})
        
        
        #tentative pour régler le cas où ciqual ne trouve pas de correspondance : 
        
        #print("len(ciqual.loc[ciqual['alim_nom_fr'] == correspondance]) pour", ingredients[i], "est", len(ciqual.loc[ciqual['alim_nom_fr'] == correspondance]))
        
        #if len(ciqual.loc[ciqual['alim_nom_fr'] == correspondance]) == 0 :
            #df_nutrition = pd.concat([df_nutrition, no_correspondance])
        #elif len(ciqual.loc[ciqual['alim_nom_fr'] == correspondance]) > 0 : 
            #df_nutrition = pd.concat([df_nutrition, ciqual.loc[ciqual['alim_nom_fr'] == correspondance]])
        
        
        #avec cette commande, l'algo ignore les ingrédients qui ne trouvent pas de correspondance dans ciqual : 
        df_nutrition = pd.concat([df_nutrition, ciqual.loc[ciqual['alim_nom_fr'] == correspondance]])
        
    driver.quit()
        
    df_ingredient = pd.DataFrame(df_nutrition['alim_nom_fr'])
    columns = df_nutrition.columns
    df_nutrition = (df_nutrition[columns[1:len(columns)]]).applymap(lambda x: clean(x))
    df_nutrition = df_ingredient.join(df_nutrition)
    
    # get the end time
    #et = time.time()

    # get the execution time
    #elapsed_time = et - st
    #print('Execution time:', elapsed_time, 'seconds')
    
    return df_nutrition

print("tout va bien")
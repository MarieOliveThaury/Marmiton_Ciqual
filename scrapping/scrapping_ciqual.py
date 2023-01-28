from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm.auto import tqdm
#from IPython.display import Image
import time
import pandas as pd
from scrapping.scrapping_marmiton import find_all_dishes, find_recipe, find_all_recipes

#setting the driver 
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')


def nutrition(df_recipe):
    """
    Args:
        df_recipe (pandas DataFrame) : a DataFrame with the name of the recipe, the number of comments, the ingredient and the quantity of the ingredient 

    Returns :
        df_nutr_all (pandas DataFrame) : a table with the name of the recipe, the number of comments, the ingredient, the quantity of the ingredient, the nutritional quality and the average content for this ingredient 
    """
    print("Etape 2 : évaluons la qualité nutritionnelle des recettes que vous propose Marmiton")
    print("Si le programme plante, veuillez relancer le Kernel, un problème lié au scrapping est peut-être survenu")
    
    #going to ciqual 
    driver = webdriver.Chrome("chromedriver", options=chrome_options)
    
    driver.get('https://ciqual.anses.fr/')
    
    #opening the french version : 
    switch_to_french = driver.find_element(By.XPATH, "//a[@id='fr-switch']")
    driver.execute_script("arguments[0].click();", switch_to_french)
    time.sleep(2)
    
    ingredients_list = df_recipe['Ingrédient']
    
    df_nutr_list = []
    
    for ingredient in tqdm(ingredients_list):
        
        #going to the page correponding to the ingredient 
        research_bar = driver.find_element("xpath", "//input[@id='champ-recherche']")
        research_bar.clear()
        research_bar.send_keys(ingredient)
        if ingredient == ingredients_list[0]:
            time.sleep(2)
        
        search_button = driver.find_element("xpath", "//a[@id='loupe']")
        search_button.click()
        time.sleep(.5)
        
        
        no_result = driver.find_elements("xpath", '//*[@id="no-result"]/div[2]/div[1]/span')
        if len(no_result) == 0: #checking if ciqual finds a correspondance to this ingredient 
            
            #going to "composition abrégée" (basic composition) : 
            search_button_essentials = driver.find_elements("xpath", "//a[@data-toggle='tab']")
            search_button_essentials[1].click()
            time.sleep(.5)
            
            #collecting the nutrition qualities (e.g. lipids) and the average content for this ingredient 
            nb_nutr = driver.find_elements("xpath", '//*[@id="compo-inco"]/table/tbody/tr')
            nutr_list = []
            qty_list = []
            for i in range(1, len(nb_nutr)+1):
                nutr = driver.find_element("xpath", '//*[@id="compo-inco"]/table/tbody/tr[' + str(i) + ']/td[1]/span')
                nutr_list.append(nutr.text)
                qty = driver.find_element("xpath", '//*[@id="compo-inco"]/table/tbody/tr[' + str(i) + ']/td[2]')
                qty_list.append(qty.text)
            
            nutr_qty_list = zip(nutr_list, qty_list)
            df_nutr = pd.DataFrame(nutr_qty_list, columns = ['Nutriment', 'Teneur moyenne'])
            df_nutr['Ingrédient'] = ingredient
            df_nutr_list.append(df_nutr)
    
    driver.quit()
    df_nutr_all = pd.concat(df_nutr_list, axis=0, ignore_index=True)
    
    print("La qualité nutritionnelle des recettes correspondant à votre recherche est récupérée !") 
    
    return df_nutr_all


print("scrapping_ciqual importé !\n") 
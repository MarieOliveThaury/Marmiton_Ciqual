from scrapping.scrapping_ciqual import *
import plotly.express as px
import time


def looking_for(search : str, N : int) : 
    
    st = time.time()
    
    recipes = find_all_recipes(search, N)
    #recipes.to_csv(r'recipes.csv', index = False)
    nutritions = nutrition(recipes)
    #nutritions.to_csv(r'nutritions.csv', index = False)
    result = merge_and_clean(recipes, nutritions)
    
    et = time.time()
    print("Temps d'execution :", et - st)
    
    return result


def merge_and_clean(recipe, nutrition) : 
    
    result = recipe.merge(nutrition, on='Ingrédient', how='left')
    result = result.drop_duplicates()
    result = result.pivot(index=['Nom recette', 'Ingrédient', 'Quantité'], 
                          columns='Nutriment', values='Teneur moyenne')
    columns = result.columns

    result = result.reset_index()
    for i in columns : 
        result[i] = result[i].apply(lambda x : clean(x))
        result[i] = result[i]*result['Quantité']/100
        if i == 'Protéines, N x 6.25 (g/100 g)' : 
            result[i] = result[i]*6.25
    
    result.rename(columns = {'AG saturés (g/100 g)' : 'AG saturés (g)', 
                'Energie, Règlement UE N° 1169/2011 (kJ/100 g)' : 'Energie, Règlement UE N° 1169/2011 (kJ)', 
                'Energie, Règlement UE N° 1169/2011 (kcal/100 g)' : 'Energie, Règlement UE N° 1169/2011 (kcal)',
                'Glucides (g/100 g)' : 'Glucides (g)', 
                'Lipides (g/100 g)' : 'Lipides (g)', 
                'Protéines, N x 6.25 (g/100 g)' : 'Protéines (g)', 
                'Sel chlorure de sodium (g/100 g)' : 'Sel chlorure de sodium (g)', 
                'Sucres (g/100 g)' : 'Sucres (g)'}, inplace = True)
    
    return result

def compare_recipes(df_recipes, nutritional_quality : str) :
    
    fig = px.bar(df_recipes, x="Nom recette", y=nutritional_quality, color="Ingrédient", 
                 title=nutritional_quality, width=800, height=500)
    fig.update_layout(showlegend=False)
    return fig



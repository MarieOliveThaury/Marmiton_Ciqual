from scrapping.scrapping_ciqual import *


def merge(recipe, nutrition) : 
    
    result = recipe.merge(nutrition, on='Ingrédient', how='left')
    result = result.drop_duplicates()
    result = result.pivot(index=['Nom recette', 'Ingrédient', 'Quantité'], columns='Nutriment', values='Teneur moyenne')
    columns = result.columns

    result = result.reset_index()
    for i in columns : 
        result[i] = result[i].apply(lambda x : clean(x))
        result[i] = result[i]*result['Quantité']
    
    return result



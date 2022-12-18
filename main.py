from scrapping.scrapping_ciqual import *
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


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
        result[i] = result[i].apply(lambda x : string_to_float(x))
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

def nutriStandard(recipe):
    
    totalProt = recipe['Protéines (g)'].sum()
    totalLip = recipe['Lipides (g)'].sum()
    totalGluc = recipe['Glucides (g)'].sum()
    totalKcal = recipe['Energie, Règlement UE N° 1169/2011 (kcal)'].sum()
    
    standardProt = 0.15 * totalKcal / 4
    standardLip = 0.35 * totalKcal / 9
    standardGluc = 0.50 * totalKcal / 4
    
    #Let's remove columns that we do not use for this graph
    recipe = recipe.drop(recipe.columns[[2,3,4,5,9,10]], axis=1)
    recipe = recipe.melt(id_vars = ['Nom recette', 'Ingrédient'], value_name='Valeur')
    
    fig = make_subplots()
    fig.update_layout(xaxis2= {'anchor' : 'y', 'overlaying' : 'x', 'side' : 'top'})
    
    fig.add_trace(
        go.Bar(x=recipe['Nutriment'], y=recipe['Valeur'],
        name='Apport nutritionnel par nutriment'))
    
    fig.add_trace(go.Scatter(x=[0,0.8], y=[standardGluc, standardGluc], name='Objectif en glucides', line_color='#ff0040'))
    fig.add_trace(go.Scatter(x=[1.1,1.9], y=[standardLip, standardLip], name='Objectif en lipides', line_color='#00ff00'))
    fig.add_trace(go.Scatter(x=[2.2,3], y=[standardProt, standardProt], name='Objectif en protéines', line_color='#ffff00'))
    fig.data[1].update(xaxis='x2')
    fig.data[2].update(xaxis='x2')
    fig.data[3].update(xaxis='x2')
    
    fig.update_layout(height=800, title_text='Apports nutritionnels par portion de ' + recipe['Nom recette'][0])
    
    return fig

def comparison(recette : str, n : int):
    base_non_vege=looking_for(recette,n)
    recette_vege=recette+' vege'
    base_vege=looking_for(recette_vege,n)
    moyenne_non_vege=base_non_vege.groupby('Nom recette').sum().mean()
    moyenne_vege=base_vege.groupby('Nom recette').sum().mean()
    moyenne_non_vege=moyenne_non_vege.to_frame()
    moyenne_vege=moyenne_vege.to_frame()
    moyenne_vege=moyenne_vege.drop('Quantité').drop('Energie, Règlement UE N° 1169/2011 (kJ)').drop('Energie, Règlement UE N° 1169/2011 (kcal)')
    moyenne_non_vege=moyenne_non_vege.drop('Quantité').drop('Energie, Règlement UE N° 1169/2011 (kJ)').drop('Energie, Règlement UE N° 1169/2011 (kcal)')
    moyenne_non_vege['type']='non végétarien'
    moyenne_vege['type']='végétarien'
    moyenne_non_vege=moyenne_non_vege.rename(columns={0:'Quantités'})
    moyenne_vege=moyenne_vege.rename(columns={0:'Quantités'})
    moyenne_finale=pd.concat([moyenne_non_vege,moyenne_vege])
    fig = px.bar(moyenne_finale, x=moyenne_finale.index,y=moyenne_finale['Quantités'],color='type',barmode='group')
    
    return fig
from scrapping.scrapping_ciqual import nutrition
from scrapping.scrapping_marmiton import find_all_recipes
from tools.data_tools import string_to_float
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import statsmodels.api as sm
import pandas as pd
import numpy as np
import time 

### preparing the data ##############################

def looking_for(search : str, N : int) : 
    """This function combines other scrapping function to get a full DataFrame with all the data needed from Marmiton and Ciqual.
    
    Args :
        search (str) : the research on Marmiton
        N (int) : the number of recipes you want to request
    
    Returns :
        result (DataFrame) : contains merged data from Ciqual and Marmiton
    """
    
    st = time.time()
    
    recipes = find_all_recipes(search, N)
    nutritions = nutrition(recipes)
    result = merge_and_clean(recipes, nutritions)
    
    et = time.time()
    print("Temps d'execution :", et - st, '\n')
    
    return result


def merge_and_clean(recipe, nutrition) : 
    """a function to merge Marmiton and Ciquals
    Args : 
        recipe : a pandas DataFrame containing the Marmiton scrapped data for one or several recipes 
        nutrition : a pandas DataFrame containing the Ciqual scrapped data for one or several recipes 
        
    Returns :
         result : a pandas DataFrame gathering Marmiton and Ciqual scrapped data, and for the nutrients, transforming the transforming the content into an effective quantity
    """
    
    result = recipe.merge(nutrition, on='Ingrédient', how='left')
    result = result.drop_duplicates()
    result = result.pivot(index=['Nom recette', 'Nombre de commentaires', 'Ingrédient', 'Quantité'], 
                          columns='Nutriment', values='Teneur moyenne')
    columns = result.columns

    result = result.reset_index()
    for i in columns : 
        result[i] = result[i].apply(lambda x : string_to_float(x))
        result[i] = result[i]*result['Quantité']/100
    
    result.rename(columns = {'AG saturés (g/100 g)' : 'AG saturés (g)', 
                'Energie, Règlement UE N° 1169/2011 (kJ/100 g)' : 'Energie, Règlement UE N° 1169/2011 (kJ)', 
                'Energie, Règlement UE N° 1169/2011 (kcal/100 g)' : 'Energie, Règlement UE N° 1169/2011 (kcal)',
                'Glucides (g/100 g)' : 'Glucides (g)', 
                'Lipides (g/100 g)' : 'Lipides (g)', 
                'Protéines, N x 6.25 (g/100 g)' : 'Protéines (g)', 
                'Sel chlorure de sodium (g/100 g)' : 'Sel chlorure de sodium (g)', 
                'Sucres (g/100 g)' : 'Sucres (g)'}, inplace = True)
    
    return result




### graphs ##############################

def compare_recipes(df_recipes, nutritional_quality : str) :
    """
    Args : 
        df_recipes : a pandas DataFrame which contains several recipes
        
    Produces : 
        a plotly graph to compare the presence and weight of a nutrient in several recipes, and to explain the presence of that nutrient in a recipe using the different ingredients in the recipe.
    """
    fig = px.bar(df_recipes, x="Nom recette", y=nutritional_quality, color="Ingrédient", 
                 title='Comparaison pour '+ nutritional_quality, width=800, height=500)
    fig.update_layout(showlegend=False)
    
    return fig


def compare_food(df_recipes_1, type1 : str, df_recipes_2, type2 : str):
    
    """ 
    Args : 
        df_recipes_1 : a pandas DataFrame containing recipes of type 1 (e.g. 100 recipes for 'vegetarien')
        type1 (str) : e.g. 'vegetarien'
        df_recipes_2 : a pandas DataFrame containing recipes of type 2 (e.g. 100 recipes for 'viande')
        type2 (str) : e.g. 'viande'
        
    Produces : 
        a plotly graph to compare the average intake for each nutrient of the two types of dishes.
    """ 
     
    dfs = [df_recipes_1, df_recipes_2]
    types = [type1, type2]  
    
    final_mean = pd.DataFrame([])
    for i in range(2) :     
        mean = dfs[i].groupby('Nom recette').sum(numeric_only = True).mean(numeric_only = True)
        mean = mean.to_frame()
        mean = mean.drop('Quantité').drop('Energie, Règlement UE N° 1169/2011 (kJ)').drop('Energie, Règlement UE N° 1169/2011 (kcal)').drop('Nombre de commentaires')
        mean['Type'] = types[i]
        mean = mean.rename(columns={0:'Quantité moyenne en nutriment'})
        final_mean = pd.concat([final_mean, mean])
        
    final_mean = final_mean.reset_index().rename(columns = {'index' : 'Nutriment'})
    
    fig = px.bar(final_mean, x = final_mean['Nutriment'], y = final_mean['Quantité moyenne en nutriment'], 
                 color='Type', barmode='group', title = 'Comparaison nutritionnelle de ' + type1 + ' et ' + type2)
    
    return fig



def nutriStandard(recipe):
    
    """This function generates a graph on which we can compare the quantity of nutrients (Lipids, Proteins and Glucids) in a given recipe
    with the recommended quantity of nutrients in purcentage of total calorie intake.
    
    The conversion from grams to calories is made as following :
    - 1g of lipids = 9 kcal
    - 1g of glucids = 4 kcal
    - 1g of proteins = 4 kcal
    
    Args :
        recipe (pandas DataFrame) : a DataFrame that contains a single recipe, with every ingredient and nutrients in it
    
    Returns :
        fig (plotly figure) : a graph that shows the quantity of nutrients for the given recipe, and the recommended value for each nutrient"""
    
    #recipe = looking_for(search, 1)
    
    totalProt = recipe['Protéines (g)'].sum()
    totalLip = recipe['Lipides (g)'].sum()
    totalGluc = recipe['Glucides (g)'].sum()
    totalKcal = recipe['Energie, Règlement UE N° 1169/2011 (kcal)'].sum()
    
    #To be satisfying, the protein intake must be between 10 and 20% of total calorie intake
    standardProtLower = 0.10 * totalKcal / 4
    standardProtUpper = 0.20 * totalKcal / 4
    
    #To be satisfying, the lipid intake must be between 35 and 40% of total calorie intake
    standardLipLower = 0.35 * totalKcal / 9
    standardLipUpper = 0.40 * totalKcal / 9
    
    #To be satisfying, the glucid intake must be between 40 and 55% of total calorie intake
    standardGlucLower = 0.45 * totalKcal / 4
    standardGlucUpper = 0.55 * totalKcal / 4

    name_recipe = recipe['Nom recette'][0]
    
    #Let's remove columns that we do not use for this graph
    recipe = recipe[['Ingrédient', 'Glucides (g)', 'Lipides (g)', 'Protéines (g)']]
    recipe = recipe.melt(id_vars = ['Ingrédient'], value_name='Valeur')
    recipe = recipe.rename(columns = {'variable' : 'Nutriment'})
    recipe = recipe.pivot(index=['Nutriment'], columns='Ingrédient', values='Valeur')
    recipe = recipe.reset_index()
    
    recipe['Nutriment'] = recipe['Nutriment'].astype('category')
    recipe['Nutriment_cd'] = recipe['Nutriment'].astype('category').cat.codes
    
    ingredients = recipe.columns[1:-1]
    clrs = {}
    rgb = np.linspace(50, 250, len(ingredients))
    i = 0
    for ingredient in ingredients : 
        clrs[ingredient] = 'rgb(0,' + str(rgb[i]) + ',' + str(rgb[i]) + ')'
        i += 1

    fig = make_subplots()
    for ingredient in ingredients :
        ingredient = str(ingredient)
        fig.add_trace(go.Bar(x=recipe['Nutriment_cd'], y=recipe[ingredient], name=ingredient, 
                             marker= {'color' : clrs[ingredient]}, xaxis = 'x2'), secondary_y=False)
        
        
    #Thresholds for carbohydrates
    fig.add_trace(go.Scatter(x=[-0.5,0.5], y=[standardGlucLower, standardGlucLower], name='Apport recommandé en glucides (min)', line_color='#ff0040'))
    fig.add_trace(go.Scatter(x=[-0.5,0.5], y=[standardGlucUpper, standardGlucUpper], name='Apport recommandé en glucides (max)', line_color='#ff0040'))

    #Thresholds for lipids
    fig.add_trace(go.Scatter(x=[0.5,1.5], y=[standardLipLower, standardLipLower], name='Apport recommandé en lipides (min)', line_color='#00ff00'))
    fig.add_trace(go.Scatter(x=[0.5,1.5], y=[standardLipUpper, standardLipUpper], name='Apport recommandé en lipides (max)', line_color='#00ff00'))

    #Thresholds for proteins
    fig.add_trace(go.Scatter(x=[1.5,2.5], y=[standardProtLower, standardProtLower], name='Apport recommandé en protéines (min)', line_color='#0000f0'))
    fig.add_trace(go.Scatter(x=[1.5,2.5], y=[standardProtUpper, standardProtUpper], name='Apport recommandé en protéines (max)', line_color='#0000f0'))

    fig.update_layout(xaxis2= {'anchor' : 'y', 'overlaying' : 'x', 'side' : 'bottom'})
    fig.update_layout(width=800, height=500, title_text='Apports nutritionnels par portion de ' + name_recipe, barmode='stack')
    fig.update_xaxes(tickvals=[0,1,2], ticktext=recipe['Nutriment'].tolist())
    return fig




def nutriTest(df_recipes):
    """This function checks if macronutrients intake for a given recipe can be considered as satisfying.
    
    Args :
        df_recipe (DataFrame) : a pandas DataFrame which contains one or several recipes.
        
    Returns :
        nutritest : a pandas DataFrame with 3 columns telling in the recipe is satisfying in each macronutrient (True / False), and a fourth column telling whether the recipe can be considered as balanced or not.
    """
    
    list_recipes = list(df_recipes['Nom recette'].unique())
    
    df_nutritest_list = []
    
    for i in range(len(list_recipes)):
        
        recipe = df_recipes[df_recipes['Nom recette'] == list_recipes[i]]
    
        totalProt = recipe['Protéines (g)'].sum()
        totalLip = recipe['Lipides (g)'].sum()
        totalGluc = recipe['Glucides (g)'].sum()
        totalKcal = recipe['Energie, Règlement UE N° 1169/2011 (kcal)'].sum()
    
        #To be satisfying, the protein intake must be between 10 and 20% of total calorie intake
        standardProtLower = 0.10 * totalKcal / 4
        standardProtUpper = 0.20 * totalKcal / 4
    
        #To be satisfying, the lipid intake must be between 35 and 40% of total calorie intake
        standardLipLower = 0.35 * totalKcal / 9
        standardLipUpper = 0.40 * totalKcal / 9
    
        #To be satisfying, the glucid intake must be between 40 and 55% of total calorie intake
        standardGlucLower = 0.45 * totalKcal / 4
        standardGlucUpper = 0.55 * totalKcal / 4
    
        nutritest = {'Satisfaisant en protéines' : (totalProt >= standardProtLower and totalProt <= standardProtUpper),
                 'Satisfaisant en lipides' : (totalLip >= standardLipLower and totalLip <= standardLipUpper),
                 'Satisfaisant en glucides' : (totalGluc >= standardGlucLower and totalGluc <= standardGlucUpper)}
    
        df_nutritest = pd.DataFrame(nutritest, index = [0])
        df_nutritest['Nom recette'] = list_recipes[i]
        
        df_nutritest_list.append(df_nutritest)
    
    full_df = pd.concat(df_nutritest_list, axis=0, ignore_index=True)
    col = ['Nom recette', 'Satisfaisant en protéines', 'Satisfaisant en lipides', 'Satisfaisant en glucides']
    full_df = full_df.reindex(columns=col)
    
    full_df['Repas équilibré'] = (full_df['Satisfaisant en protéines'] & full_df['Satisfaisant en glucides'] & full_df['Satisfaisant en lipides'])
    
    return full_df


### Linear model ###

def prepare_reg(df1, df2) : 
    """
    Args : 
        df1 : a pandas DataFrame containing recipes of type 1 (e.g. 100 recipes for 'vegetarien')
        df2 : a pandas DataFrame containing recipes of type 2 (e.g. 100 recipes for 'meat')
        
    Returns : 
        final_df : a pandasDataFrame with all the recipes of df1 and df2 that : 
        - standardises the nutrient content of a recipe to a content per 100 grams (e.g. 45 g of protein/100 g of food),
        - creates a new variable Type corresponding to the type of food, 
        - indicates if the meal meets the nutritional criteria for proteins, glucids and lipids and global nutrition (cf nutriTest) 
    
    """

    
    dfs = [df1, df2] 
    
    nutrition = pd.DataFrame([])
    opinions = pd.DataFrame([])
    final_df = pd.DataFrame([])
    for i in range(2) :
        #for the nutrition test 
        nutriSt = nutriTest(dfs[i])
        nutrition =  pd.concat([nutrition, nutriSt])
        
        #for the number of comments 
        df_comments = dfs[i].groupby('Nom recette').agg({'Nombre de commentaires':'first'})
        opinions = pd.concat([opinions, df_comments])
        
        #for the nutritional content 
        sum_nutrition = dfs[i].groupby('Nom recette').sum(numeric_only = True)
        sum_nutrition = sum_nutrition.div(sum_nutrition['Quantité'],axis=0)*100
        
        #for the type of food ('vegetarien' vs 'meat') 
        sum_nutrition['Type'] = i
        sum_nutrition = (pd.DataFrame(sum_nutrition)).drop(columns = ['Nombre de commentaires'])
        final_df = pd.concat([final_df, sum_nutrition])
        
        
    final_df = final_df.merge(opinions, on='Nom recette', how='left')
    final_df = final_df.merge(nutrition, on='Nom recette', how='left')
    
    #Let's convert True and False values in 1 and 0 integers
    final_df["Satisfaisant en lipides"] = final_df["Satisfaisant en lipides"].astype(int)
    final_df["Satisfaisant en glucides"] = final_df["Satisfaisant en glucides"].astype(int)
    final_df["Satisfaisant en protéines"] = final_df["Satisfaisant en protéines"].astype(int)
    final_df["Repas équilibré"] = final_df["Repas équilibré"].astype(int)
        
    return final_df
    

def reg(df1, df2, Y : str, X : list):
    
    """ 
    Args : 
        df1 : a pandas DataFrame containing recipes of type 1 (e.g. 100 recipes for 'vegetarien')
        df2 : a pandas DataFrame containing recipes of type 2 (e.g. 100 recipes for 'meat')
        Y (str) : the variable we want to predict
        X (list) : the explanatory variables
    
    Prints : 
        the summary of the OLS linear regression of Y on X
    """
    y = prepare_reg(df1, df2)[Y]
    x = prepare_reg(df1, df2)[X]
    x = sm.add_constant(x)
    model = sm.OLS(y, x)
    
    results = model.fit()
    print(results.summary())

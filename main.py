from scrapping.scrapping_ciqual import *
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import statsmodels.api as sm


def looking_for(search : str, N : int) : 
    
    st = time.time()
    
    recipes = find_all_recipes(search, N)
    #recipes.to_csv(r'recipes.csv', index = False)
    nutritions = nutrition(recipes)
    #nutritions.to_csv(r'nutritions.csv', index = False)
    result = merge_and_clean(recipes, nutritions)
    
    et = time.time()
    print("Temps d'execution :", et - st, '\n')
    
    return result




def merge_and_clean(recipe, nutrition) : 
    
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






def compare_recipes(df_recipes, nutritional_quality : str) :
    
    fig = px.bar(df_recipes, x="Nom recette", y=nutritional_quality, color="Ingrédient", 
                 title='Comparaison pour '+ nutritional_quality, width=800, height=500)
    fig.update_layout(showlegend=False)
    return fig


def compare_food(df_recipes_1, type1 : str, df_recipes_2, type2 : str):
     
    mean1 = df_recipes_1.groupby('Nom recette').sum(numeric_only = True).mean(numeric_only = True)
    mean1 = mean1.to_frame()
    mean1 = mean1.drop('Quantité').drop('Energie, Règlement UE N° 1169/2011 (kJ)').drop('Energie, Règlement UE N° 1169/2011 (kcal)').drop('Nombre de commentaires')
    mean1['Type'] = type1
    mean1 = mean1.rename(columns={0:'Quantité moyenne en nutriment'})
           
    mean2 = df_recipes_2.groupby('Nom recette').sum(numeric_only = True).mean(numeric_only = True)
    mean2 = mean2.to_frame()
    mean2 = mean2.drop('Quantité').drop('Energie, Règlement UE N° 1169/2011 (kJ)').drop('Energie, Règlement UE N° 1169/2011 (kcal)').drop('Nombre de commentaires')
    mean2['Type'] = type2
    mean2 = mean2.rename(columns={0:'Quantité moyenne en nutriment'})
    
    final_mean = pd.concat([mean1,mean2])
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
        recipe (DataFrame) : 
        
    Returns :
        nutritest : a dictionary"""
    
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

def reg_simple(x,y):
    x = sm.add_constant(x)
    model = sm.OLS(y, x)
    
    results = model.fit()
    print(results.summary())
    
def reg_multiple(variables,y):
    x = sm.add_constant(variables)
    model = sm.OLS(y, x)
    results = model.fit()
    print(results.summary())
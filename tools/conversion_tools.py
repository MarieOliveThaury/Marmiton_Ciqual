import re

corres = open("references/Poids.txt", "r")
poids = corres.readlines()
dicopoids = {}
for ligne in poids:
    dicopoids[str(''.join(z for z in ligne if not z.isdigit()).replace(" \n", "").lower())] = int("".join(re.findall('\d',str(ligne))))
     
corres2 = open("references/Quantificateurs.txt", "r")
quantif = corres2.readlines()
dicoquantif = {}
for ligne in quantif:
    dicoquantif[str(''.join(z for z in ligne if not z.isdigit()).replace(" \n",       "").lower())] = int("".join(re.findall('\d',str(ligne))))
     

def convert(dico):
    """
    Args :
        dico (dict) : a dictionnary containing for each dish the name of the dish, the recipe, the number of people and the number of comments. 
The form of the dictionary is as follows : 
{name1 : {recipe : {ingredient11: quantity11, ingredient12 : quantity12}, nb_people : nb_people1, nb_comments : nb_comments1}, 
name2 : {recipe : {ingredient21: quantity21, ingredient22 : quantity22, ingredient23 : quantity23}, nb_people : nb_people2, nb_comments : nb_comments2}}

    Modifies : 
        dico (dict) : the same dictionnary but with all the quantities converted to grams    
    """
    
    for infos in dico.values():
        for ingred,qty in infos['recette'].items():
            if type(qty) == str:
                if qty != '':
                    if '⁄' in qty: #dealing with quantities such as "1/2 Litre de lait" "1/4 de verre"
                        if '1⁄4' in qty:
                            n = 0.25
                        if '1⁄3' in qty:
                            n = 0.33
                        if '1⁄2' in qty:
                            n = 0.5
                        for ingred_ref,qty_ref in dicopoids.items():
                            if ingred_ref in ingred: #1/2 concombre -> 1/2*200g concombre
                                infos['recette'].update({ingred:str(qty_ref*n)+"g"})
                        for ingred_ref,qty_ref in dicoquantif.items(): #1/2 cuillères à soupe -> 1/2*15g
                            if unit in ['.'+ ingred_ref,ingred_ref,ingred_ref +'s','.'+ingred_ref+'s','⁄'+ingred_ref,'⁄'+ingred_ref+'s'] :
                                infos['recette'].update({ingred:str(qty_ref*n)+"g"})
                            
                    else:
                        n = float(("".join(re.findall('\d',str(qty)))))
                        unit = str(''.join(z for z in qty if not z.isdigit()))
                        
                        if unit not in ['g','.g'] :
                            for ingred_ref,qty_ref in dicopoids.items(): #2 concombre -> 2*200g concombre
                                if ingred_ref in ingred:
                                    infos['recette'].update({ingred:str(qty_ref*n)+"g"})
                            for ingred_ref,qty_ref in dicoquantif.items(): #3 cuillère à soupe -> 3*15g 
                                if unit in ['.'+ingred_ref,ingred_ref,ingred_ref+'s','.'+ingred_ref+'s','⁄'+ingred_ref,'⁄'+ingred_ref+'s'] : 
                                    infos['recette'].update({ingred:str(qty_ref*n)+"g"})
                                        
                elif qty == "": #we define a standard value for ingredients with missing quantity. 
                    #These elements are often used in limited quantities.
                    infos['recette'].update({ingred:str(2*int(infos['nombre de personnes']))+"g"})
                
def what_s_missing(dico):
    """ a useful function to know what kind of quantity we forgot to put in dicopoids or dicoquantif
    Args :
        dico (dict) : a dictionnary containing for each dish the name of the dish, the recipe, the number of people and the number of comments. The form of the dictionary is as indicated above.
     
    Prints : 
        The ingredients and the quantities that haven't been converted to grams
    """ 
    for infos in dico.values():
        for ingred,qty in infos['recette'].items():
            unit = str(''.join(z for z in qty if not z.isdigit()))
            if unit not in ['.g','g']:
                print(ingred,qty)
           
        
def delete_exception(dico):
    """a function that deletes the ingredients for which the quantity is too complicated.
    Args :
        dico (dict) : a dictionnary containing for each dish the name of the dish, the recipe, the number of people and the number of comments. The form of the dictionary is as indicated above.
    
    Modifies : 
        the same dictionnary but without those complicated ingredients. 
    """
    for infos in dico.values():
        exceptions = []
        for ingred,qty in infos['recette'].items():
            qty = str(qty)
            unit = str(''.join(z for z in qty if not z.isdigit()))
            if unit not in ['.g','g']:
                exceptions = exceptions+[ingred]
                        
        for exception in exceptions:
            del infos['recette'][exception]

def usable(dico):
    """
    Args :
        dico (dict) : a dictionnary containing for each dish the name of the dish, the recipe, the number of people and the number of comments. The form of the dictionary is as indicated above.
    
    Modifies : 
        dico (dict) : the same dictionnary but with all the quantities as floats.
    """
    for infos in dico.values():
        for ingred,qty in infos['recette'].items():
            n = float(str(qty).replace('g',''))
            infos['recette'].update({ingred:float(n)})
                
def per_person(dico):
    """
    Args :
        dico (dict) : a dictionnary containing for each dish the name of the dish, the recipe, the number of people and the number of comments. The form of the dictionary is as indicated above.
    
    Modifies : 
        dico (dict) : the same dictionnary but with all the quantities for one person only.
    """
    for infos in dico.values():
        for ingred,qty in infos['recette'].items() :
            infos['recette'].update({ingred:qty/infos['nombre de personnes']})
    

                
def conversion(dico):
    """
    Args :
        dico (dict) : a dictionnary containing for each dish the name of the dish, the recipe, the number of people and the number of comments. The form of the dictionary is as indicated above.
        
    Modifies : 
        dico (dict) : the same dictionnary with all the previous modifications 
    """
    convert(dico)
    delete_exception(dico)
    usable(dico)
    per_person(dico)
    
print("conversion_tools importé !")
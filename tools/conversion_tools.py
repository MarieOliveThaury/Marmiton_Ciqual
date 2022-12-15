import re

corres = open("references/Poids.txt", "r")
poids=corres.readlines()
dicopoids={}
for ligne in poids:
    dicopoids[str(''.join(z for z in ligne if not z.isdigit()).replace(" \n", "").lower())]=int("".join(re.findall('\d',str(ligne))))
     
corres2 = open("references/Quantificateurs.txt", "r")
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
                
def what_s_missing(dico):
    for x,y in dico.items():
                for k,v in y['recette'].items():
                    l=str(''.join(z for z in v if not z.isdigit()))
                    if l not in ['.g','g']:
                        print(k,v)
           
        
def filler(dico):
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
                
def per_personne(dico):
    for x,y in dico.items():
        for k,v in y['recette'].items():
                
                y['recette'].update({k:v/y['nombre de personnes']})
    

                
def conversion(dico):
    convert(dico)
    filler(dico)
    usable(dico)
    per_personne(dico)
    
print("conversion_tools importé !")
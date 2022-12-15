import unidecode
import math

def CleanString(pl : str):
     """Function that makes a string singular originally in the plural and removes the accents
        caution : this function only works for french words related to food 
    
    Args:
        pl (str) : raw text corresponding to an ingrendient 

    Returns:
        plural (str) : the singular of pl, without the accents 
    """
    
    plural = unidecode.unidecode(pl)
    
    #First, let's pay attention to some execptions : 

    except_ou = ['choux'] #foods ending in "-ou" and that take an "-x" in the plural
    except_sg_s = ['anchois', 'brebis', 'jus', 'pois', 'radis']  #foods ending in "-s" even in the singular 
    except_pl = ['rillettes'] #Foods that are always used in the plural, that do not really exist in the singular
    al_aux = ['chevaux', 'vegetaux'] #Foods ending in "-al" in the singular and "-aux" in the plural 


    #Now we treat all possible cases : 
    if plural in except_pl:
        return plural
    elif plural in except_ou:
        return plural[:-1]
    elif plural[-3:] == 'aux':
        if plural[-4:] == 'eaux':
            return plural[:-1]
        else:
            if plural in al_aux:
                return plural[:-2] + 'l'
            else:
                return plural[:-1]
    elif plural[-1:] == 's':
        if (plural in except_sg_s) or ('frais' in plural):
            return plural
        else:
            return plural[:-1]
    else:
        #print(plural, 'n\'est pas référencé. Erreur possible.')
        return plural
    

def clean(string) :
     """cleans the collected data corresponding to the average content of an ingredient (e.g. tomato) in a nutritional quality (e.g. lipids) 

    Args:
        string (str) : the average content of an ingredient (e.g. tomato) in a nutritional quality (e.g. lipids) 

    Returns:
        string (float) : the average content of an ingredient (e.g. tomato) in a nutritional quality (e.g. lipids) ready to be analysed
    """
    if type(string) == str : 
        if ("<" in string) or (string.isalpha()) or (string =="-"): 
            string = "0"
        string = float(string.replace(',', '.'))
    return string

print("data_tools importé !")

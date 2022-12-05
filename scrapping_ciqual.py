#Fonction qui met un mot au pluriel au singulier
#Attention, elle fonctionne pour le lexique de la nourriture mais n'est pas généralisable !



def PlSg(pluriel : str):
    
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
        print(pluriel, 'n\'est pas référencé. Erreur possible.')
        return pluriel
        
#Problème : cette fonction ne marche que pour des mots isolés
#Gérer le cas des groupes nominaux
# **Evaluation de la qualité nutritionnelle de recettes Marmiton**

ENSAE ParisTech 2022-2023 

Nathan GUESSE • Matthieu KRUBA • Marie-Olive THAURY

*Ce projet est réalisé dans le cadre du cours de **Python pour la data-science (2A)** de Lino GALIANA pour l'année 2022-2023. Il est supervisé par Romain AVOUAC*.

Le but de ce projet est d'évaluer la qualité nutritionnelle de recettes propoposées par le site de cuisine [Marmiton](https://www.marmiton.org/). 
Pour cela nous nous appuierons sur la [Table de composition nutritionnelle des aliments Ciqual](https://ciqual.anses.fr/) qui est un jeu de données produit par l'*Agence nationale de sécurité sanitaire de l'alimentation, de l'environnement et du travail* sur la composition nutritionnelle des aliments. 


## I) Récupération des recettes proposées par Marmiton pour une recherche 

### Scrapping de Marmiton 

pourquoi on a utilisé BeautifulSoup plutôt que Selenium : permet d'éviter les cookies + plus simple à coder 

### Nettoyage des données et conversions 

ici c'est Nathan : expliquer comment tu fais tes conversions, à quoi servent tes dictionnaires, tes fonctions etc...


## II) Evaluation de la qualité nutritionnelle des recettes 

### Scrapping de Ciqual 

Une fois les données de Marmiton obtenues, notre objectif était de croiser ces données avec les données nutritionnelles de la base Ciqual de l’ANSES. Pour chaque ingrédient de chaque recette scrappée sur Marmiton, nous souhaitions obtenir les apports nutritionnels globaux (apport calorique et énergétique), ainsi que la composition nutritionnelle pour quelques nutriments principaux (lipides, glucides, protéines…).

Pour récupérer les données souhaitées, deux possibilités s’offraient à nous : 
1)	Ou bien nous téléchargions le fichier Excel de la base Ciqual, libre d’accès, et nous cherchions nous-mêmes les entrées qui correspondaient le mieux à nos ingrédients, avant de sélectionner manuellement les variables souhaitées.
2)	Ou bien nous scrappions directement le site internet de Ciqual, pour ne récupérer que les données souhaitées.

Nous avons opté pour la deuxième méthode, car celle-ci présentait plusieurs avantages : tout d’abord, nous bénéficiions du moteur de recherche de Ciqual, et n’avions qu’à nous assurer de formuler correctement notre recherche pour obtenir un résultat adéquat. Ensuite, le site de Ciqual offrait la possibilité de consulter directement la composition abrégée de l’ingrédient cherché, soit les nutriments principaux retenus pour notre étude. Enfin, cette méthode présentait pour nous un intérêt pédagogique : le site de Ciqual étant codé de façon dynamique, le scrapping nécessitait ici l’utilisation de Selenium.


### Graphiques 

## III) Modélisation ?  

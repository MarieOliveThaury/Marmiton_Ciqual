# **Evaluation de la qualité nutritionnelle de recettes Marmiton**

ENSAE ParisTech 2022-2023 

Nathan GUESSE • Matthieu KRUBA • Marie-Olive THAURY

*Ce projet est réalisé dans le cadre du cours de **Python pour la data-science (2A)** de Lino GALIANA. Il est supervisé par Romain AVOUAC*.

## Introduction 

Le but de ce projet est d'évaluer la qualité nutritionnelle de recettes propoposées par le site de cuisine [Marmiton](https://www.marmiton.org/). 
Pour cela nous nous appuierons sur la [Table de composition nutritionnelle des aliments Ciqual](https://ciqual.anses.fr/) qui est un jeu de données produit par l'*Agence nationale de sécurité sanitaire de l'alimentation, de l'environnement et du travail* sur la composition nutritionnelle des aliments. 

Même si les fonctions codées sont généralisables à tout type de recette, nous porterons une attention toute particulière aux recettes végétariennes, comparativement aux recettes avec viande, le but étant d'évaluer dans quelle mesure les recettes végétariennes sont envisageables pour avoir une alimentation équilibrée et saine. 


## I) Récupération des recettes proposées par Marmiton pour une recherche 

### Scrapping de Marmiton 

La première étape a été de récupérer les données provenant de Marmiton. Dans le fichier `scrapping_marmiton.py` se trouvent l'ensemble des fonctions nécessaires pour l'extraction de ces données. 

Pour scrapper les données de Marmiton, nous avons fait le choix de réaliser un scrapping statique grâce à la méthode `BeautifulSoup`. Comparée à un scrapping dynamique, cette technique présentait pour nous deux avantages : 
1) déjà, n'ayant jamais fait de scrapping auparavant, cette méthode était plus abordable et plus facile à coder. 
2) ensuite, elle ignore complètement la présence de fenêtres pop-up publicitaires, présentes dès l'ouverture de la page d'accueil, et pouvant apparaître au cours de la recherche. Ne pas avoir à gérer ces fenêtres publicitaires nous a notamment permis d'optimiser le temps d'execution de l'algorithme car nous n'avions pas besoin d'utiliser des commandes telles que `time.sleep()`.


Le scrapping des données Marmiton à partir d'une recherche de type `'végétarien'` se fait en trois étapes :

1) tout d'abord, la fonction `find_all_dishes` trouve l'ensemble des pages de proposition correspondant à la recherche `'végétarien'`, une page de recherche étant une page sur laquelle s'affiche une dizaine de plats : 

<div align="center">
  <img src="images/marmiton_1.png"><br>
</div>

2) ensuite, cette même fonction récupère à partir de ces pages de proposition, les urls des pages des plats proposés pour la recherche `'végétarien'` : 

<div align="center">
  <img src="images/marmiton_2.png"><br>
</div>

3) finalement, la fonction `find_all_recipes` récupère grâce à la fonction `find_recipe` pour chaque plat proposé pour la recherche `'végétarien'` : 
- le nom de la recette,
- la recette (ingrédients et quantités), 
- le nombre de personnes,  
- le nombre de commentaires. 

### Nettoyage des données et conversions 

Afin de pouvoir exploiter nos données, nous devions nous ramener à une unité commune pour tous les ingrédients, à savoir le gramme. 

Les fruits et légumes étant souvent indiqués en nombre ( par exemple, 3 poires  ), certains liquides étant donnés en litres (1/2 L de lait) ou en unité de mesure de cuisine ( par exemple, 2 cuillères à soupe), l'une des grosses difficulté a donc été de formater l'ensemble de ces quantités en grammes.

Dans le fichier `conversion_tools.py` se trouvent l'ensemble des fonctions nécessaires pour le nettoyage de ces données.

Le fichier `references/Poids.txt` recense une liste d'ingrédients et leur valeur en grammes associée, par exemple « reblochon 500 » ou « Échalote 40 ». 
Le fichier `references/Quantificateurs.txt` recense une liste d'unités et leur valeur en grammes associée, par exemple « sachet 15 » ou « c.à.s 15 ».


La fonction `convert` gère les quantités dont l'unité n'est pas exprimée en grammes. La fonction : 
1) détecte les quantités non libellées en grammes,
2) parcourt le dictionnaire `dicopoids` (issu du fichier `references/Poids.txt`) pour le nom du produit, 
3) parcourt le dictionnaire `dicoquantif` (issu du fichier `references/Quantificateurs.txt`) sur les caractères non digitaux de la quantité renseignée sur Marmiton (« cuillères à soupe » dans «  3 cuillères à soupe »).

*Notons que ces deux dictionnaires ont été enrichi à l’aide de la fonction `what_s_missing` qui détecte les éléments manquants.* 

Ensuite, les caractères digitaux du quantificateur sont multipliés par la valeur correspondante dans les dictionnaires associés. Ainsi pour «  3 cuillères à soupe », on obtient 3x15 g, tandis que pour « 3 poires » on obtient 3x120 g. 

Pour les ingrédients dont la quantité n'est pas spécifiée et n'apparaissant pas dans les dictionnaires, on attribue une valeur standard. 

Finalement, on supprime les ingrédients présentant une quantité trop spéciale (`delete_exeception`), on convertit les quantités en `float` afin qu'elles soit exploitables (`usable`) et on se ramène à des portions individuelles (`per_person`).



## II) Evaluation de la qualité nutritionnelle des recettes 

### Scrapping de Ciqual 

Une fois les données de Marmiton obtenues, notre objectif était de croiser ces données avec les données nutritionnelles de la base Ciqual de l’ANSES. Pour chaque ingrédient de chaque recette scrappée sur Marmiton, nous souhaitions obtenir les apports nutritionnels globaux (apport calorique et énergétique), ainsi que la composition nutritionnelle pour quelques nutriments principaux (lipides, glucides, protéines…).

Pour récupérer les données souhaitées, deux possibilités s’offraient à nous : 
1)	Ou bien nous téléchargions le fichier Excel de la base Ciqual, libre d’accès, et nous cherchions nous-mêmes les entrées qui correspondaient le mieux à nos ingrédients, avant de sélectionner manuellement les variables souhaitées.
2)	Ou bien nous scrappions directement le site internet de Ciqual, pour ne récupérer que les données souhaitées.

Nous avons opté pour la deuxième méthode, car celle-ci présentait plusieurs avantages : tout d’abord, nous bénéficiions du moteur de recherche de Ciqual, et n’avions qu’à nous assurer de formuler correctement notre recherche pour obtenir un résultat adéquat ; pour chaque recherche, nous avons ainsi gardé le premier résultat. Ensuite, le site de Ciqual offrait la possibilité de consulter directement la composition abrégée de l’ingrédient cherché, soit les nutriments principaux retenus pour notre étude. Enfin, cette méthode présentait pour nous un intérêt pédagogique : le site de Ciqual étant codé de façon dynamique, le scrapping nécessitait ici l’utilisation de `Selenium`.

Dans le fichier `scrapping_ciqual.py` vous trouverez la fonction `nutrition` nécessaire à la collecte des données Ciqual. Notre scrapper fonctionne avec le browser `chromedriver`. 

En pratique, nous avons rencontré plusieurs problèmes avec `Selenium`, que nous avons heureusement pu résoudre :
-	La base Ciqual possède deux versions, l’une anglaise et l’autre française. Nos recherches étant formulées avec des noms français d’ingrédients, nous avons dû programmer Selenium pour passer sur la version française du site au préalable. Comme le bouton de changement de langue n’apparaît pas toujours explicitement sur la page (en particulier, il disparaît lorsque la fenêtre du navigateur rétrécit), nous avons eu recours à la fonction `execute_script` du driver plutôt qu’à un simple `click`.
-	Les balises composant le code source du tableau de données abrégées de Ciqual possèdent toutes une forme similaire, sans qu’un attribut unique tel qu’un identifiant permette de les différencier. Pour ne sélectionner que les données souhaitées, nous avons dû jouer sur la structure de la page et sur la forme du `xpath` de chaque élément souhaité.
-	Le temps de chargement de la page étant parfois plus long que le temps d’exécution du programme, nous avons parfois dû implanter des pauses dans l’exécution du programme (`time.sleep()`) pour être certains d’obtenir les bonnes données.



### Graphiques 

Vous trouverez dans le fichier `main.py` l'ensemble des fonctions nécessaires à la réalisation des graphiques. 

#### Comparaison de plusieurs recettes d'une même recherche pour un critère nutritionnel. 

Notre première intention a été d'aider l'utilisateur à choisir la meilleure recette parmi une liste de propositions Marmiton pour une recherche commune. 

Par exemple, l'utilisateur cherche à cuisiner un  plat *végétarien* tout en minimisant les apports en sucres. Pour cela, le graphique associé à la fonction `compare_recipe` lui permet  de comparer les différentes recettes proposées par Marmiton pour *végétarien*. En survolant le graphique, il pourra même avoir accès à l'apport en sucre pour chaque ingrédient. 

<div align="center">
  <img src="images/graphique_1.png"><br>
</div>


#### Comparaison de deux types de plats. 

Ici, l'objectif est d'aider l'utilisateur à choisir entre deux types de plats. Imaginons qu'il hésite entre deux repas : repas *végétarien* ou avec *viande* ? 

Ce graphique permet de comparer les apports en nutriments de deux plats différents. La fonction `compare_food` associée calcule les moyennes des apports en nutriments de chaque plat sur N recettes, puis représente ces apports dans un diagramme en barres de manière comparative.

Ainsi, l'utilisateur connaîtra parfaitement et immédiatement les apports nutritionels moyens des recettes des deux types de repas.

<div align="center">
  <img src="images/graphique_2.png"><br>
</div>


#### Une approche normative : recettes végétariennes et apports nutritionnels recommandés

Nous avons souhaité vérifier si les apports nutritionnels des recettes végétariennes en macronutriments (Lipides, Glucides et Protéines) pouvaient être considérés comme satisfaisants.

Dans toute cette partie, les données additionnelles que nous utilisons comme critères normatifs (Apport Satisfaisant en Lipides, Protéines et Glucides pour un adulte à faible activité physique) sont issues d’un [rapport de l’ANSES](https://www.anses.fr/fr/system/files/NUT2012SA0103Ra-2.pdf), publié en 2016 dans le cadre du Programme National Nutrition Santé (PNNS). En particulier, pour un adulte ayant une faible activité physique :
-	L’apport calorique en protéines est considéré comme satisfaisant s’il représente entre 10 et 20% de l’apport calorique total.
-	L’apport calorique en lipides est considéré comme satisfaisant s’il représente entre 35 et 40% de l’apport calorique total.
-	L’apport calorique en glucides est considéré comme satisfaisant s’il représente entre 45 et 55% de l’apport calorique total.

A partir de ces seuils, nous avons défini un repas équilibré comme ayant un apport satisfaisant en chacun des trois macronutriments.

Afin de convertir l'apport brut en nutriments (en grammes), dont nous disposons, en pourcentage de l’apport calorique total, une conversion des grammes en calories est nécessaire, selon les rapports suivants :
-	Protéines : 1 g = 4 kcal
-	Glucides : 1 g = 4 kcal
-	Lipides : 1 g = 9 kcal

La fonction `nutriStandard` permet de visualiser pour une recette les macronutriments Lipides, Glucides et Protéines contenus dans le plat ainsi que les seuils préconisés, tandis que la fonctions `nutriTest` renvoie simplement un Booléen indiquant si la recette est équilibrée ou non. 

<div align="center">
  <img src="images/graphique_3.png"><br>
</div>


## III) Popularité d'une recette en fonction de ses qualités nutritionnelles :

Nous voulions enfin dans notre projet étudier la popularité des recettes et tenter de dégager des facteurs qui peuvent avoir une influence sur cette popularité. Nous avons choisi comme mesure de popularité le nombre de commentaires sur les recettes. La note moyenne ne nous paraissait pas pertinente puisqu'elle nous indiquait davantage la qualité gustative d'une recette plutôt que sa popularité. Ici, en supposant qu'une fraction x constante d'utilisateurs donne son avis dès qu'ils essaient une recette, alors on peut considérer que plus une recette a d'avis, plus elle a été essayée par des utilisateurs. De plus, les notes données sur Marmiton sont généralement comprises entre 4.5 et 5 étoiles et donc n'est pas révélatrice en soit. Par contre, plus la recette est commentée (= notée), plus cette note est pertinente. 

La fonction `reg` présente dans `main.py` permet de produire des régressions linéaires.

Nous avons utilisé les bases de 100 recettes végétariennes et de 100 recettes carnées que nous avons scrappées. Nous avons ajouté une variable bianaire nommée `type` qui vaut 1 en si la recette contient de la viande, et 0 sinon. 

La première régression a été celle du nombre de commentaires sur la présence de viande. Ici, la présence de viande a un impact positif sur le nombre de commentaires, avec en outre un coefficient significatif au seuil de 5%. 

Après la première régression, un doute subsistait. Nous avons vu précedemment que les recettes carnées étaient en moyenne plus riches en protéines que les recettes végétariennes. Les recettes végétariennes se voient d'ailleurs souvent reprochées leur plus faible teneur en protéines, qui est perçue comme leur principal défaut. Nous avons donc voulu observer l'impact de la présence de viande sur la popularité d'une recette à égale teneur en protéines. Nous avons pour cela régressé le nombre de commentaires sur la teneur en protéines et la présence de viande. On note que le coefficient de la teneur en protéines n'est significatif à aucun seuil usuel. La présence de viande en revanche augmente toutes choses égales par ailleurs de 9 le nombre de commentaires sur une recette. Ce coefficient est significatif au seuil de 10%. Ici aussi, la présence de viande a un effet assez significative sur le nombre d'avis. 

Enfin, nous avons voulu prendre en compte les principales teneurs en nutriment pour tenter d'expliquer la popularité d'une recette. Nous avons donc régressé le nombre de commentaires sur les principales teneurs en nutriments et sur la présence de viande. Ici, les résultats sont assez décevants. Le R² est très faible, et surtout, aucun coefficient n'est significatif au seuil de 10%. 

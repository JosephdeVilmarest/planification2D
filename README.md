#planification2D

Le but de ce projet est de planifier le mouvement d'un objet polygonal dans le plan avec des obstacles polygonaux. On travaille avec des entiers. Le langage choisi est python


Je (Joseph) pense qu'il faudrait effectuer les étapes suivantes:
-on demande à l'utilisateur de définir les obstacles, puis l'objet à déplacer
-on calcule le problème équivalent consistant à déplacer un point avec des obstacles constitués des sommes de Minkovski -> fonction simplify.py
-graphe de visibilité
-construction des cellules (trapèzes) par balayage
-diagramme de Voronoi
-on repasse du ptoblème simplifié au problème de départ

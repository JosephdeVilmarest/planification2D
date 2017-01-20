from simplify import *
from colorsys import hsv_to_rgb
from math import atan2

def standardValidation(*conf):
    """ Renvoie
        - "" si la configuration est valide
        - Un message d'erreur sinon
    """
    return ""

def standardTransformation(*conf):
    """ Renvoie
        - Nouvelle configuration
        - Liste d'items : (Polygone, CouleurBord, Couleur)
    """
    return conf,[]



########### Décomposition en convexes ############
# Suppose l'environement dans le sens trigo
def convexDecompositionValidation(environment, *conf):
    if not len(environment): return "Environnement vide"
    for p in environment:
        if polyIsCrossed(p):
            return "Polygone(s) de l'environnement croisé(s)"
    return ""

def convexDecompositionTransformation(environment, *conf):
    envi = convexDecomposition(environment)
    items = []
    for i,p in enumerate(envi) :
        rvb = [int(o*255) for o in hsv_to_rgb((30*i%360)/360, 1,1)]
        items.append((p,(200,0,250,255),(rvb[0], rvb[1], rvb[2])))
    return [envi]+list(conf),items



########### Somme de Minkovsky ############
# Suppose l'environement convexe
def minkovskySumValidation(environment, object, *conf):
    if len(object) < 3: return ""
    if polyIsCrossed(object):
        return "Polygone object croisé"
    angle = lambda i,j : atan2(object[j][0]-object[i][0],object[j][1]-object[i][1])
    a = 0
    p0 = 0
    for i in range(0,len(object)):
        if det(object[i-2], object[i-1], object[i]) > 0 :
            return "Polygone object non convexe"
    return ""

def minkovskySumTransformation(environment, object, *conf):
    return [],[]

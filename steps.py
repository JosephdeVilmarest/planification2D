from simplify import *
from colorsys import hsv_to_rgb

def standardValidation(*conf):
    return True

def standardTransformation(*conf):
    """ Renvoie
        - Nouvelle configuration
        - Liste d'items : (Polygone, CouleurBord, Couleur)
    """
    return conf,[]



########### Décomposition en convexes ############
# Suppose l'environement dans le sens trigo
def convexDecompositionValidation(environment, *conf):
    if not len(environment): return False
    for p in environment:
        l = len(p)
        if l > 2:
            for i in range(2,l):
                for j in range((i==l-1),i-1):
                    if segmentsIntersect(p[i],p[i-l+1],p[j],p[j+1]):
                        return False
    return True

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
    # Vérif object convexe
    return True

def minkovskySumTransformation(environment, object, *conf):
    return [],[]

from simplify import *
from scanning import scanning
from colorsys import hsv_to_rgb
from math import atan2
from dijkstra import dijkstra
from commun import *
from visibility import visibility_graph
from PyQt4.QtGui import QPolygon
from PyQt4.QtCore import QPoint

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
    if not len(environment): return ""
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
    # !!!! TEMPORAIRE : envi.
    return [envi]+list(conf),items

########### Décomposition en convexes ############
# Suppose l'environement dans le sens trigo
def convexDecompositionValidation2(environment, *conf):
    if not len(environment): return ""
    for p in environment:
        if polyIsCrossed(p):
            return "Polygone(s) de l'environnement croisé(s)"
    return ""

def convexDecompositionTransformation2(environment, *conf):
    envi = convexDecomposition2(environment)
    items = []
    for i,p in enumerate(envi) :
        rvb = [int(o*255) for o in hsv_to_rgb((30*i%360)/360, 1,1)]
        items.append((p,(200,0,250,255),(rvb[0], rvb[1], rvb[2])))
    # !!!! TEMPORAIRE : envi.
    return [envi]+list(conf),items


########### Somme de Minkovsky ############
# Suppose l'environement convexe
def minkovskySumValidation(environment, object, *conf):
    if not len(object): return "Objet non défini"
    if len(object) < 3: return ""
    for i in environment:
        if len(i)<3:
            return "Obstacles ponctuels/linéaires non pris en charge"
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
    if len(object) == 1:
        return [environment]+list(conf),[]
    print(environment, object)
    envi = MinkowskiSum(environment, object)
    items = []
    for p in envi:
        items.append((p, (220,220,220,240),(220,220,220,20)))
    return [envi]+list(conf),items


########### Suppression des superpositions ############
# 
def unificationValidation(environment, *conf):
    return ""

def unificationTransformation(environment, *conf):
    e = []
    for i in environment:
        p = QPolygon([QPoint(*i) for  i in i]+[QPoint(*i[0])])
        for k,q in enumerate(e):
            if len(q.intersected(p)):
                e[k] = q.united(p)
                break
        else:
            e.append(p)
    lim = QPolygon([QPoint(0,0),QPoint(0,LEN),QPoint(LEN,LEN),QPoint(LEN,0)])
    envi = [[(q.x(),q.y()) for q in p.intersected(lim)[:-1]] for p in e]
    for po in envi:
        if len(po) > 2 :
            ind, pt = max(enumerate(po), key = lambda i : i[1][0]*LEN+i[1][1])
            if ((po[(ind+1)%len(po)][0]-pt[0])*(po[(ind-1)%len(po)][1]-pt[1])-
                (po[(ind+1)%len(po)][1]-pt[1])*(po[(ind-1)%len(po)][0]-pt[0])) <0:
                po.reverse()
    items = []
    for p in envi:
        items.append((p, (220,220,220,240),(220,220,220,100)))
    return [envi]+list(conf),items


########### Décomposition en cellules ############
# Pas de point / segment seul + pas de superposition
def cellDecompositionValidation(environment, *conf):
    for i in environment:
        if len(i)<3:
            return "Obstacle plat (point ou segment)"
    for i in range(len(environment)):
        for j in range(i):
            if len(QPolygon([QPoint(*p) for p in environment[i]]).intersected(
                QPolygon([QPoint(*p) for p in environment[j]]))):
                return "Obstacles superposés"
    return ""

def cellDecompositionTransformation(environment, *conf):
    s = scanning(environment, LEN)
    items = []
    pts = []
    cps = []
    for i,p in enumerate(s):
        rvb = [int(o*255) for o in hsv_to_rgb((10*i%360)/360, 1,1)]
        #items.append((p, (0,100,0),(rvb[0], rvb[1], rvb[2],100)))
        items.append((p.trap, (rvb[0], rvb[1], rvb[2],150),(rvb[0], rvb[1], rvb[2],80)))
        pi = len(pts)
        pts.append(p.bar)
        for c in p.previousCells:
            if c.rightHeight >= p.leftHeight:
                
                items.append(((p.bar,(p.xMin, p.leftY)), (rvb[0]//2, rvb[1]//2, rvb[2]//2),(0,0,0,0)))
            else:
                items.append(((p.bar,(p.xMin, c.rightY)), (rvb[0]//2, rvb[1]//2, rvb[2]//2),(0,0,0,0)))
        for c in p.nextCells:
            if p.rightHeight < c.leftHeight:
                items.append(((p.bar,(p.xMax, p.rightY)), (rvb[0]//2, rvb[1]//2, rvb[2]//2),(0,0,0,0)))
            else:
                items.append(((p.bar,(p.xMax, c.leftY)), (rvb[0]//2, rvb[1]//2, rvb[2]//2),(0,0,0,0)))
    
    return [],items




########### Graphe de visibilité ############
# Pas de point / segment seul + pas de superposition
def visibilityGraphValidation(environment, posI, posF, *conf):
    if posI == None or posF == None:
        return "Pas de point de départ/arrivée"
    pi = QPoint(*posI)
    pf = QPoint(*posF)
    for i in environment:
        p = QPolygon([QPoint(*p) for p in i])
        if p.containsPoint(pi,0):
            return "Position intiale en colision"
        if p.containsPoint(pf,0):
            return "Position finale en colision"
    return ""

def visibilityGraphTransformation(environment, posI, posF, *conf):
    s,m = visibility_graph(posI,posF,environment)
    items = []
    for i in range(len(s)):
        for j in range(i):
            if m[i][j]:
                items.append(((s[i],s[j]), (0,180,50),(0,0,0,0)))
    return [s,m],items

########### Dijkstra ############
#
def dijkstraValidation(pts, ma, *conf):
    return ""

def dijkstraTransformation(pts, ma, *conf):
    print("hum")
    print(pts, ma)
    p = dijkstra(pts,ma)
    print(p)
    items = []
    for i in range(len(p)-1):
        items.append(((p[i],p[i+1]), (0,0,0),(0,0,0)))
    return [],items

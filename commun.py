
LEN = 100000

def det(i,j,k):
    """ Calcule det((IJ),(IK)) """
    return (i[0]-j[0])*(k[1]-j[1])-(i[1]-j[1])*(k[0]-j[0])
def proj(i,j,k):
    """ Calcule (IJ).(IK) """
    return (i[0]-j[0])*(k[0]-j[0])+(i[1]-j[1])*(k[1]-j[1])
def norm2(i,j):
    """ Calcule ||IJ|| """
    return (i[0]-j[0])**2+(i[1]-j[1])**2
def segmentContains(a,b, c):
    """ Teste si c est dans [a,b] """
    return proj(a,c,b) == -norm2(a,c)-norm2(c,b)
def segmentsIntersect(a,b, c,d):
    """ Teste si [a,b] coupe [c,d] """
    return (det(a,c,b)*det(b,d,a) > 0 and det(c,a,d)*det(d,b,c) > 0) or (
                segmentContains(a,b, c) or segmentContains(a,b, d) or
                segmentContains(b,c, a) or segmentContains(b,c, b)) 

def barycenter(l):
    """ Calcul le barycentre d'une liste de points """
    x = 0
    y = 0
    for i in l:
        x += i[0]
        y += i[1]
    return (x/len(l), y/len(l))


def barycenterInt(l):
    """ Calcul le barycentre d'une liste de points version entier"""
    return tuple(map(int,barycenter(l)))

def isDirect(po):
    """ Vérifie si le polygone est en sens direct """
    if len(po) <= 2 : return True
    ind, pt = max(enumerate(po), key = lambda i : i[1][0]*LEN+i[1][1])
    return det(po[(ind+1)%len(po)],pt,po[(ind-1)%len(po)]) >= 0
    

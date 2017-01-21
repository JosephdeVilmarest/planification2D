
LEN = 100000

def det(i,j,k):
    """ Calcule det((IJ),(IK)) """
    return (i[0]-j[0])*(k[1]-j[1])-(i[1]-j[1])*(k[0]-j[0])
def proj(i,j,k):
    """ Calcule (IJ).(IK) """
    return (i[0]-j[0])*(k[0]-j[0])+(i[1]-j[1])*(k[1]-j[1])
def norm2(i,j):
    """ Calculz ||IJ|| """
    return (i[0]-j[0])**2+(i[1]-j[1])**2
def segmentContains(a,b, c):
    """ Teste si c est dans [a,b] """
    return proj(a,c,b) == -norm2(a,c)-norm2(c,b)
def segmentsIntersect(a,b, c,d):
    """ Teste si [a,b] coupe [c,d] """
    return (det(a,c,b)*det(b,d,a) > 0 and det(c,a,d)*det(d,b,c) > 0) or (
                segmentContains(a,b, c) or segmentContains(a,b, d) or
                segmentContains(b,c, a) or segmentContains(b,c, b)) 

from math import sqrt, atan2, pi
from commun import *



def polyIsCrossed(p):
    l = len(p)
    if l > 2:
        for i in range(2,l):
            for j in range((i==l-1),i-1):
                if segmentsIntersect(p[i],p[i-l+1],p[j],p[j+1]):
                    return True


def interieur(polygone, point):
    m=len(polygone)
    #je teste si le point est a gauche de chaque arete orientee du polygone
    for i in range(m):
        if ((point[0]-polygone[i][0])*(polygone[i][1]-polygone[(i+1)%m][1])+
            (point[1]-polygone[i][1])*(polygone[(i+1)%m][0]-polygone[i][0])
                                <=0):
            return False
    return True

def get_convex(polygon):
    #on renvoie une liste de polygones convexes dont 
    #l'union (disjointe) est egale au polygone de depart
    #à completer: pour l'instant on prend des polygones convexes ^^
    def coupe(i,j):
        """Tells if the (i;j) edge is in the polygon"""
        l = len(polygon)
        if (i+1)%l == j:return False
        for k in range(l):
            if not {k,(k-1)%l}&{i,j} and segmentsIntersect(polygon[i],polygon[j],polygon[k],polygon[k-1]):
                return False
        a1 = atan2(polygon[i-1][0]-polygon[i][0],polygon[i-1][1]-polygon[i][1])
        a2 = atan2(polygon[(i+1)%l][0]-polygon[i][0],polygon[(i+1)%l][1]-polygon[i][1])
        if a2<a1 : a2+=2*pi
        a3 = atan2(polygon[j][0]-polygon[i][0],polygon[j][1]-polygon[i][1])
        if a3<a1 : a3+=2*pi
        return a3<a2
    #l2 = [[polygon[i],polygon[j]] for i in range(len(polygon)) for j in range(i-1) if coupe(i,j)]
    l=[]
    
    def recalcl():
        l.clear()
        for i in range(len(polygon)):
            for j in range(i-1):
                if coupe(i,j):
                    l.append((j,i))
#print("")
    recalcl()
    connus = {}
#    print(polygon)
#    print(l)

    def convexe(p):
        a,b = (p-1)%n, (p+1)%n
        return (min(a,b),max(a,b)) in l
    #print(len(polygon))
    if False:
#        retires = []
        while True:
            n = len(polygon)
            for p in range(len(polygon)):
                a,b = (p-1)%n, (p+1)%n
                if convexe(p) and convexe(b) and convexe(a):
                    del polygon[p]        
                    recalcl()
                    break
            else:
                break
    #print(len(polygon))

    app,appc = 0,0
    tt=0
    def best(p):
        nonlocal app, appc, tt
        app+=1
        p=tuple(p)
        if p in connus:
            appc+=1
            return connus[p]
        #t=time()
        if all((p[i],p[j]) in l for i in range(len(p)) for j in range(i+2, len(p) if i>0 else len(p)-1)):
            connus[p] = 0,[p]
            return 0,[p]
        m = 10000, None
        for i,a in enumerate(l):
            k,j = a
            if k in p and j in p:
                p0, p1 = decoupe(p,k,j)
                #print(p,k,j,p0,p1)
                if len(p0)>2 and len(p1)>2:
                    v0,l0 = best(p0)
                    v1,l1 = best(p1)
                    v = v1+v0+1
                    if v < m[0]:
                        m = v, l0+l1
        connus[p] = m
        return m
    
    ret = [[polygon[i] for i in p] for p in best(range(len(polygon)))[1]]
    #print(app,appc,time()-tt2,tt)
    return ret
    #return l#best(tuple(polygone))[0]


def decoupe(p, k, j):
    p0, p1 = [], []
    for i in range(len(p)):
        p0.append(p[i])
        if p[i]==k: break
    for i in range(i,len(p)):
        p1.append(p[i])
        if p[i]==j: break
    p0.extend(p[i:])
    return p0, p1
        
def angle_normal(polygone, epsilon):
    #on renvoie la liste des angles entre -pi et pi des normales aux aretes
    #epsilon=1 correspond aux obstacles: normales extérieures
    #epsilon=-1 correspond à l'objet: normales intérieures
    n=len(polygone)
    return [atan2(-epsilon*(polygone[(i+1)%n][0]-polygone[i][0]),
              epsilon*(polygone[(i+1)%n][1]-polygone[i][1])) 
                            for i in range(n)]


def sum_Minkowski(polygone, objet):
    n=len(polygone)
    m=len(objet)
    #le polygone est convexe donc ap est ordonnée, à une rotation près
    ap=angle_normal(polygone, 1)
    ao=angle_normal(objet, -1)
    i0=0
    while not((ap[(i0-1)%n]<=ao[0] and ao[0]<=ap[i0]) or 
                (ap[i0]<=ap[(i0-1)%n] and ao[0]<=ap[i0]) or 
                (ap[(i0-1)%n]<=ao[0] and ap[i0]<=ap[(i0-1)%n])):
        i0=(i0+1)%n
    i=i0 #indice de parcours de ap
    j=1  #indice de parcours de ao
    S=[(polygone[i][0]-(objet[1][0]-objet[0][0]), 
                        polygone[i][1]-(objet[1][1]-objet[0][1]))]
    P=S[0]  #dernier point utilisé
    a=ao[0] #dernier angle utilisé
    flag=True
    while j!=0 or i!=i0:
        if (flag and ((ap[i]>=a and ao[j]>ap[i]) or (ap[i]>=a and ao[j]<a)
            or (ao[j]<a and ao[j]>ap[i]))):
            P=(P[0]+(polygone[(i+1)%n][0]-polygone[i][0]),
               P[1]+(polygone[(i+1)%n][1]-polygone[i][1]))
            S.append(P)
            a=ap[i]
            i=(i+1)%n
            if i==i0:
                flag=False
        else:
            P=(P[0]-(objet[(j+1)%m][0]-objet[j][0]),
               P[1]-(objet[(j+1)%m][1]-objet[j][1]))
            S.append(P)
            a=ao[j]
            j=(j+1)%m
    return S


def convexDecomposition(environment):
    convex = []
    for polygon in environment:
        convex.extend(get_convex(polygon))
    return convex
    

def simplify(lobstacles, objet = []):
    #l est la liste des obstacles: liste de polygones
    #o est l'objet que l'on veut déplacer (polygone)
    #print(lobstacles, objet)
    lconvexe=[]
    for polygone in lobstacles:
        lconvexe.extend(get_convex(polygone))
    #la liste des obstacles est maintenant la liste des polygones convexes
    #print("ici", lconvexe)
    p = []#[sum_Minkowski(polygone,objet) for polygone in lconvexe]
    #print("ok")
    #lconvexe = [p]#[[(10,10),(5000,5000),(2000,2000)]]
    return p, lconvexe

def MinkowskiSum(envi,obj):
    l = []
    for p in envi:
        l.append(sum_Minkowski(p,obj))
    return l

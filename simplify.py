from math import sqrt, atan2

def get_convex(polygone):
    #on renvoie une liste de polygones convexes dont 
    #l'union (disjointe) est égale au polygone de départ
    #à compléter: pour l'instant on prend des polygones convexes ^^
    n=len(polygone)
    i=0
    while ((polygone[(i+1)%n][1]-polygone[i][1])*
                (polygone[(i+2)%n][0]-polygone[(i+1)%n][0])-
           (polygone[(i+1)%n][0]-polygone[i][0])*
                (polygone[(i+2)%n][1]-polygone[(i+1)%n][1])>0):
        #on trouve un premier "point convexe"
        i+=1
    i0=i
    i+=1
    while ((polygone[(i+1)%n][1]-polygone[i][1])*
                (polygone[(i+2)%n][0]-polygone[(i+1)%n][0])-
           (polygone[(i+1)%n][0]-polygone[i][0])*
                (polygone[(i+2)%n][1]-polygone[(i+1)%n][1])<0) and (i!=i0):
        #on trouve un "point concave" s'il existe
        i=(i+1)%n
    if (i==i0):
        #le polygone est convexe
        return [polygone]
    j=(i-1)%n
    while ((polygone[(i+1)%n][1]-polygone[i][1])*
                (polygone[j][0]-polygone[(i+1)%n][0])-
           (polygone[(i+1)%n][0]-polygone[i][0])*
                (polygone[j][1]-polygone[(i+1)%n][1])<0):
        #on cherche un grand sous-polygone-convexe
        j=(j-1)%n
    j=(j+1)%n
    if j<i+1:
        ans=get_convex(polygone[(i+1):]+polygone[:(j+1)])
        ans.extend(get_convex(polygone[j:(i+2)]))
    else:
        ans=get_convex(polygone[(i+1):(j+1)])
        ans.extend(get_convex(polygone[j:]+polygone[:(i+2)]))
    return ans


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
    i0=1
    while ap[i0-1]>ao[0] or ap[i0%n]<ao[0]:
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



def simplify(lobstacles, objet):
    #l est la liste des obstacles: liste de polygones
    #o est l'objet que l'on veut déplacer (polygone)
    print(lobstacles, objet)
    lconvexe=[]
    for polygone in lobstacles:
        lconvexe.extend(get_convex(polygone))
    #la liste des obstacles est maintenant la liste des polygones convexes
    print("ici", lconvexe)
    p = []#[sum_Minkowski(polygone,objet) for polygone in lconvexe]
    print("ok")
    return p, lconvexe

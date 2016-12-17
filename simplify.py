def get_convex(polygone):
    #on renvoie une liste de polygones convexes dont 
    #l'union (disjointe) est égale au polygone de départ
    #à compléter: pour l'instant on prend des polygones convexes ^^
    return [polygone]

def angle_normal(polygone, epsilon):
    #on renvoie la liste des angles entre -pi et pi des normales aux aretes
    #epsilon=1 correspond aux obstacles: normales extérieures
    #epsilon=-1 correspond à l'objet: normales intérieures
    n=len(polygone)
    l=[atan2(-epsilon*(l[i+1][1]-l[i][1]),epsilon*(l[i+1][0]-l[i][0])) 
                            for i in range(n-1)]
    l.append(atan2(-epsilon*(l[0][1]-l[n-1][1]),epsilon*(l[0][0]-l[n-1][0])))
    return l

def sum_Minkovski(polygone, objet):
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
    S=[polygone[i], (polygone[i][0]+(objet[1][0]-objet[0][0]), 
                        polygone[i][1]+(objet[1][1]-objet[0][1]))]
    P=S[1]  #dernier point utilisé
    a=ao[0] #dernier angle utilisé
    while j!=0 or i!=i0:
        if (ap[i]>=a and ao[j]>ap[i]) or (ap[i]>=a and ao[j]<a)
            or (ao[i]<a and ao[i]>ap[i]):
            P=(P[0]+(polygone[(i+1)%n][0]-polygone[i][0]),
               P[1]+(polygone[(i+1)%n][1]-polygone[i][1]))
            S.append(P)
            a=ap[i]
            i=(i+1)%n
        else:
            P=(P[0]+(objet[(j+1)%m][0]-objet[j][0]),
               P[1]+(objet[(j+1)%m][1]-objet[j][1]))
            S.append(P)
            a=ap[j]
            j=(j+1)%n
    return S

def simplify(lobstacles, objet):
    #l est la liste des obstacles: liste de polygones
    #un polygone est une liste de points
    #un point est un couple d'entiers
    #o est l'objet que l'on veut déplacer (polygone)

    lconvexe=[]
    for polygone in lobstacles:
        lconvexe.extend(get_convexe(polygone))
    #la liste des obstacles est maintenant la liste des polygones convexes

    return [sum_Minkovski(polygone,objet) for polygone in lconvexe] 

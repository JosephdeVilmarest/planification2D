from math import sqrt, atan2

def interieur(polygone, point):
    m=len(polygone)
    #je teste si le point est a gauche de chaque arete orientee du polygone
    for i in range(m):
        if ((point[0]-polygone[i][0])*(polygone[i][1]-polygone[(i+1)%m][1])+
            (point[1]-polygone[i][1])*(polygone[(i+1)%m][0]-polygone[i][0])
                                <=0):
            return False
    return True

def is_angle_convex(p1,p2,p3):
    return ((p3[1]-p2[1])*(p2[0]-p1[0])-(p3[0]-p2[0])*(p2[1]-p1[1])>=0)

def get_convex(polygone):
    #on renvoie une liste de polygones convexes dont 
    #l'union (disjointe) est egale au polygone de depart
    #à completer: pour l'instant on prend des polygones convexes ^^
    n=len(polygone)
    i=0
    while True:
        while not(is_angle_convex(polygone[i],
                polygone[(i+1)%n],polygone[(i+2)%n])):
            #on trouve un premier "point convexe"
            i=(i+1)%n
        i0=i
        i=(i+1)%n
        while is_angle_convex(polygone[i],
                polygone[(i+1)%n],polygone[(i+2)%n]) and (i!=i0):
            #on trouve un "point concave" s'il existe
            i=(i+1)%n
        print("i vaut", i)
        if (i==i0):
            #le polygone est convexe
            print("le polygone est convexe",polygone)
            return [polygone]
        j=(i-1)%n
        flag=True
        while is_angle_convex(polygone[i],
                polygone[(i+1)%n],polygone[j]) and flag and (j!=i):
            #on cherche un grand sous-polygone convexe
            print(j)
            if j<(i+1)%n:
                pol=polygone[j:(i+2)]
                for k in range(j):
                    if interieur(pol,polygone[k]):
                        flag=False
                for k in range(i+2,n):
                    if interieur(pol,polygone[k]):
                        flag=False
            else:
                pol=polygone[j:]+polygone[:(i+2)]
                for k in range(i+2,j):
                    if interieur(pol,polygone[k]):
                        flag=False
            j=(j-1)%n

        j=(j+1)%n
        if not(flag):
            j=(j+1)%n
        print("j vaut ",j)

        if j==(i-1)%n:
            #on n'a qu'un segment
            i+=1

        else:
            if j<(i+1)%n:
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

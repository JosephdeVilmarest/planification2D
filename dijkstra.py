from math import sqrt


def eucl_dist(p1,p2):
    return sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)


def dijkstra(S,M):
    #S est la liste des points comme defini dans visibility
    #M matrice d'adjacence
    #On cherche le plus court chemin entre depart et arrivee
    #qui sont les 2 premiers points de S
    
    n=len(S)
    #on initialise les differentes listes utilisees
    visite=[0 for i in range(n)]
    visite[0]=1
    
    #on stocke dans distances la longueur du meilleur chemin connu
    #on stocke egalement le dernier sommet par lequel on passerait
    distances=[(M[i][0]*eucl_dist(S[0],S[i]), 0) for i in range(n)]

    chemins=[[] for i in range(n)]

    flag=True #devient False si plus aucun sommet ne peut etre relie
    #on applique Dijkstra jusqu'a trouver un chemin de 0 a 1
    while flag and not(visite[1]):
        #on regarde quel est le sommet le plus proche
        imin=0
        for i in range(1,n):
            if (not(visite[i]) and distances[i][0]!=0 and 
                    (imin==0 or distances[i][0]<distances[imin][0])):
                    imin=i
        if imin==0:
            #on n'a trouve aucun sommet a ajouter
            flag=False
        else:
            #on marque le chemin optimal trouve pour imin
            visite[imin]=1
            chemins[imin]=chemins[distances[imin][1]]+[S[distances[imin][1]][0]]

            #on met a jour les distances grace au nouveau chemin optimal
            for i in range(1,n):
                if (not(visite[i]) and M[imin][i] and (distances[i][0]==0
                        or (distances[imin][0]+eucl_dist(S[imin],S[i])
                                                        <distances[i][0]))):
                    distances[i]=[distances[imin][0]
                                        +eucl_dist(S[imin],S[i]),imin]
    
    #on teste si on a trouve un chemin
    if visite[1]:
        return chemins[1]+[S[1]]

    return []

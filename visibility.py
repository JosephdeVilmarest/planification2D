def intersect(p1,p2,p3,p4):
    #On regarde si les segments [p1,p2] et [p3,p4] s'intersectent
    #Pour cela on calcule le point d'intersection des droites
    #et on regarde s'il appartient aux deux segments
    u=(p2[0]-p1[0], p2[1]-p1[1])
    v=(p4[0]-p3[0], p4[1]-p3[1])

    #On traite le cas ou les segments sont paralleles
    if u[0]*v[1]-u[1]*v[0]==0:
        if v[0]:
            a=(p1[0]-p3[0])/v[0]
        elif v[1]:
            a=(p1[1]-p3[1])/v[1]
        if ((v[0] or v[1]) and p1[0]==p3[0]+a*v[0] and 
                        p1[1]==p3[1]+a*v[1] and 0<=a and a<=1):
            return True
        
        if v[0]:
            a=(p2[0]-p3[0])/v[0]
        elif v[1]:
            a=(p2[1]-p3[1])/v[1]
        if ((v[0] or v[1]) and p2[0]==p3[0]+a*v[0] and 
                        p2[1]==p3[1]+a*v[1] and 0<=a and a<=1):
            return True
        
        return False
    
    a=(v[1]*(p3[0]-p1[0])-v[0]*(p3[1]-p1[1]))/(u[0]*v[1]-u[1]*v[0])
    b=(u[1]*(p3[0]-p1[0])-u[0]*(p3[1]-p1[1]))/(-u[1]*v[0]+u[0]*v[1])
    return (0<=a and a<=1 and 0<=b and b<=1)



def visibility_graph(depart, arrivee, lobstacles):
    #je calcule le graphe de visibilite du problème
    #sous la forme (sommets, matrice d'adjacence)

    #On met d'abord les sommets dans S:
    #chaque sommet est le couple (point, numero du polygone)
    #en affectant -1 aux points de départ et d'arrivée
    S=[(depart,-1), (arrivee,-1)]
    for i in range(len(lobstacles)):
        for point in lobstacles[i]:
            S.append((point,i))

    n=len(S)
    M=[[0 for j in range(n)] for i in range(n)]

    #Premieres aretes: celles des polygones
    i=2
    while i<n:
        m=len(lobstacles[S[i][1]])
        M[i][i+m-1]=1
        M[i+m-1][i]=1
        for k in range(m-1):
            M[i+k][i+k+1]=1
            M[i+k+1][i+k]=1
        i=i+m

    #Secondes aretes: entre points n'appartenant pas au meme polygone
    for i in range(n):
        for j in range(i):
            #On évite les aretes entre points d'un meme polygone
            if S[i][1]==-1 or S[i][1]!=S[j][1]:
                flag=True
                #on regarde si [i,j] intersecte une arete
                for polygone in lobstacles:
                    m=len(polygone)
                    for k in range(m):
                        #cette condition est necessaire car on refuse
                        #l'arete lorsqu'elle passe par un autre point
                        if (polygone[k]!=S[i][0] and polygone[k]!=S[j][0]
                            and polygone[(k+1)%m]!=S[i][0]
                            and polygone[(k+1)%m]!=S[j][0]
                            and intersect(S[i][0],S[j][0],
                                polygone[k],polygone[(k+1)%m])):
                            flag=False
                if flag:
                    M[i][j]=1
                    M[j][i]=1
    return (S,M)

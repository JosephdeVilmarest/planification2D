def merge(l1,l2):
    n,m=len(l1),len(l2)
    i,j=0,0
    l=[]
    while i<n and j<m:
        if l1[i][0][0]<l2[j][0][0]:
            l.append(l1[i])
            i += 1
        else:
            l.append(l2[j])
            j += 1
    if i<n:
        l.extend(l1[i:])
    else:
        l.extend(l2[j:])
    return l

def merge_sort(l):
    #on renvoie les indices de l triee par abscisse croissante
    #il y a surement une fonction python qui fait ca que je ne connais pas
    l=[[l[i],i] for i in range(len(l))]
    def aux(l):
        if len(l)<2:
            return l
        return merge(aux(l[:len(l)//2]),aux(l[len(l)//2:]))
    lprime=aux(l)
    return [lprime[i][1] for i in range(len(l))]




def evaldroite(p1,p2,x):
    if p1[1] in ["Infneg", "Infpos"]:
        #dans ce cas notons qu'on a aussi p2[1] infini
        return p1[1]
    if p1[0]==p2[0]:
        #c'est un cas singulier
        return "Inf"
    return p1[1]+(x-p1[0])*(p2[1]-p1[1])/(p2[0]-p1[0])

def droite_inf(point,droites):
    #dans droites il y a les droites infinies a la fin
    m=len(droites)-2
    flag=True
    ymax=0
    imax=0
    for i in range(m):
        if droites[i]:
            y=evaldroite(droites[i][0][0],droites[i][0][1],point[0])
            if (y!="Inf" and y<point[1] and (flag or y>ymax)):
                flag=False
                ymax=y
                imax=i
    if flag:
        return m+1
    return imax

def droite_sup(point,droites):
    #dans droites il y a les droites infinies a la fin
    m=len(droites)-2
    flag=True
    ymin=0
    imin=0
    for i in range(m):
        if droites[i]:
            y=evaldroite(droites[i][1][0],droites[i][1][1],point[0])
            if (y!="Inf" and y>point[1] and (flag or y<ymin)):
                flag=False
                ymin=y
                imin=i
    if flag:
        return m
    return imin




def scanning(lobstacles):
    #renvoie la liste des cellules 
    S=[]
    for i in range(len(lobstacles)):
        for point in lobstacles[i]:
            S.append((point,i))
    n=len(S)
    I=merge_sort([S[i][0] for i in range(n)])
    #on garde les segments de chaque polygone qu'on a commence a voir
    #on ajoute des segments infinis
    droites=[[] for i in range(len(lobstacles))]
    droites.append([[("Infneg","Infpos"), ("Infpos","Infpos")],
                        [("Infneg","Infpos"), ("Infpos","Infpos")]])
    droites.append([[("Infneg","Infneg"), ("Infpos","Infneg")],
                        [("Infneg","Infneg"), ("Infpos","Infneg")]])
    #on definit une cellule par 4 points eventuellement infinis
    cellules=[]

    for j in range(n):
        i=I[j]
        point=S[i][0]
        np=S[i][1]
        if droites[np]==[]:
            iinf=droite_inf(point,droites)
            p1=droites[iinf][0][0]
            p2=droites[iinf][0][1]
            pinf=(point[0], evaldroite(p1,p2,point[0]))
            
            isup=droite_sup(point,droites)
            p1=droites[isup][1][0]
            p2=droites[isup][1][1]
            psup=(point[0],evaldroite(p1,p2,point[0]))

            cellules.append((droites[isup][1][0],droites[iinf][0][0],
                                pinf,psup))
            #on met a jour les droites rencontrees
            droites[iinf][0][0]=pinf
            droites[isup][1][0]=psup
            #on ajoute les droites du polygone
            if (i>0 and S[i-1][1]==np):
                droites[np].append([point,S[i-1][0]])
            else:
                droites[np].append([point,S[i+len(lobstacles[np])-1][0]])
            if (i+1<n and S[i+1][1]==np):
                droites[np].append([point,S[i+1][0]])
            else:
                droites[np].append([point,S[i-(len(lobstacles[np])-1)][0]])

        elif not(point in droites[np][0]):
            #dans ce cas point=droites[np][1][1]
            #iinf: indice de la premiere droite sous point
            iinf=droite_inf(point,droites)
            p1=droites[iinf][0][0]
            p2=droites[iinf][0][1]
            p=(point[0], evaldroite(p1,p2,point[0]))
            cellules.append((droites[np][1][0],droites[iinf][0][0],p,point))
            
            #on met a jour les droites
            if (i+1<n and S[i+1][1]==np):
                droites[np][1]=[point,S[i+1][0]]
            else:
                droites[np][1]=[point,S[i-(len(lobstacles[np])-1)][0]]
            droites[iinf][0][0]=p

        elif not(point in droites[np][1]):
            #dans ce cas point=droites[np][0][1]
            #iinf: indice de la premiere droite sous point
            isup=droite_sup(point,droites)
            p1=droites[isup][1][0]
            p2=droites[isup][1][1]
            p=(point[0],evaldroite(p1,p2,point[0]))
            cellules.append((droites[isup][1][0],droites[np][0][0],point,p))
            
            #on met a jour les droites
            if S[i-1][1]==np:
                droites[np][0]=[point,S[i-1][0]]
            else:
                droites[np][0]=[point,S[i+(len(lobstacles[np])-1)]]
            droites[isup][1][0]=p
        
        else:
            #point=droites[np][0][1]=droites[np][1][1]
            iinf=droite_inf(point,droites)
            p1=droites[iinf][0][0]
            p2=droites[iinf][0][1]
            pinf=(point[0], evaldroite(p1,p2,point[0]))
            cellules.append((droites[np][1][0],droites[iinf][0][0],
                                    pinf,point))
            
            isup=droite_sup(point,droites)
            p1=droites[isup][1][0]
            p2=droites[isup][1][1]
            psup=(point[0],evaldroite(p1,p2,point[0]))
            cellules.append((droites[isup][1][0],droites[np][0][0],
                                    point,psup))
            
            #on met a jour les droites:
            #les droites rencontrees
            droites[iinf][0][0]=pinf
            droites[isup][1][0]=psup
            #on supprime les droites du polygone car on a fini de le visiter
            droites[np]=[]

    #on ajoute la derniere cellule
    cellules.append(((S[I[n-1]][0][0],"Infpos"),(S[I[n-1]][0][0], "Infneg"),
                        ("Infpos", "Infneg"),("Infpos", "Infpos")))

    return cellules

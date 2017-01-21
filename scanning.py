from commun import *

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




def eval_droite(p1,p2,x):
    return p1[1]+(x-p1[0])*(p2[1]-p1[1])//(p2[0]-p1[0])

def evalDroite(d,x):
    return eval_droite(d[0][1],d[1][1],x)

def droite_inf(point,droites):
    #dans droites il y a les droites infinies a la fin
    for i in reversed(droites):
        y = evalDroite(i,point[0])
        if y < point[1] or y == point[1] and y != LEN:
            return i
    assert False,"Droite inf non trouvée"

def droite_sup(point,droites):
    #dans droites il y a les droites infinies a la fin
    for i in droites:
        y = evalDroite(i,point[0])
        if y > point[1] or y == point[1] and y != 0:
            return i
    assert False,"Droite sup non trouvée"

class Segment():
    def __init__(self, p1, p2, x, y):
        self.data = [p1,p2,x,y]
    def __getitem__(self,i):
        return self.data[i]
    def __setitem__(self,i,d):
        self.data[i] = d
    def __eq__(self,s):
        return self is s

def scanning(lobstacles,LEN):
    #renvoie la liste des cellules
    #print(lobstacles)
    cells = []
    
    envi = []
    for p in lobstacles:
        l = len(p)
        for i in range(l):
            p[i] = [None,p[i],None]
        for i in range(l):
            p[i-1][2] = p[i]
            p[(i+1)%l][0] = p[i]
        envi += p
    envi.sort(key = lambda e : LEN*e[1][0]+e[1][1])

    p = [None, (LEN,0), None]
    p = [p, (0,0), p]
    p[0][2] = p
    p[2][0] = p
    q = [None, (LEN,LEN), None]
    q = [q, (0,LEN), q]
    q[0][2] = q
    q[2][0] = q
    # Point1, Point2, x dernière droite vue
    segments = [Segment(p,p[0],0,p[1][1]),
                Segment(q,q[0],0,q[1][1])]

    for pt in envi:
        p = list(filter(lambda e : pt is e[1], segments))
        if len(p) == 0:
            drSup = droite_sup(pt[1], segments)
            drInf = droite_inf(pt[1], segments)
            k = segments.index(drSup)
            if det(pt[0][1],pt[1],pt[2][1])<0:
                assert drSup[2]==drInf[2], "Bizarre"
                cells.append(((pt[1][0],evalDroite(drSup,pt[1][0])),
                              (drSup[2],evalDroite(drSup,drSup[2])),
                #              (drSup[2],pt[1][1]),(pt[1][0],pt[1][1])))
                #cells.append(((pt[1][0],pt[1][1]),(drInf[2],pt[1][1]),
                              (drInf[2],evalDroite(drInf,drInf[2])),
                              (pt[1][0],evalDroite(drInf,pt[1][0]))))
                drSup[2] = pt[1][0]
                drSup[3] = evalDroite(drSup, pt[1][0])
                drInf[2] = pt[1][0]
                drInf[3] = evalDroite(drInf, pt[1][0])
                segments.insert(k,Segment(pt,pt[0],pt[1][0],pt[1][1]))
                segments.insert(k,Segment(pt,pt[2],pt[1][0],pt[1][1]))
            else:
                segments.insert(k,Segment(pt,pt[2],pt[1][0],pt[1][1]))
                segments.insert(k,Segment(pt,pt[0],pt[1][0],pt[1][1]))
        elif len(p) == 1:
            dr = p[0]
            if dr[0] is pt[0]: # vers le bas
                segments.remove(dr)
                drInf = droite_inf(pt[1],segments)
                assert drInf[2]==dr[2], "Bizarre"
                cells.append(((pt[1][0],pt[1][1]),
                              (dr[2],dr[3]),(drInf[2],drInf[3]),
                              (pt[1][0],evalDroite(drInf, pt[1][0]))))
                drInf[2] = pt[1][0]
                drInf[3] = evalDroite(drInf, pt[1][0])
                segments.insert(segments.index(drInf)+1,
                                Segment(pt,pt[2],pt[1][0],pt[1][1]))
            elif dr[0] is pt[2]: # vers le haut
                segments.remove(dr)
                drSup = droite_sup(pt[1],segments)
                assert drSup[2]==dr[2], "Bizarre"
                cells.append(((pt[1][0],evalDroite(drSup, pt[1][0])),
                              (drSup[2],drSup[3]),(dr[2],dr[3]),
                              (pt[1][0],pt[1][1])))
                drSup[2] = pt[1][0]
                drSup[3] = evalDroite(drSup, pt[1][0])
                segments.insert(segments.index(drSup),
                                Segment(pt,pt[0],pt[1][0],pt[1][1]))
            else:
                assert False,"Pas dans la droite"
        elif len(p) == 2:
            di = p[0]
            ds = p[1]
            segments.remove(ds)
            segments.remove(di)
            drSup = droite_sup(pt[1], segments)
            drInf = droite_inf(pt[1], segments)
            if det(pt[0][1],pt[1],pt[2][1])<0:
                assert di[2]==drInf[2], "Bizarre"
                assert ds[2]==drSup[2], "Bizarre"
                cells.append(((pt[1][0],evalDroite(drSup, pt[1][0])),
                              (drSup[2],drSup[3]),(ds[2],ds[3]),
                              (pt[1][0],pt[1][1])))
                cells.append(((pt[1][0],pt[1][1]),
                              (di[2],di[3]),(drInf[2],drInf[3]),
                              (pt[1][0],evalDroite(drInf, pt[1][0]))))
                drSup[2] = pt[1][0]
                drSup[3] = evalDroite(drSup, pt[1][0])
                drInf[2] = pt[1][0]
                drInf[3] = evalDroite(drInf, pt[1][0])
            else:
                assert ds[2]==di[2], "Bizarre"
                cells.append(((pt[1][0],pt[1][1]),
                              (ds[2],ds[3]),(di[2],di[3]),
                              (pt[1][0],pt[1][1])))
                
        else:
            assert False
    assert len(segments)==2
    cells.append(((segments[0][2],segments[0][3]),
                  (segments[0][1][1][0],segments[0][1][1][1]),
                  (segments[-1][1][1][0],segments[-1][1][1][1]),
                  (segments[-1][2],segments[-1][3])))
    return cells


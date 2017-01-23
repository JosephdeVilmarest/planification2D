from commun import *


def eval_droite(p1,p2,x):
    if x == p2[0]: return p2[1]
    return p1[1]+(x-p1[0])*(p2[1]-p1[1])//(p2[0]-p1[0])

def evalDroite(d,x):
    return eval_droite(d[0][1],d[1][1],x)

def droite_inf(point,droites):
    #dans droites il y a les droites infinies a la fin
    for i in reversed(droites):
        y = i.value(point[0])
        if y < point[1] or y == point[1] and y != LEN:
            return i
    assert False,"Droite inf non trouvée"

def droite_sup(point,droites):
    #dans droites il y a les droites infinies a la fin
    for i in droites:
        y = i.value(point[0])
        if y > point[1] or y == point[1] and y != 0:
            return i
    assert False,"Droite sup non trouvée"


class Segment():
    def __init__(self, p1, p2, x, y, cell):
        self.data = [p1,p2,x,y,cell]
    def __getitem__(self,i):
        return self.data[i]
    def __setitem__(self,i,d):
        self.data[i] = d
    def __eq__(self,s):
        return self is s
    
class Segment():
    def __init__(self, p1,p2,cell=None):
        self.p1 = p1
        self.p2 = p2
        self.lastX = p1[1][0]
        self.lastY = p1[1][1]
        self.lastCell = cell

    def value(self, x):
        return eval_droite(self.p1[1],self.p2[1],x)
        
class Cell():
    def __init__(self,x,sMin,sMax):
        self.isEmpty = True
        assert sMin.lastX == sMax.lastX
        yMin = sMin.value(x)
        yMax = sMax.value(x)
        self.trap = [(x,yMax),(sMax.lastX,sMax.lastY),
                     (sMin.lastX,sMin.lastY),(x,yMin)]
        self.bar = barycenterInt(self.trap)
        self.rightHeight = yMax-yMin
        if sMin.lastY != sMax.lastY:
            self.isEmpty = False
            if sMin.lastCell:
                sMin.lastCell.addNext(self)
            sMin.lastCell = None
            if sMax.lastCell:
                sMax.lastCell.addNext(self)
            sMax.lastCell = None
        if self.rightHeight:
            self.isEmpty = False
            sMin.lastCell = self
            sMax.lastCell = self
        sMin.lastX = x
        sMax.lastX = x
        sMin.lastY = yMin
        sMax.lastY = yMax
        self.nextCells = []

    def addNext(self,cell):
        self.nextCells.append(cell)

    def realCell(self):
        return None if self.isEmpty else self

def scanning(lobstacles,LEN):
    #renvoie la liste des cellules
    cells = []

    envi = []
    
    for p in lobstacles:
        l = len(p)
        q = [None]*l
        for i in range(l):
            q[i] = [None,p[i],None]
        for i in range(l):
            q[i-1][2] = q[i]
            q[(i+1)%l][0] = q[i]
        envi += q
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
    segments = [Segment(p,p[0]),
                Segment(q,q[0])]

    for pt in envi:
        p = list(filter(lambda e : pt is e.p2, segments))
        x = pt[1][0]
        if len(p) == 0:
            drSup = droite_sup(pt[1], segments)
            drInf = droite_inf(pt[1], segments)
            k = segments.index(drSup)
            if det(pt[0][1],pt[1],pt[2][1])<0:
                c = Cell(x,drInf,drSup).realCell()
                if c : cells.append(c)
                segments.insert(k,Segment(pt,pt[0],c))
                segments.insert(k,Segment(pt,pt[2],c))
            else:
                segments.insert(k,Segment(pt,pt[2]))
                segments.insert(k,Segment(pt,pt[0]))
        elif len(p) == 1:
            dr = p[0]
            if dr.p1 is pt[0]: # vers le bas
                segments.remove(dr)
                drInf = droite_inf(pt[1],segments)
                c = Cell(x, drInf, dr).realCell()
                if c : cells.append(c)
                segments.insert(segments.index(drInf)+1, Segment(pt,pt[2],c))
            elif dr.p1 is pt[2]: # vers le haut
                segments.remove(dr)
                drSup = droite_sup(pt[1],segments)
                c = Cell(x, dr, drSup).realCell()
                if c : cells.append(c)
                segments.insert(segments.index(drSup), Segment(pt,pt[0],c))
            else:
                assert False,"Pas dans la droite"
        elif len(p) == 2:
            di = p[0]
            ds = p[1]
            segments.remove(ds)
            segments.remove(di)
            if det(pt[0][1],pt[1],pt[2][1])<0:
                drSup = droite_sup(pt[1], segments)
                drInf = droite_inf(pt[1], segments)
                c = Cell(x, ds, drSup).realCell()
                if c : cells.append(c)
                c = Cell(x, drInf, di).realCell()
                if c : cells.append(c)
            else:
                c = Cell(x, di, ds).realCell()
                if c : cells.append(c)
        else:
            assert False
    assert len(segments)==2 # Ambitieux !
    c = Cell(LEN,segments[0], segments[-1]).realCell()
    if c : cells.append(c)
    return cells


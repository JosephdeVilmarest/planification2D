from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sys import argv
from enum import IntEnum
from simplify import simplify
from visibility import visibility_graph
from dijkstra import dijkstra

State = IntEnum("State", "Idle Adding Begin End")

class Main(QMainWindow):
    """ La fenêtre principale """
    def __init__(self, *args):
        super().__init__(*args)
        self.setWindowTitle("Planification 2D")
        self.zone = Zone()
        self.resize(800,600)
        self.setCentralWidget(self.zone)
        #self.setFixedSize(400,400)
        tb = self.addToolBar("Plan2D")
        act = QAction("Effacer", self)
        act.triggered.connect(self.clear)
        tb.addAction(act)
        act = QAction("Simplifier", self)
        act.setToolTip("Prend le premier polygone, le supprime et l'applique aux autres")
        act.triggered.connect(self.simplify)
        tb.addAction(act)
        act = QAction("Visibilité", self)
        act.setToolTip("Graphe de visibilité")
        act.triggered.connect(self.visibility)
        tb.addAction(act)
        act = QAction("Dijkstra", self)
        act.setToolTip("Graphe de visibilité")
        act.triggered.connect(self.dijkstra)
        tb.addAction(act)

    def clear(self):
        self.zones.clear()
        self.update()
        
    def simplify(self):
        if len(self.zone.polys)<2:
            QMessageBox.information(self, "Simplify", "Créez au moins deux polygones...")
            return
        self.zone.polys = simplify(self.zone.polys[1:], self.zone.polys[0])
        self.update()
    
    def visibility(self):
        if not self.zone.begin or not self.zone.end:
            QMessageBox.information(self, "visibility", "Posez un point de début, un point d'arrivée et relancez")
            self.zone.state = State.Begin
            return
        self.zone.vg = visibility_graph(self.zone.begin, self.zone.end, self.zone.polys)
        self.update()

    def dijkstra(self):
        if not self.zone.vg:
            QMessageBox.information(self, "dijkstra", "Créez d'abord le graphe de visibilité")
            return
        self.zone.dj = dijkstra(*self.zone.vg)
        self.update()
        

class Zone(QWidget):
    """ La zone où sont affichés les polygones """
    def __init__(self, *args):
        super().__init__(*args)
        self.clear()
        
    def clear(self):
        self.polys = []    
        self.state = State.Idle
        self.points = []
        self.begin = None
        self.end = None
        self.dj=None
        self.vg = None
        
    def paintEvent(self, event):
        paint = QPainter(self)
        #grad = QRadialGradient(0,0, 100)
        #grad.setColorAt(0, Qt.white)
        #grad.setColorAt(1, Qt.red)
        paint.setBrush(Qt.red)
        for pl in self.polys:
            paint.drawPolygon(QPolygon([QPoint(*p) for p in pl]))
        for i in range(len(self.points)-1):
            paint.drawLine(*self.points[i], *self.points[i+1])
        for p in self.points:
            paint.drawEllipse(*p, 5, 5)
        paint.setBrush(Qt.green)
        if self.begin:
            paint.drawEllipse(*self.begin, 5, 5)
        if self.end:
            paint.drawEllipse(*self.end, 5, 5)
        if self.vg:
            S, M = self.vg
            for i in range(len(S)):
                paint.drawEllipse(*S[i][0], 5, 5)
            for i in range(len(M)):
                for j in range(i,len(M[0])):
                    if M[i][j]:
                        paint.drawLine(*S[i][0], *S[j][0])
        if self.dj:
            pen = QPen(Qt.darkGreen)
            pen.setWidth(3)
            paint.setPen(pen)
            for i in range(len(self.dj)-1):
                paint.drawLine(*self.dj[i], *self.dj[i+1])
            
#        QPolygon([QPoint(*p) for p in self.points]))
        
    def mousePressEvent(self, event):
        x,y = event.x(), event.y()
        if event.button() ==  Qt.LeftButton:
            if self.state == State.Idle:
                self.state = State.Adding
            if self.state == State.Adding:
                for px,py in self.points:
                    if dist((x,y),(px,py))<20:
                        self.polys.append(self.points)
                        #
                        self.points = []
                        self.state = State.Idle
                        break
                else:                  
                    self.points.append((x,y))
            if self.state == State.Begin:
                self.begin = x,y
                self.state = State.End
            elif self.state ==  State.End:
                self.end = x,y
                self.state = State.Idle
        elif event.button() == Qt.RightButton:
            self.state = State.Idle
            self.points = []
        self.update()

def dist(p1,p2):
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**.5

app = QApplication(argv)
fen = Main()
fen.show()
app.exec()

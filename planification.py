from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.uic import loadUiType
import sys
from colorsys import hsv_to_rgb

from random import randint
from simplify import simplify

EL_SIZE = 15
LEN = 100000

class Step(QObject):
    stateChanged = pyqtSignal()
    def __init__(self, name = "Étape i", image = "tracer.png", parent = None):
        super().__init__()
        self.isValidConfig = lambda *conf : True
        self.transform = lambda *conf : (conf,[])
        self.nextSteps = []
        self.parent = parent
        if parent:
            parent.nextSteps.append(self)
        self.name = name
        self.image = image
        self.nextStep = None

    def setEnabled(self, e):
        if not e:
            for i in self.nextSteps:
                i.setEnabled(e)
        elif self.button.isChecked():
            for step in self.nextSteps:
                step.setEnabled(True)
        self.button.setEnabled(e)
        
        
    def setActive(self, a):
        self.button.setChecked(a)
        if a:
            if self.parent:
                for i in filter(lambda a : a!=self, self.parent.nextSteps):
                    i.setActive(False)
            for step in self.nextSteps:
                step.setEnabled(True)
        else:
            for step in self.nextSteps:
                step.setActive(a)
                step.setEnabled(False)
        self.stateChanged.emit()
        if self.parent:
            self.parent.nextStep = self if a else None
            


    def update(self, *conf):
        if self.isValidConfig(*conf):
            self.setEnabled(True)
            if not self.button.isChecked():
                return []
            conf,items = self.transform(*conf)
            return items + self.nextStep.update(*conf) if self.nextStep else []
        self.setEnabled(False)


class StepPainter(QWidget):
    pipeLineChanged = pyqtSignal()
    def __init__(self, initStep, *args):
        super().__init__(*args)
        self.initStep = initStep
        self.lay = QVBoxLayout()
        self.setLayout(self.lay)
        self.lay.setSpacing(20)
        def addSteps(steps):
            nextSteps = []
            hLay = QHBoxLayout();
            self.lay.addLayout(hLay)
            for step in steps:
                but = QToolButton(self)
                hLay.addWidget(but)
                but.setText(step.name)
                but.setIcon(QIcon(step.image))
                but.setIconSize(QSize(128,64))
                but.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                but.setCheckable(True)
                step.button = but
                step.stateChanged.connect(self.update)
                step.stateChanged.connect(lambda : self.pipeLineChanged.emit())
                but.toggled.connect(step.setActive)
                nextSteps += step.nextSteps
            if nextSteps:
                addSteps(nextSteps)
        addSteps([initStep])
        self.lay.addItem(QSpacerItem(0,0,QSizePolicy.Expanding, QSizePolicy.Expanding))
        initStep.setActive(False)

    def paintEvent(self, pe):
        pa = QPainter(self)
        pa.setRenderHint(QPainter.Antialiasing)
        palette = self.palette()
        p = QPen(palette.color(QPalette.Button))
        p.setWidth(3)
        def drawRelation(step):
            for nextStep in step.nextSteps:
                p.setColor(palette.color(QPalette.Text) if nextStep.button.isChecked() else
                           palette.color(QPalette.Mid))
                pa.setPen(p)
                pa.drawLine(step.button.pos() + QPoint(step.button.width()//2,step.button.height()//2),
                            nextStep.button.pos() + QPoint(step.button.width()//2,step.button.height()//2))
                drawRelation(nextStep)
        pa.begin(self)
        drawRelation(self.initStep)
        pa.end()
        super().paintEvent(pe)




                                                
class Controller(QGraphicsEllipseItem):
    def __init__(self, scene, previous, *args):
        super().__init__(*args)
        self.previous = self
        self.next = self
        self.scene = scene
        self.setPrevious(previous)
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIgnoresTransformations |
                      QGraphicsItem.ItemSendsScenePositionChanges)
        self.new = True
        self.setCurrent(False)
        self.scene.setCurrentController(self)
        

    def setCurrent(self, b = True):
        self.setBrush(QColor(255,255,0) if b else QColor(255,100,0))
        self.setZValue(b)
        self.current = b

    def setPrevious(self, previous):
        if previous:
            previous.next.previous = self
            self.next = previous.next
            previous.next = self
            self.previous = previous
        else:
            self.previous = self
            self.next = self
            
    def contains(self, p):
        print("grrr")
        return False
        
    def setPos(self, p, quiet = False):
        super().setPos(p)
        if not quiet:
            self.scene.controllerMoved()
        self.scene.updateDirectLine()

    def mouseMoveEvent(self, me):
        super().mouseMoveEvent(me)
        self.wasCurrent = False
        self.setCursor(Qt.ClosedHandCursor)
        self.scene.controllerMoved()
        self.scene.updateDirectLine()
        

    def mousePressEvent(self, me):
        if me.button() == Qt.RightButton:
            self.scene.removeController(self)
            return
        self.wasCurrent = self.current
        self.scene.setCurrentController(self)
        super().mousePressEvent(me)

    def mouseReleaseEvent(self, me):
        super().mouseReleaseEvent(me)
        self.setCursor(Qt.ArrowCursor)
        if self.new:
            self.wasCurrent = False
            self.new = False
        self.setCurrent(not self.wasCurrent)
        if self.wasCurrent:
            self.scene.setCurrentController(None)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            rect = self.scene.rect.rect()
            if not rect.contains(value):
                value.setX(min(rect.right(), max(value.x(), rect.left())))
                value.setY(min(rect.bottom(), max(value.y(), rect.top())))
        return value


class Polygon(QGraphicsPolygonItem):
    def __init__(self, cts, *args):
        c = cts[0]
        cts.remove(c)
        l = [c.pos()]
        self.ctrl = [(c,c.pos())]
        ct = c.next
        while ct != c:
            cts.remove(ct)
            l.append(ct.pos())
            self.ctrl.append((ct,ct.pos()))
            ct = ct.next
        super().__init__(QPolygonF(l), *args)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.setBrush(QBrush(QColor(0,255,255)))
        self.setZValue(-2)

    def mousePressEvent(self, me):
        if me.buttons() & Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
        self.setZValue(3)
        for c in self.ctrl:
            c[0].setZValue(2.5)
        super().mousePressEvent(me)
        

    def mouseMoveEvent(self, me):
        super().mouseMoveEvent(me)
        p = self.pos()
        for c in self.ctrl:
            c[0].setPos(c[1]+p, True)

    def mouseReleaseEvent(self, me):
        self.setCursor(Qt.ArrowCursor)
        self.setZValue(-2)
        for c in self.ctrl:
            c[0].setZValue(c[0].current)
        super().mouseReleaseEvent(me)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            rect = self.scene().rect.rect()
            dpx = 0
            dpy = 0
            dmx = 0
            dmy = 0
            for c in self.ctrl:
                dpx = max(dpx, rect.left()-c[1].x()-value.x())
                dpy = max(dpy, rect.top()-c[1].y()-value.y())
                dmx = min(dmx, rect.right()-c[1].x()-value.x())
                dmy = min(dmy, rect.bottom()-c[1].y()-value.y())
            value.setX(value.x() + dpx + dmx)
            value.setY(value.y() + dpy + dmy)
        return value


class PolygonPos(QGraphicsPolygonItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)

    def mousePressEvent(self, me):
        if me.buttons() & Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(me)
        

    def mouseMoveEvent(self, me):
        super().mouseMoveEvent(me)

    def mouseReleaseEvent(self, me):
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(me)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            rect = QRect(0,0,100,100)
            dpx = 0
            dpy = 0
            dmx = 0
            dmy = 0
            for c in self.polygon():
                dpx = max(dpx, rect.left()-c[1].x()-value.x())
                dpy = max(dpy, rect.top()-c[1].y()-value.y())
                dmx = min(dmx, rect.right()-c[1].x()-value.x())
                dmy = min(dmy, rect.bottom()-c[1].y()-value.y())
            value.setX(value.x() + dpx + dmx)
            value.setY(value.y() + dpy + dmy)
        return value


class PolyScene(QGraphicsScene):
    polyChanged = pyqtSignal()
    def __init__(self, *args):
        super().__init__(*args)
        self.scale = 1
        self.controllers = []
        self.currentController = None
        self.polygons = []
        self.directLine = None
        self.setSceneRect(QRectF(0,0,100,100))
        self.rect = self.addRect(QRectF(0,0,100,100), QPen(QColor(0,0,0)), QBrush(QColor(255,255,255)))
        self.rect.setZValue(-10)
        

    def updateDirectLine(self):
        if self.directLine:
            self.removeItem(self.directLine)
        if self.currentController:
            self.directLine = QGraphicsLineItem(QLineF(self.currentController.pos(),
                                                       self.currentController.next.pos()))
            self.directLine.setPen(QPen(QColor(0,0,255)))
            self.directLine.setZValue(-.5)
            self.addItem(self.directLine)

    def mousePressEvent(self, me):
        #print(self.itemAt(me.scenePos(), self.view.transform()))
        #print(self.rect)
        if not self.itemAt(me.scenePos(), self.view.transform()) in [None, self.rect]:
            super().mousePressEvent(me)
            return
        print("ajout")
        self.addController(me.scenePos())
        super().mousePressEvent(me)

    def addController(self, pos):
        ctrl = Controller(self,self.currentController, QRectF(-QPointF(EL_SIZE//2,EL_SIZE//2),QSizeF(EL_SIZE,EL_SIZE)))
        self.controllers.append(ctrl)
        self.addItem(self.controllers[-1])
        ctrl.setPos(pos)
        self.polyChanged.emit()

    def removeController(self, ctrl):
        self.setCurrentController(None)
        ctrl.previous.next = ctrl.next
        ctrl.next.previous = ctrl.previous
        self.controllers.remove(ctrl)
        self.removeItem(ctrl)
        self.controllerMoved()
        self.polyChanged.emit()

    def setCurrentController(self, ctrl):
        if self.currentController:
            self.currentController.setCurrent(False)
        self.currentController = ctrl
        if self.currentController:
            self.currentController.setCurrent(True)
        self.updateDirectLine()

    def controllerMoved(self):
        self.polyChanged.emit()
        for p in self.polygons:
            self.removeItem(p)
        self.polygons = []
        cts = list(self.controllers)
        while len(cts):
            self.polygons.append(Polygon(cts))
            self.addItem(self.polygons[-1])
            
    def keyPressEvent(self, ke):
        if ke.key() == Qt.Key_Escape:
            self.setCurrentController(None)


    def environment(self, LEN):
        return [[(int(LEN*p.x()/100), int(LEN*p.y()/100)) for p in i.polygon()] for i in self.polygons]

    def clear(self):
        for i in self.polygons:
            self.removeItem(i)
        self.polygons = []
        for i in self.controllers:
            self.removeItem(i)
        self.removeItem(self.directLine)
        self.directLine = None
        self.currentController = None
        self.controllers = []

class EnvironmentScene(PolyScene):
    def __init__(self,*args):
        super().__init__(*args)
        self.initialPos = None
        self.finalPos = None

    @pyqtSlot(list)
    def setObject(self, polygon):
        if self.initialPos:
            self.removeItem(self.initialPos)
            self.removeItem(self.finalPos)
        if len(polygon) < 3:
            self.initialPos = None
            self.finalPos = None
        else:
            print(polygon)
            self.initialPos = PolygonPos(QPolygonF([QPointF(p[0]*20/LEN+10,p[1]*20/LEN+10) for p in polygon]))
            self.initialPos.setPen(QPen(Qt.NoPen))
            self.initialPos.setBrush(QBrush(QColor(255,100,100)))
            self.initialPos.setZValue(60)
            self.initialPos.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.addItem(self.initialPos)
            self.finalPos = PolygonPos(QPolygonF([QPointF(p[0]*20/LEN+90,p[1]*20/LEN+90) for p in polygon]))
            self.finalPos.setPen(QPen(Qt.NoPen))
            self.finalPos.setBrush(QBrush(QColor(100,255,100)))
            self.finalPos.setZValue(60)
            self.addItem(self.finalPos)
            
class ObjectScene(PolyScene):
    def __init__(self,*args):
        super().__init__(*args)

    def environment(self, l):
        l = super().environment(l)
        return l[0] if len(l) else []

        
class Main(*loadUiType("planification.ui")):
    def __init__(self, *args):
        super().__init__(*args)
        self.setupUi(self)
        self.splitter_2.setSizes([300,150,150])
        self.toolBar.addAction(self.actionNouveau)
        self.toolBar.addAction(self.actionOuvrir)
        self.toolBar.addAction(self.actionEnregistrer)
        self.toolBar.addAction(self.actionEnregistrerSous)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionAnnuler)
        self.toolBar.addAction(self.actionRetablir)
        self.splitter.setSizes([170,25])
        l = QHBoxLayout()
        l.setContentsMargins(0,1,0,0)
        ##l.addWidget(QLabel("Bonjour"))
        la = QLabel()
        ##la.setAutoFillBackground(True)
        la.setFrameShape(QFrame.HLine)
        la.setFrameShadow(QFrame.Plain)
        l.addWidget(la)
        #p = QLabel("Environnement",self.splitter_2)
        #f = p.font()
        #f.setBold(True)
        #f.setItalic(True)
        #p.setFont(f)
        #p.move(0,50)
        #self.splitter_2.splitterMoved.connect(lambda e,i : p.move(0,e-p.height()//2))
        #self.splitter_2.handle(1).setLayout(l)
        #print(self.splitter_2.handle(1).paintEvent)
        self.vue = []
        
        self.currentItem = None

        self.drawEnvi = Step("Décomposition en\npolygones convexes")
        def val(*conf) :
            if sum(map(len,conf[0]))%2:
                return True
            self.error(self.drawEnvi, "Nombre de sommets pair")
            return False
        self.drawEnvi.isValidConfig = val#lambda *conf : sum(map(len,conf[0]))%2
        a = Step(parent = self.drawEnvi)
        Step(parent = a)
        a = Step(parent = Step(parent = a))
        Step(parent = a)
        Step(parent = a)
        #Step(a)
        a=(Step(parent = self.drawEnvi))
        sp = StepPainter(self.drawEnvi)
        sp.pipeLineChanged.connect(self.updatePipeLine)
        self.steps.addWidget(sp)

        self.envi.setRenderHint(QPainter.Antialiasing)
        
        self.environment = EnvironmentScene(self)
        self.environment.view = self.envi

        self.object = ObjectScene(self)
        self.obj.setScene(self.object)
        self.object.view = self.obj
        #self.environment.addItem(it)


        self.envi.setScene(self.environment)
        def wheelEvent(view):
            def wheelEvent(we):
                if we.modifiers() & Qt.ControlModifier:
                    a = .9 if we.delta() < 0 else 1.1
                    view.scale(a,a)
                    we.accept()
                else:
                    #print(we.delta())
                    #b = -5 if we.delta() < 0 else 5
                    b = -we.delta()/4
                    if we.modifiers() & Qt.ShiftModifier:
                        view.horizontalScrollBar().setValue(
                            view.horizontalScrollBar().value() + b)
                    else:
                        view.verticalScrollBar().setValue(
                            view.verticalScrollBar().value() + b)
            view.wheelEvent = wheelEvent
        wheelEvent(self.envi)
        wheelEvent(self.obj)

        QTimer.singleShot(20, lambda : self.envi.scale(min(self.envi.width()/120, self.envi.height()/120),
                                                       min(self.envi.width()/120, self.envi.height()/120)))
        QTimer.singleShot(20, lambda : self.obj.scale(min(self.obj.width()/120, self.obj.height()/120),
                                                       min(self.obj.width()/120, self.obj.height()/120)))

        self.environment.polyChanged.connect(self.on_actionSimplifier_triggered)
        #self.environment.polyChanged.connect(self.updatePipeLine)
        #self.object.polyChanged.connect(self.updateObject)
        #self.envi.setSceneRect(QRectF(-10,-10,120,120))
        #self.obj.setSceneRect(QRectF(-10,-10,120,120))
       


    @pyqtSlot()
    def on_actionNouveau_triggered(self):
        self.object.clear()

    @pyqtSlot()
    def on_actionClearEnvironment_triggered(self):
        self.environment.clear()
    
    @pyqtSlot()
    def on_actionQuitter_triggered(self):
        self.close()

    @pyqtSlot()
    def on_actionProposQt_triggered(self):
        QMessageBox.aboutQt(self,"À propos de Qt")

    @pyqtSlot()
    def on_actionSimplifier_triggered(self):
        print("Bonjour !")
        e = self.environment.environment(LEN)
        o = self.object.environment(LEN)
        m = (sum(i[0] for i in o)/len(o)-o[0][0],sum(i[1] for i in o)/len(o)-o[0][1])
        for po in e:
            ind, pt = max(enumerate(po), key = lambda i : i[1][0]*LEN+i[1][1])
            if ((po[(ind+1)%len(po)][0]-pt[0])*(po[(ind-1)%len(po)][1]-pt[1])-
                (po[(ind+1)%len(po)][1]-pt[1])*(po[(ind-1)%len(po)][0]-pt[0])) <0:
                po.reverse()
        print("Je m'en vais")
        poly, conv = simplify(e, o)
        print(len(conv))
        m = [0,0]
        for i in self.vue:
            self.environment.removeItem(i)
        self.vue = []
        for i,p in enumerate(conv):
            rvb = [int(o*255) for o in hsv_to_rgb((30*i%360)/360, 1,1)]
            self.vue.append(self.environment.addPolygon(QPolygonF([QPointF((i[0]+m[0])*100/LEN,(i[1]+m[1])*100/LEN) for i in p]),
                               QPen(QColor(0,0,0,0)),
                               QBrush(QColor(rvb[0], rvb[1], rvb[2]))))
        print("Au revoir")
        #for p in poly:
        #    self.environment.addItem(QGraphicsPolygonItem(QPolygonF([QPointF((i[0]+m[0])*100/LEN,(i[1]+m[1])*100/LEN) for i in p])))

    def setModel(self, model):
        pass


    @pyqtSlot()
    def updateObject(self):
        self.environment.setObject(self.object.environment(LEN))

    
    @pyqtSlot()
    def updatePipeLine(self):
        self.drawEnvi.update(self.environment.environment(LEN))

    @pyqtSlot()
    def on_actionClearConsole_triggered(self):
        self.textEdit.clear()
        
    def error(self, obj, arg):
        self.textEdit.append("<font color=\"Blue\">"+QTime.currentTime().toString() +
                             "</font> <b><font color=\"Red\">Erreur</font></b> " +
                             obj.name.replace('\n', ' '))
        self.textEdit.append("    "+arg)

app = QApplication(sys.argv)
fen = Main()
fen.show()
app.exec()

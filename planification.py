from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.uic import loadUiType
import sys

EL_SIZE = 15

class Step:
    def __init__(self, parent = None):
        self.nextSteps = []
        self.parent = parent
        if parent:
            parent.nextSteps.append(self)
        self.name = "Étape i"
        self.image = "tracer.png"

    def changeState(self, a):
        if a and self.parent:
            for step in self.parent.nextSteps:
                if(step==self):
                    step.setActive(True)
                else:
                    step.button.setChecked(False)
        else:
            self.setActive(a)
        self.button.parent().update()
        
    def setActive(self, a):
        if a:
            for step in self.nextSteps:
                step.button.setEnabled(True)
        else:
            for step in self.nextSteps:
                step.setActive(a)
                step.button.setEnabled(False)
                step.button.setChecked(False)

class StepPainter(QWidget):
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
                but.toggled.connect(step.changeState)
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
            rect = self.scene.sceneRect()
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
            rect = self.scene().sceneRect()
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

class PolyScene(QGraphicsScene):
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
        print(self.itemAt(me.scenePos(), self.view.transform()))
        print(self.rect)
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

    def removeController(self, ctrl):
        self.setCurrentController(None)
        ctrl.previous.next = ctrl.next
        ctrl.next.previous = ctrl.previous
        self.controllers.remove(ctrl)
        self.removeItem(ctrl)
        self.controllerMoved()

    def setCurrentController(self, ctrl):
        if self.currentController:
            self.currentController.setCurrent(False)
        self.currentController = ctrl
        if self.currentController:
            self.currentController.setCurrent(True)
        self.updateDirectLine()

    def controllerMoved(self):
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

        
class Model:
    def __init__(self):
        self.object = []
        self.envi = []#(10,10),(90,10),(90,90),(10,90)]#[(0,0), (0,1000),(1000,1000),(1000,0)]



class Main(*loadUiType("planification.ui")):
    def __init__(self, *args):
        super().__init__(*args)
        self.setupUi(self)
        self.splitter_2.setSizes([300,150,150])
        
        self.currentItem = None
        self.model = Model()
        self.drawEnvi = Step()
        a = Step(self.drawEnvi)
        Step(a)
        a = Step(Step(a))
        Step(a)
        Step(a)
        Step(a)
        a=Step(Step(self.drawEnvi))
        self.steps.setWidget(StepPainter(self.drawEnvi))

        self.envi.setSceneRect(QRectF(0,0,100,100))
        self.envi.setRenderHint(QPainter.Antialiasing)
        it = QGraphicsPolygonItem()
        it.setPolygon(QPolygonF([QPoint(*p) for p in self.model.envi]))
        self.sc = PolyScene(self)
        self.sc.view = self.envi
        #self.sc.addItem(it)

        # BUG de Qt (Il faudrait utiliser 5...)
        self.actionProposQt.triggered.connect(self.on_actionProposDeQt_triggered, Qt.UniqueConnection)

        self.envi.setScene(self.sc)
        def wheelEvent(we):
            if we.modifiers() & Qt.ControlModifier:
                a = .9 if we.delta() < 0 else 1.1
                self.envi.scale(a,a)
                we.accept()
            else:
                #print(we.delta())
                #b = -5 if we.delta() < 0 else 5
                b = -we.delta()/4
                if we.modifiers() & Qt.ShiftModifier:
                    self.envi.horizontalScrollBar().setValue(
                        self.envi.horizontalScrollBar().value() + b)
                else:
                    self.envi.verticalScrollBar().setValue(
                        self.envi.verticalScrollBar().value() + b)

        self.envi.wheelEvent = wheelEvent



    def on_actionNouveau_triggered(self):
        pass
    
    def on_actionQuitter_triggered(self):
        self.close()

    def on_actionProposDeQt_triggered(self):
        QMessageBox.aboutQt(self,"À propos de Qt")
        

    def setModel(self, model):
        pass

app = QApplication(sys.argv)
fen = Main()
fen.show()
app.exec()

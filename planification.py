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
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIgnoresTransformations)
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

        
    def setPos(self, p):
        super().setPos(p)
        self.scene.controllerMoved()

    def mouseMoveEvent(self, me):
        super().mouseMoveEvent(me)
        self.scene.controllerMoved()

    def mousePressEvent(self, me):
        if me.button() == Qt.RightButton:
            self.scene.removeController(self)
            return
        self.scene.setCurrentController(self)
        print("press")
        super().mousePressEvent(me)

    def mouseReleaseEvent(self, me):
        print("release")
        super().mouseReleaseEvent(me)


class PolyScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 1
        self.controllers = []
        self.currentController = None
        self.polygon = None

    def mousePressEvent(self, me):
        if self.itemAt(me.scenePos()) != None:
            print("oups")
            super().mousePressEvent(me)
            return
        self.addController(me.scenePos())
        super().mousePressEvent(me)

    def addController(self, pos):
        ctrl = Controller(self,self.currentController, QRectF(-QPointF(EL_SIZE//2,EL_SIZE//2),QSizeF(EL_SIZE,EL_SIZE)))
        ctrl.setPos(pos)
        self.controllers.append(ctrl)
        self.addItem(self.controllers[-1])

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

    def controllerMoved(self):
        self.removeItem(self.polygon)
        if len(self.controllers):
            c = self.controllers[0]
            l = [c.pos()]
            ct = c.next
            while ct != c:
                l.append(ct.pos())
                ct = ct.next
            #print(l)
            self.polygon = QGraphicsPolygonItem(QPolygonF(l))
            self.polygon.setBrush(QBrush(QColor(0,255,255)))
            self.polygon.setZValue(-2)
            self.addItem(self.polygon)


        
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
        it = QGraphicsPolygonItem()
        it.setPolygon(QPolygonF([QPoint(*p) for p in self.model.envi]))
        self.sc = PolyScene(self)
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
                b = -5 if we.delta() < 0 else 5
                b = we.delta()/4
                if we.modifiers() & Qt.ShiftModifier:
                    self.envi.horizontalScrollBar().setValue(
                        self.envi.horizontalScrollBar().value() + b)
                else:
                    self.envi.verticalScrollBar().setValue(
                        self.envi.verticalScrollBar().value() + b)


        def mousePressEvent(me):
            if self.sc.itemAt(me.scenePos()) != None:
                QGraphicsScene.mousePressEvent(self.sc, me)
                return
            el = Controller(QRectF(me.scenePos()-QPointF(7,7),QSizeF(15,15)))

            def mousePressEvent(me):
                if me.button() == Qt.RightButton:
                    el.previous.next = el.next
                    el.next.previous = el.previous
                    self.sc.removeItem(el)
                    self.currentItem = None
                    return
                if self.currentItem == el:
                    self.currentItem.setCurrent(False)
                    self.currentItem = None
                else:
                    if self.currentItem:
                        self.currentItem.setCurrent(False)
                    self.currentItem = el
                    el.setCurrent()
            el.mousePressEvent = mousePressEvent
            print("hum")
            el.setPrevious(self.currentItem)
            self.sc.addItem(el)
            self.sc.mousePressEvent(me)
        #self.sc.mousePressEvent = mousePressEvent
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

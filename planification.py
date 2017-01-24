from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.uic import loadUiType
from sys import argv
from colorsys import hsv_to_rgb

from random import randint
from simplify import simplify
from steps import *

EL_SIZE = 15

def ptsToPoly(p,LEN):
    return QPolygonF([QPointF(i[0]*100/LEN, i[1]*100/LEN) for i in p])

def polyToPts(p,LEN):
    return [(int(i.x()*LEN/100+.5),int(i.y()*LEN/100+.5)) for i in p]

class Step(QObject):
    stateChanged = pyqtSignal()
    def __init__(self, output, parent = [],
                 validation = standardValidation,
                 transformation = standardTransformation,
                 name = "Étape", image = "tracer.png"):
        super().__init__()
        self.added = False
        self.output = output
        self.validation = validation
        self.transformation = transformation
        self.nextSteps = []
        self.parent = list(filter(lambda e:e, parent if type(parent)==list else [parent]))
        for p in self.parent:
            p.nextSteps.append(self)
        self.name = name
        self.image = image
        self.nextStep = None
        self.isActive = True


    def setEnabled(self, e):
        if self.parent:
            if not e:
                for i in self.nextSteps:
                    i.setEnabled(e)
            elif self.button.isChecked():
                for step in self.nextSteps:
                    step.setEnabled(True)
            self.button.setEnabled(e)
            self.action.setEnabled(e)
        
        
    @pyqtSlot(bool)
    def setActive(self, a):
        self.isActive = a
        if self.parent:
            self.button.setChecked(a)
            self.action.setChecked(a)
        if a:
            for p in self.parent:
                for i in filter(lambda a : a!=self, p.nextSteps):
                    i.setActive(False)
            for step in self.nextSteps:
                step.setEnabled(True)
        else:
            for step in self.nextSteps:
                step.setActive(a)
                step.setEnabled(False)
        for p in self.parent:
            p.nextStep = self if a else None
        self.stateChanged.emit()
            


    def update(self, *conf):
        m = self.validation(*conf)
        if not len(m):
            self.setEnabled(True)
            if self.parent and not self.button.isChecked():
                return []
            #try:
            conf,items = self.transformation(*conf)
            #except:
            #    self.output.error(self, "Erreur inconnue")
            #    return []
            for c in self.nextSteps:
                if c != self.nextStep:
                    c.update(*conf)
            return items + (self.nextStep.update(*conf) if self.nextStep else [])
        self.output.error(self, m)
        self.setEnabled(False)
        return []


class StepPainter(QWidget):
    pipeLineChanged = pyqtSignal()
    def __init__(self, initStep, win, *args):
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
                act = QAction(self)
                act.setText(step.name.replace("\n"," "))
                act.setCheckable(True)
                act.toggled.connect(step.setActive)
                step.action = act
                win.menuPlanification.addAction(act)
                but.setText(step.name)
                but.setIcon(QIcon(step.image))
                but.setIconSize(QSize(128,64))
                but.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                but.setCheckable(True)
                step.button = but
                step.added = True
                step.stateChanged.connect(self.update)
                step.stateChanged.connect(lambda : self.pipeLineChanged.emit())
                but.toggled.connect(step.setActive)
                for s in step.nextSteps:
                    for p in s.parent:
                        if not p.added:
                            break
                    else:
                        nextSteps.append(s)
            if nextSteps:
                addSteps(nextSteps)
        initStep.added = True
        addSteps(initStep.nextSteps)
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
                p.setColor(palette.color(QPalette.Text) if step.isActive and nextStep.isActive else
                           palette.color(QPalette.Mid))
                pa.setPen(p)
                pa.drawLine(step.button.pos() + QPoint(step.button.width()//2,step.button.height()//2),
                            nextStep.button.pos() + QPoint(step.button.width()//2,step.button.height()//2))
                drawRelation(nextStep)
        pa.begin(self)
        for i in self.initStep.nextSteps:
            drawRelation(i)
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
        self.setZValue(b+.1)
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
        self.move = me.buttons() & Qt.RightButton
        if me.buttons() & Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
        self.setZValue(3)
        for c in self.ctrl:
            c[0].setZValue(2.5)
        super().mousePressEvent(me)
        

    def mouseMoveEvent(self, me):
        self.move = False
        super().mouseMoveEvent(me)
        p = self.pos()
        for c in self.ctrl:
            c[0].setPos(c[1]+p, True)
        self.scene().polyMoved()

    def mouseReleaseEvent(self, me):
        self.setCursor(Qt.ArrowCursor)
        self.setZValue(-2)
        if self.move:
            s = self.scene()
            for i in self.ctrl:
                s.removeController(i[0])
            super().mouseReleaseEvent(me)
            return
        for c in self.ctrl:
            c[0].setZValue(c[0].current+.1)
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
        c = QGraphicsEllipseItem(-2,-2,4,4,self)
        c.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        c.setBrush(QColor(0,0,0))

    def mousePressEvent(self, me):
        if me.buttons() & Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
        self.setZValue(61)
        super().mousePressEvent(me)
        

    def mouseMoveEvent(self, me):
        super().mouseMoveEvent(me)
        self.scene().polyMoved()

    def mouseReleaseEvent(self, me):
        self.setCursor(Qt.ArrowCursor)
        self.setZValue(60)
        super().mouseReleaseEvent(me)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            rect = QRect(0,0,101,101)
            dpx = 0
            dpy = 0
            dmx = 0
            dmy = 0
            for c in self.polygon():
                dpx = max(dpx, rect.left()-c.x()-value.x())
                dpy = max(dpy, rect.top()-c.y()-value.y())
                dmx = min(dmx, rect.right()-c.x()-value.x())
                dmy = min(dmy, rect.bottom()-c.y()-value.y())
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
            self.directLine.setZValue(+.5)
            self.addItem(self.directLine)

    def mousePressEvent(self, me):
        #print(self.itemAt(me.scenePos(), self.view.transform()))
        #print(self.rect)
        i = self.items(me.scenePos(), Qt.IntersectsItemShape, Qt.AscendingOrder, self.view.transform())
        for it in i:
            if it.flags() & QGraphicsItem.ItemIsMovable:
                super().mousePressEvent(me)
                return
        self.addController(me.scenePos())
        super().mousePressEvent(me)
        return
        #if i != None and i.flags() & QGraphicsItem.ItemIsMovable:
        super().mousePressEvent(me)
        #    return
        if not me.isAccepted():
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
        self.updateDirectLine()

    def setCurrentController(self, ctrl):
        if self.currentController:
            self.currentController.setCurrent(False)
        self.currentController = ctrl
        if self.currentController:
            self.currentController.setCurrent(True)
        self.updateDirectLine()

    def polyMoved(self):
        self.polyChanged.emit()

    def controllerMoved(self):
        for p in self.polygons:
            self.removeItem(p)
        self.polygons = []
        cts = list(self.controllers)
        while len(cts):
            self.polygons.append(Polygon(cts))
            self.addItem(self.polygons[-1])
        self.polyChanged.emit()
            
    def keyPressEvent(self, ke):
        if ke.key() == Qt.Key_Escape:
            self.setCurrentController(None)


    def environment(self, LEN):
        polygons = [[(int(LEN*p[0].x()/100), int(LEN*p[0].y()/100)) for p in i.ctrl] for i in self.polygons]
        for po in polygons:
            if not isDirect(po):
                po.reverse()
        return polygons

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
        self.polyChanged.emit()

class EnvironmentScene(PolyScene):
    def __init__(self,*args):
        super().__init__(*args)
        self.initialPos = None
        self.finalPos = None

    def controlPosition(self):
        if self.initialPos == None:
            return (None,None)
        return tuple(polyToPts([self.initialPos,self.finalPos],LEN))

    @pyqtSlot(list)
    def setObject(self, polygon):
        pi = QPointF(20,20)
        pf = QPointF(80,80)
        if self.initialPos:
            pi = self.initialPos.pos()
            self.removeItem(self.initialPos)
            pf = self.finalPos.pos()
            self.removeItem(self.finalPos)
        if len(polygon) < 3:
            self.initialPos = None
            self.finalPos = None
        else:
##            x = y = 0
##            for i in polygon:
##                x += i[0]
##                y += i[1]
##            x /= len(polygon)
##            y /= len(polygon)
            #self.initialPos = PolygonPos(QPolygonF([QPointF((p[0]-x)*20/LEN,(p[1]-y)*20/LEN) for p in polygon]))
            self.initialPos = PolygonPos(ptsToPoly(polygon,LEN))
            self.initialPos.setPen(QPen())
            self.initialPos.setBrush(QBrush(QColor(255,150,150)))
            self.initialPos.setZValue(60)
            self.initialPos.setPos(QPointF(pi))
            self.addItem(self.initialPos)
            #self.finalPos = PolygonPos(QPolygonF([QPointF((p[0]-x)*20/LEN,(p[1]-y)*20/LEN) for p in polygon]))
            self.finalPos = PolygonPos(ptsToPoly(polygon,LEN))
            self.finalPos.setPen(QPen())
            self.finalPos.setBrush(QBrush(QColor(150,255,150)))
            self.finalPos.setZValue(60)
            self.finalPos.setPos(QPointF(pf))
            self.addItem(self.finalPos)
            
class ObjectScene(PolyScene):
    def __init__(self,*args):
        super().__init__(*args)

    def environment(self, l):
        l = super().environment(l)
        if not len(l):
            return []
        l = l[0]
        x,y = (0,0)
        for i in l:
            x+=i[0]
            y+=i[1]
        x/=len(l)
        y/=len(l)
        return [(int((i[0]-x)/5+.5), int((i[1]-y)/5+.5)) for i in l]

    def environmentSave(self,l):
        l = PolyScene.environment(self, l)
        if len(l): return l[0]
        return []

    def removeController(self, ctrl):
        ctrl.previous.next = ctrl.next
        ctrl.next.previous = ctrl.previous
        self.controllers.remove(ctrl)
        self.removeItem(ctrl)
        self.controllerMoved()
        self.setCurrentController(None if ctrl.previous == ctrl else ctrl.previous)
        self.polyChanged.emit()
        self.updateDirectLine()

    def setCurrentController(self, ctrl):
        if self.currentController:
            self.currentController.setCurrent(False)
        if ctrl == None:
            if self.currentController in self.controllers:
                ctrl = self.currentController
            elif len(self.controllers):
                ctrl = self.controllers[0]
        self.currentController = ctrl
        if self.currentController:
            self.currentController.setCurrent(True)
        self.updateDirectLine()
# Problèmes:
# visi qui n'a que faire des limites
# obstacles toriques...
        
class Main(*loadUiType("planification.ui")):
    def __init__(self, *args):
        super().__init__(*args)
        self.setupUi(self)
        self.setWindowIcon(QIcon("images/tracer.png"))
        self.enr = ""
        self.splitter_2.setSizes([300,150,150])
        self.toolBar.addAction(self.actionNouveau)
        self.toolBar.addAction(self.actionOuvrir)
        self.toolBar.addAction(self.actionEnregistrer)
        self.toolBar.addAction(self.actionEnregistrerSous)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionClearEnvironment)
        self.toolBar.addAction(self.actionClearObject)
        self.splitter.setSizes([170,25])
        self.statusbar.addPermanentWidget(QLabel("<i>Ctrl+roulette : changer le zoom"))
        self.statusbar.addPermanentWidget(QLabel("<i>Clic gauche : ajouter des éléments"))
        self.statusbar.addPermanentWidget(QLabel("<i>Clic droit : supprimer des éléments"))

        self.vue = []
        
        self.currentItem = None
        self.hiddenStep = Step(self)

        self.convDecomp = Step(self, self.hiddenStep, convexDecompositionValidation2,
                               convexDecompositionTransformation2,
                               "Décomposition en\npolygones convexes\n(optimale)", image="images/convexes.png")
        self.convDecomp2 = Step(self, self.hiddenStep, convexDecompositionValidation,
                               convexDecompositionTransformation,
                               "Décomposition en\npolygones convexes\n(non optimale)", image="images/convexes.png")
        a = Step(self, [self.convDecomp,self.convDecomp2], minkovskySumValidation,
                 minkovskySumTransformation,
                 "Somme de\nMinkowski", image="images/minkow.png")
        a = Step(self, a, unificationValidation,
                 unificationTransformation,
                 "Unification", image="images/unif.png")
        c = Step(self, a, visibilityGraphValidation,
             visibilityGraphTransformation,
             "Graphe de\nvisibitlité", image="images/visi.png")
        d = Step(self, c, graphSimplificationValidation,
             graphSimplificationTransformation,
             "Retrait arêtes\nentrantes", image="images/gsim.png")
        #Step(a)
        b = Step(self, a,
                cellDecompositionValidation,
                cellDecompositionTransformation,
                "Décomposition en\ntrapèzes", image="images/trap.png")
        
        Step(self, [b,d],
             dijkstraValidation,
             dijkstraTransformation,
             "Plus court\nchemin", image="images/dijk.png")

        #Step(self, parent = a)
        #a=(Step(self, self.hiddenStep,
        #        cellDecompositionValidation,
        #        cellDecompositionTransformation,
        #        "Décomposition en\ntrapèzes"))
        sp = StepPainter(self.hiddenStep, self)
        sp.pipeLineChanged.connect(self.updatePipeLine)
        self.steps.addWidget(sp)

        self.envi.setRenderHint(QPainter.Antialiasing)
        
        self.environment = EnvironmentScene(self)
        self.environment.view = self.envi

        self.object = ObjectScene(self)
        self.obj.setScene(self.object)
        self.object.view = self.obj
        
        self.envi.setScene(self.environment)
        def wheelEvent(view):
            def wheelEvent(we):
                if we.modifiers() & Qt.ControlModifier:
                    a = .9 if we.delta() < 0 else 1.1
                    view.scale(a,a)
                    we.accept()
                else:
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

        self.environment.polyChanged.connect(self.updatePipeLine)
        self.object.polyChanged.connect(self.updateObject)
        self.updatePipeLine()
       

    @pyqtSlot()
    def on_actionNouveau_triggered(self):
        self.enr = ""
        self.on_actionClearObject_triggered()
        self.on_actionClearEnvironment_triggered()

    @pyqtSlot()
    def on_actionClearObject_triggered(self):
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
    def on_actionPropos_triggered(self):
        QMessageBox.about(self,"À propos","""
<b>Planification du mouvement</b><br><br>
Logiciel de visualisation d'aglorithmes<br> de planification
du mouvement.
<br><br>
Joseph Moullart De Vilmarest,<br>
Marc Coudriau, Baptiste Pauget<br><br>
Janvier 2017
""")
        
    @pyqtSlot()
    def updateObject(self):
        self.environment.setObject(self.object.environment(LEN))
        self.updatePipeLine()

    
    @pyqtSlot()
    def updatePipeLine(self):
        self.messages.setText("")
        for i in self.vue:
            self.environment.removeItem(i)
        self.vue = []
        for i in self.hiddenStep.update(self.environment.environment(LEN),
                                        self.object.environment(LEN),*self.environment.controlPosition()):
            self.vue.append(self.environment.addPolygon(ptsToPoly(i[0],LEN),
                                                        QPen(QColor(*i[1])),
                                                        QBrush(QColor(*i[2]))))


        
    def error(self, obj, arg):
        self.messages.setText("<b><font color=\"Red\">Erreur</font></b> : <font color=\"Blue\">" +
                             obj.name.replace('\n', ' ')+"</font><br> &#160;&#160;&#160;&#160;"+arg)

    @pyqtSlot()
    def on_actionOuvrir_triggered(self):
        a = QFileDialog.getOpenFileName(self, "Ouvrir", self.enr, "Fichier de plannification (*.pln)")
        if len(a):
            try:
                f = open(a)
                l = eval(f.readline()[:-1])
                e = eval(f.readline()[:-1])
                o = eval(f.readline()[:-1])
                pb = eval(f.readline()[:-1])
            except:
                self.messages.setText("<b><font color=\"Red\">Erreur</font></b> : <font color=\"Blue\">" +
                                      a+"</font><br> &#160;&#160;&#160;&#160;Fichier incorrect")
                return

            self.on_actionNouveau_triggered()
            self.enr = a
            e = [ptsToPoly(p,l) for p in e]
            o = ptsToPoly(o,l)
            for p in o:
                self.object.addController(p)
            for p in e:
                for p in p:
                    self.environment.addController(p)
                self.environment.setCurrentController(None)
            self.environment.initialPos.setPos(QPointF(pb[0][0]*100/l,pb[0][1]*100/l))
            self.environment.finalPos.setPos(QPointF(pb[1][0]*100/l,pb[1][1]*100/l))

    @pyqtSlot()
    def on_actionEnregistrer_triggered(self):
        self.save()

    @pyqtSlot()
    def on_actionEnregistrerSous_triggered(self):
        self.getName()
        if len(self.enr):
            self.save()
            
    def getName(self):
        a = QFileDialog.getSaveFileName(self, "Enregistrer sous", self.enr, "Fichier de plannification (*.pln)")
        if len(a):
            self.enr = a
        

    def save(self):
        if not len(self.enr):
            self.getName()
        if len(self.enr):
            f = open(self.enr, mode='w')
            f.write(str(LEN)+"\n")
            f.write(str(self.environment.environment(LEN))+ "\n" +
                    str(self.object.environmentSave(LEN))+ "\n")
            f.write(str(self.environment.controlPosition())+"\n")
            f.close()
def convex(p):
    l = [p]
    return [QGraphicsPolygonItem(QPolygonF([QPointF(*i) for i in p])) for p in l],l

app = QApplication(argv)
fen = Main()
fen.show()
app.exec()

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.uic import loadUiType
import sys


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
        self.lay.addItem(QSpacerItem(0,500))
        initStep.setActive(False)

    def paintEvent(self, pe):
        pa = QPainter(self)
        palette = self.palette()
        p = QPen(palette.color(QPalette.Button))
        p.setWidth(3)
        def drawRelation(step):
            for nextStep in step.nextSteps:
                p.setColor(palette.color(QPalette.Text) if nextStep.button.isChecked() else
                           palette.color(QPalette.AlternateBase))
                pa.setPen(p)
                pa.drawLine(step.button.pos() + QPoint(step.button.width()//2,step.button.height()//2),
                            nextStep.button.pos() + QPoint(step.button.width()//2,step.button.height()//2))
                drawRelation(nextStep)
        pa.begin(self)
        drawRelation(self.initStep)
        pa.end()
        super().paintEvent(pe)
                                                

class Model:
    def __init__(self):
        self.object = []
        self.envi = [(0,10),(10,10),(10,0)]



class Main(*loadUiType("plannification.ui")):
    def __init__(self, *args):
        super().__init__(*args)
        self.setupUi(self)
        self.splitter_2.setSizes([300,150,150])
        

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
        
        it = QGraphicsPolygonItem()
        it.setPolygon(QPolygonF([QPoint(*p) for p in self.model.envi]))
        sc = QGraphicsScene(self)
        sc.addItem(it)

        self.envi.setScene(sc)
        def wheelEvent(we):
            if we.modifiers() & Qt.ControlModifier:
                a = .9 if we.delta() < 0 else 1.1
                self.envi.scale(a,a)
                we.accept()
            else:
                QGraphicsView.wheelEvent(self.envi, we)
        self.envi.wheelEvent = wheelEvent



    def on_actionNouveau_triggered(self):
        pass
    
    def on_actionQuitter_triggered(self):
        self.close()
        

    def setModel(self, model):
        pass

app = QApplication(sys.argv)
fen = Main()
fen.show()
app.exec()

from PyQt5.QtCore import QByteArray, QRectF, Qt
from PyQt5.QtGui import QFont, QPainter,QWheelEvent
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox,QWidget,QVBoxLayout,QGraphicsScene,QGraphicsView
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QGraphicsScene,QGraphicsView
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer
import sys
sys.path.append('src')

from calcterm.core.latex import *
from calcterm.widgets.common import *
import calcterm.core.exception_parser as err

class LatexDisplay(QWidget):
    class _GraphicsView(QGraphicsView):
        def __init__(self,parent):
            super().__init__(parent)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        def wheelEvent(self, event:QWheelEvent):
            if event.modifiers() & Qt.ControlModifier:
                factor=1.25 if event.angleDelta().y()>0 else 0.8
                self.scale(factor, factor)
                event.accept()

            elif event.modifiers() & Qt.ShiftModifier:
                horizontal_wheel_event = QWheelEvent(
                    event.pos(),
                    event.globalPos(),
                    event.pixelDelta(),
                    event.angleDelta(),
                    event.angleDelta().x() if event.angleDelta().x() != 0 else event.angleDelta().y(),  # qt4Delta
                    Qt.Horizontal,
                    event.buttons(),
                    Qt.KeyboardModifiers(),
                    event.phase(),
                    event.inverted(),
                    event.source()
                )
                QApplication.sendEvent(self.horizontalScrollBar(),horizontal_wheel_event)
            else:
                return super().wheelEvent(event)
    def __init__(self,tex:str,font_size=12,*args,**kw):
        super().__init__(*args,**kw)
        self.tex=tex
        self.font_size=font_size

        self.scene=QGraphicsScene()
        self.renderer=QSvgRenderer()
        self.svg_item=QGraphicsSvgItem()
        self.svg_item.setSharedRenderer(self.renderer)
        self.scene.addItem(self.svg_item)
        self.view=self._GraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)

        layout=QVBoxLayout()
        layout.addWidget(self.view)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        self.setLatex(tex,font_size)
        self.setFocus()
    
    def setLatex(self,tex:str,font_size=None):
        if font_size is not None:self.font_size=font_size
        self.tex=tex
        try:
            svg_data=latex2svg(tex,self.font_size)
        except Exception as e:
            QMessageBox.warning(self,'错误',str(e))
        svg_bytes=QByteArray(svg_data.encode('utf-8'))
        self.renderer.load(svg_bytes)
        
        if self.renderer.isValid():
            self.svg_item.setElementId('')
            self.svg_item.setPos(0,0)
            self.scene.setSceneRect(self.renderer.viewBoxF())
            QTimer.singleShot(0,lambda:self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio))
    
class LatexOutput(QMainWindow):
    def __init__(self,expr:str,raw=False):
        super().__init__()
        self.setWindowTitle('Latex预览')

        self.central=QWidget()
        self.main_layout=QVBoxLayout()
        try:
            print(expr.strip())
            self.display=LatexDisplay((exp if raw else expr2latex(exp))) if (exp:=expr.strip()) else (QLabel('预览内容为空'))
        except SyntaxError as e:
            QMessageBox.warning(self,'错误',f'表达式有语法错误，请更正后再试。\n错误详情:{err.syntaxErrTranslate(e)}')
            self.destroy()
            return
        except Exception as e:
            QMessageBox.warning(self,'错误',f'预览出错，错误详情:{e.__repr__()}')
            self.destroy()
            return
        self.setCentralWidget(self.central)
        self.central.setLayout(self.main_layout)
        self.main_layout.addWidget(self.display)

        self.show()

if __name__ == '__main__':
    app=QApplication(sys.argv)
    display=LatexOutput(r'5**(1/4)')
    #         return super().wheelEvent(event)
    app.exec_()
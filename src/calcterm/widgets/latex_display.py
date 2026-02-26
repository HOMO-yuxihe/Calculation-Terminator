from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QPainter,QWheelEvent
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox,QWidget,QVBoxLayout,QGraphicsScene,QGraphicsView
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QGraphicsScene,QGraphicsView
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer
import sys
sys.path.append('src')

from calcterm.core.latex import *
from calcterm.widgets.common import *

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
                    # 1. 基础位置参数（保持和原事件一致）
                    event.pos(),                  # pos: QPoint（鼠标位置）
                    event.globalPos(),            # globalPos: QPoint（全局位置）
                    # 2. 滚动增量（保持和原事件一致）
                    event.pixelDelta(),           # pixelDelta: QPoint（像素增量）
                    event.angleDelta(),           # angleDelta: QPoint（角度增量）
                    # 3. Qt4 兼容参数（Qt5 必需，根据方向赋值）
                    event.angleDelta().x() if event.angleDelta().x() != 0 else event.angleDelta().y(),  # qt4Delta
                    Qt.Horizontal,                # qt4Orientation: 改为水平方向
                    # 4. 按键/修饰键状态（保持和原事件一致）
                    event.buttons(),              # buttons: 鼠标按键
                    Qt.KeyboardModifiers(),            # modifiers: 键盘修饰键（保留 Shift）
                    # 5. 扩展参数（Qt5 重载必需）
                    event.phase(),          # phase: 滚动阶段
                    event.inverted(),             # inverted: 是否反向滚动
                    event.source()                # source: 事件源
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
        svg_data=latex2svg(tex,self.font_size)
        svg_bytes=QByteArray(svg_data.encode('utf-8'))
        self.renderer.load(svg_bytes)
        
        if self.renderer.isValid():
            self.svg_item.setElementId('')
            self.svg_item.setPos(0,0)
            self.scene.setSceneRect(self.renderer.viewBoxF())
            self.view.fitInView(self.scene.sceneRect(), mode=1)
    
    # def wheelEvent(self, event:QWheelEvent):
    #     if event.modifiers() & Qt.ControlModifier:
    #         factor=1.25 if event.angleDelta().y()>0 else 0.8
    #         self.view.scale(factor,factor)
    #         event.ignore()
    #     else:
    #         return super().wheelEvent(event)\

class LatexOutput(WithSubwindow):
    def __init__(self,expr:str):
        super().__init__()
        self.setWindowTitle('Latex预览')

        self.central=QWidget()
        self.main_layout=QVBoxLayout()
        self.display=LatexDisplay(expr2latex(expr)) if expr.strip() else (QLabel('预览内容为空'))
        self.setCentralWidget(self.central)
        self.central.setLayout(self.main_layout)
        self.main_layout.addWidget(self.display)

        self.show()

if __name__ == '__main__':
    app=QApplication(sys.argv)
    display=LatexOutput(r'\frac{1}{2}\int_a^b f(x)dx')
    #         return super().wheelEvent(event)

if __name__ == '__main__':
    app=QApplication(sys.argv)
    display=LatexDisplay(r'\frac{1}{2}\int_a^b f(x)dx')
    display.show()
    sys.exit(app.exec_())
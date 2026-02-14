import sys
from typing import List
from PyQt5.QtWidgets import (QTextEdit,QAction,QLineEdit,QWidget,
                             QScrollArea,QVBoxLayout,QShortcut,
                             QCheckBox)
from PyQt5.QtGui import QKeySequence,QKeyEvent
from PyQt5.QtCore import Qt,QTimer,QEvent
from sympy import var

class MTextEdit(QTextEdit):
    def __init__(self,menus=[],*args,**kw):
        super().__init__(*args,**kw)
        self.menu=menus
    
    def setMenu(self,menus:List[QAction]=[]):
        self.menu=menus
    
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        for i in self.menu:menu.addAction(i)
        menu.exec(event.globalPos())

class MultiLineEdit(QWidget):
    class _LineEdit(QLineEdit):
        def __init__(self,parent,canBeDeleted=True,*args,**kw):
            super().__init__(*args,**kw)
            self.par=parent
            self.canBeDeleted=canBeDeleted
        
        def keyPressEvent(self, event:QKeyEvent):
            if event.key()==Qt.Key.Key_Backspace and self.canBeDeleted:
                if not self.text():
                    self.par.deleteCur(self)
                else:
                    return super().keyPressEvent(event)
            elif event.key()==Qt.Key_Return:
                self.par.add(self)
            elif event.key()==Qt.Key_Up:
                self.par.up(self)
            elif event.key()==Qt.Key_Down:
                self.par.down(self)
            elif event.key()==Qt.Key_Delete:
                index=self.par.content_layout.indexOf(self)
                curpos=self.cursorPosition()
                if index<len(self.par.lines)-1 and curpos==len(self.text()):
                    nxt=self.par.lines[index+1]
                    if not nxt.text().strip():
                        self.par.deleteCur(nxt)
                    else:return super().keyPressEvent(event)
                else:return super().keyPressEvent(event)
            else:
                return super().keyPressEvent(event)
    def __init__(self,*args,**kw):
        super().__init__(*args,**kw)
        self.main_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea(self,widgetResizable=1)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget,spacing=8)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.lines = [self._LineEdit(self,False)]
        self.lines[0].returnPressed.connect(lambda: self.add(self.lines[0]))
        self.content_layout.addWidget(self.lines[0])
        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area, stretch=1)

    def add(self,obj:QWidget):
        item = self._LineEdit(self)
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Backspace),item,
                             context=Qt.WidgetShortcut,activated=lambda:self.delete(item))
        index = self.content_layout.indexOf(obj) + 1
        self.lines.insert(index, item)
        self.content_layout.insertWidget(index, item)
        item.setFocus()
    
    def deleteCur(self,obj:QWidget):
        try:
            self.lines[self.content_layout.indexOf(obj)-1].setFocus()
            self.lines.remove(obj)
            self.content_layout.removeWidget(obj)
            obj.deleteLater()
        except Exception as e:
            print(e)

    # def deleteNxt(self,obj:QWidget):
    #             try:
    #                 self.lines.remove(nxt)
    #                 self.content_layout.removeWidget(nxt)
    #                 nxt.deleteLater()
    #             except Exception as e:
    #                 print(e)

    def up(self,obj:QWidget):
        index=self.content_layout.indexOf(obj)
        if index>=1:
            self.lines[index-1].setFocus()
            self.lines[index-1].setCursorPosition(len(self.lines[index-1].text()))
    def down(self,obj:QWidget):
        index=self.content_layout.indexOf(obj)
        if index<len(self.lines)-1:
            self.lines[index+1].setFocus()
            self.lines[index+1].setCursorPosition(len(self.lines[index+1].text()))

class MultiLineSelector(QWidget):
    def __init__(self,vars:List[str],*args,**kw):
        super().__init__(*args,**kw)
        self.main_layout=QVBoxLayout()
        self.setLayout(self.main_layout)
        self.scroll_area=QScrollArea(widgetResizable=1)
        self.content_widget=QWidget()
        self.content_layout=QVBoxLayout(spacing=8)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.variables=vars
        self.lines=[]
        for i in vars:
            checkBox=QCheckBox(i)
            checkBox.setCheckState(Qt.Checked)
            self.content_layout.addWidget(checkBox)
            self.lines.append(checkBox)
        self.content_widget.setLayout(self.content_layout)
        self.scroll_area.setWidget(self.content_widget)        
        self.main_layout.addWidget(self.scroll_area)
    
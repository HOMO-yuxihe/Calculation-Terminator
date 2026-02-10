import sys,time
sys.path.append('src')
from keyword import iskeyword
from PyQt5.QtWidgets import (
    QApplication,QLabel,QMainWindow,QTabWidget,
    QWidget,QVBoxLayout,QHBoxLayout,QTextEdit,
    QPushButton,QAction,QScrollArea,QLineEdit,
    QShortcut,QInputDialog,QListView,QMenuBar,
    QMenu,QMessageBox,QDialog)
from PyQt5.QtGui import QFont,QKeySequence,QStandardItem,QStandardItemModel,QKeyEvent
from PyQt5.QtCore import Qt,QTimer,pyqtSignal,QModelIndex
import calcterm.core.calc as parser
from calcterm.widgets.common import MTextEdit,MultiLineEdit
from typing import List,Dict,Union

font1=QFont()
font1.setFamily('Microsoft Yahei'),font1.setPointSize(12)
font2=QFont()
font2.setFamily('Consolas'),font2.setPointSize(18)
fontdefault=QFont()
fontdefault.setFamily('Microsoft Yahei'),fontdefault.setPointSize(9)

class Subwindow(QMainWindow):
    def __init__(self,parent):
        super().__init__()
        self.par=parent
    
    def closeEvent(self, event):
        self.par.closeSubwindow(self)
        return super().closeEvent(event)

class WithSubwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.windows=[]

    def closeSubwindow(self,target:QMainWindow):
        self.windows.remove(target)
        target.close()
    
    def closeEvent(self, event):
        for i in self.windows.copy():
            i.close()
        return super().closeEvent(event)

class OutputWindow(Subwindow):
    def __init__(self,parent,content):
        super().__init__(parent)
        self.setWindowTitle('计算结果')
        self.resize(600,400)
        self.setMinimumSize(400,200)
        self.par=parent

        simplifyAction=QAction('化简 (Ctrl+S)',shortcut='Ctrl+S',triggered=self.simplify)
        evalAction=QAction('求值 (Ctrl+E)',shortcut='Ctrl+E',triggered=self.eval)
        self.closeShortcut=QShortcut(QKeySequence('Escape'),self,activated=self.close)
        self.display=MTextEdit([simplifyAction,evalAction],content,font=font2,readOnly=1)

        self.setCentralWidget(self.display)
        self.show()
    
    # def keyPressEvent(self, event):
    #     if event.key()==Qt.Key.Key_Escape:
    #         self.closeEvent(None)
    
    def simplify(self):
        content=self.display.toPlainText()
        result=parser.parse_expr(f'simplify({content})')
        self.display.setPlainText(str(result))
    
    def eval(self):
        content=self.display.toPlainText()
        digit,ok=QInputDialog.getInt(self,'有效数字位数','高精度计算',15)
        if ok:
            result=parser.parse_expr(f'simplify({content})')
            self.display.setPlainText(str(result.evalf(digit)))

class VariableModifier(QDialog):

    def __init__(self,parent,variable:parser.Variable={'id':'','name':'','assumptions':{}},variableList=[]):
        super().__init__(parent=parent)
        self.varIds=[i['id'] for i in variableList]
        self.setWindowTitle('修改变量')
        # self.setMinimumSize(200,100)
        self.setFont(font1)
        self.setSizePolicy(0,0)

        self.mainLayout=QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.idLayout=QHBoxLayout()
        self.nameLayout=QHBoxLayout()
        self.exitLayout=QHBoxLayout()
        self.mainLayout.addLayout(self.idLayout)
        self.mainLayout.addLayout(self.nameLayout)
        self.mainLayout.addLayout(self.exitLayout)

        self.idTip=QLabel('变量标识符:')
        self.id=QLineEdit(variable['id'])
        self.srcid=variable['id']
        self.idLayout.addWidget(self.idTip)
        self.idLayout.addWidget(self.id)
        self.nameTip=QLabel('变量显示名:')
        self.name=QLineEdit(variable['name'])
        self.nameLayout.addWidget(self.nameTip)
        self.nameLayout.addWidget(self.name)
        self.addBtn=QPushButton('完成')
        self.addBtn.clicked.connect(self.mod)
        self.cancelBtn=QPushButton('取消')
        self.cancelBtn.clicked.connect(self.reject)
        self.exitLayout.addWidget(self.addBtn)
        self.exitLayout.addWidget(self.cancelBtn)
        self.res={}
    
    def mod(self):
        if not self.id.text().strip():
            QMessageBox.warning(self,'错误','标识符不能为空')
            return
        if not self.name.text().strip():
            self.name.setText(self.id.text())
            return
        if iskeyword(self.id.text().strip()):
            QMessageBox.warning(self,'错误','标识符不能包含关键字')
            return
        if not self.id.text().strip().isidentifier():
            QMessageBox.warning(self,'错误','标识符不符合命名格式')
            return
        if self.id.text() in self.varIds and self.id.text() != self.srcid:
            QMessageBox.warning(self,'错误','标识符已存在')
            return
        self.res={'id':self.id.text(),'name':self.name.text(),'assumptions':{}}
        self.accept()
    
    @staticmethod
    def get(parent,variable:parser.Variable={'id':'','name':'','assumptions':{}},variableList=[]):
        dialog=VariableModifier(parent,variable,variableList)
        result=dialog.exec_()
        return dialog.res,(result==QDialog.Accepted)


class VariableManager(Subwindow):
    class _ListView(QListView):
        def __init__(self,parent,*args,**kw):
            super().__init__(*args,**kw)
            self.par=parent
        def keyPressEvent(self, event:QKeyEvent):
            if event.key()==Qt.Key_F5:
                self.par.refresh()
                event.ignore()
            else:
                return super().keyPressEvent(event)
    def __init__(self,parent,variables):
        Subwindow.__init__(self,parent)
        # WithSubwindow.__init__(self)
        self.resize(400,300)
        self.setMinimumSize(300,200)
        self.setWindowTitle('变量管理器')
        self.par=parent
        self.setFont(font1)

        self.central=QWidget()
        self.setCentralWidget(self.central)
        self.mainLayout=QHBoxLayout()
        self.central.setLayout(self.mainLayout)
        self.variables:List[parser.Variable]=variables
        self.varModel=QStandardItemModel()

        self.list=self._ListView(self,font=font2)
        self.list.setModel(self.varModel)
        self.list.clicked.connect(self.showInfo)
        self.sidebar=QVBoxLayout()

        self.addBtn=QPushButton('添加')
        self.editBtn=QPushButton('修改')
        self.delBtn=QPushButton('删除')
        self.info=QTextEdit()
        self.info.setFixedWidth(150)
        self.info.setReadOnly(1)
        self.addBtn.clicked.connect(self.addOpen)
        self.editBtn.clicked.connect(self.editOpen)
        self.delBtn.clicked.connect(self.remove)

        self.sidebar.addWidget(self.addBtn)
        self.sidebar.addWidget(self.editBtn)
        self.sidebar.addWidget(self.delBtn)
        self.sidebar.addWidget(self.info)

        self.mainLayout.addWidget(self.list)
        self.mainLayout.addLayout(self.sidebar)

        self.refresh()
    
    def addOpen(self):
        var,ok=VariableModifier.get(self,variableList=self.variables)
        if ok:
            self.variables.append(var)
            self.varModel.appendRow(QStandardItem(var['id']))
    
    def editOpen(self):
        model=self.list.selectionModel()
        indexes=model.selectedIndexes()
        if indexes:
            mod,ok=VariableModifier.get(self,self.variables[indexes[0].row()],self.variables)
            if ok:
                self.variables[indexes[0].row()]=mod
                self.varModel.setData(indexes[0],mod['id'])
                self.showInfo()
        else:
            QMessageBox.warning(self,'错误','请选中一个变量')

    def remove(self):
        model=self.list.selectionModel()
        indexes=model.selectedIndexes()
        if indexes:
            index=indexes[0].row()
            self.varModel.removeRow(index)
            self.variables.pop(index)
            self.showInfo()
        else:
            QMessageBox.warning(self,'错误','请选中一个变量')

    def refresh(self):
        self.varModel.clear()
        for i in self.variables:
            if not i:
                self.variables.remove(i)
                continue
            self.varModel.appendRow(QStandardItem(i['id']))
    
    def showInfo(self,index:QModelIndex=None):
        if index==None:
            indexes=self.list.selectionModel().selectedIndexes()
            if indexes:
                row=indexes[0].row()
            else:
                self.info.clear()
                return
        else:
            row=index.row()
        var=self.variables[row]
        self.info.setPlainText(f"标识符: {var['id']}\n显示名: {var['name']}\n断言: {'无' if not var['assumptions'].items() else ','.join(f'{i}:{j}' for i,j in var['assumptions'].items())}")
    


class MainWindow(WithSubwindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("计算器")
        self.resize(800,600)
        self.setMinimumSize(400,400)

        self.setFont(font1)
        self.windows=[]

        self.menubar=QMenuBar(self,font=fontdefault)
        self.setMenuBar(self.menubar)
        self.variables=[]
        self.variablemanager=VariableManager(self,self.variables)
        self.windows.append(self.variablemanager)
        self.varMgmt=QAction('变量管理',self.menubar,triggered=self.openVariableManager)
        self.varMgmtopened=0
        self.menubar.addAction(self.varMgmt)

        #标签页部分
        self.Tab_font=QFont()
        self.Tab_font.setFamily('Microsoft Yahei'),self.Tab_font.setPointSize(10)
        self.Tab=QTabWidget(self,font=self.Tab_font)
        self.calcTab=QWidget(self.Tab)
        self.eqalTab=QWidget(self.Tab)
        self.ineqalTab=QWidget(self.Tab)
        self.lagrangeTab=QWidget(self.Tab)
        self.Tab.addTab(self.calcTab,'代数/数值计算')
        self.Tab.addTab(self.eqalTab,'方程求解')
        self.Tab.addTab(self.ineqalTab,'不等式求解')
        self.Tab.addTab(self.lagrangeTab,'拉格朗日乘数')
        self.setCentralWidget(self.Tab)

        #基础计算部分
        self.calc_layout=QVBoxLayout()
        self.calcTab.setLayout(self.calc_layout)
        self.calc_inputTip=QLabel('输入表达式',font=font1,alignment=Qt.AlignCenter)
        self.calc_input=QTextEdit(font=font2)
        self.calc_layout.addWidget(self.calc_inputTip)
        self.calc_layout.addWidget(self.calc_input)

        self.calc_output_layout=QHBoxLayout()
        self.calc_layout.addLayout(self.calc_output_layout)
        self.calc_outputTip=QLabel('计算结果',font=font1,alignment=Qt.AlignCenter)
        self.calc_calc=QPushButton('计算/执行',font=font1)
        self.calc_calc.pressed.connect(self.calc)
        # self.calc_output_layout_lFilling=QLabel()
        # self.calc_output_layout_lFilling.setFixedWidth(100)
        # self.calc_output_layout.addWidget(self.calc_output_layout_lFilling)
        # self.calc_output_layout.addWidget(self.calc_outputTip)
        self.calc_output_layout.addWidget(self.calc_calc)

        #拉格朗日部分
        self.lagrange_layout=QVBoxLayout()
        self.lagrangeTab.setLayout(self.lagrange_layout)
        self.lagrange_limitsTip=QLabel('约束条件',font=font1,alignment=Qt.AlignCenter)
        self.lagrange_limitsInput=MultiLineEdit(font=font2)
        self.lagrange_targetTip=QLabel('目标函数',font=font1,alignment=Qt.AlignCenter)
        self.lagrange_targetInput=QTextEdit(font=font2)
        self.lagrange_calc=QPushButton('开始计算',font=font1)
        self.lagrange_calc.pressed.connect(self.lagrange)

        
        self.lagrange_layout.addWidget(self.lagrange_limitsTip)
        self.lagrange_layout.addWidget(self.lagrange_limitsInput,stretch=1)
        self.lagrange_layout.addWidget(self.lagrange_targetTip)
        self.lagrange_layout.addWidget(self.lagrange_targetInput,stretch=1)
        self.lagrange_layout.addWidget(self.lagrange_calc)

    def calc(self):
        expr=self.calc_input.toPlainText()
        if not expr.strip():
            QMessageBox.warning(self,'错误','表达式不能为空')
            return
        result=parser.calc(expr,self.variables)
        self.windows.append(OutputWindow(self,result))
        self.calc_calc.setDisabled(1)
        QTimer.singleShot(100,lambda:self.calc_calc.setDisabled(0))
        print(self.windows)
        print(self.variables)

        # sys.exit(0)
    
    def lagrange(self):
        limits=[i.text().strip() for i in self.lagrange_limitsInput.lines if i.text().strip()]
        target=self.lagrange_targetInput.toPlainText()
        if not target.strip():
            QMessageBox.warning(self,'错误','目标函数不能为空')
            return
        res=parser.lagrange(limits,target,self.variables)
        if isinstance(res,str):
            self.windows.append(OutputWindow(self,res))
        else:
            self.windows.append(OutputWindow(self,'\n'.join(map(str,res))))
        
    
    def openVariableManager(self):
        if self.variablemanager in self.windows:
            self.variablemanager.show()
            self.variablemanager.raise_()
            self.variablemanager.activateWindow()
            self.variablemanager.setFocus()
        else:
            self.variablemanager=VariableManager(self,self.variables)
            self.variablemanager.show()
            self.windows.append(self.variablemanager)
    
    def closeEvent(self, event):
        super().closeEvent(event)
        self.close()
        sys.exit(0)

if __name__ == '__main__':
    app=QApplication(sys.argv)

    window=MainWindow()
    window.show()
    sys.exit(app.exec_())
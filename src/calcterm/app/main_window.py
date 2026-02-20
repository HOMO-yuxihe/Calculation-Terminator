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
from calcterm.widgets.common import *
from typing import List,Dict,Union

font1=QFont()
font1.setFamily('Microsoft Yahei'),font1.setPointSize(12)
font2=QFont()
font2.setFamily('Consolas'),font2.setPointSize(18)
fontdefault=QFont()
fontdefault.setFamily('Microsoft Yahei'),fontdefault.setPointSize(9)

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
        result=parser.simplify(content)
        self.display.setPlainText(str(result))
    
    def eval(self):
        content=self.display.toPlainText()
        if (res:=QInputDialog.getInt(self,'有效数字位数','高精度计算',15))[1]:
            self.display.setPlainText(parser.evalf(content,res[0]))

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
        self.res:parser.Variable={'id':self.id.text(),'name':self.name.text(),'assumptions':{}}
        self.accept()
    
    @staticmethod
    def get(parent,variable:parser.Variable={'id':'','name':'','assumptions':{}},variableList=[]):
        dialog=VariableModifier(parent,variable,variableList)
        result=dialog.exec_()
        return dialog.res,(result==QDialog.Accepted)


class VariableManager(GenericModifier):
    def __init__(self,parent,variables):
        super().__init__(parent,'变量管理器',(font1,font2),VariableModifier,variables)
    
    def showInfo(self,index:QModelIndex=None):
        if index==None:
            if indexes:=self.list.selectionModel().selectedIndexes():
                row=indexes[0].row()
            else:
                self.info.clear()
                return
        else:
            row=index.row()
        var=self.variables[row]
        self.info.setPlainText(f"标识符: {var['id']}\n显示名: {var['name']}\n断言: {'无' if not var['assumptions'].items() else ','.join(f'{i}:{j}' for i,j in var['assumptions'].items())}")

class FunctionManager(GenericModifier):
    def __init__(self,parent,functions):
        super().__init__(parent,'函数管理器',(font1,font2),VariableModifier,functions)
    def showInfo(self,index:QModelIndex=None):
        if index==None:
            if indexes:=self.list.selectionModel().selectedIndexes():
                row=indexes[0].row()
            else:
                self.info.clear()
                return
        else:
            row=index.row()
        var=self.variables[row]
        self.info.setPlainText(f"标识符: {var['id']}\n显示名: {var['name']}\n断言: {'无' if not var['assumptions'].items() else ','.join(f'{i}:{j}' for i,j in var['assumptions'].items())}")  
    
class VariableSelector(QDialog):
    def __init__(self,parent,vars:List[str]):
        super().__init__(parent=parent)
        self.setWindowTitle('选择求解的变量')
        self.setFont(font1)
        self.mainLayout=QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.variableList=MultiLineSelector(vars)
        self.mainLayout.addWidget(self.variableList)

        self.exitLayout=QHBoxLayout()
        self.confirmBtn=QPushButton('确定')
        self.confirmBtn.clicked.connect(self.confirm)
        self.cancelBtn=QPushButton('取消')
        self.cancelBtn.clicked.connect(self.reject)
        self.exitLayout.addWidget(self.confirmBtn)
        self.exitLayout.addWidget(self.cancelBtn)
        self.mainLayout.addLayout(self.exitLayout)
        self.res=[False]*len(vars)
        self.null=self.res
    
    def confirm(self):
        self.res=[i.checkState()==Qt.Checked for i in self.variableList.lines]
        self.accept()

    @staticmethod
    def get(parent,vars:List[str]):
        dialog=VariableSelector(parent,vars)
        result=dialog.exec_()
        return dialog.res,((result==QDialog.Accepted) if dialog.res!=dialog.null else False)

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
        self.functions=[]
        self.variablemanager=VariableManager(self,self.variables)
        self.functionmanager=FunctionManager(self,self.functions)
        self.windows.append(self.variablemanager)
        self.varMgmt=QAction('变量管理',self.menubar,triggered=self.openVariableManager)
        self.varMgmtopened=0
        self.funcMgmt=QAction('函数管理',self.menubar,triggered=self.openFunctionManager)
        self.funcMgmtopened=0
        self.namespaceMgmt=QMenu('命名空间管理',self.menubar)
        self.namespaceMgmt.addAction(self.varMgmt)
        self.namespaceMgmt.addAction(self.funcMgmt)
        self.menubar.addMenu(self.namespaceMgmt)

        #标签页部分
        self.Tab_font=QFont('Microsoft Yahei',10)
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

        #方程求解部分
        self.eqal_layout=QVBoxLayout()
        self.eqalTab.setLayout(self.eqal_layout)
        self.eqal_inputTip=QLabel('输入方程',font=font1,alignment=Qt.AlignCenter)
        self.eqal_input=MultiLineEdit(font=font2)
        self.eqal_calc=QPushButton('求解',font=font1)
        self.eqal_calc.clicked.connect(self.solve)
        self.eqal_layout.addWidget(self.eqal_inputTip)
        self.eqal_layout.addWidget(self.eqal_input)
        self.eqal_layout.addWidget(self.eqal_calc)

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
        result=parser.calc(expr,self.variables,self.functions)
        self.windows.append(OutputWindow(self,result))
        self.calc_calc.setDisabled(1)
        QTimer.singleShot(100,lambda:self.calc_calc.setDisabled(0))
        print(self.windows)
        print(self.variables)

        # sys.exit(0)
    
    def solve(self):
        exprs=[j for i in self.eqal_input.lines if (j:=i.text().strip())]
        if not exprs:
            QMessageBox.warning(self,'错误','方程组不能为空')
            return
        solver=parser.smartsolver(exprs,self.variables,self.functions)
        try:
            usedVariables=solver.__next__()
        except StopIteration as e:
            QMessageBox.warning(self,'错误',str(e))
            return
        target,ok=VariableSelector.get(self,usedVariables)
        if not ok:return
        res=solver.send(target)
        self.windows.append(OutputWindow(self,str(res)))
        

    def lagrange(self):
        limits=[j for i in self.lagrange_limitsInput.lines if (j:=i.text().strip())]
        target=self.lagrange_targetInput.toPlainText()
        if not target.strip():
            QMessageBox.warning(self,'错误','目标函数不能为空')
            return
        if isinstance(res:=parser.lagrange(limits,target,self.variables,self.functions),str):
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

    def openFunctionManager(self):
        if self.functionmanager in self.windows:
            self.functionmanager.show()
            self.functionmanager.raise_()
            self.functionmanager.activateWindow()
            self.functionmanager.setFocus()
        else:
            self.functionmanager=FunctionManager(self,self.functions)
            self.functionmanager.show()
            self.windows.append(self.functionmanager)
    
    def closeEvent(self, event):
        super().closeEvent(event)
        self.close()
        sys.exit(0)

if __name__ == '__main__':
    app=QApplication(sys.argv)

    window=MainWindow()
    window.show()
    sys.exit(app.exec_())
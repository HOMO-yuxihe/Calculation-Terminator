import sys,time
from typing_extensions import ReadOnly
sys.path.append('src')
from keyword import iskeyword
from PyQt5.QtWidgets import (
    QApplication, QFrame,QLabel,QMainWindow,QTabWidget,
    QWidget,QVBoxLayout,QHBoxLayout,QTextEdit,
    QPushButton,QAction,QScrollArea,QLineEdit,
    QShortcut,QInputDialog,QListView,QMenuBar,
    QMenu,QMessageBox,QDialog)
from PyQt5.QtGui import QFont,QKeySequence,QStandardItem,QStandardItemModel,QKeyEvent
from PyQt5.QtCore import Qt,QTimer,pyqtSignal,QModelIndex
import calcterm.core.calc as parser
import calcterm.core.exception_parser as err
from calcterm.widgets.common import *
from calcterm.widgets.latex_display import *
from calcterm.app.config import *
from calcterm.app.namespacemgmt import *
from typing import List,Dict,Union

class OutputWindow(Subwindow):
    def __init__(self,parent,content):
        super().__init__(parent)
        self.setWindowTitle('计算结果')
        self.resize(600,400)
        self.setMinimumSize(400,200)
        self.par=parent

        simplifyAction=QAction('化简',shortcut='Ctrl+S',triggered=self.simplify)
        evalAction=QAction('求值',shortcut='Ctrl+E',triggered=self.eval)
        viewAction=QAction('预览',shortcut='Ctrl+Alt+V',triggered=self.view)
        self.closeShortcut=QShortcut(QKeySequence('Escape'),self,activated=self.close)
        self.display=MTextEdit([simplifyAction,evalAction,viewAction],content,font=font2,readOnly=1)

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
    
    def view(self):
        content=self.display.toPlainText()
        disp=LatexOutput(content)
        disp.show()
        self.par.windows.append(disp)

class MultiSolvesOutputWindow(Subwindow,WithSubwindow):
    class SingleSolve(QFrame):
        class OneSolve(QWidget):
            def __init__(self,par,var:str,val:str):
                super().__init__()
                print(var,val)
                self.main_layout=QHBoxLayout()
                self.main_layout.setContentsMargins(0,0,0,0)
                self.setLayout(self.main_layout)
                self.var=QLabel(f'{var}=',font=font2)
                self.val=MLineEdit([QAction('预览',shortcut='Ctrl+Alt+V',triggered=lambda:par.windows.append(LatexOutput(self.val.text())))],val,font=font2,readOnly=1)
                self.val.setCursorPosition(0)
                self.main_layout.addWidget(self.var)
                self.main_layout.addWidget(self.val,stretch=1)

        def __init__(self,par,content:Dict[str,str]):
            super().__init__()
            self.setObjectName('SingleSolve')
            self.main_layout=QVBoxLayout(spacing=1)
            self.setLayout(self.main_layout)

            for i,j in content.items():
                self.main_layout.addWidget(self.OneSolve(par,i,j))
            self.setStyleSheet('''
                QFrame#SingleSolve {
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    padding: 8px;
                }
            ''')

    def __init__(self,parent,content:List[Dict[str,str]]):
        super().__init__(parent)
        self.setWindowTitle('计算结果')
        self.resize(600,400)
        self.setMinimumSize(400,200)
        self.par=parent

        self.central=QWidget()
        self.main_layout=QVBoxLayout()
        self.scroll_area=QScrollArea()
        self.scroll_layout=QVBoxLayout()
        self.display=QWidget()

        self.central.setLayout(self.main_layout)
        self.main_layout.addWidget(self.scroll_area)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.display.setLayout(self.scroll_layout)
        self.scroll_area.setWidgetResizable(1)
        self.scroll_area.setWidget(self.display)

        print(content)
        if not content:
            self.scroll_layout.addWidget(QLabel('方程无解',font=QFont('Microsoft Yahei',40),alignment=Qt.AlignCenter))
        else:
            for i in content:
                self.scroll_layout.addWidget(self.SingleSolve(self,i))

        self.setCentralWidget(self.central)
        self.central.setLayout(self.main_layout)
        self.show()

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
        
        self.info.setPlainText(f"标识符: {var['id']}\n显示名: {var['name']}\n断言: \n"+('无' if not var['assumptions'].items() else ';\n'.join(f'{i}:{j}' for i,j in var['assumptions'].items())))

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
    
    def view(self):
        content=self.display.toPlainText()
        disp=LatexDisplay(expr2latex(content))
        disp.show()
        self.par.windows.append(disp)
  
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
        self.namespace={'variables':[],'functions':[],'lambdas':[]}
        self.namespacemanager=NamespaceManager(self,self.namespace)
        self.windows.append(self.namespacemanager)
        self.namespaceMgmt=QAction('命名空间管理',self.menubar,triggered=self.openNamespaceManager)
        self.menubar.addAction(self.namespaceMgmt)

        #标签页部分
        self.Tab_font=QFont('Microsoft Yahei',10)
        self.Tab=QTabWidget(self,font=self.Tab_font)
        self.calcTab=QWidget(self.Tab)
        self.eqalTab=QWidget(self.Tab)
        self.deqalTab=QWidget(self.Tab)
        self.ineqalTab=QWidget(self.Tab)
        self.lagrangeTab=QWidget(self.Tab)
        self.Tab.addTab(self.calcTab,'代数/数值计算')
        self.Tab.addTab(self.eqalTab,'方程求解')
        self.Tab.addTab(self.deqalTab,'微分方程求解')
        self.Tab.addTab(self.ineqalTab,'不等式求解')
        self.Tab.addTab(self.lagrangeTab,'拉格朗日乘数')
        self.setCentralWidget(self.Tab)

        #基础计算部分
        self.calc_layout=QVBoxLayout()
        self.calcTab.setLayout(self.calc_layout)
        self.calc_inputTip=QLabel('输入表达式',font=font1,alignment=Qt.AlignCenter)
        self.calc_input=MTextEdit(font=font2,menus=[QAction('预览',shortcut='Ctrl+Alt+V',triggered=lambda:self.windows.append(LatexOutput(self.calc_input.toPlainText())))])
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
        self.eqal_input=MultiMLineEdit(font=font2,menus=[('预览','Ctrl+Alt+V',lambda i:self.windows.append(LatexOutput(i.text())))])
        # self.eqal_input=MultiLineEdit(font=font2)
        self.eqal_calc=QPushButton('求解',font=font1)
        self.eqal_calc.clicked.connect(self.solve)
        self.eqal_layout.addWidget(self.eqal_inputTip)
        self.eqal_layout.addWidget(self.eqal_input)
        self.eqal_layout.addWidget(self.eqal_calc)

        #微分方程求解部分
        self.deqal_layout=QVBoxLayout()
        self.deqalTab.setLayout(self.deqal_layout)
        self.deqal_inputTip=QLabel('输入微分方程',font=font1,alignment=Qt.AlignCenter)
        self.deqal_input=MultiMLineEdit(menus=[('预览','Ctrl+Alt+V',lambda i:self.windows.append(LatexOutput(i.text())))],font=font2)
        self.deqal_ics_inputTip=QLabel('微分方程的初始条件',font=font1,alignment=Qt.AlignCenter)
        self.deqal_ics_input=MultiMLineEdit(menus=[('预览','Ctrl+Alt+V',lambda i:self.windows.append(LatexOutput(i.text())))],font=font2)
        self.deqal_calc=QPushButton('求解',font=font1)
        self.deqal_calc.clicked.connect(self.dsolve)
        self.deqal_layout.addWidget(self.deqal_inputTip)
        self.deqal_layout.addWidget(self.deqal_input)
        self.deqal_layout.addWidget(self.deqal_ics_inputTip)
        self.deqal_layout.addWidget(self.deqal_ics_input)
        self.deqal_layout.addWidget(self.deqal_calc)

        #拉格朗日部分
        self.lagrange_layout=QVBoxLayout()
        self.lagrangeTab.setLayout(self.lagrange_layout)
        self.lagrange_limitsTip=QLabel('约束条件',font=font1,alignment=Qt.AlignCenter)
        self.lagrange_limitsInput=MultiMLineEdit(font=font2,menus=[('预览','Ctrl+Alt+V',lambda i:self.windows.append(LatexOutput(i.text())))])
        self.lagrange_targetTip=QLabel('目标函数',font=font1,alignment=Qt.AlignCenter)
        self.lagrange_targetInput=MTextEdit(font=font2,menus=[QAction('预览',shortcut='Ctrl+Alt+V',triggered=lambda:self.windows.append(LatexOutput(self.lagrange_targetInput.toPlainText())))])
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
        try:
            result=parser.calc(expr,self.namespace)
        except SyntaxError as e:
            QMessageBox.warning(self,'错误',err.syntaxErrTranslate(e))
            return
        self.windows.append(OutputWindow(self,result))
        self.calc_calc.setDisabled(1)
        QTimer.singleShot(100,lambda:self.calc_calc.setDisabled(0))
        print(self.windows)
        print(self.namespace['variables'])

        # sys.exit(0)
    
    def solve(self):
        exprs=[j for i in self.eqal_input.lines if (j:=i.text().strip())]
        if not exprs:
            QMessageBox.warning(self,'错误','方程组不能为空')
            return
        solver=parser.smartsolver(exprs,self.namespace)
        try:
            usedVariables=solver.__next__()
        except StopIteration as e:
            QMessageBox.warning(self,'错误',str(e))
            return
        except SyntaxError as e:
            QMessageBox.warning(self,'错误',err.syntaxErrTranslate(e))
            return
        target,ok=VariableSelector.get(self,usedVariables)
        if not ok:return
        res=solver.send(target)
        print(res)
        self.windows.append(MultiSolvesOutputWindow(self,[{str(j):str(k) for j,k in i.items()} for i in res]))
    
    def dsolve(self):
        exprs=[j for i in self.deqal_input.lines if (j:=i.text().strip())]
        ics=[j for i in self.deqal_ics_input.lines if (j:=i.text().strip())]
        if not exprs:
            QMessageBox.warning(self,'错误','方程组不能为空')
            return
        solver=parser.dsolver(exprs,self.namespace,ics)
        try:
            usedFunctions=solver.__next__()
        except StopIteration as e:
            QMessageBox.warning(self,'错误',str(e))
            return
        except SyntaxError as e:
            QMessageBox.warning(self,'错误',err.syntaxErrTranslate(e))
            return
        except ValueError as e:
            QMessageBox.warning(self,'错误',str(e))
            return
        target,ok=VariableSelector.get(self,usedFunctions)
        if not ok:return
        res=solver.send(target)
        self.windows.append(MultiSolvesOutputWindow(self,[{str(j):str(k) for j,k in i.items()} for i in res]))
        

    def lagrange(self):
        limits=[j for i in self.lagrange_limitsInput.lines if (j:=i.text().strip())]
        target=self.lagrange_targetInput.toPlainText()
        if not target.strip():
            QMessageBox.warning(self,'错误','目标函数不能为空')
            return
        try:
            res=parser.lagrange(limits,target,self.namespace)
        except SyntaxError as e:
            QMessageBox.warning(self,'错误',err.syntaxErrTranslate(e))
            return
        if isinstance(res,str):
            self.windows.append(OutputWindow(self,res))
        else:
            self.windows.append(MultiSolvesOutputWindow(self,[{str(j):str(k) for j,k in i.items()} for i in res]))
        
    
    def openNamespaceManager(self):
        if self.namespacemanager in self.windows:
            self.namespacemanager.show()
            self.namespacemanager.raise_()
            self.namespacemanager.activateWindow()
            self.namespacemanager.setFocus()
        else:
            self.namespacemanager=NamespaceManager(self,self.namespace)
            self.namespacemanager.show()
            self.windows.append(self.namespacemanager)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.close()
        sys.exit(0)

if __name__ == '__main__':
    app=QApplication(sys.argv)

    window=MainWindow()
    window.show()
    sys.exit(app.exec_())
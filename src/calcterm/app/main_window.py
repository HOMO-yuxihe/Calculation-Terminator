from keyword import iskeyword
import sys,time
from PyQt5.QtWidgets import (QMainWindow,
    QApplication,QWidget,QVBoxLayout,QHBoxLayout,
    QLabel,QTextEdit,QPushButton,QMenuBar,QAction,
    QDialog,QLineEdit,QMessageBox,QListView,QShortcut,
    QInputDialog
)
from PyQt5.QtCore import Qt,QModelIndex,QTimer
from PyQt5.QtGui import (
    QFont,QKeyEvent,QStandardItemModel,QStandardItem,
    QKeySequence
)
from qfluentwidgets import (
    FluentWindow,NavigationItemPosition,
    Theme,PushButton,FluentIcon  # 替换原生QPushButton为Fluent风格
)
import calcterm.core.calc as parser
from calcterm.widgets.common import MTextEdit,MultiLineEdit
from typing import List,Dict,Union

from keyword import iskeyword
import sys
from typing import List,Dict,Union

font1=QFont("Segoe UI",12)
fontdefault=QFont("Segoe UI",10)
font2=QFont("Consolas",14)

class Subwindow(QMainWindow):
    def __init__(self,parent):
        super().__init__()
        self.par=parent
    
    def closeEvent(self,event):
        self.par.closeSubwindow(self)
        return super().closeEvent(event)

class WithSubwindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.windows=[]

    def closeSubwindow(self,target:QMainWindow):
        self.windows.remove(target)
        target.close()
    
    def closeEvent(self,event):
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

        simplifyAction=QAction('化简 (Ctrl+S)')
        simplifyAction.setShortcut('Ctrl+S')
        simplifyAction.triggered.connect(self.simplify)
        evalAction=QAction('求值 (Ctrl+E)')
        evalAction.setShortcut('Ctrl+E')
        evalAction.triggered.connect(self.eval)
        self.closeShortcut=QShortcut(QKeySequence('Escape'),self)
        self.closeShortcut.activated.connect(self.close)
        self.display=MTextEdit([simplifyAction,evalAction],content,font=font2)
        self.display.setReadOnly(1)

        self.setCentralWidget(self.display)
        self.show()
    
    # def keyPressEvent(self,event):
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
        if self.id.text() in self.varIds and self.id.text() !=self.srcid:
            QMessageBox.warning(self,'错误','标识符已存在')
            return
        self.res={'id':self.id.text(),'name':self.name.text(),'assumptions':{}}
        self.accept()
    
    @staticmethod
    def get(parent,variable:parser.Variable={'id':'','name':'','assumptions':{}},variableList=[]):
        dialog=VariableModifier(parent,variable,variableList)
        result=dialog.exec_()
        return dialog.res,(result==QDialog.Accepted)

# 变量管理窗口（简化实现，保留原有逻辑）
class VariableManager(Subwindow):
    class _ListView(QListView):
        def __init__(self,parent):
            super().__init__()
            self.par=parent
        def keyPressEvent(self,event:QKeyEvent):
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

        self.list=self._ListView(self)
        self.list.setFont(font2)
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
    
#==========核心：拆分原Tab为独立的子界面==========
# 1. 代数/数值计算子界面（对应原calcTab）
class CalcInterface(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.par=parent
        self.init_ui()

    def init_ui(self):
        self.setFont(font1)
        self.layout_=QVBoxLayout(self)
        
        # 输入部分
        self.calc_inputTip=QLabel('输入表达式')
        self.calc_inputTip.setFont(font1)
        self.calc_inputTip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_.addWidget(self.calc_inputTip)
        
        self.calc_input=QTextEdit()
        self.calc_input.setFont(font2)
        self.layout_.addWidget(self.calc_input)

        
        # 替换为Fluent风格按钮
        self.calc_calc=PushButton('计算/执行')
        self.calc_calc.setFont(font1)
        # 保留原有点击逻辑（需自行实现calc方法）
        self.calc_calc.pressed.connect(self.calc)
        
        self.layout_.addWidget(self.calc_calc)
        self.setObjectName('Calculator')

    def calc(self):
        expr=self.calc_input.toPlainText()
        result=parser.calc(expr,self.par.variables)
        self.par.windows.append(OutputWindow(self.par,result))
        self.calc_calc.setDisabled(1)
        QTimer.singleShot(100,lambda:self.calc_calc.setDisabled(0))
        print(self.par.windows)
        print(self.par.variables)


# 2. 方程求解子界面（对应原eqalTab，简化占位）
class EqalInterface(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel("方程求解面板",alignment=Qt.AlignCenter))
        layout.addWidget(QTextEdit("输入方程...",font=font2))
        layout.addWidget(PushButton("求解方程"))
        self.setObjectName('Eqalities Solver')

# 3. 不等式求解子界面（对应原ineqalTab，简化占位）
class InequalInterface(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel("不等式求解面板",alignment=Qt.AlignCenter))
        layout.addWidget(QTextEdit("输入不等式...",font=font2))
        layout.addWidget(PushButton("求解不等式"))
        self.setObjectName('Inqalities Solver')

# 4. 拉格朗日乘数子界面（对应原lagrangeTab）
class LagrangeInterface(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.par=parent
        self.init_ui()

    def init_ui(self):
        self.setFont(font1)
        layout=QVBoxLayout(self)
        
        self.lagrange_limitsTip=QLabel('约束条件')
        self.lagrange_limitsTip.setFont(font1)
        self.lagrange_limitsTip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lagrange_limitsTip)
        
        self.lagrange_limitsInput=MultiLineEdit()
        self.lagrange_limitsInput.setFont(font2)
        layout.addWidget(self.lagrange_limitsInput,stretch=1)
        
        self.lagrange_targetTip=QLabel('目标函数')
        self.lagrange_targetTip.setFont(font1)
        self.lagrange_targetTip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lagrange_targetTip)
        
        self.lagrange_targetInput=QTextEdit()
        self.lagrange_targetInput.setFont(font2)
        layout.addWidget(self.lagrange_targetInput,stretch=1)
        
        # 替换为Fluent风格按钮
        self.lagrange_calc=PushButton('开始计算')
        self.lagrange_calc.setFont(font1)
        # 保留原有点击逻辑（需自行实现lagrange方法）
        self.lagrange_calc.pressed.connect(self.lagrange)
        layout.addWidget(self.lagrange_calc)
        self.setObjectName('Lagrange Solver')
    
    def lagrange(self):
        self.lagrange_calc.setDisabled(1)
        QTimer.singleShot(100,lambda:self.lagrange_calc.setDisabled(0))
        limits=[i.text().strip() for i in self.lagrange_limitsInput.lines if i.text().strip()]
        target=self.lagrange_targetInput.toPlainText()
        res=parser.lagrange(limits,target,self.par.variables)
        if isinstance(res,str):
            self.par.windows.append(OutputWindow(self.par,res))
        else:
            self.par.windows.append(OutputWindow(self.par,'\n'.join(map(str,res))))


#==========主窗口：FluentWindow + 侧边栏==========
class MainWindow(WithSubwindow):
    def __init__(self):
        super().__init__()
        # 基础窗口设置
        self.setWindowTitle("计算器")
        self.resize(800,600)
        self.setMinimumSize(400,400)
        # (Theme.LIGHT)  # 设置WinUI 3浅色主题
        self.setFont(font1)

        # 菜单栏（保留原有逻辑）
        # self.menubar=QMenuBar(self)
        # self.menubar.setFont(fontdefault)
        # self.setMenuBar(self.menubar)
        self.variables=[]
        self.variablemanager=VariableManager(self,self.variables)
        self.windows=[self.variablemanager]
        self.varMgmt=QShortcut(QKeySequence(Qt.Key_F3),self)
        self.varMgmt.activated.connect(self.openVariableManager)
        self.varMgmtopened=0
        # self.menubar.addAction(self.varMgmt)

        # 核心：添加侧边导航项（替代原QTabWidget）
        self.init_navigation()

    def init_navigation(self):
        # 1. 代数/数值计算（顶部导航）
        self.calc_interface=CalcInterface(self)
        self.addSubInterface(
            self.calc_interface,
            FluentIcon.CODE,
            "代数/数值计算",
            NavigationItemPosition.TOP
        )

        # 2. 方程求解
        self.eqal_interface=EqalInterface(self)
        self.addSubInterface(
            self.eqal_interface,
            FluentIcon.EDIT,
            "方程求解",
            NavigationItemPosition.TOP
        )

        # 3. 不等式求解
        self.inequal_interface=InequalInterface(self)
        self.addSubInterface(
            self.inequal_interface,
            FluentIcon.PAGE_LEFT,
            "不等式求解",
            NavigationItemPosition.TOP
        )

        # 4. 拉格朗日乘数
        self.lagrange_interface=LagrangeInterface(self)
        self.addSubInterface(
            self.lagrange_interface,
            FluentIcon.DEVELOPER_TOOLS,
            "拉格朗日乘数",
            NavigationItemPosition.TOP
        )

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

if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyle("Fusion")  # 兼容Fluent样式
    window=MainWindow()
    window.show()
    sys.exit(app.exec_())
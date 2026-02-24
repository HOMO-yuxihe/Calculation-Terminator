from keyword import iskeyword
import sys
sys.path.append('src')

from PyQt5.QtGui import QFont, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit, QListView, QMainWindow, QMessageBox,
                             QPushButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget)
from PyQt5.QtCore import QModelIndex, Qt

from calcterm.core.struct_template import *
from calcterm.app.config import *
from calcterm.core import calc as parser
from calcterm.widgets.common import *

typeIndex={
    'variable':'变量',
    'function':'函数',
    'lambda':'匿名函数'
}

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


class FunctionModifier(QDialog):
    def __init__(self,parent,variable:parser.UndefinedFunction={'id':'','name':'','assumptions':{}},variableList=[]):
        super().__init__(parent=parent)
        self.varIds=[i['id'] for i in variableList]
        self.setWindowTitle('修改函数')
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

        self.idTip=QLabel('函数标识符:')
        self.id=QLineEdit(variable['id'])
        self.srcid=variable['id']
        self.idLayout.addWidget(self.idTip)
        self.idLayout.addWidget(self.id)
        self.nameTip=QLabel('函数显示名:')
        self.name=QLineEdit(variable['name'])
        self.nameLayout.addWidget(self.nameTip)
        self.nameLayout.addWidget(self.name)
        self.addBtn=QPushButton('完成')
        self.addBtn.clicked.connect(self.mod)
        self.cancelBtn=QPushButton('取消')
        self.cancelBtn.clicked.connect(self.reject)
        self.exitLayout.addWidget(self.addBtn)
        self.exitLayout.addWidget(self.cancelBtn)
    
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
    def get(parent,variable:parser.UndefinedFunction={'id':'','name':'','assumptions':{}},variableList=[]):
        dialog=FunctionModifier(parent,variable,variableList)
        result=dialog.exec_()
        return dialog.res,(result==QDialog.Accepted)


class NamespaceManager(Subwindow):
    def __init__(self,parent,namespace:Namespace={'variables':[],'functions':[],'lambdas':[]}):
        super().__init__(parent)
        self.setWindowTitle('命名空间管理')
        self.resize(400,600)
        self.setMinimumSize(300,500)
        self.setFont(font1)
        self.namespace=namespace
        self.variablesModel=QStandardItemModel()
        self.functionsModel=QStandardItemModel()
        self.lambdasModel=QStandardItemModel()

        self.central=QWidget()
        self.setCentralWidget(self.central)
        self.main_layout=QVBoxLayout()
        self.central.setLayout(self.main_layout)

        self.variablesViewLayout=QHBoxLayout()
        self.variablesEditLayout=QVBoxLayout()
        self.variablesTip=QLabel('变量列表',alignment=Qt.AlignCenter)
        self.variablesList=QListView()
        self.variablesList.setModel(self.variablesModel)
        self.variablesList.clicked.connect(self.showVarInfo)
        self.variablesAdd=QPushButton('添加')
        self.variablesAdd.clicked.connect(self.varAdd)
        self.variablesEdit=QPushButton('修改')
        self.variablesEdit.clicked.connect(self.varEdit)
        self.variablesDelete=QPushButton('删除')
        self.variablesDelete.clicked.connect(self.varDelete)
        self.variablesInfo=QTextEdit()
        self.variablesInfo.setFixedWidth(150)

        self.main_layout.addWidget(self.variablesTip)
        self.main_layout.addLayout(self.variablesViewLayout)
        self.variablesViewLayout.addWidget(self.variablesList)
        self.variablesViewLayout.addLayout(self.variablesEditLayout)
        self.variablesEditLayout.addWidget(self.variablesAdd)
        self.variablesEditLayout.addWidget(self.variablesEdit)
        self.variablesEditLayout.addWidget(self.variablesDelete)
        self.variablesEditLayout.addWidget(self.variablesInfo)
        
        self.functionsViewLayout=QHBoxLayout()
        self.functionsEditLayout=QVBoxLayout()
        self.functionsTip=QLabel('函数列表',alignment=Qt.AlignCenter)
        self.functionsList=QListView()
        self.functionsList.setModel(self.functionsModel)
        self.functionsList.clicked.connect(self.showFuncInfo)
        self.functionsAdd=QPushButton('添加')
        self.functionsAdd.clicked.connect(self.funcAdd)
        self.functionsEdit=QPushButton('修改')
        self.functionsEdit.clicked.connect(self.funcEdit)
        self.functionsDelete=QPushButton('删除')
        self.functionsDelete.clicked.connect(self.funcDelete)
        self.functionsInfo=QTextEdit()
        self.functionsInfo.setFixedWidth(150)

        self.main_layout.addWidget(self.functionsTip)
        self.main_layout.addLayout(self.functionsViewLayout)
        self.functionsViewLayout.addWidget(self.functionsList)
        self.functionsViewLayout.addLayout(self.functionsEditLayout)
        self.functionsEditLayout.addWidget(self.functionsAdd)
        self.functionsEditLayout.addWidget(self.functionsEdit)
        self.functionsEditLayout.addWidget(self.functionsDelete)
        self.functionsEditLayout.addWidget(self.functionsInfo)
    
    def varAdd(self):
        res,ok=VariableModifier.get(self,variableList=self.namespace['variables'])
        if ok:
            self.namespace['variables'].append(res)
            self.refresh()
    
    def varEdit(self):
        model=self.variablesList.selectionModel()
        if indexes:=model.selectedIndexes():
            if (res:=VariableModifier.get(self,self.namespace['variables'][indexes[0].row()],self.namespace['variables']))[1]:
                self.namespace['variables'][indexes[0].row()]=res[0]
                self.variablesModel.setData(indexes[0],res[0]['id'])
                self.showVarInfo(indexes[0])
        else:
            QMessageBox.warning(self,'错误','请选中一个变量')

    def varDelete(self):
        model=self.variablesList.selectionModel()
        if indexes:=model.selectedIndexes():
            index=indexes[0].row()
            self.variablesModel.removeRow(index)
            self.namespace['variables'].pop(index)
            self.showVarInfo()
        else:
            QMessageBox.warning(self,'错误','请选中一个变量')
    
    def showVarInfo(self,index:QModelIndex=None):
        if index==None:
            if indexes:=self.variablesList.selectionModel().selectedIndexes():
                row=indexes[0].row()
            else:
                self.variablesInfo.clear()
                return
        else:
            row=index.row()
        var=self.namespace['variables'][row]
        self.variablesInfo.setPlainText(f"标识符: {var['id']}\n显示名: {var['name']}\n断言: {'无' if not var['assumptions'].items() else ','.join(f'{i}:{j}' for i,j in var['assumptions'].items())}")
    
    def funcAdd(self):
        res,ok=FunctionModifier.get(self,variableList=self.namespace['variables'])
        if ok:
            self.namespace['functions'].append(res)
            self.refresh()

    def funcEdit(self):
        model=self.functionsList.selectionModel()
        if indexes:=model.selectedIndexes():
            if (res:=FunctionModifier.get(self,self.namespace['functions'][indexes[0].row()],self.namespace['variables']))[1]:
                self.namespace['functions'][indexes[0].row()]=res[0]
                self.functionsModel.setData(indexes[0],res[0]['id'])
                self.showFuncInfo(indexes[0])
        else:
            QMessageBox.warning(self,'错误','请选中一个函数')
    
    def funcDelete(self):
        model=self.functionsList.selectionModel()
        if indexes:=model.selectedIndexes():
            index=indexes[0].row()
            self.functionsModel.removeRow(index)
            self.namespace['functions'].pop(index)
            self.showFuncInfo()
        else:
            QMessageBox.warning(self,'错误','请选中一个函数')
    
    def showFuncInfo(self,index:QModelIndex=None):
        if index==None:
            if indexes:=self.functionsList.selectionModel().selectedIndexes():
                row=indexes[0].row()
            else:
                self.functionsInfo.clear()
                return
        else:
            row=index.row()
        var=self.namespace['functions'][row]
        self.functionsInfo.setPlainText(f"标识符: {var['id']}\n显示名: {var['name']}\n断言: {'无' if not var['assumptions'].items() else ','.join(f'{i}:{j}' for i,j in var['assumptions'].items())}")

    
    def refresh(self):
        self.variablesModel.clear()
        self.functionsModel.clear()
        for i in self.namespace['variables']:
            self.variablesModel.appendRow(QStandardItem(i['id']))
        for i in self.namespace['functions']:
            self.functionsModel.appendRow(QStandardItem(i['id']))


if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app=QApplication(sys.argv)
    par=WithSubwindow()
    win=NamespaceManager(par)
    win.show()
    par.windows.append(win)
    sys.exit(app.exec_())
#!/usr/bin/python
#coding=utf-8
import os,glob,re

try:
    from PySide2 import QtGui
    from PySide2 import QtCore
    from PySide2 import QtUiTools
    from PySide2.QtGui import *
    from PySide2 import QtWidgets
    from PySide2.QtCore import Signal
except ImportError:
    from PySide import QtGui
    from PySide import QtCore
    from PySide import QtUiTools
    from PySide.QtGui import *
    from PySide import QtWidgets

currentPath = r"E:/work_ref/transferUE4/transferUE4"
uiPath = os.path.join(currentPath, "transferUE4.ui")
subUiPath = os.path.join(currentPath, "checkFiles.ui")
iconsPath = os.path.join(currentPath,"icons")
projPath = r"N:/projectServer"
assetPaths = ["production","asset"]
shotPaths = ["production","shot"]
#1功能错误。 2系统找不到指定的文件。3系统找不到指定的路径。4系统无法打开文件。 5拒绝访问 6句柄无效
errorIO = {"[Error 1]":"[功能错误]","[Error 2]":"[找不到文件]","[Error 3]":"[找不到路径]","[Error 4]":"[无法打开文件]","[Error 5]":"[拒绝访问]","[Error 6]":"[句柄无效]"}

#创建子窗口类
class ChildWindow(QtWidgets.QDialog):
    sub_Signal = Signal(list)
    def __init__(self):
        super(ChildWindow, self).__init__()
        #引入子窗口类
        self.uifile = subUiPath
        self.loader = self.loadUi()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.loader)
        self.setLayout(layout)
        self.icons = iconsPath
        self.loadIcon()
        self.setupConnect()
        self.setWindowTitle("确认导出多个文件")
        self.loader.listLW.reset()
        self.loader.listLW.clear()
        #self.loadItems()

    def get_data(self,childList):
        print(childList)
        self.childList = childList
        self.loadItems()
        return

    def loadUi(self):
        loader = QtUiTools.QUiLoader()
        strfile = QtCore.QFile(self.uifile)
        strfile.open(QtCore.QFile.ReadOnly)
        loadedUi = loader.load(strfile)
        strfile.close()
        return loadedUi

    def loadItems(self):
        self.loader.listLW.clear()
        for child in self.childList:
            item = QtWidgets.QListWidgetItem(child)
            item.setCheckState(QtCore.Qt.CheckState.Checked)
            item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
            self.loader.listLW.addItem(item)
    
    def loadIcon(self):
        iconDict = {'green_ok_24px_1075415_easyicon.net.png':self.loader.allCheckedBTN,
        'red_delete_24px_1075470_easyicon.net.png':self.loader.clearCheckedBTN,
        'selin_32.png':self.loader.insertCheckedBTN,
        'shot_32px.png':self.loader.sortBTN}
        buttonL = []
        for icon in iconDict.keys():
            img0 = QtGui.QImage(os.path.join(self.icons,icon)) # 这里图片路径可以不给格式：QtGui.QImage(r'd:/test')
            pixmap = QtGui.QPixmap(img0)
            fitPixmap = pixmap.scaled(16, 16, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)    #注意 scaled() 返回一个 QtGui.QPixmap
            #icon = QtGui.QIcon(fitPixmap)
            iconDict[icon].setIcon(QtGui.QIcon(fitPixmap))
            iconDict[icon].setIconSize(QtCore.QSize(16, 16))

    def sentToMain(self):
        checkedL = []
        count = self.loader.listLW.count()
        for i in range(count):
            if self.loader.listLW.item(i).checkState() == QtCore.Qt.CheckState.Checked:
                checkedL.append(self.loader.listLW.item(i).text())
        self.sub_Signal.emit(checkedL)
        return

    #:SIGNAL connect
    def setupConnect(self):
        self.loader.applyBTN.clicked.connect(self.apply)
        self.loader.cancelBTN.clicked.connect(self.close)
        self.loader.allCheckedBTN.clicked.connect(self.allCheck)
        self.loader.clearCheckedBTN.clicked.connect(self.clear)
        self.loader.insertCheckedBTN.clicked.connect(self.insert)
        self.loader.sortBTN.clicked.connect(self.sort)

    def apply(self):
        self.sentToMain()
        self.close()

    def sort(self):
        self.loader.listLW.sortItems()
        return

    def clear(self):
        count = self.loader.listLW.count()
        for i in range(count):
            self.loader.listLW.item(i).setCheckState(QtCore.Qt.CheckState.Unchecked)
        return

    def insert(self):
        count = self.loader.listLW.count()
        for i in range(count):
            if self.loader.listLW.item(i).checkState() == QtCore.Qt.CheckState.Checked:
                self.loader.listLW.item(i).setCheckState(QtCore.Qt.CheckState.Unchecked)
            else:
                self.loader.listLW.item(i).setCheckState(QtCore.Qt.CheckState.Checked)
        return

    def allCheck(self):
        count = self.loader.listLW.count()
        for i in range(count):
            self.loader.listLW.item(i).setCheckState(QtCore.Qt.CheckState.Checked)
        return
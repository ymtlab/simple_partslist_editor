# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.treeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.treeView.setObjectName("treeView")
        self.verticalLayout.addWidget(self.treeView)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 400, 27))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuImport = QtWidgets.QMenu(self.menuFile)
        self.menuImport.setObjectName("menuImport")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionAddChild = QtWidgets.QAction(MainWindow)
        self.actionAddChild.setObjectName("actionAddChild")
        self.actionDelete = QtWidgets.QAction(MainWindow)
        self.actionDelete.setObjectName("actionDelete")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionImportJSON = QtWidgets.QAction(MainWindow)
        self.actionImportJSON.setObjectName("actionImportJSON")
        self.actionImportCSV = QtWidgets.QAction(MainWindow)
        self.actionImportCSV.setObjectName("actionImportCSV")
        self.menuImport.addAction(self.actionImportJSON)
        self.menuImport.addAction(self.actionImportCSV)
        self.menuFile.addAction(self.menuImport.menuAction())
        self.menuFile.addAction(self.actionSave)
        self.menuEdit.addAction(self.actionAddChild)
        self.menuEdit.addAction(self.actionDelete)
        self.menuSettings.addAction(self.actionSettings)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuImport.setTitle(_translate("MainWindow", "Import"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionAddChild.setText(_translate("MainWindow", "Add child"))
        self.actionDelete.setText(_translate("MainWindow", "Delete"))
        self.actionSettings.setText(_translate("MainWindow", "Setting"))
        self.actionImportJSON.setText(_translate("MainWindow", "JSON"))
        self.actionImportCSV.setText(_translate("MainWindow", "CSV"))

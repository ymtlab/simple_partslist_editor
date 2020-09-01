# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from settings import Ui_Dialog
from model import Model
from item import Item
from delegate import Delegate
from column import Column

class Settings(QtWidgets.QDialog):
    def __init__(self, parent, columns):
        super().__init__(parent)
        
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = Model( self, Item(), Column() )
        self.ui.listView.setModel(self.model)
        self.ui.listView.setItemDelegate( Delegate() )
        self.ui.listView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listView.customContextMenuRequested.connect(self.context_menu)

        self.model.insertColumn(0)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, 'column')
        self.model.insertRows( 0, len(columns) )
        for row, column in enumerate(columns):
            index = self.model.index(row, 0)
            self.model.setData(index, column)

    def append(self):
        self.model.insertRow( self.model.rowCount() )

    def columns(self):
        result = self.exec()
        columns = [ item.data('column') for item in self.model.root().children() ]
        return (columns, result == QtWidgets.QDialog.Accepted)
        
    def context_menu(self, point):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('Add', self.append)
        self.menu.addAction('Delete', self.remove)
        self.menu.exec( self.focusWidget().mapToGlobal(point) )
        
    def remove(self):
        indexes = self.ui.listView.selectedIndexes()
        for index in indexes[::-1]:
            self.model.removeRow(index.row())

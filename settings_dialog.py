# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from settings import Ui_Dialog
from model import Model
from item import Item
from delegate import Delegate
from column import Column

class Settings(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = Model( self, Item(), Column() )
        self.ui.listView.setModel(self.model)
        self.ui.listView.setItemDelegate( Delegate() )
        self.ui.listView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listView.customContextMenuRequested.connect(self.context_menu)

        self.model.insertColumn(0)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, 'column')

        # get all columns from parent model
        all_columns = []
        def recursion(item):
            for key in item.data().keys():
                if not key in all_columns:
                    all_columns.append(key)
            for child in item.children():
                recursion(child)
        recursion(parent.model.root())

        # get shown columns at treeview
        column_list = range( parent.model.columnCount() )
        columns = [ parent.model.headerData(i, QtCore.Qt.Horizontal) for i in column_list ]

        self.model.insertRows( 0, len(all_columns) )

        selection_model = self.ui.listView.selectionModel()
        for row, column in enumerate(all_columns):
            index = self.model.index(row, 0)
            self.model.setData(index, column)

            if column in columns:
                selection_model.select(index, QtCore.QItemSelectionModel.Select)
        
        self.ui.lineEdit.setText( parent.partslist.get('key_column') )
        self.ui.lineEdit_2.setText( parent.partslist.get('quantity_column') )

    def accept(self):
        super().accept()

        #columns = [ item.data('column') for item in self.model.root().children() ]
        columns = [ self.model.data(index) for index in self.ui.listView.selectedIndexes() ]
        keys = [ self.ui.lineEdit.text(), self.ui.lineEdit_2.text() ]

        parent_model = self.parent.model
        partslist = self.parent.partslist

        parent_model.removeColumns(0, parent_model.columnCount())
        parent_model.insertColumns(0, len(columns))
        for i, column in enumerate(columns):
            parent_model.setHeaderData(i, QtCore.Qt.Horizontal, column)
        
        partslist['key_column'] = keys[0]
        partslist['quantity_column'] = keys[1]
        parent_model.quantities_key = partslist['quantity_column']

    def append(self):
        self.model.insertRow( self.model.rowCount() )

    def context_menu(self, point):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('Add', self.append)
        self.menu.addAction('Delete', self.remove)
        self.menu.exec( self.focusWidget().mapToGlobal(point) )
        
    def remove(self):
        indexes = self.ui.listView.selectedIndexes()
        for index in indexes[::-1]:
            self.model.removeRow(index.row())

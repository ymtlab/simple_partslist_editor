# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QModelIndex

class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent, root, columns):
        super(Model, self).__init__(parent)
        self.root = root
        self.columns = columns

    def columnCount(self, parent=QModelIndex()):
        return self.columns.count()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        
        if role == Qt.EditRole or role == Qt.DisplayRole:
            return self.item(index).data( self.columns.data(index.column()) )
        
        return QtCore.QVariant()

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, i, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns.data(i)
        
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return i + 1

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if parent == QModelIndex():
            return self.createIndex( row, column, self.root.child(row) )

        if parent.isValid():
            return self.createIndex( row, column, self.item(parent).child(row) )

        return QModelIndex()

    def insertColumn(self, start, column, parent=QModelIndex()):
        self.beginInsertColumns(parent, start, start)
        self.columns.insert(start, column)
        self.endInsertColumns()

    def insertColumns(self, start, columns, parent=QModelIndex()):
        self.beginInsertColumns(parent, start, start + len(columns) - 1)
        self.columns.insert(start, columns)
        self.endInsertColumns()

    def insertRow(self, start, item, parent=QModelIndex()):
        self.beginInsertRows(parent, start, start)
        self.item(parent).insert(start, item)
        self.endInsertRows()

    def insertRows(self, start, items, parent=QModelIndex()):
        self.beginInsertRows(parent, start, start + len(items) - 1)
        self.item(parent).insert(start, items)
        self.endInsertRows()

    def item(self, index):
        if index == QModelIndex():
            return self.root
        elif index.isValid():
            return index.internalPointer()
        return QModelIndex()
        
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        
        if self.item(index).parent == self.root:
            return QModelIndex()
        
        return self.createIndex(self.item(index).parent.row(), 0, self.item(index).parent)

    def removeColumn(self, column, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column)
        self.columns.remove(column, column)
        self.endRemoveColumns()

    def removeColumns(self, column, count, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column + count - 1)
        self.columns.remove(column, column + count)
        self.endRemoveColumns()

    def removeRow(self, row, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        self.item(parent).remove(row)
        self.endRemoveRows()

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self.item(parent).remove(row, row + count)
        self.endRemoveRows()

    def rowCount(self, parent=QModelIndex()):
        return self.item(parent).child_count()

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self.item(index).data( self.columns.data(index.column()), value )
            return True
        return False

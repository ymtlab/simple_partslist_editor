# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
 
class Item(object):
    def __init__(self, parent_item=None, dictionary={}):
        self._dict = dictionary
        self._parent_item = parent_item
        self._children = []

    def child(self, row):
        if row > len(self._children):
            return QtCore.QModelIndex()
        return self._children[row]

    def children(self):
        return self._children

    def childCount(self):
        return len(self._children)

    def data(self, column):
        if column in self._dict:
            return self._dict[column]
        return ''

    def insertChildren(self, items, row):
        self._children[row:row] = items

    def parent(self):
        return self._parent_item
        
    def removeChildren(self, start, end):
        del self._children[start:end]

    def row(self):
        if self._parent_item:
            return self._parent_item._children.index(self)
        return 0

    def set_data(self, column, data):
        self._dict[column] = data

    def set_dict(self, _dict):
        self._dict = _dict

class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent_=None):
        super(Model, self).__init__(parent_)
        self.root_item = Item(QtCore.QModelIndex())
        self._columns = []

    def columns(self):
        return self._columns

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._columns)

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            item = index.internalPointer()
            return item.data( self._columns[index.column()] )
        return QtCore.QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, i, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._columns[i]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return i + 1
 
    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QtCore.QModelIndex()
 
    def insertColumns(self, start_column, columns, parent=QtCore.QModelIndex()):
        self.beginInsertColumns( parent, start_column, start_column + len(columns) - 1 )
        self._columns[ start_column : start_column + len(columns) - 1 ] = columns
        self.endInsertColumns()

    def insertRows(self, start_row, count, parent=QtCore.QModelIndex()):
        if parent == QtCore.QModelIndex():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        items = [ Item(parent_item, {}) for i in range(count) ]
        self.beginInsertRows(parent, start_row, start_row + count - 1)
        parent_item.insertChildren(items, start_row)
        self.endInsertRows()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        child_item = index.internalPointer()
        parent_item = child_item.parent()
        if parent_item == self.root_item:
            return QtCore.QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)
        
    def removeColumns(self, column, count, parent=QtCore.QModelIndex()):
        self.beginRemoveColumns(parent, column, column + count - 1)
        del self._columns[column : column + count]
        self.endRemoveColumns()

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        self.beginRemoveRows(parent, row, row + count - 1)
        parent_item.removeChildren(row, row + count)
        self.endRemoveRows()
 
    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            parentItem = self.root_item
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            index.internalPointer().set_data( self._columns[index.column()], value )
            return True
        return False
 
class Delegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, setModelDataEvent=None):
        super(Delegate, self).__init__(parent)
        self.setModelDataEvent = setModelDataEvent
 
    def createEditor(self, parent, option, index):
        return QtWidgets.QLineEdit(parent)
 
    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(str(value))
 
    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())
        if not self.setModelDataEvent is None:
            self.setModelDataEvent()

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QModelIndex, QVariant

class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent, root, columns):
        super(Model, self).__init__(parent)
        self.__root__ = root
        self.columns = columns
        self.mimeTypeString = 'application/vnd.treeviewdragdrop.list'

    def all_emit(self):
        def recursion(item):
            for column in range(len(item.data().keys())):
                index = self.createIndex(item.row(), column, item)
                self.dataChanged.emit(index, index)
        self.dataChanged.emit(QModelIndex(), QModelIndex())
        for child in self.__root__.children():
            recursion(child)

    def canDropMimeData(self, data, action, row, column, parent):
        if not data.hasFormat(self.mimeTypeString):
            return False

        if column > 0:
            return False
        
        if self.rowCount() <= 0:
            return False

        if row < 0:
            return False

        return True

    def columnCount(self, parent=QModelIndex()):
        return self.columns.count()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        if role == Qt.EditRole or role == Qt.DisplayRole:
            return self.item(index).data( self.columns.data(index.column()) )
        
        return QVariant()

    def dropMimeData(self, data, action, row, column, parent):

        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        if action == Qt.IgnoreAction:
            return True
        
        beginRow = 0
        if row != -1:
            beginRow = row
        elif parent.isValid():
            beginRow = parent.row()
        else:
            beginRow = self.rowCount(parent)

        encoded_data = data.data(self.mimeTypeString)
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.ReadOnly)
        source_items = []
        while not stream.atEnd():
            variant = QtCore.QVariant()
            stream >> variant
            source_items.append( variant.value() )

        self.insertRows(beginRow, len(source_items), parent)

        parent_children = parent.internalPointer().children()
        parent_item = parent.internalPointer()
        for i, source_item in enumerate(source_items):
            parent_children[beginRow + i] = source_item.copy(parent_item)

        return True

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return Qt.ItemIsEnabled

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns.data(section)
        
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if parent == QModelIndex():
            return self.createIndex( row, column, self.__root__.child(row) )

        if parent.isValid():
            return self.createIndex( row, column, self.item(parent).child(row) )

        return QModelIndex()

    def insertColumn(self, column, parent=QModelIndex()):
        self.beginInsertColumns(parent, column, column)
        self.columns.insert(column, 1)
        self.endInsertColumns()
        return True

    def insertColumns(self, column, count, parent=QModelIndex()):
        self.beginInsertColumns(parent, column, column + count - 1)
        self.columns.insert(column, count)
        self.endInsertColumns()
        return True

    def insertRow(self, row, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row)
        self.item(parent).insert(row, 1)
        self.endInsertRows()
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        self.item(parent).insert(row, count)
        self.endInsertRows()
        return True

    def item(self, index):
        if index == QModelIndex():
            return self.__root__
        elif index.isValid():
            return index.internalPointer()
        return QModelIndex()
        
    def mimeTypes(self):
        return [self.mimeTypeString]

    def mimeData(self, indexes):
        mimedata = QtCore.QMimeData()
        encoded_data = QtCore.QByteArray()
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.WriteOnly)
        for index in indexes:
            stream << QtCore.QVariant( index.internalPointer() )
        mimedata.setData(self.mimeTypeString, encoded_data)
        return mimedata

    def moveRow(self, sourceParent, sourceRow, destinationParent, destinationChild):
        self.beginMoveRows(sourceParent, sourceRow, sourceRow, destinationParent, destinationChild)
        self.item(sourceParent).insert(sourceRow, 1)
        self.item(destinationParent).remove(destinationChild, 1)
        self.endMoveRows()

    def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):
        self.beginMoveRows(sourceParent, sourceRow, sourceRow+count-1, destinationParent, destinationChild)
        self.item(sourceParent).insert(sourceRow, count)
        self.item(destinationParent).remove(destinationChild, count)
        self.endMoveRows()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        
        if self.item(index).parent() == self.__root__:
            return QModelIndex()
        
        return self.createIndex(index.row(), 0, self.item(index).parent())

    def removeColumn(self, column, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column)
        self.columns.remove(column, 1)
        self.endRemoveColumns()

    def removeColumns(self, column, count, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column + count - 1)
        self.columns.remove(column, count)
        self.endRemoveColumns()

    def removeRow(self, row, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        self.item(parent).remove(row, 1)
        self.endRemoveRows()

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self.item(parent).remove(row, count)
        self.endRemoveRows()

    def rowCount(self, parent=QModelIndex()):
        return self.item(parent).child_count()

    def root(self, item=None):
        if item is None:
            return self.__root__
        self.__root__ = item

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self.item(index).data( self.columns.data(index.column()), value )
            return True
        return False

    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
        if orientation==Qt.Horizontal and role==Qt.EditRole:
            self.columns.data(section, value)
        return True

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

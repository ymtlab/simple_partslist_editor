# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QModelIndex, QVariant

class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent, root, columns):
        super(Model, self).__init__(parent)
        self.__root__ = root
        self.columns = columns
        self.mimeTypeString = 'application/vnd.treeviewdragdrop.list'

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
        
        destinationChild = 0
        if not row == -1:
            destinationChild = row
        elif parent.isValid():
            destinationChild = parent.row()
        else:
            destinationChild = self.rowCount(parent)

        encoded_data = data.data(self.mimeTypeString)
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.ReadOnly)

        mime_datas = []
        while not stream.atEnd():
            variant = QtCore.QVariant()
            stream >> variant
            mime_datas.append( variant.value() )

        for parent_rows in mime_datas:
            sourceParent = self.parent_rows_to_index(parent_rows).parent()
            sourceRow = parent_rows[-1]
            self.moveRow(sourceParent, sourceRow, parent, destinationChild)

        return True

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
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
        self.insertColumns(column, 1, parent)

    def insertColumns(self, column, count, parent=QModelIndex()):
        self.beginInsertColumns(parent, column, column + count - 1)
        self.columns.insert(column, count)
        self.endInsertColumns()

    def insertRow(self, row, parent=QModelIndex()):
        self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        self.item(parent).insert(row, count)
        self.endInsertRows()

    def item(self, index):
        if index == QModelIndex() or index is None:
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
        for item in set([ index.internalPointer() for index in indexes ]):
            stream << QtCore.QVariant(item.parent_rows())
        mimedata.setData(self.mimeTypeString, encoded_data)
        return mimedata

    def moveRow(self, sourceParent, sourceRow, destinationParent, destinationChild):
        self.moveRows(sourceParent, sourceRow, 1, destinationParent, destinationChild)

    def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):

        insert_row = destinationChild
        source_rows = sourceParent.internalPointer().parent_rows()
        destin_rows = destinationParent.internalPointer().parent_rows()

        if source_rows == destin_rows:
            sourceParent = destinationParent
            s_parent_item = self.item(destinationParent)
            if sourceRow < destinationChild:
                insert_row = insert_row - count
        else:
            s_parent_item = self.parent_rows_to_item(source_rows)

        d_parent_item = self.item(destinationParent)

        item_datas = []
        for item in s_parent_item.children(sourceRow, count):
            item_datas.append([ item.data(), item.children() ])

        self.beginMoveRows(sourceParent, sourceRow, sourceRow+count-1, destinationParent, destinationChild)

        s_parent_item.remove(sourceRow, count)
        d_parent_item.insert(insert_row, count)

        for i, item_data in enumerate(item_datas):
            d_parent_item.child(insert_row + i).data(item_data[0])
            children = [ child.copy( d_parent_item.child(insert_row + i) ) for child in item_data[1] ]
            d_parent_item.child(insert_row + i).children(children)

        self.endMoveRows()
        return True

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        item = self.item(index)
        if item.parent() == self.__root__:
            return QModelIndex()
        return self.createIndex(index.row(), 0, self.item(index).parent())

    def parent_rows(self, item):
        def recursion(item2):
            if item2 is None:
                return
            rows.append( item2.row() )
            recursion( item2.parent() )
        rows = []
        recursion(item)
        return rows[:-1][::-1]

    def parent_rows_to_index(self, rows):
        item = self.root()
        for row in rows:
            item = item.child(row)
        index = self.createIndex(rows[-1], 0, item)
        return index

    def parent_rows_to_item(self, rows):
        item = self.root()
        for row in rows:
            item = item.child(row)
        return item

    def removeColumn(self, column, parent=QModelIndex()):
        self.removeColumns(column, 1, parent)

    def removeColumns(self, column, count, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column + count - 1)
        self.columns.remove(column, count)
        self.endRemoveColumns()

    def removeRow(self, row, parent=QModelIndex()):
        self.removeRows(row, 1, parent)

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

    def search_item(self, target_item, source_item):
        if source_item.same(target_item):
            return source_item
        for child in source_item.children():
            return self.search_item(target_item, child)
        return None

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

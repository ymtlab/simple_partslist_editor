# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QModelIndex, QVariant

class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent, root, columns):
        super(Model, self).__init__(parent)
        self.__root__ = root
        self.__columns__ = columns
        self.mimeTypeString = 'application/vnd.treeviewdragdrop.list'
        self.quantities_title = 'quantity'

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
        return self.__columns__.count()

    def columns(self):
        return self.__columns__

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if role == Qt.EditRole or role == Qt.DisplayRole:

            if index == QModelIndex():
                item = self.__root__
            else:
                item = index.internalPointer()
            
            if self.__columns__.data(index.column()) == self.quantities_title:
                return item.quantity()
            else:
                return item.data( self.__columns__.data(index.column()) )
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

            item = self.__root__.child(parent_rows)
            index = self.createIndex(parent_rows[-1], 0, item)
            sourceParent = index.parent()

            sourceRow = parent_rows[-1]
            self.moveRow(sourceParent, sourceRow, parent, destinationChild)

        return True

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return Qt.NoItemFlags

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.__columns__.data(section)
        
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1

        return None
        
    def index(self, row, column, parent=QModelIndex()):
        if not parent.isValid() or parent == QModelIndex():
            parent_item = self.__root__
        else:
            parent_item = parent.internalPointer()
        
        child_item = parent_item.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def insertColumn(self, column, parent=QModelIndex()):
        self.insertColumns(column, 1, parent)

    def insertColumns(self, column, count, parent=QModelIndex()):
        self.beginInsertColumns(parent, column, column + count - 1)
        self.__columns__.insert(column, count)
        self.endInsertColumns()

    def insertRow(self, row, parent=QModelIndex()):
        self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        if parent == QModelIndex():
            item = self.__root__
        else:
            item = parent.internalPointer()
        item.insert(row, count)
        self.endInsertRows()

    def mimeTypes(self):
        return [self.mimeTypeString]

    def mimeData(self, indexes):
        mimedata = QtCore.QMimeData()
        encoded_data = QtCore.QByteArray()
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.WriteOnly)
        for item in set([ index.internalPointer() for index in indexes ]):
            stream << QtCore.QVariant( item.parent_rows() )
        mimedata.setData(self.mimeTypeString, encoded_data)
        return mimedata

    def moveRow(self, sourceParent, sourceRow, destinationParent, destinationChild):
        self.moveRows(sourceParent, sourceRow, 1, destinationParent, destinationChild)

    def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):

        if destinationParent == QModelIndex():
            s_parent_item = self.__root__
        else:
            s_parent_item = sourceParent.internalPointer()
        
        if sourceParent == QModelIndex():
            d_parent_item = self.__root__
        else:
            d_parent_item = destinationParent.internalPointer()
        
        insert_row = destinationChild
        if s_parent_item == d_parent_item:
            if sourceRow < destinationChild:
                insert_row = insert_row - count

        items = s_parent_item.children(sourceRow, count)

        self.beginMoveRows(sourceParent, sourceRow, sourceRow+count-1, destinationParent, destinationChild)

        s_parent_item.remove(sourceRow, count)
        d_parent_item.insert(insert_row, count)

        for i, item in enumerate(items):
            d_parent_item.child(insert_row + i).data( item.data() )
            d_parent_item.child(insert_row + i).children(
                [c.copy( d_parent_item.child(insert_row + i) ) for c in item.children()]
            )
            d_parent_item.child(insert_row + i).quantities( item.quantities() )

        self.endMoveRows()
        return True

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        item = index.internalPointer()
        parent = item.parent()
        if parent == self.__root__:
            return QModelIndex()
        return self.createIndex( parent.row(), 0, parent )

    def removeColumn(self, column, parent=QModelIndex()):
        self.removeColumns(column, 1, parent)

    def removeColumns(self, column, count, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column + count - 1)
        self.__columns__.remove(column, count)
        self.endRemoveColumns()

    def removeRow(self, row, parent=QModelIndex()):
        self.removeRows(row, 1, parent)

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        if parent == QModelIndex():
            item = self.__root__
        else:
            item = parent.internalPointer()
        item.remove(row, count)
        self.endRemoveRows()

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            parent_item = self.__root__
        else:
            parent_item = parent.internalPointer()
        return parent_item.child_count()

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

            if index == QModelIndex():
                item = self.__root__
            else:
                item = index.internalPointer()

            if self.__columns__.data(index.column()) == self.quantities_title:
                try:
                    item.quantity( int(value) )
                except:
                    return False
            else:
                item.data( self.__columns__.data(index.column()), value )
            return True
        return False

    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
        if orientation==Qt.Horizontal and role==Qt.EditRole:
            self.__columns__.data(section, value)
            return True
        return False

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

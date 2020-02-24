import json
import sys
from mainwindow import Ui_MainWindow
from settings import Ui_Dialog
from treeview import Model, Delegate, Item
from PyQt5 import QtWidgets, QtCore

class Settings(QtWidgets.QDialog):
    def __init__(self, parent, columns):
        super().__init__(parent)
        
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = Model(self)
        self.model.insertColumns(0, ['column'])
        self.ui.listView.setModel(self.model)
        self.ui.listView.setItemDelegate(Delegate())
        self.ui.listView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listView.customContextMenuRequested.connect(self.contextMenu)

        for column in columns:
            self.model.insertRows(self.model.root_item.childCount(), 1)
            child_item = self.model.root_item.child(-1)
            child_item.set_data('column', column)

    def add_item(self):
        self.model.insertRows(self.model.root_item.childCount(), 1)

    def columns(self):
        result = self.exec()
        data = self.model.data
        index = self.model.index
        columns = [ data(index(r, 0, QtCore.QModelIndex())) for r in range(self.model.rowCount()) ]
        return (columns, result == QtWidgets.QDialog.Accepted)
        
    def contextMenu(self, point):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('Add', self.add_item)
        self.menu.addAction('Delete', self.delete_item)
        self.menu.exec_( self.focusWidget().mapToGlobal(point) )
        
    def delete_item(self):
        indexes = self.ui.listView.selectedIndexes()
        for index in indexes:
            self.model.removeItem(index)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model = Model(self)

        self.ui.treeView.setModel(self.model)
        self.ui.treeView.setItemDelegate(Delegate())
        self.ui.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.contextMenu)

        self.ui.actionAddChild.triggered.connect(self.add_child)
        self.ui.actionDelete.triggered.connect(self.delete_item)
        self.ui.actionOpen.triggered.connect(self.open_json)
        self.ui.actionSave.triggered.connect(self.save_json)
        self.ui.actionSettings.triggered.connect(self.show_settings_dialog)

    def show_settings_dialog(self):
        columns, result = Settings(self, self.model.columns()).columns()
        if not result:
            return
        self.model.removeColumns(0, self.model.columnCount())
        self.model.insertColumns(0, columns)

    def open_json(self, filename):

        def recursion(_part, _parent_index, _parts):
            _dict = { key:_part[key] for key in _part if not 'parts' == key }
            parent_item = _parent_index.internalPointer()
            if parent_item is None:
                parent_item = self.model.root_item
            self.model.insertRows(parent_item.childCount(), 1, _parent_index)
            child_item = parent_item.child(-1)
            child_item.set_dict(_dict)
            if 'parts' in _part:
                index = self.model.createIndex(parent_item.childCount(), 0, child_item)
                children = _part['parts']
                for child in children:
                    recursion(child, index, parts)
        
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Save file', '', 'JSON File (*.json)')
        if not filename[0]:
            return
        
        json_data = json.load( open(filename[0]) )
        self.model.removeColumns(0, self.model.columnCount())
        self.model.removeRows(0, self.model.root_item.childCount())
        self.model.insertColumns(0, json_data['columns'])

        parts = json_data['parts']
        for part in parts:
            recursion(part, QtCore.QModelIndex(), parts)
        
    def save_json(self):

        def recursion(parent):
            _dict1 = parent.dict
            if parent.childCount()==0:
                _dict1['parts'] = [ recursion(child) for child in parent.children() ]
            return _dict1
        
        parts = []
        for child in self.model.root_item.children():
            parts.append( recursion(child) )
        
        parts = {'columns':self.model.columns, 'parts':parts}

        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '', 'JSON File (*.json)')
        if filename[0]:
            json.dump(parts, open(filename[0],'w'), indent=4)

    def contextMenu(self, point):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('Add child', self.add_child)
        self.menu.addAction('Delete', self.delete_item)
        self.menu.exec_( self.focusWidget().mapToGlobal(point) )
 
    def add_child(self):
        indexes = self.ui.treeView.selectedIndexes()
        
        if len(indexes) == 0:
            self.model.insertRows(self.model.root_item.childCount(), 1, QtCore.QModelIndex())
            return
        
        indexes2 = []
        for index in indexes:
            if not index.row() in [ i.row() for i in indexes2 if i.parent() == index.parent() ]:
                indexes2.append(index)
        
        for index in indexes2:
            item = index.internalPointer()
            self.model.insertRows(item.childCount() + 1, 1, index)

    def delete_item(self):
        indexes = self.ui.treeView.selectedIndexes()

        if len(indexes) == 0:
            return

        indexes2 = []
        for index in indexes:
            if not index.row() in [ i.row() for i in indexes2 if i.parent() == index.parent() ]:
                indexes2.append(index)
        
        for index in indexes2:
            self.model.removeRows(index.row(), 1, index.parent())

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec_()
 
if __name__ == '__main__':
    main()

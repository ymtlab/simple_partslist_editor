# -*- coding: utf-8 -*-
import sys

from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui

from mainwindow import Ui_MainWindow
from model import Model
from item import Item
from delegate import Delegate
from column import Column
from settings_dialog import Settings
from importer_json import ImporterJson
from csv_importer_dialog import CSVimporterDialog

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model = Model( self, Item(), Column() )

        self.ui.treeView.setModel(self.model)
        self.ui.treeView.setItemDelegate(Delegate())
        self.ui.treeView.customContextMenuRequested.connect(self.contextMenu)

        self.ui.actionAppendChild.triggered.connect(self.append_child)
        self.ui.actionDelete.triggered.connect(self.remove)
        self.ui.actionImportJSON.triggered.connect(self.import_json)
        self.ui.actionImportCSV.triggered.connect(self.import_csv)
        self.ui.actionExportJSON.triggered.connect(self.export_json)
        self.ui.actionExportCSV.triggered.connect(self.export_csv)
        self.ui.actionSettings.triggered.connect(self.show_settings_dialog)
        self.ui.actionOpen.triggered.connect(self.open)
        self.ui.actionSave.triggered.connect(self.save)

        self.ui.toolButton.clicked.connect(self.append_child)
        self.ui.toolButton_2.clicked.connect(self.remove)
        self.ui.toolButton_3.clicked.connect(self.ui.treeView.expandAll)

        self.ui.treeView.clicked.connect(self.tree_view_clicked)

        self.partslist = {
            'root_item':self.model.root(), 
            'pixmaps':{}, 
            'key_column':'part number'
        }

    def append_child(self):
        indexes = self.ui.treeView.selectedIndexes()
        if len(indexes) == 0:
            self.model.insertRow(1)
            return
        for index in indexes[::-1]:
            self.model.insertRow(1, index)

    def contextMenu(self, point):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('Append child', self.append_child)
        self.menu.addAction('Remove', self.remove)
        self.menu.addAction('Copy', self.copy)
        self.menu.addAction('Paste', self.paste)
        self.menu.addAction('Sum quantity with duplication parts', self.sum_quantity_with_duplication_parts)
        self.menu.addAction('test', self.test)
        self.menu.exec( self.focusWidget().mapToGlobal(point) )

    def copy(self):
        clipboard = QtWidgets.QApplication.clipboard()
        mimedata = QtCore.QMimeData()
        encoded_data = QtCore.QByteArray()
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.WriteOnly)

        indexes = self.ui.treeView.selectedIndexes()
        setted_items = set([index.internalPointer() for index in indexes])
        for item in setted_items:
            stream << QtCore.QVariant(item)
        mimedata.setData(self.model.mimeTypeString, encoded_data)

        clipboard.setMimeData(mimedata)

    def export_csv(self):
        dialog = CSVimporterDialog(self, self.model)
        dialog.save()

    def export_json(self):
        importer_json = ImporterJson(self, self.model)
        importer_json.save()

    def import_csv(self):
        dialog = CSVimporterDialog(self, self.model, self.partslist)
        dialog.exec()
        self.ui.comboBox.addItems(self.model.columns().data())
        self.ui.comboBox.setCurrentText(self.partslist['key_column'])

    def import_json(self):
        importer_json = ImporterJson(self, self.model)
        importer_json.open()

    def open(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'DAT File (*.dat)')
        if not filename[0]:
            return

        if self.model.columnCount() > 0:
            self.model.removeColumns( 0, self.model.columnCount() )
        
        if self.model.rowCount() > 0:
            self.model.removeRows( 0, self.model.root().child_count() )
        
        # open binary to root item of model
        data = {}
        with open(filename[0], 'rb') as f:
            byte_array = QtCore.QByteArray( f.read() )
            stream = QtCore.QDataStream(byte_array, QtCore.QIODevice.ReadOnly)
            variant = QtCore.QVariant()
            stream >> variant
            data = variant.value()

        # set partslist
        for key in self.partslist:
            if key in data.keys():
                self.partslist[key] = data[key]
        
        # set root item
        self.model.root( self.partslist['root_item'] )

        # set columns
        columns = list(self.model.root().child(0).data().keys())
        self.model.insertColumns(0, len(columns))
        for i, column in enumerate(columns):
            self.model.setHeaderData(i, QtCore.Qt.Horizontal, column)
            
        # combox
        self.ui.comboBox.addItems(columns)

    def paste(self):
        clipboard = QtWidgets.QApplication.clipboard()
        mime_data = clipboard.mimeData()

        encoded_data = mime_data.data(self.model.mimeTypeString)
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.ReadOnly)

        items = []
        while not stream.atEnd():
            variant = QtCore.QVariant()
            stream >> variant
            items.append( variant.value() )

        indexes = self.ui.treeView.selectedIndexes()
        if len(indexes) < 1:
            return
        
        index = indexes[0]
        for r, item in enumerate(items):
            row = index.row() + 1 + r
            self.model.insertRow( row, index.parent() )
            inserted_item = index.parent().internalPointer().child(row)
            children = inserted_item.children()
            self.model.insertRows( row, len(children), index.parent() )
            for r2, child in enumerate(children):
                inserted_item.child( r2, child.copy(inserted_item) )
            inserted_item.data( item.data() )
            inserted_item.quantities( item.quantities() )

    def remove(self):
        for index in self.ui.treeView.selectedIndexes()[::-1]:
            self.model.removeRow(index.row(), index.parent())
            
    def save(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save DAT file', '', 'DAT File (*.dat)')
        if not filename[0]:
            return
        self.partslist['key_column'] = self.ui.comboBox.currentText()
        byte_array = QtCore.QByteArray()
        stream = QtCore.QDataStream(byte_array, QtCore.QIODevice.WriteOnly)
        stream << QtCore.QVariant( self.partslist )
        with open(filename[0], 'wb') as f:
            f.write(byte_array)

    def show_settings_dialog(self):
        
        column_list = range( self.model.columnCount() )
        columns = [ self.model.headerData(i, QtCore.Qt.Horizontal) for i in column_list ]
        columns, result = Settings(self, columns).columns()

        if not result:
            return
        
        self.model.removeColumns(0, self.model.columnCount())
        self.model.insertColumns(0, len(columns))
        for i, column in enumerate(columns):
            self.model.setHeaderData(i, QtCore.Qt.Horizontal, column)

    def sum_quantity_with_duplication_parts(self):
        indexes = self.ui.treeView.selectedIndexes()
        setted_items = set([index.internalPointer() for index in indexes])
        key_column = self.ui.comboBox.currentText()

        for item in setted_items:

            # sum quantity
            delete_rows = []
            quantities = {}
            for row, child in enumerate(item.children()):
                key = child.data(key_column)
                if not key in quantities.keys():
                    quantities[key] = 0
                else:
                    delete_rows.append(row)
                quantities[key] += int( child.quantity() )

            # delete children
            for row in delete_rows[::-1]:
                index = self.model.createIndex(row, 0, item)
                self.model.removeRow(row, index)

            # set quantities
            sorted_quantities = [ quantities[c.data(key_column)] for c in item.children() ]
            item.quantities(sorted_quantities)

    def test(self):
        indexes = self.ui.treeView.selectedIndexes()
        for index in indexes:
            print( index.internalPointer().quantities() )
            print( index.internalPointer().quantity() )
            print( index.internalPointer().row() )

    def tree_ctrl_c(self, model, selectedIndexes):
        preRow = selectedIndexes[0].internalPointer().row()
        text = ''
        
        for selectedIndex in selectedIndexes:
            row = selectedIndex.row()
            #column = selectedIndex.column()
            #selectedItem = selectedIndex.internalPointer()
            
            if not row == preRow:
                text = text[:-1]
                text = text + '\n'
            
            text = text + str(model.data(selectedIndex)) + '\t'
            preRow = row
        
        text = text[:-1]
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)
        
    def tree_view_clicked(self, index):
        item = index.internalPointer()
        key_column = self.ui.comboBox.currentText()
        search_name = item.data(key_column)
        if not search_name in self.partslist['pixmaps']:
            return
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap( QtGui.QPixmap( self.partslist['pixmaps'][search_name] ) )
        self.ui.graphicsView.setScene(scene)
        self.ui.graphicsView.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()
 
if __name__ == '__main__':
    main()

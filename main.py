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
from importer_csv_dialog import ImporterCSV
from importer_image import importer_image

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
        self.ui.actionDelete.triggered.connect(self.remove_items)
        self.ui.actionImportJSON.triggered.connect( lambda : ImporterJson(self).open() )
        self.ui.actionImportCSV.triggered.connect( lambda : ImporterCSV(self).exec() )
        self.ui.actionExportJSON.triggered.connect( lambda : ImporterJson(self).save() )
        self.ui.actionExportCSV.triggered.connect( lambda : ImporterCSV(self).save() )
        self.ui.actionSettings.triggered.connect( lambda : Settings(self).exec() )
        self.ui.actionOpen.triggered.connect(self.open)
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionImpoertImage.triggered.connect( lambda : importer_image(self) )
        
        self.ui.toolButton.clicked.connect(self.append_child)
        self.ui.toolButton_2.clicked.connect(self.remove_items)
        self.ui.toolButton_3.clicked.connect(self.ui.treeView.expandAll)
        self.ui.toolButton_4.clicked.connect(self.search_and_replace)

        self.ui.treeView.clicked.connect(self.tree_view_clicked)

        self.partslist = {
            'root_item':self.model.root(), 
            'pixmaps':{}, 
            'key_column':None,
            'quantity_column':None
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
        
        edit_data_menu = QtWidgets.QMenu('Edit data', self)
        edit_data_menu.addAction('Copy data', self.copy_datas)
        edit_data_menu.addAction('Paste data', self.paste_datas)
        edit_data_menu.addAction('Input text to selected indexes', self.input_text_to_selectedindexes)
        self.menu.addMenu(edit_data_menu)

        edit_item_menu = QtWidgets.QMenu('Edit item', self)
        edit_item_menu.addAction('Append child', self.append_child)
        edit_item_menu.addAction('Remove item', self.remove_items)
        edit_item_menu.addAction('Copy item', self.copy_items)
        edit_item_menu.addAction('Paste item', self.paste_items)
        self.menu.addMenu(edit_item_menu)
        
        sum_menu = QtWidgets.QMenu('Sum', self)
        sum_menu.addAction('Sum quantity with duplication parts', self.sum_quantity_with_duplication_parts)
        sum_menu.addAction('Sum quantity with duplication parts recursion', self.sum_quantity_with_duplication_parts_recursion)
        self.menu.addMenu(sum_menu)

        test_menu = QtWidgets.QMenu('Test', self)
        test_menu.addAction('test', self.test)
        test_menu.addAction('parent', self.print_parent)
        test_menu.addAction('root children', self.root_children)
        self.menu.addMenu(test_menu)

        self.menu.exec( self.focusWidget().mapToGlobal(point) )

    def copy_datas(self):

        indexes = self.ui.treeView.selectedIndexes()
        first_index = indexes[0]
        last_parent_item = first_index.internalPointer().parent()
        last_row = first_index.row()
        datas = [ [self.model.data(first_index)] ]

        for index in indexes[1:]:
            
            parent_item = index.internalPointer().parent()

            if parent_item is last_parent_item and index.row() == last_row:
                datas[-1].append(self.model.data(index))
                continue

            if not parent_item is last_parent_item:
                last_parent_item = index.internalPointer().parent()

            if not index.row() is last_row:
                last_row = index.row()

            datas.append([self.model.data(index)])
        
        text = '\n'.join(
            [ '\t'.join([ cell for cell in row ]) for row in datas ]
        )

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)
        
    def copy_items(self):

        items = []
        for index in self.ui.treeView.selectedIndexes():
            item = index.internalPointer()
            if not item in items:
                items.append(item)

        encoded_data = QtCore.QByteArray()
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.WriteOnly)
        for item in items:
            stream << QtCore.QVariant( item.parent_rows() )
        
        mimedata = QtCore.QMimeData()
        mimedata.setData('application/x-qabstractitemmodeldatalist', encoded_data)
        QtWidgets.QApplication.clipboard().setMimeData(mimedata)

    def input_text_to_selectedindexes(self):

        text, ok = QtWidgets.QInputDialog().getText(
            self, "Input text dialog",
            "Input text", QtWidgets.QLineEdit.Normal,
            "text"
            )
        
        if ok and text:
            for index in self.ui.treeView.selectedIndexes():
                self.model.setData(index, text)

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
        columns = list( self.model.root().child(0).data().keys() )
        self.model.insertColumns( 0, len(columns) )
        for i, column in enumerate(columns):
            self.model.setHeaderData(i, QtCore.Qt.Horizontal, column)
        
        self.model.quantities_key = self.partslist['quantity_column']

    def paste_datas(self):
        clipboard = QtWidgets.QApplication.clipboard()
        datas = [ [t for t in row.split('\t')] for row in clipboard.text().strip().splitlines() ]

        indexes = self.ui.treeView.selectedIndexes()

        if len(indexes) == 0:
            return
        
        selected_index = indexes[0]
        selected_item_parent = selected_index.internalPointer().parent()
        start_row = selected_index.row()
        start_column = selected_index.column()
        max_column = self.model.columnCount()
        max_row = selected_item_parent.child_count()

        for r, data in enumerate(datas):
            r2 = start_row + r
            input_item = selected_item_parent.child(r2)
            for c, d in enumerate(data):
                c2 = start_column + c
                if c2 > max_column:
                    continue
                if r2 > max_row:
                    return
                index = self.model.createIndex(r2, c2, input_item)
                self.model.setData(index, d)

    def paste_items(self):
        mime_data = QtWidgets.QApplication.clipboard().mimeData()
        encoded_data = mime_data.data('application/x-qabstractitemmodeldatalist')
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.ReadOnly)

        data = []
        while not stream.atEnd():
            variant = QtCore.QVariant()
            stream >> variant
            data.append( variant.value() )

        for item in data:
            print(item)

    def print_parent(self):
        for index in self.ui.treeView.selectedIndexes():
            print(index.internalPoitner().data(self.partslist['key_column']))
        
    def remove_items(self):
        for index in self.ui.treeView.selectedIndexes()[::-1]:
            self.model.removeRow(index.row(), index.parent())
            
    def root_children(self):
        print([ c.data('品番') for c in self.model.root().children() ])

    def save(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save DAT file', '', 'DAT File (*.dat)')
        if not filename[0]:
            return
        
        # get all columns
        columns = []
        def recursion(item):
            columns.extend( list(item.data().keys()) )
            for child in item.children():
                recursion(child)
        recursion(self.model.root())
        columns = list(set(columns))
        self.partslist['all_columns'] = columns
        self.partslist['columns'] = self.model.columns().data()

        byte_array = QtCore.QByteArray()
        stream = QtCore.QDataStream(byte_array, QtCore.QIODevice.WriteOnly)
        stream << QtCore.QVariant( self.partslist )
        with open(filename[0], 'wb') as f:
            f.write(byte_array)

    def search_and_replace(self):

        def recursion(item, search_text, replace_text, is_perfect_matching, search_column):
            data = item.data()
            for key in data:
                text = data[key]
                if is_perfect_matching:
                    if text == search_text:
                        data[key] = replace_text
                else:
                    data[key] = text.replace(search_text, replace_text)
            for child in item.children():
                recursion(child, search_text, replace_text, is_perfect_matching, search_column)

        search_column = self.ui.comboBox.currentText()
        search_text = self.ui.lineEdit.text()
        replace_text = self.ui.lineEdit_2.text()

        if self.ui.comboBox_2.currentText() == 'Perfect matching':
            is_perfect_matching = True
        else:
            is_perfect_matching = False
        
        recursion( self.model.root(), search_text, replace_text, is_perfect_matching, search_column )

    def sum_quantity_with_duplication_parts(self):
        indexes = self.ui.treeView.selectedIndexes()
        setted_items = set([ index.internalPointer() for index in indexes ])
        key_column = self.partslist['key_column']

        for item in setted_items:
            
            parent_index = self.model.createIndex(item.row(), 0, item)

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
                self.model.removeRow(row, parent_index)

            # set quantities
            sorted_quantities = [ quantities[c.data(key_column)] for c in item.children() ]
            item.quantities(sorted_quantities)

    def sum_quantity_with_duplication_parts_recursion(self):
        def recursion(item):

            parent_index = self.model.createIndex(item.row(), 0, item)

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
                self.model.removeRow(row, parent_index)

            # set quantities
            sorted_quantities = [ quantities[c.data(key_column)] for c in item.children() ]
            item.quantities(sorted_quantities)

            for child in item.children():
                recursion(child)

        indexes = self.ui.treeView.selectedIndexes()
        setted_items = set([ index.internalPointer() for index in indexes ])
        key_column = self.partslist['key_column']

        for item in setted_items:
            recursion(item)

    def test(self):
        indexes = self.ui.treeView.selectedIndexes()
        for index in indexes:
            item = index.internalPointer()
            print('quantities')
            print( item.quantities() )
            print('quantity')
            print( item.quantity() )
            print('row')
            print( item.row() )

    def tree_view_clicked(self, index):
        item = index.internalPointer()
        search_name = item.data( self.partslist['key_column'] )
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

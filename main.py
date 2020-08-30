# -*- coding: utf-8 -*-
import csv
import json
import sys
from PyQt5 import QtWidgets, QtCore
from mainwindow import Ui_MainWindow
from model import Model
from item import Item
from delegate import Delegate
from column import Column
from settings_dialog import Settings
from importer_json import ImporterJson
from importer_csv import ImporterCSV

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model = Model( self, Item(), Column() )
        self.importer_json = ImporterJson(self.model)
        self.importer_csv = ImporterCSV(self.model)

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
        self.menu.addAction('parent rows', self.parent_rows)
        self.menu.exec( self.focusWidget().mapToGlobal(point) )
 
    def import_csv(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'CSV File (*.csv)')
        if filename[0]:
            self.importer_csv.open(filename[0])

    def import_json(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'JSON File (*.json)')
        if filename[0]:
            self.importer_json.open(filename[0])

    def remove(self):
        for index in self.ui.treeView.selectedIndexes()[::-1]:
            self.model.removeRow(index.row(), index.parent())

    def export_json(self):
        data = self.importer_json.save()
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save JSON file', '', 'JSON File (*.json)')
        if filename[0]:
            json.dump(data, open(filename[0],'w'), indent=4)

    def export_csv(self):
        data = self.importer_csv.save()
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save CSV file', '', 'CSV File (*.csv)')
        if filename[0]:
            with open(filename[0], 'w', newline='') as f:
                writer = csv.DictWriter(f, data[0].keys())
                writer.writeheader()
                for row in data:
                    writer.writerow(row)

    def open(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'DAT File (*.dat)')
        if not filename[0]:
            return

        if self.model.columnCount() > 0:
            self.model.removeColumns(0, self.model.columnCount())
        
        if self.model.rowCount() > 0:
            self.model.removeRows(0, self.model.root().child_count())
        
        with open(filename[0], 'rb') as f:
            byte_array = QtCore.QByteArray( f.read() )
            stream = QtCore.QDataStream(byte_array, QtCore.QIODevice.ReadOnly)
            variant = QtCore.QVariant()
            stream >> variant
            self.model.root( variant.value() )

        columns = self.model.root().child(0).data().keys()
        self.model.insertColumns(0, len(columns))
        for i, column in enumerate(columns):
            self.model.setHeaderData(i, QtCore.Qt.Horizontal, column)
        
        def recursion(item):
            index1 = self.model.createIndex(item.row(), 0, item)
            index2 = self.model.createIndex(item.row(), len(item.data()), item)
            self.model.dataChanged.emit(index1, index2)
            for child in item.children():
                recursion(child)
        recursion(self.model.root())

    def parent_rows(self):
        indexes = self.ui.treeView.selectedIndexes()
        for index in indexes:
            print( self.model.parent_rows(index.internalPointer()) )

    def save(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save DAT file', '', 'DAT File (*.dat)')
        if not filename[0]:
            return
        byte_array = QtCore.QByteArray()
        stream = QtCore.QDataStream(byte_array, QtCore.QIODevice.WriteOnly)
        stream << QtCore.QVariant( self.model.root() )

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

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()
 
if __name__ == '__main__':
    main()

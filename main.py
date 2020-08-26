# -*- coding: utf-8 -*-
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
        self.ui.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.contextMenu)

        self.ui.actionAddChild.triggered.connect(self.append_child)
        self.ui.actionDelete.triggered.connect(self.remove)
        self.ui.actionImportJSON.triggered.connect(self.import_json)
        self.ui.actionImportCSV.triggered.connect(self.import_csv)
        self.ui.actionSave.triggered.connect(self.save_json)
        self.ui.actionSettings.triggered.connect(self.show_settings_dialog)

    def append_child(self):
        for index in self.ui.treeView.selectedIndexes()[::-1]:
            self.model.insertRow(
                self.model.item(index).child_count(), 
                Item( {}, index.internalPointer() ), 
                index
            )

    def contextMenu(self, point):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('Append child', self.append_child)
        self.menu.addAction('Remove', self.remove)
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

    def save_json(self):
        data = self.importer_json.save()
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '', 'JSON File (*.json)')
        if filename[0]:
            json.dump(data, open(filename[0],'w'), indent=4)

    def show_settings_dialog(self):
        columns, result = Settings(self, self.model.columns.all()).columns()
        if not result:
            return
        self.model.removeColumns(0, self.model.columnCount())
        self.model.insertColumns(0, columns)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()
 
if __name__ == '__main__':
    main()

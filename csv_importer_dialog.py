# -*- coding: utf-8 -*-
import csv
import sys

from chardet.universaldetector import UniversalDetector
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui

from column import Column
from csv_importer import Ui_Dialog
from delegate import Delegate
from item import Item
from model import Model

class CSVimporterDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, parent_model=None, partslist=None):
        super().__init__(parent)
        
        self.__parent__ = parent
        self.parent_model = parent_model
        self.partslist = partslist
        self.rank_title = 'rank'
        self.quantities_title = 'quantity'
        self.dicts = None

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # list view
        self.model_rank = Model( self, Item(), Column() )
        self.ui.listView.setModel(self.model_rank)
        self.ui.listView.setItemDelegate( Delegate() )

        # list view 2
        self.model_quantity = Model( self, Item(), Column() )
        self.ui.listView_2.setModel(self.model_quantity)
        self.ui.listView_2.setItemDelegate( Delegate() )

        # list view 2
        self.model_key_column = Model( self, Item(), Column() )
        self.ui.listView_3.setModel(self.model_key_column)
        self.ui.listView_3.setItemDelegate( Delegate() )

        # table view
        self.model_csv = Model( self, Item(), Column() )
        self.ui.tableView.setModel(self.model_csv)
        self.ui.tableView.setItemDelegate( Delegate() )

        self.ui.pushButton.clicked.connect(self.open_file)

    def accept(self):
        super().accept()
        self.dicts_to_parent_model()

    def check_encoding(self, file_path):
        detector = UniversalDetector()
        with open(file_path, mode='rb') as f:
            for binary in f:
                detector.feed(binary)
                if detector.done:
                    break
        detector.close()
        return detector.result['encoding']

    def dicts_to_parent_model(self):

        model = self.parent_model
        dicts = self.dicts

        if model is None or dicts is None:
            return

        # get titles
        indexes = self.ui.listView.selectedIndexes()
        if len(indexes) > 0:
            self.rank_title = self.model_rank.data( indexes[0] )

        indexes = self.ui.listView_2.selectedIndexes()
        if len(indexes) > 0:
            self.quantities_title = self.model_quantity.data( indexes[0] )

        indexes = self.ui.listView_3.selectedIndexes()
        if len(indexes) > 0:
            self.partslist['key_column'] = self.model_key_column.data( indexes[0] )

        if self.rank_title is None:
            return
        
        # delete columns and rows
        if model.columnCount() > 0:
            model.removeColumns( 0, model.columnCount() )
        if model.rowCount() > 0:
            model.removeRows( 0, model.root().child_count() )
        
        # input columns
        columns = list( dicts[0].keys() )
        model.insertColumns( 0, len(columns) )
        for i, column in enumerate(columns):
            model.setHeaderData(i, QtCore.Qt.Horizontal, column)

        # input rows
        def recursion1(item, rank):
            if int( item.data(self.rank_title) ) == rank:
                return item
            return recursion1(item.parent(), rank)
        model.insertRow( model.rowCount() )
        index = model.index(model.rowCount()-1, 0)
        last = index.internalPointer()
        last.data( dicts[0] )

        for part in dicts[1:]:

            rank = int( part[self.rank_title] )
            rank_deff = int( last.data(self.rank_title) ) - rank

            if rank_deff < 0:
                parent = model.createIndex(last.row(), 0, last)
                row = last.child_count()
                model.insertRow(row, parent)
                last = last.child(-1)
            else:
                parent = recursion1(last, rank - 1 )
                row = parent.child_count()
                parent_index = model.createIndex(parent.row(), 0, parent)
                model.insertRow(row, parent_index)
                last = parent.child(-1)

            last.quantity( part.pop(self.quantities_title) )
            last.data(part)

        # remove rank column and data
        def recursion2(item):
            if self.rank_title in item.data().keys():
                item.delete(self.rank_title)
            for child in item.children():
                recursion2(child)
        column = model.columns().data().index(self.rank_title)
        model.removeColumn(column)
        recursion2( model.root() )
    
    def open_file(self):

        ret = QtWidgets.QFileDialog.getOpenFileName(self.__parent__, 'Open file', '', 'CSV File (*.csv)')
        if not ret[0]:
            return
        filename = ret[0]

        # read file
        self.ui.lineEdit.setText( str(filename) )
        encode = self.check_encoding(filename)
        with open(filename, encoding=encode) as f:
            self.dicts = [ d for d in csv.DictReader(f) ]
        
        # reset models
        models = [self.model_csv, self.model_key_column, self.model_quantity, self.model_rank]
        for model in models:
            if model.columnCount() > 0:
                model.removeColumns( 0, model.columnCount() )
            if model.rowCount() > 0:
                model.removeRows( 0, model.root().child_count() )

        # input columns
        columns = list( self.dicts[0].keys() )
        for model in [self.model_key_column, self.model_quantity, self.model_rank]:
            model.insertColumn(0)
            model.setHeaderData(0, QtCore.Qt.Horizontal, 'column')
            model.insertRows( 0, len(columns) )
            for row, value in enumerate(columns):
                model.setData( model.index(row, 0), value )

        # input csv model
        self.model_csv.insertColumns( 0, len(columns) )
        for section, column in enumerate(columns):
            self.model_csv.setHeaderData(section, QtCore.Qt.Horizontal, column)

        self.model_csv.insertRows( 0, len(self.dicts) )
        for row, data in enumerate(self.dicts):
            for column, key in enumerate(data):
                index = self.model_csv.index(row, column)
                self.model_csv.setData( index, data[key] )

    def save(self):

        def recursion(parent, data):
            data.append( parent.data() )
            for child in parent.children():
                recursion(child, data)
        
        data = []
        for child in self.parent_model.root().children():
            recursion(child, data)
        
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save CSV file', '', 'CSV File (*.csv)')
        if filename[0]:
            with open(filename[0], 'w', newline='') as f:
                writer = csv.DictWriter(f, data[0].keys())
                writer.writeheader()
                for row in data:
                    writer.writerow(row)

def main():
    app = QtWidgets.QApplication(sys.argv)
    model = Model(None, Item(), Column())
    dialog = CSVimporterDialog(None, model)
    dialog.exec()

if __name__ == '__main__':
    main()

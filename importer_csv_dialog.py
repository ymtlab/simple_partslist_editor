# -*- coding: utf-8 -*-
import csv
import sys

from chardet.universaldetector import UniversalDetector
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui

from column import Column
from importer_csv import Ui_Dialog
from delegate import Delegate
from item import Item
from model import Model

class ImporterCSV(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.__parent__ = parent
        self.parent_model = parent.model
        self.partslist = parent.partslist
        self.rank_title = 'rank'
        self.quantities_key = 'quantity'
        self.key_column = 'key'

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

        # list view 3
        self.model_key = Model( self, Item(), Column() )
        self.ui.listView_3.setModel(self.model_key)
        self.ui.listView_3.setItemDelegate( Delegate() )

        # table view
        self.model_csv = Model( self, Item(), Column() )
        self.ui.tableView.setModel(self.model_csv)
        self.ui.tableView.setItemDelegate( Delegate() )

        self.ui.pushButton.clicked.connect(self.open_file)

    def accept(self):
        super().accept()

        # get titles
        indexes = self.ui.listView.selectedIndexes()
        if len(indexes) > 0:
            self.rank_column = self.model_rank.data( indexes[0] )
        indexes = self.ui.listView_2.selectedIndexes()
        if len(indexes) > 0:
            self.quantity_column = self.model_quantity.data( indexes[0] )
        indexes = self.ui.listView_3.selectedIndexes()
        if len(indexes) > 0:
            self.key_column = self.model_key.data( indexes[0] )

        if self.rank_title is None:
            return
        
        # csv to item
        item = self.csv_to_item(self.ui.lineEdit.text(), self.rank_column, self.quantity_column)

        # set item to parent item
        model = self.parent_model
        def recursion(csv_item, parent_index, parent_item):
            model.insertRow(parent_item.child_count(), parent_index)
            inserted_item = parent_item.child(-1)
            inserted_item.data( csv_item.data() )
            parent_index2 = model.createIndex(inserted_item.row(), 0, inserted_item)
            for child in csv_item.children():
                recursion(child, parent_index2, inserted_item)
        recursion( item, QtCore.QModelIndex(), model.root() )

        if self.partslist['key_column'] is None:
            self.partslist['key_column'] = self.key_column
        
        if self.partslist['quantity_column'] is None:
            self.partslist['quantity_column'] = self.quantity_column
        
        columns = self.parent_model.columns().data()
        for column in item.data().keys():
            if not column in columns:
                self.parent_model.columns().append(column)
        
    def check_encoding(self, file_path):
        detector = UniversalDetector()
        with open(file_path, mode='rb') as f:
            for binary in f:
                detector.feed(binary)
                if detector.done:
                    break
        detector.close()
        return detector.result['encoding']

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
        models = [self.model_csv, self.model_quantity, self.model_rank, self.model_key]
        for model in models:
            if model.columnCount() > 0:
                model.removeColumns( 0, model.columnCount() )
            if model.rowCount() > 0:
                model.removeRows( 0, model.root().child_count() )

        # input columns
        columns = list( self.dicts[0].keys() )
        for model in [self.model_quantity, self.model_rank, self.model_key]:
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

    def csv_to_item(self, filepath, rank_column, quantity_column):

        # read file
        encode = self.check_encoding(filepath)
        with open(filepath, encoding=encode) as f:
            dicts = [ d for d in csv.DictReader(f) ]
        
        # input rows
        def recursion1(item, rank):
            if int( item.data(rank_column) ) == rank:
                return item
            return recursion1(item.parent(), rank)
        
        # first row to root item
        root_item = Item(None)
        root_item.data( dicts[0] )
        last = root_item

        # second row to last
        for part in dicts[1:]:

            rank = int( part[rank_column] )
            rank_deff = int( last.data(rank_column) ) - rank

            if rank_deff < 0:
                parent = last
            else:
                parent = recursion1(last, rank - 1 )
            
            parent.append()
            last = parent.child(-1)
            q = int( part.pop(quantity_column) )
            last.quantity(q)
            last.data(part)

        # remove rank column and data
        def recursion2(item):
            if rank_column in item.data().keys():
                item.delete(rank_column)
            for child in item.children():
                recursion2(child)
        recursion2( root_item )

        return root_item
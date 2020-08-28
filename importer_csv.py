# -*- coding: utf-8 -*-
import csv
from PyQt5 import QtCore

class ImporterCSV():
    def __init__(self, model):
        self.model = model
        self.rank_title = 'rank'

    def open(self, filename):

        with open(filename) as f:
            dicts = [ d for d in csv.DictReader(f) ]
        
        if self.model.columnCount() > 0:
            self.model.removeColumns(0, self.model.columnCount())
        
        if self.model.rowCount() > 0:
            self.model.removeRows(0, self.model.root().child_count())
        
        columns = list( dicts[0].keys() )
        self.model.insertColumns(0, len(columns))
        for i, column in enumerate(columns):
            self.model.setHeaderData(i, QtCore.Qt.Horizontal, column)

        self.model.insertRow( self.model.rowCount() )
        index = self.model.index(self.model.rowCount(), 0)
        last = self.model.item(index).child(-1)
        last.data(dicts[0])

        for part in dicts[1:]:

            rank = int( part[self.rank_title] )
            rank_deff = int( last.data(self.rank_title) ) - rank

            if rank_deff < 0:
                parent = self.model.createIndex(last.row(), 0, last)
                row = last.child_count()
                self.model.insertRow(row, parent)
                last = last.child(-1)
                last.data(part)
            else:
                parent = self.parent(last, rank - 1 )
                row = parent.child_count()
                parent_index = self.model.createIndex(parent.row(), 0, parent)
                self.model.insertRow(row, parent_index)
                last = parent.child(-1)
                last.data(part)

    def parent(self, item, rank):
        if int( item.data(self.rank_title) ) == rank:
            return item
        return self.parent(item.parent(), rank)

    def save(self):

        def recursion(parent, data):
            data.append( parent.data() )
            for child in parent.children():
                recursion(child, data)
        
        data = []
        for child in self.model.root().children():
            recursion(child, data)
        
        return data

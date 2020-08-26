# -*- coding: utf-8 -*-
import csv
from item import Item

class ImporterCSV():
    def __init__(self, model):
        self.model = model
        self.rank_title = 'rank'

    def open(self, filename):

        with open(filename) as f:
            dicts = [ d for d in csv.DictReader(f) ]
        
        if self.model.columns.count() > 0:
            self.model.removeColumns(0, self.model.columnCount())
        
        if self.model.rowCount() > 0:
            self.model.removeRows(0, self.model.root.child_count())
        
        self.model.insertColumns( 0, list(dicts[0].keys()) )

        self.model.insertRow( self.model.rowCount(), Item(dicts[0], self.model.root) )

        last = self.model.root.child(-1)

        for part in dicts[1:]:

            rank = int( part[self.rank_title] )
            rank_deff = int( last.data(self.rank_title) ) - rank

            if rank_deff < 0:
                item = Item(part, last)
                parent = self.model.createIndex(last.row(), 0, last)
                row = last.child_count()
                self.model.insertRow(row, item, parent)
                last = last.child(-1)
            else:
                parent = self.parent(last, rank - 1 )
                item = Item(part, parent)
                row = parent.child_count()
                parent_index = self.model.createIndex(item.parent.row(), 0, parent)
                self.model.insertRow(row, item, parent_index)
                last = parent.child(-1)

    def parent(self, item, rank):
        if int( item.data(self.rank_title) ) == rank:
            return item
        return self.parent(item.parent, rank)

    def save(self):

        def recursion(parent):
            data = { 'data' : parent.dict }
            if parent.child_count() > 0:
                data['parts'] = [ recursion(child) for child in parent.children ]
            return data
        
        parts = []
        for child in self.model.root.children:
            parts.append( recursion(child) )
        
        return {'columns':self.model.columns.all(), 'parts':parts}

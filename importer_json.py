# -*- coding: utf-8 -*-
import json
from item import Item

class ImporterJson():
    def __init__(self, model):
        self.model = model

    def open(self, filename):

        def recursion(part, parent=None):
            
            if parent is None:
                self.model.insertRow(
                    self.model.rowCount(),
                    Item(part['data'], self.model.root)
                )
                parent = self.model.root.child(-1)
            else:
                self.model.insertRow(
                    parent.child_count(),
                    Item(part['data'], parent), 
                    self.model.createIndex(parent.row(), 0, parent)
                )
                parent = parent.child(-1)
            
            if 'parts' in part.keys():
                for part in part['parts']:
                    recursion(part, parent)
        
        with open(filename) as f:
            json_data = json.load(f)
        
        if self.model.columns.count() > 0:
            self.model.removeColumns(0, self.model.columnCount())
        
        if self.model.rowCount() > 0:
            self.model.removeRows(0, self.model.root.child_count())
        
        self.model.insertColumns(0, json_data['columns'])

        for part in json_data['parts']:
            recursion(part)

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

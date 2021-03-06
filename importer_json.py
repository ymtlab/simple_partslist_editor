# -*- coding: utf-8 -*-
import json
from PyQt5 import QtCore, QtWidgets

class ImporterJson():
    def __init__(self, parent):
        self.parent = parent
        self.model = parent.model
        self.quantities_key = 'quantities'
        
    def open(self):

        filename = QtWidgets.QFileDialog.getOpenFileName(self.parent, 'Open file', '', 'JSON File (*.json)')
        if not filename[0]:
            return

        def recursion(part, item=None):
            if item is None:
                self.model.insertRow( self.model.rowCount() )
                index = self.model.index(self.model.rowCount(), 0)
            else:
                index = self.model.createIndex(item.row(), 0, item)
                self.model.insertRow( self.model.rowCount(), index )
                index = self.model.createIndex(item.row(), 0, item)
            
            parent = self.model.item(index).child(-1)
            parent.data(part['data'])

            if 'parts' in part.keys():
                for part in part['parts']:
                    recursion(part, parent)
        
        with open(filename[0]) as f:
            json_data = json.load(f)
        
        if self.model.columnCount() > 0:
            self.model.removeColumns(0, self.model.columnCount())
        
        if self.model.rowCount() > 0:
            self.model.removeRows(0, self.model.root().child_count())
        
        columns = json_data['columns']
        self.model.insertColumns(0, len(columns))
        for i, column in enumerate(columns):
            self.model.setHeaderData(i, QtCore.Qt.Horizontal, column)

        for part in json_data['parts']:
            recursion(part)

    def save(self):

        def recursion(parent):
            data = { 'data' : parent.data() }
            if parent.child_count() > 0:
                data['parts'] = [ recursion(child) for child in parent.children() ]
            return data
        
        parts = []
        for child in self.model.root().children():
            parts.append( recursion(child) )
        
        data = {'columns' : self.model.columns().data(), 'parts' : parts}
        
        filename = QtWidgets.QFileDialog.getSaveFileName(self.parent, 'Save JSON file', '', 'JSON File (*.json)')
        if filename[0]:
            json.dump(data, open(filename[0],'w'), indent=4)

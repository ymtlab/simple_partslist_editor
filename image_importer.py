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

    def open_folder(self):
        foldername = QtWidgets.QFileDialog.getExistingDirectory(self.__parent__, 'Open file', '')
        if foldername is None:
            return
        self.ui.lineEdit_2.setText(foldername)
        
    def dict_to_pixmaps(self):
        items = self.parent_model.root().unique_children()

        key_column = self.listview_select_index(self.ui.listView_3, 'key_column')
        if key_column is None:
            key_column = 'part number'
        search_folder = Path('images')
        images = {}
        
        for item in items:
            search_name = item.data(key_column)
            files = search_folder.glob('**/' + search_name + '.*')
            files = list(files)
            if len(files) < 1:
                continue
            f = files[0]
            images[f.stem] = QtGui.QPixmap( str(f) )
        
        self.partslist['pixmaps'] = images

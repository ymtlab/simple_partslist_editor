# -*- coding: utf-8 -*-
from pathlib import Path
from PyQt5 import QtWidgets, QtGui

def importer_image(parent):

    model = parent.model
    key_column = parent.partslist['key_column']
    
    foldername = QtWidgets.QFileDialog.getExistingDirectory(parent, 'Open file', '')

    if foldername is None:
        return
    
    items = model.root().unique_children()
    search_folder = Path(foldername)
    images = {}

    for item in items:

        search_name = item.data(key_column)
        files = search_folder.glob('**/' + search_name + '.*')
        files = list(files)

        if len(files) < 1:
            continue
        
        f = files[0]
        images[f.stem] = QtGui.QPixmap( str(f) )
    
    parent.partslist['pixmaps'] = images

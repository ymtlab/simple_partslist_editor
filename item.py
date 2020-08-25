# -*- coding: utf-8 -*-

class Item(object):
    def __init__(self, dict={}, parent=None):
        self.dict = dict
        self.parent = parent
        self.children = []
        self.quantities = []

    def append(self, child, quantity=1):
        self.children.append(child)
        self.quantities.append(quantity)

    def child(self, row):
        return self.children[row]

    def child_count(self):
        return len(self.children)

    def data(self, key, data=None):
        if data is None:
            return self.dict.get(key)
        self.dict[key] = data

    def extend(self, children, quantities=None):
        self.children.extend(children)
        if quantities is None:
            quantities = [ 1 for i in range(len(children))]
        self.quantities.extend(quantities)

    def insert(self, row, children, quantities=None):
        if type(children) is list:
            self.children[row:row] = children
            if quantities is None:
                quantities = [ 1 for i in range(len(children))]
            self.quantities[row:row] = quantities
        else:
            self.children.insert(row, children)
            if quantities is None:
                quantities = 1
            self.quantities.insert(row, quantities)

    def remove(self, start, end=None):
        if end is None:
            del self.children[start]
            del self.quantities[start]
            return
        del self.children[start:end]
        del self.quantities[start:end]

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

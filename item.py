# -*- coding: utf-8 -*-
from collections import OrderedDict

class Item(object):
    def __init__(self, parent=None):
        self.__data__ = {}
        self.__parent__ = parent
        self.__children__ = []
        self.__quantities__ = []

    def append(self, quantity=1):
        self.__children__.append( Item(self) )
        self.__quantities__.append(quantity)

    def copy(self, parent=None):
        item = Item(parent)
        item.data( { key:self.__data__[key] for key in self.__data__ } )
        item.children( [ c.copy(item) for c in self.__children__ ] )
        item.quantities( [ q for q in self.__quantities__ ] )
        return item
        
    def child(self, row, item=None):

        if type(row) is list:
            child = self
            for r in row:
                child = child.child(r)
            return child

        if item is None:
            return self.__children__[row]

        if type(item) is Item:
            self.__children__[row] = item
            return

        return self.__children__[row]

    def child_count(self):
        return len(self.__children__)

    def children(self, row=None, count=None):
        if row is None:
            return self.__children__

        if type(row) is list:
            self.__children__ = row
            return

        return self.__children__[row:row+count]

    def data(self, key=None, value=None):
        if key is None:
            return self.__data__

        if type(key) is dict or type(key) is OrderedDict:
            self.__data__ = key
            return

        if value is None:
            return self.__data__.get(key)

        self.__data__[key] = value

    def delete(self, key):
        del self.__data__[key]

    def extend(self, children, quantities=None):
        self.__children__.extend(children)
        if quantities is None:
            quantities = [ 1 for i in range(len(children)) ]
        self.__quantities__.extend(quantities)

    def insert(self, row, count=1):
        self.__children__[row:row] = [ Item(self) for i in range(count) ]
        self.__quantities__[row:row] = [ 1 for i in range(count) ]

    def move(self, row, count, destination):
        d = self.__children__[row:row+count]
        q = self.__quantities__[row:row+count]
        del self.__children__[row:row+count]
        del self.__quantities__[row:row+count]
        self.__children__[destination:destination] = d
        self.__quantities__[destination:destination] = q

    def parent(self, item=None):
        if item is None:
            return self.__parent__
        else:
            self.__parent__ = item

    def parent_rows(self):
        def recursion(item):
            if item.parent() is None:
                return
            rows.append( item.row() )
            recursion( item.parent() )
        rows = []
        recursion(self)
        return rows[::-1]

    def pop(self, row, count=1):
        d = self.__children__[row:row+count]
        q = self.__quantities__[row:row+count]
        del self.__children__[row:row+count]
        del self.__quantities__[row:row+count]
        return d, q

    def quantity(self, data=None):
        if data is None:
            return self.__parent__.quantities( self.row() )
        self.__parent__.quantities()[ self.row() ] = data

    def quantities(self, data=None):
        if data is None:
            return self.__quantities__

        if type(data) is list:
            self.__quantities__ = data
            return

        return self.__quantities__[data]

    def remove(self, row, count=1):
        del self.__children__[row:row+count]
        del self.__quantities__[row:row+count]

    def row(self):
        if self.__parent__:
            if self in self.__parent__.children():
                return self.__parent__.children().index(self)
        return 0

    def same(self, item):
        if not self.__data__ == item.data():
            return False
        if not self.__quantities__ == item.quantities():
            return False
        if not self.__parent__ == item.parent():
            return False
        if not self.__children__ == item.children():
            return False
        return True

    def unique_children(self):
        def recursion(children):
            for child in children:
                if not child in unique_children:
                    unique_children.append(child)
                recursion( child.children() )
        unique_children = []
        recursion( self.__children__ )
        return unique_children

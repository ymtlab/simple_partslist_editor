# -*- coding: utf-8 -*-

class Item(object):
    def __init__(self, dict={}, parent=None):
        self.__data__ = dict
        self.__parent__ = parent
        self.__children__ = []
        self.__quantities__ = []

    def append(self, quantity=1):
        self.__children__.append( Item({}, self) )
        self.__quantities__.append(quantity)

    def copy(self, parent=None):
        item = Item({}, parent)
        item.__data__ = { key:self.__data__[key] for key in self.__data__ }
        item.__children__ = [ c.copy(item) for c in self.__children__ ]
        item.__quantities__ = [ q for q in self.__quantities__ ]
        return item

    def child(self, row):
        return self.__children__[row]

    def child_count(self):
        return len(self.__children__)

    def children(self, row=None, count=None):
        if row is None:
            return self.__children__
        return self.__children__[row:row+count]

    def data(self, key=None, value=None):
        if key is None:
            return self.__data__
        if type(key) is dict:
            self.__data__ = key
            return
        if value is None:
            return self.__data__.get(key)
        self.__data__[key] = value

    def extend(self, children, quantities=None):
        self.__children__.extend(children)
        if quantities is None:
            quantities = [ 1 for i in range(len(children)) ]
        self.__quantities__.extend(quantities)

    def insert(self, row, count=1):
        self.__children__[row:row] = [ Item({}, self) for i in range(count) ]
        self.__quantities__[row:row] = [ 1 for i in range(count) ]

    def is_same(self, item):
        if self.__parent__ is item.parent():
            if self.row() == item.row():
                return True
        return False

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
        self.__parent__ = item

    def pop(self, row, count=1):
        d = self.__children__[row:row+count]
        q = self.__quantities__[row:row+count]
        del self.__children__[row:row+count]
        del self.__quantities__[row:row+count]
        return d, q

    def quantities(self, __list__=None):
        if __list__ is None:
            return self.__quantities__
        self.__quantities__ = __list__

    def remove(self, row, count=1):
        del self.__children__[row:row+count]
        del self.__quantities__[row:row+count]

    def row(self):
        if self.parent():
            return self.parent().children().index(self)
        return 0

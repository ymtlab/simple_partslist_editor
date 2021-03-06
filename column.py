# -*- coding: utf-8 -*-

class Column():
    def __init__(self):
        self.__data__ = []

    def append(self, column=''):
        self.__data__.append(column)

    def count(self):
        return len(self.__data__)

    def data(self, column=None, value=None):
        if column is None:
            return self.__data__
        if value is None:
            return self.__data__[column]
        self.__data__[column] = value

    def extend(self, columns):
        self.__data__.extend(columns)

    def insert(self, column, count=1):
        self.__data__[column:column] = [ '' for i in range(count) ]

    def remove(self, column, count=1):
        del self.__data__[column:column+count]

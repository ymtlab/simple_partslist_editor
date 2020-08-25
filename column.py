# -*- coding: utf-8 -*-

class Column():
    def __init__(self, data=[]):
        self.__data__ = data

    def all(self):
        return self.__data__
        
    def append(self, column):
        self.__data__.append(column)

    def count(self):
        return len(self.__data__)

    def data(self, column, value=None):
        if value is None:
            return self.__data__[column]
        self.__data__[column] = value

    def extend(self, columns):
        self.__data__.extend(columns)

    def insert(self, column, columns):
        if type(columns) is list:
            self.__data__[column:column] = columns
        else:
            self.__data__.insert(column, columns)

    def remove(self, start, end):
        del self.__data__[start:end]

"""
 Handles the symbols table module
"""

#Define constants
STATIC_STRING = 'STATIC'
FIELD_STRING = 'FIELD'
ARG_STRING = 'ARG'
VAR_STRING = 'VAR'


class SymbolsTable:
    """
    Represents a symbols table object, contains 2 tables
    one for the class level and one for subroutine level
    holding an array of symbolTuples objects
    """

    """constructs a symbols table object"""
    def __init__(self):
        self.symbolsTableStatic = []
        self.symbolsTableField = []
        self.symbolsTableArg = []
        self.symbolsTableVar = []

    """ Adds tuple to one of the symbols depending on it's kind"""
    def define(self, name, typeOf, kind):
        self.getMatchingST(kind).append((name, typeOf, kind))

    """returns number of tuples in table"""
    def varCount(self, kind):
        return len(self.getMatchingST(kind))

    """Looks for the matching name in all tables and returns it's kind"""
    def kindOf(self, name):
        matchingTable = self.getMatchingST_byName(name)
        for nameOf, typeOf, kind in matchingTable:
            if name == nameOf:
                return kind

    """Returns type of name in matching table"""
    def typeOf(self, name):
        matchingTable = self.getMatchingST_byName(name)
        if matchingTable is None:
            return None
        for nameOf, typeOf, kind in matchingTable:
            if name == nameOf:
                return typeOf
        return None

    """returns in index of name in matching table"""
    def indexOf(self, name):
        matchingTable = self.getMatchingST_byName(name)
        if matchingTable is None:
            return None
        for nameOf, typeOf, kind in matchingTable:
            if name == nameOf:
                return matchingTable.index((nameOf, typeOf, kind))
        return None

    """Erases the subroutine tables"""
    def eraseSubroutineTables(self):
        self.symbolsTableArg = []
        self.symbolsTableVar = []

    """gets the matching table according to kind"""
    def getMatchingST(self, kind):
        if kind == STATIC_STRING:
            return self.symbolsTableStatic
        elif kind == FIELD_STRING:
            return self.symbolsTableField
        elif kind == ARG_STRING:
            return self.symbolsTableArg
        elif kind == VAR_STRING:
            return self.symbolsTableVar
        return None

    """returns the matching symbols table contains the name, None otherwise"""
    def getMatchingST_byName(self, name):
        for nameOf, typeOf, kind in self.symbolsTableStatic:
            if name == nameOf:
                return self.symbolsTableStatic
        for nameOf, typeOf, kind in self.symbolsTableField:
            if name == nameOf:
                return self.symbolsTableField
        for nameOf, typeOf, kind in self.symbolsTableVar:
            if name == nameOf:
                return self.symbolsTableVar
        for nameOf, typeOf, kind in self.symbolsTableArg:
            if name == nameOf:
                return self.symbolsTableArg
        return None


import SymbolTable
import VMWriter
import Tokenizer
import os
import sys


"""
Compilation Engine for EX11
"""

"""
Determines whether a value is in keywords array
"""


def checkIfTokenInArray(strippedToken):
    keywordsArray = ['let', 'var', 'do', 'while', 'if', 'return']
    if strippedToken in keywordsArray:
        return True
    return False


"""
Strip tags from token line
"""


def stripTags(taggedToken):
    token = taggedToken[taggedToken.index(">") + 1:taggedToken.rindex("<")]
    return token.strip()


"""
get type of Token
"""


def getTokenType(taggedToken):
    return taggedToken[taggedToken.index("<") + 1: taggedToken.index(">")]


def handleTabsArray(tabbedArray):
    return list(filter(lambda line: line != '\t', tabbedArray))


"""
Get segment based on kind
"""


def getKindAsSegment(kind):
    # Define constants
    STATIC_STRING = 'STATIC'
    FIELD_STRING = 'FIELD'
    ARG_STRING = 'ARG'
    VAR_STRING = 'VAR'
    if kind == STATIC_STRING:
        return 'static'
    elif kind == FIELD_STRING:
        return 'this'
    elif kind == VAR_STRING:
        return 'local'
    elif kind == ARG_STRING:
        return 'argument'
    return None


def getWriteOperator(operator):
    opAndCommandTable = [("+", 'add'), ("-", 'sub'), ("*", 'Math.multiply'),
                         ('/', 'Math.divide'), ('&amp;', 'and'), ('|', 'or'),
                         ('&lt;', 'lt'), ('&gt;', 'gt'), ("=", 'eq')]
    for op, command in opAndCommandTable:
        if operator == op:
            return command
    return None


class Compiler:
    """represents the second stage of compiling a jack file to xm
       receives the Txml in array format and runs compile engine"""

    def __init__(self, tokenizedArray):
        self.tokenizedArray = tokenizedArray
        self.tokenizedArraySize = len(tokenizedArray)
        self.curIndex = 0
        self.indentLevel = 0
        self.compiledArray = []
        self.INDENT_SIZE = 2
        self.className = ''
        self.labelsCounter = 0
        self.symbolsTable = SymbolTable.SymbolsTable()
        self.VMWriter = VMWriter.VMWriter()

    """
    boolean method for validating if token matches grammar
    """

    def checkMatchForToken(self, comparisonVal):

        curToken = stripTags(self.tokenizedArray[self.curIndex])
        if curToken == comparisonVal:
            return True
        else:
            return False

    """
    This is the only method that can advance the global index for current token
    """

    def advanceIndex(self):
        self.curIndex += 1
        return

    """
    Append title to scope in Xml array
    """

    def appendBlockTitle(self, isOpenBlock, blockTitle):
        whiteSpaceStr = " "
        if isOpenBlock:
            toAppend = whiteSpaceStr * self.indentLevel + "<" + blockTitle + ">\n"
            self.updateIndentLevel(True)
        else:
            self.updateIndentLevel(False)
            toAppend = whiteSpaceStr * self.indentLevel + "</" + blockTitle + ">\n"
        self.compiledArray.append(toAppend)
        return

    """
    Append tokenized line to Xml array
    """

    def appendTokenizedLine(self, tokenizedLine):
        whiteSpaceStr = " "
        self.compiledArray.append(whiteSpaceStr * self.indentLevel + tokenizedLine)
        return

    """
    increment or decrement indent level
    """

    def updateIndentLevel(self, toIncrement):
        if toIncrement:
            self.indentLevel += self.INDENT_SIZE
        else:
            self.indentLevel -= self.INDENT_SIZE
            if self.indentLevel < 0:
                self.indentLevel = 0
        return

    """
    get current token line
    """

    def getCurToken(self):
        return self.tokenizedArray[self.curIndex]

    """
    Peeks at next token
    """

    def peekNextToken(self):
        return stripTags(self.tokenizedArray[self.curIndex + 1])

    """
    Runs compile engine
    """

    def compileEngine(self):
        while self.curIndex < self.tokenizedArraySize:
            self.compileClass()
        return

    def compileClass(self):
        self.appendBlockTitle(True, "class")
        self.appendTokenizedLine(self.getCurToken())  #'class'
        self.advanceIndex()
        self.appendTokenizedLine(self.getCurToken())  #'className'
        self.className = stripTags(self.getCurToken())  # Add class name
        self.advanceIndex()
        if not self.checkMatchForToken("{"):
            print("Error in compile class", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #'open curly brackets'
        self.advanceIndex()  #classVarDec or subRoutineDec
        while True:
            curToken = stripTags(self.getCurToken())
            if curToken == 'static' or curToken == 'field':
                self.compileVarDec(True)
            elif curToken == 'constructor' or curToken == 'function' or curToken == 'method':
                self.compileSubroutine()
            elif self.checkMatchForToken("}"):
                self.appendTokenizedLine(self.getCurToken())  #close curly brackets
                self.appendBlockTitle(False, "class")
                self.advanceIndex()
                return
            else:
                print("Error in compiling class", self.curIndex)
                return
        return

    def compileVarDec(self, isClassVarDec):
        localsCounter = 1
        if isClassVarDec:
            blockTitle = "classVarDec"
        else:
            blockTitle = "varDec"
        self.appendBlockTitle(True, blockTitle)
        self.appendTokenizedLine(self.getCurToken())   #static, field or var (identifier)
        symbolKind = stripTags(self.getCurToken()).upper()
        self.advanceIndex()
        self.appendTokenizedLine(self.getCurToken())  #type (identifier) or keyword
        symbolType = stripTags(self.getCurToken())
        self.advanceIndex()
        self.appendTokenizedLine(self.getCurToken())  #varName (identifier)
        symbolName = stripTags(self.getCurToken())
        self.symbolsTable.define(symbolName, symbolType, symbolKind)
        self.advanceIndex()
        if self.checkMatchForToken(';'):
            self.appendTokenizedLine(self.getCurToken())  #semicolon
            self.appendBlockTitle(False, blockTitle)
            self.advanceIndex()
            return localsCounter
        while True:
            if self.checkMatchForToken(","):
                self.appendTokenizedLine(self.getCurToken())  #comma
                self.advanceIndex()
                if not getTokenType(self.getCurToken()) == "identifier":
                    print("Error in classVarDec", self.curIndex)
                    return
                self.appendTokenizedLine(self.getCurToken())  #varName
                symbolName = stripTags(self.getCurToken())
                self.symbolsTable.define(symbolName, symbolType, symbolKind)
                localsCounter += 1
                self.advanceIndex()
            elif self.checkMatchForToken(";"):
                self.appendTokenizedLine(self.getCurToken())  #semicolon
                self.appendBlockTitle(False, blockTitle)
                self.advanceIndex()
                return localsCounter
            else:
                print("Error in classVarDec", self.curIndex)
                return

        return

    def compileSubroutine(self):
        self.appendBlockTitle(True, "subroutineDec")
        self.appendTokenizedLine(self.getCurToken())  # const func method
        subroutineType = stripTags(self.getCurToken())
        if subroutineType == 'method':
            self.symbolsTable.define('$%%$', '$%%$', 'ARG')
        self.advanceIndex()
        self.appendTokenizedLine(self.getCurToken())  # void or type
        self.advanceIndex()
        if not getTokenType(self.getCurToken()) == "identifier":
            print("Error in compile subroutine", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  # subroutineName
        subroutineName = self.className + '.' + stripTags(self.getCurToken())
        self.advanceIndex()
        self.appendTokenizedLine(self.getCurToken())  # open brackets
        self.advanceIndex()
        self.compileParameterList()
        self.appendTokenizedLine(self.getCurToken())  # closing brackets
        self.advanceIndex()
        self.compileSubroutineBody(subroutineName, subroutineType)
        self.appendBlockTitle(False, "subroutineDec")
        self.symbolsTable.eraseSubroutineTables()  #Delete temporary tables
        return

    def compileSubroutineBody(self, subroutineName, subroutineType):
        self.appendBlockTitle(True, "subroutineBody")
        if not self.checkMatchForToken("{"):
            print("Error in compile subroutineBody", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())  #open curly brackets
        numOfLocals = 0
        self.advanceIndex()
        while self.checkMatchForToken("var"):
            numOfLocals += self.compileVarDec(False)
        self.VMWriter.writeFunction(subroutineName, numOfLocals)
        if subroutineType == 'constructor':
            sizeToAlloc = len(self.symbolsTable.symbolsTableField)
            self.VMWriter.writePush('constant', sizeToAlloc)
            self.VMWriter.writeCall('Memory.alloc', 1)
            self.VMWriter.writePop('pointer', 0)
        if subroutineType == 'method':
            self.VMWriter.writePush('argument', 0)
            self.VMWriter.writePop('pointer', 0)
        self.compileStatements()
        if not self.checkMatchForToken("}"):
            print("Error in compile subroutineBody", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())  #Closing curly brackets
        self.appendBlockTitle(False, "subroutineBody")
        self.advanceIndex()
        return

    def compileParameterList(self):
        self.appendBlockTitle(True, "parameterList")
        if self.checkMatchForToken(')'):
            self.appendBlockTitle(False, "parameterList")
            return
        self.appendTokenizedLine(self.getCurToken())  #type, parameter list not empty
        symbolType = stripTags(self.getCurToken())
        self.advanceIndex()
        if not getTokenType(self.getCurToken()) == "identifier":
            print("Error in compiling parameters list", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())  #varName
        symbolName = stripTags(self.getCurToken())
        symbolKind = 'ARG'
        self.symbolsTable.define(symbolName, symbolType, symbolKind)
        self.advanceIndex()
        while True:
            if self.checkMatchForToken(","):
                self.appendTokenizedLine(self.getCurToken())  #comma
                self.advanceIndex()
                self.appendTokenizedLine(self.getCurToken())  #type
                symbolType = stripTags(self.getCurToken())
                self.advanceIndex()
                if not getTokenType(self.getCurToken()) == "identifier":
                    print("Error in compiling parameters list", self.curIndex)
                    return
                self.appendTokenizedLine(self.getCurToken())  #varName
                symbolName = stripTags(self.getCurToken())
                self.symbolsTable.define(symbolName, symbolType, symbolKind)
                self.advanceIndex()
            elif self.checkMatchForToken(")"):
                break
        self.appendBlockTitle(False, "parameterList")
        return

    def compileStatements(self):
        self.appendBlockTitle(True, "statements")
        while True:

            if self.checkMatchForToken("let"):
                self.compileLet()
            elif self.checkMatchForToken("if"):
                self.compileIf()
            elif self.checkMatchForToken("while"):
                self.compileWhile()
            elif self.checkMatchForToken("do"):
                self.compileDo()
            elif self.checkMatchForToken("return"):
                self.compileReturn()
            elif self.checkMatchForToken("var"):
                self.compileVarDec(False)
            elif self.checkMatchForToken("}"):
                self.appendBlockTitle(False, "statements")
                return
            else:
                print("Error in compile statements line ", self.curIndex)
                return
        return

    def compileDo(self):
        self.appendBlockTitle(True, "doStatement")
        if not self.checkMatchForToken('do'):
            print("Error in compile do ", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #'do'
        self.advanceIndex()
        self.compileSubroutineCall(self.peekNextToken())
        if not self.checkMatchForToken(";"):
            print("Error in compile do ", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #semicolon
        self.VMWriter.writePop('temp', 0)
        self.appendBlockTitle(False, "doStatement")
        self.advanceIndex()
        return

    def compileLet(self):
        self.appendBlockTitle(True, "letStatement")
        if not self.checkMatchForToken('let'):
            print("Error in compile let ", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #let
        self.advanceIndex()
        if not getTokenType(self.getCurToken()) == "identifier":
            print("Error in compile let ", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #varName
        varName = stripTags(self.getCurToken())
        isArrayOnLeft = False
        self.advanceIndex()
        if self.checkMatchForToken("["):
            self.appendTokenizedLine(self.getCurToken())  #open square brackets
            self.advanceIndex()
            self.compileExpression()
            self.VMWriter.writePush(getKindAsSegment(self.symbolsTable.kindOf(varName)),
                                    self.symbolsTable.indexOf(varName))
            self.VMWriter.writeArithmetic('add')
            isArrayOnLeft = True
            if not self.checkMatchForToken("]"):
                print("Error in compile let ", self.curIndex)
                return
            self.appendTokenizedLine(self.getCurToken())  #close square brackets
            self.advanceIndex()
        if not self.checkMatchForToken("="):
            print("Error in compile let ", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #equal sign
        self.advanceIndex()
        self.compileExpression()
        if not isArrayOnLeft:
            self.VMWriter.writePop(getKindAsSegment(self.symbolsTable.kindOf(varName)),
                                   self.symbolsTable.indexOf(varName))
        if isArrayOnLeft:
            self.VMWriter.writePop('temp', 0)
            self.VMWriter.writePop('pointer', 1)
            self.VMWriter.writePush('temp', 0)
            self.VMWriter.writePop('that', 0)

        if not self.checkMatchForToken(";"):
            print("Error in compile let ", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #semicolon
        self.appendBlockTitle(False, "letStatement")
        self.advanceIndex()
        return

    def compileWhile(self):

        self.labelsCounter += 1
        labelTitle = self.labelsCounter
        self.appendBlockTitle(True, "whileStatement")
        if not self.checkMatchForToken("while"):
            print("Error in compile while", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #'while'
        self.advanceIndex()
        if not self.checkMatchForToken("("):
            print("Error in compile while", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #open brackets
        self.VMWriter.writeLabel('WHILE_EXP' + str(labelTitle))
        self.advanceIndex()
        self.compileExpression()
        if not self.checkMatchForToken(")"):
            print("Error in compile while", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #close brackets
        self.VMWriter.writeArithmetic('not')  #Change to neg?
        self.VMWriter.writeIf('WHILE_END' + str(labelTitle))
        self.advanceIndex()
        if not self.checkMatchForToken("{"):
            print("Error in compile while", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #open curly brackets
        self.advanceIndex()
        self.compileStatements()
        if not self.checkMatchForToken("}"):
            print("Error in compile while", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #close curly brackets
        self.VMWriter.writeGoto('WHILE_EXP' + str(labelTitle))
        self.VMWriter.writeLabel('WHILE_END' + str(labelTitle))
        self.appendBlockTitle(False, "whileStatement")
        self.advanceIndex()
        return

    def compileReturn(self):
        self.appendBlockTitle(True, "returnStatement")
        if not self.checkMatchForToken("return"):
            print("Error in compile return", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #'return'
        self.advanceIndex()
        if not self.checkMatchForToken(";"):
            ##TODO add another if condition here for some case
            if self.checkMatchForToken('this'):
                self.VMWriter.writePush('pointer', 0)
            else:
                self.compileExpression()
        else:
            self.VMWriter.writePush('constant', 0)  #dummy value
        self.appendTokenizedLine(self.getCurToken())  #semicolon
        self.appendBlockTitle(False, "returnStatement")
        self.VMWriter.writeReturn()
        self.advanceIndex()
        return

    def compileIf(self):
        if not self.checkMatchForToken("if"):
            print("Error in compile if", self.curIndex)
            return
        self.appendBlockTitle(True, "ifStatement")
        self.labelsCounter += 1
        labelTitle = self.labelsCounter
        self.appendTokenizedLine(self.getCurToken())  #if
        self.advanceIndex()
        if not self.checkMatchForToken("("):
            print("Error in compile if", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #open brackets
        self.advanceIndex()
        self.compileExpression()
        if not self.checkMatchForToken(")"):
            print("Error in compile if", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #close brackets
        self.VMWriter.writeIf('IF_TRUE' + str(labelTitle))
        self.VMWriter.writeGoto('IF_FALSE' + str(labelTitle))
        self.VMWriter.writeLabel('IF_TRUE' + str(labelTitle))
        self.advanceIndex()
        if not self.checkMatchForToken("{"):
            print("Error in compile if", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #open curly brackets
        self.advanceIndex()
        self.compileStatements()
        if not self.checkMatchForToken("}"):
            print("Error in compile if", self.curIndex)
            return
        self.appendTokenizedLine(self.getCurToken())  #close curly brackets
        self.advanceIndex()
        if self.checkMatchForToken("else"):
            self.VMWriter.writeGoto('END_ELSE' + str(labelTitle))
            self.VMWriter.writeLabel('IF_FALSE' + str(labelTitle))
            self.appendTokenizedLine(self.getCurToken())  #'else'
            self.advanceIndex()
            if not self.checkMatchForToken("{"):
                print("Error in compile if", self.curIndex)
                return
            self.appendTokenizedLine(self.getCurToken())  #open curly brackets
            self.advanceIndex()
            self.compileStatements()
            if not self.checkMatchForToken("}"):
                print("Error in compile if", self.curIndex)
                return
            self.appendTokenizedLine(self.getCurToken())  #close curly brackets
            self.advanceIndex()
            self.VMWriter.writeLabel('END_ELSE' + str(labelTitle))
            self.VMWriter.writeLabel('IF_FALSE' + str(labelTitle))
        else:
            self.VMWriter.writeLabel('IF_FALSE' + str(labelTitle))
        self.appendBlockTitle(False, "ifStatement")
        return

    def compileExpression(self):
        opTable = ["+", "-", "*", '/', '&amp;', '|', '&lt;', '&gt;', "="]
        self.appendBlockTitle(True, "expression")
        self.compileTerm()
        while stripTags(self.getCurToken()) in opTable:
            self.appendTokenizedLine(self.getCurToken())  #op sign
            operator = stripTags(self.getCurToken())
            self.advanceIndex()
            self.compileTerm()
            opMatch = getWriteOperator(operator)
            if opMatch in ['Math.multiply', 'Math.divide']:
                self.VMWriter.writeCall(opMatch, 2)
            else:
                self.VMWriter.writeArithmetic(opMatch)



        self.appendBlockTitle(False, "expression")
        return

    def compileTerm(self):
        unaryOpTable = ['-', '~']
        keywordConstantsTable = ['true', 'false', 'null', 'this']
        self.appendBlockTitle(True, "term")
        if getTokenType(self.getCurToken()) == 'integerConstant' \
                or getTokenType(self.getCurToken()) == 'stringConstant':
            self.appendTokenizedLine(self.getCurToken())  #'constant'
            if getTokenType(self.getCurToken()) == 'integerConstant':
                intVal = stripTags(self.getCurToken())
                self.VMWriter.writePush('constant', int(intVal))
            else:
                stringVal = stripTags(self.getCurToken())
                self.VMWriteStringConst(stringVal)
            self.advanceIndex()

        elif stripTags(self.getCurToken()) in keywordConstantsTable:
            self.appendTokenizedLine(self.getCurToken())  #keyword constant
            keyword = stripTags(self.getCurToken())
            if keyword == 'false' or keyword == 'null':
                self.VMWriter.writePush('constant', 0)
            elif keyword == 'true':
                self.VMWriter.writePush('constant', 1)
                self.VMWriter.writeArithmetic('neg')
            elif keyword == 'this':
                self.VMWriter.writePush('pointer', 0)
            self.advanceIndex()
        elif stripTags(self.getCurToken()) in unaryOpTable:
            self.appendTokenizedLine(self.getCurToken())  #unary op ter,
            op = stripTags(self.getCurToken())
            self.advanceIndex()
            self.compileTerm()
            if op == '-':
                self.VMWriter.writeArithmetic('neg')
            elif op == '~':
                self.VMWriter.writeArithmetic('not')
        elif self.checkMatchForToken("("):
            self.appendTokenizedLine(self.getCurToken())  #open brackets
            self.advanceIndex()
            self.compileExpression()
            self.appendTokenizedLine(self.getCurToken())  #close brackets
            self.advanceIndex()
        elif getTokenType(self.getCurToken()) == "identifier":
            nextToken = self.peekNextToken()
            if nextToken == '.' or nextToken == '(':
                self.compileSubroutineCall(nextToken)
            elif nextToken == '[':
                self.appendTokenizedLine(self.getCurToken())  #var name
                varName = stripTags(self.getCurToken())
                self.advanceIndex()
                self.appendTokenizedLine(self.getCurToken())  #open square brackets
                self.advanceIndex()
                self.compileExpression()
                self.VMWriter.writePush(getKindAsSegment(self.symbolsTable.kindOf(varName)),
                                        self.symbolsTable.indexOf(varName))
                self.VMWriter.writeArithmetic('add')
                self.VMWriter.writePop('pointer', 1)
                self.VMWriter.writePush('that', 0)
                self.appendTokenizedLine(self.getCurToken())  #close square brackets
                self.advanceIndex()
            else:
                self.appendTokenizedLine(self.getCurToken())  #varName solo
                varName = stripTags(self.getCurToken())
                self.VMWriter.writePush(getKindAsSegment(self.symbolsTable.kindOf(varName)),
                                        self.symbolsTable.indexOf(varName))
                self.advanceIndex()
        self.appendBlockTitle(False, "term")
        return

    def compileExpressionList(self):
        varCounter = 0
        self.appendBlockTitle(True, "expressionList")
        if self.checkMatchForToken(')'):
            self.appendBlockTitle(False, "expressionList")
            return varCounter
        varCounter += 1
        self.compileExpression()
        while True:
            if self.checkMatchForToken(","):
                self.appendTokenizedLine(self.getCurToken())  #comma
                self.advanceIndex()
                self.compileExpression()
                varCounter += 1
            else:
                self.appendBlockTitle(False, "expressionList")
                return varCounter
        return

    def compileSubroutineCall(self, nextToken):
        #No need for appending new scope for subroutine
        numArgs = 0
        if nextToken == '(':
            self.appendTokenizedLine(self.getCurToken())  #subroutineName
            subroutineName = stripTags(self.getCurToken())
            numArgs += 1
            self.advanceIndex()
            self.appendTokenizedLine(self.getCurToken())  #open brackets
            self.advanceIndex()
            numArgs = self.compileExpressionList()
            className = self.className
            fullCallName = className + '.' + subroutineName
            self.VMWriter.writeCall(fullCallName, numArgs)
            self.appendTokenizedLine(self.getCurToken())  #close brackets
            self.advanceIndex()
        elif nextToken == '.':
            self.appendTokenizedLine(self.getCurToken())  #classname or varName
            possibleVarName = stripTags(self.getCurToken())
            varNameActual = self.symbolsTable.typeOf(possibleVarName)
            if varNameActual is None:
                className = possibleVarName
            else:
                varName = possibleVarName
                self.VMWriter.writePush(getKindAsSegment(self.symbolsTable.kindOf(varName)),
                                        self.symbolsTable.indexOf(varName))
                numArgs += 1
                className = self.symbolsTable.typeOf(varName)
            self.advanceIndex()
            self.appendTokenizedLine(self.getCurToken())  #dot
            self.advanceIndex()
            self.appendTokenizedLine(self.getCurToken())  #subroutineName or method
            subroutineName = stripTags(self.getCurToken())
            self.advanceIndex()
            self.appendTokenizedLine(self.getCurToken())  #open brackets
            self.advanceIndex()
            numArgs += self.compileExpressionList()
            fullCallName = className + '.' + subroutineName
            self.VMWriter.writeCall(fullCallName, numArgs)
            self.appendTokenizedLine(self.getCurToken())  #closing brackets
            self.advanceIndex()
        else:
            print("Error in compile subroutineCall", self.curIndex)
            return

        return

    def VMWriteStringConst(self, stringConst):
        stringConst = stringConst.encode('unicode-escape')
        stringLen = len(stringConst)
        self.VMWriter.writePush('constant', stringLen)
        self.VMWriter.writeCall('String.new', 1)
        for char in stringConst:
            self.VMWriter.writePush('constant', char)
            self.VMWriter.writeCall('String.appendChar', 2)
        return


def writeArrayToFile(arrayToWrite, fileNameStr, isTokenized):
    if isTokenized:
        arrayToWrite.insert(0, '<tokens>\n')
        arrayToWrite.insert(len(arrayToWrite), "</tokens>\n")
        fileNameStr = fileNameStr.replace(".xml", "T.xml")
    with open(fileNameStr, 'w') as outFile:
        for line in arrayToWrite:
            outFile.write(line)
    return


"""
Receives VMArray and a file name string with .vm suffix.
Writes the array to file
"""


def writeVMArrayToFile(VMArray, filenameStr):
    with open(filenameStr, 'w') as outFile:
        for line in VMArray:
            outFile.write(line)
    return


def main(argv):
    inputStr = argv[0]
    try:
        if os.path.isdir(inputStr):
            files = [file for file in os.listdir(inputStr) if file.endswith('.jack')]
            for file in files:
                tokenizedArray = Tokenizer.tokenizeFile(inputStr + '/' + file)
                compilerEng = Compiler(handleTabsArray(tokenizedArray))
                compilerEng.compileEngine()
                outputFileName = file.replace(".jack", ".xml")
                outputStr = inputStr + '/' + outputFileName
                writeArrayToFile(compilerEng.compiledArray, outputStr, False)
                VMFileStr = inputStr + '/' + file.replace(".jack", "1.vm")
                writeVMArrayToFile(compilerEng.VMWriter.VMArray, VMFileStr)
        else:
            tokenizedArray = Tokenizer.tokenizeFile(inputStr)
            compilerEng = Compiler(handleTabsArray(tokenizedArray))
            compilerEng.compileEngine()
            outputFileName = inputStr.replace(".jack", ".xml")
            writeArrayToFile(compilerEng.compiledArray, outputFileName, False)
            VMFileStr = inputStr.replace(".jack", "1.vm")
            writeVMArrayToFile(compilerEng.VMWriter.VMArray, VMFileStr)
    except TypeError:
        print("I Love Nand")


if __name__ == "__main__":
    main(sys.argv[1:])
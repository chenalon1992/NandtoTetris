"""
Handles part II of Ex10 from Txml to Xml
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
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if not self.checkMatchForToken("{"):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        while True:
            curToken = stripTags(self.getCurToken())
            if curToken == 'static' or curToken == 'field':
                self.compileVarDec(True)
            elif curToken == 'constructor' or curToken == 'function' or curToken == 'method':
                self.compileSubroutine()
            elif self.checkMatchForToken("}"):
                self.appendTokenizedLine(self.tokenizedArray[self.curIndex])
                self.appendBlockTitle(False, "class")
                self.advanceIndex()
                return
            else:
                print("Error", self.curIndex)
                return
        return

    def compileVarDec(self, isClassVarDec):
        if isClassVarDec:
            blockTitle = "classVarDec"
        else:
            blockTitle = "varDec"
        self.appendBlockTitle(True, blockTitle)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if not getTokenType(self.tokenizedArray[self.curIndex]) == "identifier":
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        while True:
            if self.checkMatchForToken(","):
                self.appendTokenizedLine(self.getCurToken())
                self.advanceIndex()
                if not getTokenType(self.getCurToken()) == "identifier":
                    print("Error", self.curIndex)
                    return
                self.appendTokenizedLine(self.getCurToken())
                self.advanceIndex()
            elif self.checkMatchForToken(";"):
                self.appendTokenizedLine(self.getCurToken())
                self.appendBlockTitle(False, blockTitle)
                self.advanceIndex()
                return
            else:
                print("Error", self.curIndex)
                return

        return

    def compileSubroutine(self):
        self.appendBlockTitle(True, "subroutineDec")
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if not getTokenType(self.getCurToken()) == "identifier":
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        self.compileParameterList()
        self.compileSubroutineBody()
        self.appendBlockTitle(False, "subroutineDec")
        return

    def compileSubroutineBody(self):
        self.appendBlockTitle(True, "subroutineBody")
        if not self.checkMatchForToken("{"):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if self.checkMatchForToken("var"):
            while True:
                if self.checkMatchForToken("var"):
                    self.compileVarDec(False)
                else:
                    break
        self.compileStatements()
        if not self.checkMatchForToken("}"):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.appendBlockTitle(False, "subroutineBody")
        self.advanceIndex()
        return

    def compileParameterList(self):
        if not self.checkMatchForToken("("):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.appendBlockTitle(True, "parameterList")
        self.advanceIndex()
        if getTokenType(self.getCurToken()) == "keyword":
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            if not getTokenType(self.getCurToken()) == "identifier":
                print("Error", self.curIndex)
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            while True:
                if self.checkMatchForToken(","):
                    self.appendTokenizedLine(self.getCurToken())
                    self.advanceIndex()
                    if not getTokenType(self.getCurToken()) == "keyword":
                        print("Error", self.curIndex)
                    self.appendTokenizedLine(self.getCurToken())
                    self.advanceIndex()
                    if not getTokenType(self.getCurToken()) == "identifier":
                        print("Error", self.curIndex)
                    self.appendTokenizedLine(self.getCurToken())
                    self.advanceIndex()
                elif self.checkMatchForToken(")"):
                    break
        if self.checkMatchForToken(")"):
            self.appendBlockTitle(False, "parameterList")
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            return
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
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        self.compileSubroutineCall()
        if self.checkMatchForToken(")"):
            self.advanceIndex()
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            self.appendBlockTitle(False, "doStatement")
            return
        if checkIfTokenInArray(stripTags(self.getCurToken())):
            self.appendBlockTitle(False, "doStatement")
            return

        if not self.checkMatchForToken(";"):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.appendBlockTitle(False, "doStatement")
        self.advanceIndex()
        return

    def compileLet(self):
        self.appendBlockTitle(True, "letStatement")
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if not getTokenType(self.getCurToken()) == "identifier":
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if self.checkMatchForToken("["):
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            self.compileExpression()
            if not self.checkMatchForToken("]"):
                print("Error", self.curIndex)
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
        if not self.checkMatchForToken("="):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        self.compileExpression()
        if self.checkMatchForToken(';'):
            self.appendTokenizedLine(self.getCurToken())
            self.appendBlockTitle(False, "letStatement")
            self.advanceIndex()
            return
        self.advanceIndex()
        self.appendTokenizedLine(self.getCurToken())
        if checkIfTokenInArray(stripTags(self.getCurToken())):
            self.appendBlockTitle(False, "letStatement")
            return
        self.appendBlockTitle(False, "letStatement")
        self.advanceIndex()
        return

    def compileWhile(self):

        self.appendBlockTitle(True, "whileStatement")
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if not self.checkMatchForToken("("):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        self.compileExpression()
        open_brackets_flag = False
        if not self.checkMatchForToken(")"):
            if self.checkMatchForToken("{"):
                if stripTags(self.tokenizedArray[self.curIndex - 1]) == ')':
                    self.appendTokenizedLine(self.tokenizedArray[self.curIndex - 1])
                self.appendTokenizedLine(self.getCurToken())
                open_brackets_flag = True
            else:
                print("Error", self.curIndex)
        else:
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()

        if not self.checkMatchForToken("{"):
            print("Error", self.curIndex)
        if not open_brackets_flag:
            self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        self.compileStatements()
        if not self.checkMatchForToken("}"):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.appendBlockTitle(False, "whileStatement")
        self.advanceIndex()
        return

    def compileReturn(self):
        self.appendBlockTitle(True, "returnStatement")
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if not self.checkMatchForToken(";"):
            self.compileExpression()
        self.appendTokenizedLine(self.getCurToken())
        self.appendBlockTitle(False, "returnStatement")
        self.advanceIndex()
        return

    def compileIf(self):
        self.appendBlockTitle(True, "ifStatement")
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if not self.checkMatchForToken("("):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        self.compileExpression()
        if not self.checkMatchForToken(")"):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if not self.checkMatchForToken("{"):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        self.compileStatements()
        if not self.checkMatchForToken("}"):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.advanceIndex()
        if self.checkMatchForToken("else"):
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            if not self.checkMatchForToken("{"):
                print("Error", self.curIndex)
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            self.compileStatements()
            if not self.checkMatchForToken("}"):
                print("Error", self.curIndex)
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
        self.appendBlockTitle(False, "ifStatement")
        return

    def compileExpression(self):
        opTable = ["+", "-", "*", '/', '&amp;', '|', '&lt;', '&gt;', "="]
        self.appendBlockTitle(True, "expression")
        self.compileTerm()
        if stripTags(self.getCurToken()) in opTable:
            while True:
                if stripTags(self.getCurToken()) in opTable:
                    self.appendTokenizedLine(self.getCurToken())
                    self.advanceIndex()
                    self.compileTerm()
                else:
                    break
        self.appendBlockTitle(False, "expression")
        return

    def compileTerm(self):
        unaryOpTable = ['-', '~']
        keywordConstantsTable = ['true', 'false', 'null', 'this']
        self.appendBlockTitle(True, "term")
        if getTokenType(self.getCurToken()) == 'integerConstant' \
                or getTokenType(self.getCurToken()) == 'stringConstant':
            self.appendTokenizedLine(self.getCurToken())
        elif stripTags(self.getCurToken()) in keywordConstantsTable:
            self.appendTokenizedLine(self.getCurToken())
        elif stripTags(self.getCurToken()) in unaryOpTable:
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            self.compileTerm()
        elif self.checkMatchForToken("("):
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            self.compileExpression()
            if self.checkMatchForToken(";"):
                self.appendTokenizedLine(self.tokenizedArray[self.curIndex - 1])
            else:
                self.appendTokenizedLine(self.getCurToken())
        elif getTokenType(self.getCurToken()) == "identifier":
            self.compileSubroutineCall()
            self.appendBlockTitle(False, "term")
            return
        self.appendBlockTitle(False, "term")
        if self.checkMatchForToken(";"):
            return
        self.advanceIndex()  # One advance too many with token
        return

    def compileExpressionList(self):
        if not self.checkMatchForToken("("):
            print("Error", self.curIndex)
        self.appendTokenizedLine(self.getCurToken())
        self.appendBlockTitle(True, "expressionList")
        self.advanceIndex()
        if self.checkMatchForToken(')'):
            self.appendBlockTitle(False, "expressionList")
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            return
        self.compileExpression()
        while True:
            if self.checkMatchForToken(","):
                self.appendTokenizedLine(self.getCurToken())
                self.advanceIndex()
                self.compileExpression()
            else:
                self.appendBlockTitle(False, "expressionList")
                self.appendTokenizedLine(self.getCurToken())
                return
        return

    def compileSubroutineCall(self):
        nextToken = self.peekNextToken()
        if nextToken == '(':
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            self.compileExpressionList()
        elif nextToken == '[':
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            self.compileExpression()
            if not self.checkMatchForToken("]"):
                print("Error", self.curIndex)
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
        elif nextToken == '.':
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            # Now we're on the . token
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            self.compileExpressionList()
        else:
            self.appendTokenizedLine(self.getCurToken())
            self.advanceIndex()
            return
        return

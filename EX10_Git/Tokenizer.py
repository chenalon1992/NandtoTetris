import os
import re
import sys
import Compiler

"""
EX 10 - Tokenizer. Tokenize file or files from .jack to T.xml
"""

keywordsTable = ('class', 'constructor', 'function', 'method', 'field', 'static',
                 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
                 'this', 'let', 'do', 'if', 'else', 'while', 'return')

symbolsTable = ('{', '}', '[', ']', '(', ')', '.', ',', ';', '+', '-', '*', '/', '&',
                '|', '<', '>', '=', '~')

uniqueSymbolsTable = (("<", "&lt;"), (">", "&gt;"), ("\\", "&quot;"), ("&", "&amp;"))

KEYWORD = 'KEYWORD'
SYMBOL = 'SYMBOL'
INT_CONST = 'INT_CONST'
STRING_CONST = 'STRING_CONST'
IDENTIFIER = 'IDENTIFIER'
OTHER = 'OTHER'

"""
Check if int is valid
"""
def isIntVal(token):
    if token.isdigit():
        tokenInt = int(token)
        if 0 <= tokenInt <= 32767:
            return True
    return False

"""
classify token
"""
def tokenType(token):
    if token in keywordsTable:
        return KEYWORD
    if token in symbolsTable:
        return SYMBOL
    if isIntVal(token):
        return INT_CONST
    matchObj = re.match(r'[A-Za-z]+\w*', token)
    if matchObj:
        return IDENTIFIER
    else:
        return OTHER

"""
Handles keyWord token
"""
def keyWord(keyword):
    for key in keywordsTable:
        if key == keyword:
            return "<keyword> " + keyword + " </keyword>\n"
    return None

"""
Handles Symbol token
"""
def symbol(symbolVal):

    for uniqueSymbol, uniqueVal in uniqueSymbolsTable:
        if symbolVal == uniqueSymbol:
            return "<symbol> " + uniqueVal + " </symbol>\n"

    for regSymbol in symbolsTable:
        if regSymbol == symbolVal:
            return "<symbol> " + symbolVal + " </symbol>\n"

"""
Handles constant string token
"""
def stringVal(stringVal):
    return "<stringConstant>" + stringVal.strip('"') + " </stringConstant >\n"

"""
Handles identifier token
"""
def identifier(identifierVal):
    return "<identifier> " + identifierVal + " </identifier>\n"

"""
Handles constant int token
"""
def intVal(intVal):
    return "<integerConstant> " + intVal + " </integerConstant>\n"

"""
Compile a whole file, parses all token
and classify them respectively
"""
def tokenizeFile(fileStr):
    with open(fileStr, 'r') as curFile:
        #Filter annoying comments which start with an asterisk

        tokens = curFile.read()
        #Remove all kinds of comments with this pattern
        tokens = re.sub(r'//.*\n|/\*\*.*\n|^\s*\*.*\n|\n|/\*.*\n', "", tokens, flags=re.MULTILINE)


        #Split by non words combinations
        tokens = re.split('(\W)', tokens)

        #Remove empty or white spaces strings from list
        stringsToFilter = ('', ' ', '\n')
        tokens = [token for token in tokens if token not in stringsToFilter]

        tokenizedLineArray = []
        #Needed for string constant validation
        stringConstFlag = False
        tokenForStringConst = ""
        for token in tokens:

            #First we handle string constants
            if stringConstFlag and token != '"':
                tokenForStringConst += " " + token
                continue

            if token == '"':
                if stringConstFlag:
                    tokenizedLineArray.append(stringVal(tokenForStringConst))
                    tokenForStringConst = ''
                    stringConstFlag = False
                    continue
                else:
                    stringConstFlag = True
                    tokenForStringConst = ''
                    continue

            #Determine token type
            token_type = tokenType(token)
            if token_type == KEYWORD:
                tokenizedLineArray.append(keyWord(token))
            if token_type == SYMBOL:
                tokenizedLineArray.append(symbol(token))
            if token_type == INT_CONST:
                tokenizedLineArray.append(intVal(token))
            if token_type == IDENTIFIER:
                tokenizedLineArray.append(identifier(token))
            if token_type == OTHER:
                if token == '\t':
                    #tokenizedLineArray.append('\\t\n')
                    pass
        return tokenizedLineArray

def writeArrayToFile(arrayToWrite, fileNameStr, isTokenized):
    if isTokenized:
        arrayToWrite.insert(0, '<tokens>\n')
        arrayToWrite.insert(len(arrayToWrite), "</tokens>\n")
        fileNameStr = fileNameStr.replace("1.xml", "1T.xml")
    with open(fileNameStr, 'w') as outFile:
        for line in arrayToWrite:
            outFile.write(line)
    return

def main(argv):
    inputStr = argv[0]
    try:
        if os.path.isdir(inputStr):
            files = [file for file in os.listdir(inputStr) if file.endswith('.jack')]
            for file in files:
                tokenizedArray = tokenizeFile(inputStr + '/' + file)
                compilerObj = Compiler.Compiler(Compiler.handleTabsArray(tokenizedArray))
                compilerObj.compileEngine()
                outputFileName = file.replace(".jack", ".xml")
                outputStr = inputStr + '/' + outputFileName
                #writeArrayToFile(tokenizedArray, outputFileName, True)
                writeArrayToFile(compilerObj.compiledArray, outputStr, False)
        else:
            tokenizedArray = tokenizeFile(inputStr)
            compilerObj = Compiler.Compiler(Compiler.handleTabsArray(tokenizedArray))
            compilerObj.compileEngine()
            outputFileName = inputStr.replace(".jack", ".xml")
            #writeArrayToFile(tokenizedArray, outputFileName, True)
            writeArrayToFile(compilerObj.compiledArray, outputFileName, False)
    except TypeError:
        print("I Love Nand")

if __name__ == "__main__":
    main(sys.argv[1:])

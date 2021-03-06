# hybrid interpreter
import sys, time


class Token:
    def __init__(self, line, column, category, lexeme):
        self.line = line  # srce program line number of the token
        self.column = column  # srce program col in which token starts
        self.category = category  # category of the token
        self.lexeme = lexeme  # token in string form


# globals
debug = True  # controls token trace
source = ''  # receives entire source program
sourceindex = 0  # index into the source code in source
line = 0  # current line number
column = 0  # current column number
tokenlist = []  # list of tokens created by tokenizer
tokenindex = -1  # index of current token in tokens
token = None  # current token
prevchar = '\n'  # '\n' in prevchar signals start of new line
blankline = True  # reset to False if line is not blank

co_names = []
co_consts = []
co_code = []

# bytecode opcodes
UNARY_NEGATIVE    = 11      # hex 0B
BINARY_MULTIPLY   = 20      # hex 14
BINARY_ADD        = 23      # hex 17
PRINT_ITEM        = 71      # hex 47
PRINT_NEWLINE     = 72      # hex 48
STORE_NAME        = 90      # hex 5A
LOAD_CONST        = 100     # hex 64
LOAD_NAME         = 101     # hex 65


# constants that represent token categories
EOF = 0  # end of file
PRINT = 1  # 'print' keyword
UNSIGNEDINT = 2  # unsigned integer
NAME = 3  # identifier that is not a keyword
ASSIGNOP = 4  # '=' assignment operator
LEFTPAREN = 5  # '('
RIGHTPAREN = 6  # ')'
PLUS = 7  # '+'
MINUS = 8  # '-'
TIMES = 9  # '*'
NEWLINE = 10  # end of line
ERROR = 11  # if not any of the above, then error

# displayable names for each token category
catnames = ['EOF', 'print', 'UNSIGNEDINT', 'NAME', 'ASSIGNOP',
            'LEFTPAREN', 'RIGHTPAREN', 'PLUS', 'MINUS',
            'TIMES', 'NEWLINE', 'ERROR']

# keywords and their token categories}
keywords = {'print': PRINT}

# one-character tokens and their token categories
smalltokens = {'=': ASSIGNOP, '(': LEFTPAREN, ')': RIGHTPAREN,
               '+': PLUS, '-': MINUS, '*': TIMES, '\n': NEWLINE, '': EOF}


#################
# main function #
#################

# main() reads input file and calls tokenizer()
def main():
    global source

    if len(sys.argv) == 2:  # check if correct number of cmd line args
        try:
            infile = open(sys.argv[1], 'r')
            source = infile.read()  # read source program
        except IOError:
            print('Cannot read input file ' + sys.argv[1])
            sys.exit(1)

    else:
        print('Wrong number of command line arguments')
        print('Format: python p1.py <infile>')
        sys.exit(1)

    if source[-1] != '\n':  # add newline to end if missing
        source = source + '\n'
    lines = source.splitlines()

    if debug:
        print(time.strftime('%c') + '%34s' % 'YOUR NAME HERE')
        print('Interpreter = ' + sys.argv[0])
        print('Input file  = ' + sys.argv[1] + '\n')
        linenumber = 1
        print('----1-3-5-7-9-1-3-5-7-9-1-3-5-7-9-1-3-5-7-9-1- Source code')
        for s in lines:
            print(('%3d ' % linenumber) + s)
            linenumber += 1

        print('---------------------------------------------- Token trace')
        print('Line  Col Category    Lexeme\n')

    try:
        tokenizer()  # tokenize source code in source
        parser()

    # on an error, display an error message
    # token is the token object on which the error was detected
    except RuntimeError as emsg:
        # output slash n in place of newline
        lexeme = token.lexeme.replace('\n', '\\n')
        print('\nError on ' + "'" + lexeme + "'" + ' line ' +
              str(token.line) + ' column ' + str(token.column))
        print(emsg)  # message from RuntimeError object
        sys.exit(1)
    
    if debug:
        print('---------------------------------------------------- Tables')
        print('co_names  = ', co_names)
        print('co_consts = ', co_consts)
        print('co_code   = ', co_code)
        print('-------------------------------------------- Program output')        

    interpreter()


####################
# tokenizer        #
####################

def tokenizer():
    global token
    curchar = ' '  # prime curchar with space

    while True:
        # skip whitespace but not newlines
        while curchar != '\n' and curchar.isspace():
            curchar = getchar()  # get next char from source program

        # construct and initialize token
        token = Token(line, column, None, '')

        if curchar.isdigit():  # start of unsigned int?
            token.category = UNSIGNEDINT  # save category of token
            while True:
                token.lexeme += curchar  # append curchar to lexeme
                curchar = getchar()  # get next character
                if not curchar.isdigit():  # break if not a digit
                    break

        elif curchar.isalpha() or curchar == '_':  # start of name?
            while True:
                token.lexeme += curchar  # append curchar to lexeme
                curchar = getchar()  # get next character
                # break if not letter, '_', or digit
                if not (curchar.isalnum() or curchar == '_'):
                    break

            # determine if lexeme is a keyword or name of variable
            if token.lexeme in keywords:
                token.category = keywords[token.lexeme]
            else:
                token.category = NAME

        elif curchar in smalltokens:
            token.category = smalltokens[curchar]  # get category
            token.lexeme = curchar
            curchar = getchar()  # move to first char after the token

        else:
            token.category = ERROR  # invalid token
            token.lexeme = curchar
            raise RuntimeError('Invalid token')

        tokenlist.append(token)  # append token to tokens list
        displaytoken(token)
        if token.category == EOF:  # finished tokenizing?
            break


# getchar() gets next char from source and adjusts line and column
def getchar():
    global sourceindex, column, line, prevchar, blankline

    # check if starting a new line
    if prevchar == '\n':  # '\n' signals start of a new line
        line += 1  # increment line number
        column = 0  # reset column number
        blankline = True  # initialize blankline

    if sourceindex >= len(source):  # at end of source code?
        column = 1  # set EOF column to 1
        prevchar = ''  # save current char for next call
        return ''  # null str signals end of source

    c = source[sourceindex]  # get next char in the source program
    sourceindex += 1  # increment sourceindex to next character
    column += 1  # increment column number
    if not c.isspace():  # if c not whitespace then line not blank
        blankline = False  # indicate line not blank
    prevchar = c  # save current character

    # if at end of blank line, return space in place of '\n'
    if c == '\n' and blankline:
        return ' '
    else:
        return c  # return character to tokenizer()


def displaytoken(t):
    if debug:
        print("%3s %4s  %-14s %s" % (str(t.line), str(t.column),
                                     catnames[t.category], t.lexeme))


####################
# parser functions #
####################

# advances to the next token in the list tokens
def advance():
    global token, tokenindex
    tokenindex += 1
    if tokenindex >= len(tokenlist):
        raise RuntimeError('Unexpected end of file')
    token = tokenlist[tokenindex]


# advances if current token is the expected token
def consume(expectedcat):
    if (token.category == expectedcat):
        advance()
    else:
        raise RuntimeError('Expecting ' + catnames[expectedcat])


# top level function of parser
def parser():
    advance()  # advance so token holds first token
    program()  # call function corresponding to start symbol


def program():
    while token.category in [NAME, PRINT]:
        stmt()
    if token.category != EOF:
        raise RuntimeError('Expecting end of file')


def stmt():
    simplestmt()
    consume(NEWLINE)


def simplestmt():
    if token.category == NAME:
        assignmentstmt()
    elif token.category == PRINT:
        printstmt()
    else:
        raise RuntimeError('Expecting stmt')


def assignmentstmt():
    if token.lexeme in co_names:
        index = co_names.index(token.lexeme)
    else:
        index = len(co_names)
        co_names.append(token.lexeme)
    advance()
    consume(ASSIGNOP)
    expr()
    co_code.append(STORE_NAME)
    co_code.append(index)


def printstmt():
    advance()
    consume(LEFTPAREN)
    expr()
    co_code.append(PRINT_ITEM)
    co_code.append(PRINT_NEWLINE)
    consume(RIGHTPAREN)


def expr():
    term()
    while token.category == PLUS:
        advance()
        term()
        co_code.append(BINARY_ADD)


def term():
    global sign
    sign = 1
    factor()
    while token.category == TIMES:
        advance()
        sign = 1
        factor()
        co_code.append(BINARY_MULTIPLY)


def factor():
    global sign
    if token.category == PLUS:
        advance()
        factor()
    elif token.category == MINUS:
        sign = -sign
        advance()
        factor()
    elif token.category == UNSIGNEDINT:
        v = sign * int(token.lexeme)
        if v in co_consts:
            index = co_consts.index(v)
        else:
            index = len(co_consts)
            co_consts.append(v)
        co_code.append(LOAD_CONST)
        co_code.append(index)
        advance()
    elif token.category == NAME:
        if token.lexeme in co_names:
            index = co_names.index(token.lexeme)
        else:
            raise RuntimeError('Name ' + token.lexeme + ' is not defined')
        co_code.append(LOAD_NAME)        
        co_code.append(index)
        if sign == -1:
            co_code.append(UNARY_NEGATIVE)
        advance()
    elif token.category == LEFTPAREN:
        advance()
        savesign = sign
        expr()
        if savesign == -1:
            co_code.append(UNARY_NEGATIVE)
        consume(RIGHTPAREN)
    else:
        raise RuntimeError('Expecting factor')


# byte interpreter
def interpreter():
    co_values = [None] * len(co_names)
    stack = []
    pc = 0

    while pc < len(co_code):
        opcode = co_code[pc]
        pc += 1

        if opcode == UNARY_NEGATIVE:
            stack[-1] = -stack[-1]
        elif opcode == BINARY_MULTIPLY:
            right = stack.pop()
            left = stack.pop()
            stack.append(left * right)
        elif opcode == BINARY_ADD:
            pass
        elif opcode == PRINT_ITEM:
            print(stack.pop(), end='')
        elif opcode == PRINT_NEWLINE:
            pass
        elif opcode == STORE_NAME:
            pass
        elif opcode == LOAD_CONST:
            index = co_code[pc]
            pc += 1
            value = co_consts[index]
            stack.append(value)
        elif opcode == LOAD_NAME:
            index = co_code[pc]
            pc += 1
            value = co_values[index]
            if value == None:
                print('No value for ' + co_names[index])
                sys.exit(-1)
            stack.append(value)
        else:
            break

####################
# start of program #
####################

main()

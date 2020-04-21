import sys

class Token:
    def __init__(self, line, column, category, lexeme):
        self.line = line
        self.column = column
        self.category = category
        self.lexeme = lexeme

source = ''
sourceindex = 0
line = 0
column = 0
tokenlist = []
prevchar = '\n'
blankline = True

EOF           = 0      # end of file
PRINT         = 1      # 'print' keyword
UNSIGNEDINT   = 2      # integer
NAME          = 3      # identifier that is not a keyword
ASSIGNOP      = 4      # '=' assignment operator
LEFTPAREN     = 5      # '('
RIGHTPAREN    = 6      # ')'
PLUS          = 7      # '+'
MINUS         = 8      # '-'
TIMES         = 9      # '*'
NEWLINE       = 10     # newline character
ERROR         = 11     # if not any of the above, then error

catnames = ['EOF', 'print', 'UNSIGNEDINT', 'NAME', 'ASSIGNOP',
            'LEFTPAREN', 'RIGHTPAREN', 'PLUS', 'MINUS',
            'TIMES', 'NEWLINE','ERROR']

keywords = {'print': PRINT}

smalltokens = {'=':ASSIGNOP, '(':LEFTPAREN, ')':RIGHTPAREN,
               '+':PLUS, '-':MINUS, '*':TIMES, '\n':NEWLINE, '':EOF}

def main():
    global source

    if len(sys.argv) == 2:
        try:
            infile = open(sys.argv[1], 'r')
            source = infile.read()
        except IOError:
            print('Cannot read input file ' + sys.argv[1])
            sys.exit(1)
    else:
        print('Wrong number of command line arguments')
        print('format: python t1.py <infile>')
        sys.exit(1)
    
    if source[-1] != '\n':
        source += '\n'

    print('Line  Col Category       Lexeme\n')
    try:
        tokenizer()
    except RuntimeError as emsg:
        lexeme = token.lexeme.replace('\n', '\\n')
        print('\nError on '+ "'" + lexeme + "'" + ' line ' +
        str(token.line) + ' column ' + str(token.column))
        print(emsg)
        sys.exit(1)

def tokenizer():
    global token
    curchar = ' '

    while True:
        while curchar != '\n' and curchar.isspace():
            curchar = getchar()

        token = Token(line, column, None, '')

        if curchar.isdigit():
            token.category = UNSIGNEDINT
            while True:
                token.lexeme += curchar
                curchar = getchar()
                if not curchar.isdigit():
                    break
        elif curchar.isalpha() or curchar == '_':
            while True:
                token.lexeme += curchar
                curchar = getchar()
                if not (curchar.isalnum() or curchar == '_'):
                    break
            if token.lexeme in keywords:
                token.category = keywords[token.lexeme]
            else:
                token.category = NAME
        elif curchar in smalltokens:
            token.category = smalltokens[curchar]
            token.lexeme = curchar
            curchar = getchar()
        else:
            token.category = ERROR
            token.lexeme = curchar
            raise RuntimeError('Invalid token')
        
        tokenlist.append(token)
        displaytoken(token)
        if token.category == EOF:
            break

def getchar():
    global sourceindex, column, line, prevchar, blankline

    if prevchar == '\n':
        line += 1
        column = 0
        blankline = True
    
    if sourceindex >= len(source):
        column = 1
        prevchar = ''
        return ''

    c = source[sourceindex]
    sourceindex += 1
    column += 1
    if not c.isspace():
        blankline = False
    prevchar = c

    if c == '\n' and blankline:
        return ' '
    else:
        return c

def displaytoken(t):
    print("%3s %4s  %-14s %s" % (str(t.line), str(t.column), 
         catnames[t.category], t.lexeme))

# main()

    
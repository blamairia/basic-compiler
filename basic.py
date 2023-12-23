import ply.lex as lex
import ply.yacc as yacc

# Define the list of token names
tokens = (
    'TEXT',
    'STAR',
    'UNDER',
    'LBK',
    'RBK',
    'LP',
    'RP',
    'LB',
    'RB',
    'SEP',
    'VAR',
    'DEF',
    'FUNC',
    'PARAGRAPH'
)

# Regular expressions for tokens
t_STAR = r'\*'
t_UNDER = r'_'
t_LBK = r'\{'
t_RBK = r'\}'
t_LP = r'\('
t_RP = r'\)'
t_LB = r'\['
t_RB = r'\]'
t_SEP = r'\"[^\"]*\"'  # Matches a sequence between quotes
t_VAR = r'\$[a-zA-Z0-9]+'
t_DEF = r'\#def'
t_FUNC = r'\@[a-zA-Z0-9_]+'

def t_PARAGRAPH(t):
    r'(\n\n)+'
    return t

def t_TEXT(t):
    r'[^*\_{}\[\]()\"#$@\n]+'
    return t

# Track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Characters to ignore (spaces and tabs)
t_ignore = ' \t'

# Error handling for illegal characters
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()


    
def p_start(p):
    '''start : start one_def
             | start reg_block
             | empty'''
    if len(p) == 2:  # Only one item means it's 'empty' or a single block.
        p[0] = [] if p[1] is None else [p[1]]
    else:
        p[0] = (p[1] if p[1] is not None else []) + [p[2]]


def p_one_def(p):
    'one_def : DEF FUNC LP SEP RP LB smd RB'
    # Handle a definition here

def p_smd(p):
    '''smd : smd reg_block
           | reg_block'''
    # Handle SMD structure here

def p_reg_block(p):
    '''reg_block : TEXT
                 | STAR in_bold_italic STAR
                 | UNDER in_bold_italic UNDER
                 | LBK smd RBK LP TEXT RP
                 | PARAGRAPH
                 | FUNC LB smd RB
                 | VAR'''
    # Handle regular block here

def p_in_bold_italic(p):
    '''in_bold_italic : TEXT
                      | LBK smd RBK LP TEXT RP
                      | PARAGRAPH
                      | FUNC LB smd RB
                      | VAR'''
    # Handle in bold italic here

def p_empty(p):
    'empty :'
    pass

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

# Test the parser
def test_parser(input_string):
    result = parser.parse(input_string, lexer=lexer)
    return result

# Replace this with your SMD input text
test_string = "Your SMD language input text *bold* here."
result = test_parser(test_string)
print(result)
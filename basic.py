import ply.lex as lex
import ply.yacc as yacc

# Tokens as per the document
tokens = (
    'TEXT', 'STAR', 'UNDER', 'LBK', 'RBK', 'LP', 'RP', 'LB', 'RB', 'SEP', 'VAR', 'DEF', 'FUNC', 'PARAGRAPH'
)

# Regular expressions for tokens
t_ignore = ' \t'
t_STAR = r'\*'
t_UNDER = r'_'
t_LBK = r'\{'
t_RBK = r'\}'
t_LP = r'\('
t_RP = r'\)'
t_LB = r'\['
t_RB = r'\]'
t_SEP = r'\"[^\"]*\"'  # Matches a sequence between quotes
t_VAR = r'\$[a-zA-Z0-9_]+'
t_DEF = r'\#def'
t_FUNC = r'\@[a-zA-Z0-9_]+'
t_PARAGRAPH = r'(\n\n)+'  # Matches two or more newline characters

# Special case for escaped characters
def t_escape(t):
    r'\\.'
    t.type = "TEXT"
    t.value = t.value[1]  # Remove backslash
    return t

def t_TEXT(t):
    r'[^*\_{}\[\]()\"#$@\n\\]+'
    return t

# Track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling for illegal characters
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Parser rules
# Global variable to track declared functions and their definitions
declared_functions = {}

# Parsing rules based on the grammar provided
def p_start(p):
    '''start : one_def
             | start element
             | empty'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = p[1] + [p[2]]

def p_one_def(p):
    'one_def : DEF FUNC LP SEP RP LB elements RB'
    func_name = p[2][1:]  # Remove @ from the function name
    if func_name in declared_functions:
        raise SyntaxError(f"Function '{func_name}' is already defined")
    declared_functions[func_name] = {'separator': p[4], 'body': p[7]}
    p[0] = {'type': 'function_def', 'name': func_name}

def p_elements(p):
    '''elements : element
                | elements element'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]
def p_reg_block(p):
    '''reg_block : TEXT
                 | STAR bold_element STAR
                 | UNDER italic_element UNDER
                 | LBK smd RBK LP TEXT RP
                 | PARAGRAPH
                 | FUNC LB arguments RP
                 | VAR'''
    # Example for handling a link defined with { and }
    if len(p) == 7:
        # Assuming LBK smd RBK LP TEXT RP is a link
        p[0] = {'type': 'link', 'url': p[2], 'text': p[5]}
    else:
        p[0] = {'type': 'text', 'content': p[1]}
# Add this function definition to your code




# Adjust the smd rule to properly combine reg_blocks
def p_smd(p):
    '''smd : reg_block
           | smd reg_block'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]
def p_element(p):
    '''element : text_element
               | bold_element
               | italic_element
               | link_element
               | variable_element
               | paragraph_element
               | function_definition
               | function_call'''
    p[0] = p[1]

def p_text_element(p):
    'text_element : TEXT'
    p[0] = {'type': 'text', 'content': p[1]}

def p_bold_element(p):
    'bold_element : STAR TEXT STAR'
    p[0] = {'type': 'bold', 'content': p[2]}

def p_italic_element(p):
    'italic_element : UNDER TEXT UNDER'
    p[0] = {'type': 'italic', 'content': p[2]}

def p_link_element(p):
    'link_element : LB TEXT RB LP TEXT RP'
    p[0] = {'type': 'link', 'text': p[2], 'url': p[5]}

def p_variable_element(p):
    'variable_element : VAR'
    p[0] = {'type': 'variable', 'name': p[1]}

def p_paragraph_element(p):
    'paragraph_element : PARAGRAPH'
    p[0] = {'type': 'paragraph'}

def p_function_definition(p):
    'function_definition : DEF FUNC LP SEP RP LB elements RB'
    func_name = p[2][1:]  # Remove @ from the function name
    declared_functions[func_name] = {'params': p[4], 'body': p[7]}
    p[0] = {'type': 'function_def', 'name': func_name}

def p_function_call(p):
    'function_call : FUNC LP arguments RP'
    p[0] = {'type': 'function_call', 'name': p[1], 'arguments': p[3]}

def p_arguments(p):
    '''arguments : argument
                 | arguments SEP argument'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_argument(p):
    '''argument : TEXT
                | VAR
                | FUNC'''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    p[0] = []

# Error rule for syntax errors
def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' on line {p.lineno}")
    else:
        print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc()

# Rendering function
def render(parsed_elements, variables):
    html = ""
    for element in parsed_elements:
        if isinstance(element, dict):
            if element['type'] == 'text':
                html += element['content']
            elif element['type'] == 'bold':
                html += f"<strong>{element['content']}</strong>"
            elif element['type'] == 'italic':
                html += f"<i>{element['content']}</i>"
            elif element['type'] == 'link':
                html += f"<a href=\"{element['url']}\">{element['text']}</a>"
            elif element['type'] == 'variable':
                var_name = element['name'][1:]  # strip $ and replace with variable value
                html += variables.get(var_name, var_name)  # Use the variable name itself if not found in variables
            elif element['type'] == 'paragraph':
                html += "<br>"
            elif element['type'] == 'function_call':
                html += execute_function(element, variables)
        else:
            # If it's not a dictionary, it's a list or a string
            if isinstance(element, list):
                # If it's a list, recursively call render on it
                html += render(element, variables)
            else:
                # If it's a string (for plain text), just append it
                html += element
    return html

# Function execution with error checking
def execute_function(func, variables):
    func_name = func['name'][1:]  # Remove @ from the name
    if func_name not in declared_functions:
        raise NameError(f"Call to undeclared function '{func_name}'")

    function_def = declared_functions[func_name]
    args = func['arguments'][0].split(function_def['separator'])
    local_vars = {f"${i}": arg for i, arg in enumerate(args)}
    local_vars["$0"] = func['arguments'][0]

    # Check for references to variables that exceed the split array's size
    for part in function_def['body']:
        if isinstance(part, dict) and part['type'] == 'variable':
            var_name = part['content'][1:]  # strip $ and get the variable name
            if var_name not in local_vars:
                raise IndexError(f"Reference to undefined variable '{var_name}' in function '{func_name}'")
            # Replace variable with its value
            part['content'] = local_vars[var_name]

    return render(function_def['body'], local_vars)

# Example test
test_string = "Aujourd'hui, le *05 décembre 2023*, il fait doux à $ville. D'autres _informations_ sont disponibles sur [notre site](meteo.dz). @date(05/12/2023)"
variables = {
    'ville': 'Annaba',
    '@date': {
        'separator': '/',
        'body': [
            {'type': 'bold', 'content': '$1'},
            {'type': 'text', 'content': ' '},
            {'type': 'italic', 'content': '$2'},
            {'type': 'text', 'content': ' '},
            {'type': 'text', 'content': '$3'}
        ]
    }
}

try:
    parsed_elements = parser.parse(test_string, lexer=lexer)
    # Assuming 'render' is fully implemented based on document specification
    html_output = render(parsed_elements, variables)
    print(html_output)
except SyntaxError as se:
    print(f"SyntaxError: {se}")
except NameError as ne:
    print(f"NameError: {ne}")
except IndexError as ie:
    print(f"IndexError: {ie}")
 
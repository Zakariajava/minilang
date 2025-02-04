#############################################
#  compilador_minilang.py
#  Versión con llamadas a subrutina en expresiones
#  (expression : ID LPAREN arg_list RPAREN)
#
#  Maneja:
#    - const_section, var_section
#    - subroutine_section con SUBROUTINE <TYPE> <ID> (param_list) DO statements END
#    - main en minúsculas
#    - llamadas a subrutina tanto como statement (call_stmt;) como en expresiones
#
#  Pasos:
#    1) Análisis Léxico (PLY)
#    2) Análisis Sintáctico (PLY)
#    3) Construcción de AST
#    4) Análisis Semántico
#   
#   Autor : Zakaria Abouhammadi
#   Fecha : 02/01/2025
#
#############################################

import sys
import ply.lex as lex
import ply.yacc as yacc

# =========================================================
#   1) ANALISIS LEXICO
# =========================================================

# Palabras reservadas en MAYÚSCULAS
reserved = {
    'CONST':      'CONST',
    'SUBROUTINE': 'SUBROUTINE',
    'DO':         'DO',
    'END':        'END',
    'IF':         'IF',
    'THEN':       'THEN',
    'ELSE':       'ELSE',
    'WHILE':      'WHILE',
    'RETURN':     'RETURN',
    'PRINT':      'PRINT',
    'TRUE':       'TRUE',
    'FALSE':      'FALSE',
    'VOID':       'VOID',
    'INT':        'INT',
    'BOOL':       'BOOL',
    'STRING':     'STRING',
    'AND':        'AND',
    'OR':         'OR',
    'NOT':        'NOT'
}

tokens = [
    'ID',
    'PLUS', 'MINUS',
    'TIMES', 'DIVIDE',
    'EQ', 'NEQ',
    'GT', 'LT',
    'ASSIGN',
    'LPAREN', 'RPAREN',
    'SEMICOLON', 'COMMA',
    'INT_LITERAL',
    'STRING_LITERAL',
] + list(reserved.values())

# Reglas léxicas simples
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_EQ        = r'=='
t_NEQ       = r'!='
t_GT        = r'>'
t_LT        = r'<'
t_ASSIGN    = r'='
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_SEMICOLON = r';'
t_COMMA     = r','

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]  # palabra reservada
    return t

def t_INT_LITERAL(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING_LITERAL(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]  # quitar comillas
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print(f"[Lexer] Caracter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# =========================================================
#   2) ANALISIS SINTACTICO
# =========================================================

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'NOT'),
)

# -------------------------
#       AST NODES
# -------------------------
class ProgramNode:
    def __init__(self, consts, vars_, subs):
        self.consts = consts   # lista de ConstDeclNode
        self.vars_ = vars_     # lista de VarDeclNode
        self.subs = subs       # lista de SubroutineNode

class ConstDeclNode:
    def __init__(self, ctype, name, value):
        self.ctype = ctype
        self.name = name
        self.value = value

class VarDeclNode:
    def __init__(self, vtype, name, value=None):
        self.vtype = vtype
        self.name = name
        self.value = value

class SubroutineNode:
    def __init__(self, rtype, name, params, body):
        self.rtype = rtype    # 'VOID','INT','BOOL','STRING'
        self.name = name
        self.params = params  # lista de ParamNode
        self.body = body      # lista de statements

class ParamNode:
    def __init__(self, ptype, pname):
        self.ptype = ptype
        self.pname = pname

class AssignNode:
    def __init__(self, varname, expr):
        self.varname = varname
        self.expr = expr

class IfNode:
    def __init__(self, condition, then_block, else_block):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

class WhileNode:
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

class ReturnNode:
    def __init__(self, expr):
        self.expr = expr

class PrintNode:
    def __init__(self, expr):
        self.expr = expr

class CallNode:
    def __init__(self, funcname, args):
        self.funcname = funcname
        self.args = args

class BinOpNode:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnOpNode:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class IntLiteralNode:
    def __init__(self, value):
        self.value = value

class StringLiteralNode:
    def __init__(self, value):
        self.value = value

class BoolLiteralNode:
    def __init__(self, value):
        self.value = value

class VarRefNode:
    def __init__(self, name):
        self.name = name

# -------------------------
#   GRAMÁTICA
# -------------------------
def p_program(p):
    '''
    program : const_section var_section subroutine_section
    '''
    p[0] = ProgramNode(p[1], p[2], p[3])

# Sección de constantes 0..n
def p_const_section(p):
    '''
    const_section : const_section const_declaration
                  | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_const_declaration(p):
    '''
    const_declaration : CONST type ID ASSIGN expression SEMICOLON
    '''
    p[0] = ConstDeclNode(p[2], p[3], p[5])

# Sección de variables 0..n
def p_var_section(p):
    '''
    var_section : var_section var_declaration
                | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_var_declaration(p):
    '''
    var_declaration : type ID ASSIGN expression SEMICOLON
                    | type ID SEMICOLON
    '''
    if len(p) == 6:
        p[0] = VarDeclNode(p[1], p[2], p[4])
    else:
        p[0] = VarDeclNode(p[1], p[2], None)

# Sección de subrutinas 0..n
def p_subroutine_section(p):
    '''
    subroutine_section : subroutine_section subroutine_decl
                       | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_subroutine_decl(p):
    '''
    subroutine_decl : SUBROUTINE subroutine_type ID LPAREN param_list RPAREN DO statement_list END
    '''
    p[0] = SubroutineNode(p[2], p[3], p[5], p[8])

def p_subroutine_type(p):
    '''
    subroutine_type : VOID
                    | INT
                    | BOOL
                    | STRING
    '''
    p[0] = p[1]

def p_param_list(p):
    '''
    param_list : param_list COMMA param_decl
               | param_decl
               | empty
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_param_decl(p):
    '''
    param_decl : type ID
    '''
    p[0] = ParamNode(p[1], p[2])

def p_statement_list(p):
    '''
    statement_list : statement_list statement
                   | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_statement(p):
    '''
    statement : assignment_stmt
              | if_stmt
              | while_stmt
              | return_stmt
              | print_stmt
              | call_stmt SEMICOLON
    '''
    p[0] = p[1]

def p_assignment_stmt(p):
    '''
    assignment_stmt : ID ASSIGN expression SEMICOLON
    '''
    p[0] = AssignNode(p[1], p[3])

def p_if_stmt(p):
    '''
    if_stmt : IF LPAREN expression RPAREN THEN statement_list else_part END
    '''
    p[0] = IfNode(p[3], p[6], p[7])

def p_else_part(p):
    '''
    else_part : ELSE statement_list
              | empty
    '''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = []

def p_while_stmt(p):
    '''
    while_stmt : WHILE LPAREN expression RPAREN DO statement_list END
    '''
    p[0] = WhileNode(p[3], p[6])

def p_return_stmt(p):
    '''
    return_stmt : RETURN expression SEMICOLON
    '''
    p[0] = ReturnNode(p[2])

def p_print_stmt(p):
    '''
    print_stmt : PRINT LPAREN expression RPAREN SEMICOLON
    '''
    p[0] = PrintNode(p[3])

# llamada a subrutina como statement
def p_call_stmt(p):
    '''
    call_stmt : ID LPAREN arg_list RPAREN
    '''
    p[0] = CallNode(p[1], p[3])

# lista de argumentos
def p_arg_list(p):
    '''
    arg_list : arg_list COMMA expression
             | expression
             | empty
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

# ---------------------------------------------------------
#  *** CORRECCIÓN PARA LLAMADAS A SUBRUTINA EN EXPRESIONES ***
# ---------------------------------------------------------
def p_expression_call(p):
    '''
    expression : ID LPAREN arg_list RPAREN
    '''
    # Llamada a subrutina devuelta como un valor en una expresión
    p[0] = CallNode(p[1], p[3])

def p_expression_binop(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression EQ expression
               | expression NEQ expression
               | expression GT expression
               | expression LT expression
               | expression AND expression
               | expression OR expression
    '''
    p[0] = BinOpNode(p[2], p[1], p[3])

def p_expression_unop(p):
    '''
    expression : NOT expression
    '''
    p[0] = UnOpNode(p[1], p[2])

def p_expression_paren(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    p[0] = p[2]

def p_expression_int(p):
    '''
    expression : INT_LITERAL
    '''
    p[0] = IntLiteralNode(p[1])

def p_expression_string(p):
    '''
    expression : STRING_LITERAL
    '''
    p[0] = StringLiteralNode(p[1])

def p_expression_bool(p):
    '''
    expression : TRUE
               | FALSE
    '''
    val = (p[1] == 'TRUE')
    p[0] = BoolLiteralNode(val)

def p_expression_varref(p):
    '''
    expression : ID
    '''
    p[0] = VarRefNode(p[1])

def p_type(p):
    '''
    type : VOID
         | INT
         | BOOL
         | STRING
    '''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"[Parser] Error de sintaxis en token '{p.value}', línea {p.lineno}")
    else:
        print("[Parser] Error de sintaxis (EOF)")

parser = yacc.yacc()

# =========================================================
#   3) ANALISIS SEMANTICO
# =========================================================

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def declare(self, name, info):
        current = self.scopes[-1]
        if name in current:
            raise Exception(f"[Semántico] Identificador '{name}' ya declarado en este ámbito.")
        current[name] = info

    def get(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

def check_semantics(ast_root):
    symbol_table = SymbolTable()

    # 1) Declarar constantes globales
    for c in ast_root.consts:
        symbol_table.declare(c.name, {
            'type': c.ctype,
            'isConst': True
        })

    # 2) Declarar variables globales
    for v in ast_root.vars_:
        symbol_table.declare(v.name, {
            'type': v.vtype,
            'isConst': False
        })

    # 3) Declarar subrutinas
    for s in ast_root.subs:
        symbol_table.declare(s.name, {
            'type': s.rtype,
            'isSubroutine': True,
            'params': [(p.ptype, p.pname) for p in s.params]
        })

    # 4) Buscar 'main' en minúsculas
    main_found = False
    for s in ast_root.subs:
        if s.name == 'main':
            main_found = True
            if s.rtype != 'VOID':
                raise Exception("[Semántico] 'main' debe ser 'VOID'.")

    if not main_found:
        raise Exception("[Semántico] No se encontró la subrutina principal 'main'.")

# =========================================================
#   MAIN
# =========================================================

def main():
    if len(sys.argv) < 2:
        print("Uso: python compilador_minilang.py <archivo.minilang>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    try:
        ast = parser.parse(code, lexer=lexer, debug=False)  # debug=True si quieres ver la traza
    except Exception as e:
        print(e)
        sys.exit(1)

    if not ast:
        print("[Parser] No se pudo construir el AST (posible error de sintaxis).")
        sys.exit(1)

    # Análisis semántico
    try:
        check_semantics(ast)
        print("[OK] El código MiniLang es semánticamente válido.")
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
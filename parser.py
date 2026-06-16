import ply.yacc as yacc
from ast import *
from lexer import tokens, lexer

class RubricaParser:
    tokens = tokens

    def __init__(self):
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)
        self.ast = None
        self.hubo_error = False   # 🔥 bandera para detectar error sintáctico

    def parse(self, data):
        self.hubo_error = False
        self.ast = self.parser.parse(data, lexer=lexer)
        if self.hubo_error:
            return None
        return self.ast

    # Definición de precedencia (de menor a mayor)
    precedence = (
        ('left', 'IGUAL', 'DISTINTO'),      # == !=
        ('left', 'MENOR', 'MAYOR', 'MENOR_IGUAL', 'MAYOR_IGUAL'),
        ('left', 'MAS', 'MENOS'),           # + -
        ('left', 'MULT', 'DIV'),            # * /
        ('right', 'UMENOS'),                # unario -
    )

    # Cada método p_xxx define una regla gramatical.
    # p[0] es el resultado (el nodo AST), p[1], p[2], ... son los elementos de la regla.

    def p_programa(self, p):
        '''programa : sentencias'''
        p[0] = Programa(p[1])

    def p_sentencias(self, p):
        '''sentencias : sentencia sentencias
                      | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_sentencia(self, p):
        '''sentencia : declaracion_var
                     | asignacion
                     | estructura_control
                     | definicion_rubrica'''
        p[0] = p[1]

    def p_declaracion_var(self, p):
        '''declaracion_var : tipo IDENT PUNTO_Y_COMA
                           | tipo IDENT ASIGN expr PUNTO_Y_COMA'''
        if len(p) == 4:   # sin inicialización
            p[0] = DeclaracionVar(p[1], p[2], None, p.lineno(2), self.find_column(p.slice[2]))
        else:             # con inicialización
            p[0] = DeclaracionVar(p[1], p[2], p[4], p.lineno(2), self.find_column(p.slice[2]))

    def p_tipo(self, p):
        '''tipo : TIPO_NUMERO
                | TIPO_DECIMAL
                | TIPO_CADENA'''
        p[0] = p[1]   # devuelve el string: 'numero', 'decimal', 'cadena'

    def p_asignacion(self, p):
        '''asignacion : IDENT ASIGN expr PUNTO_Y_COMA'''
        p[0] = Asignacion(p[1], p[3], p.lineno(1), self.find_column(p.slice[1]))

    def p_estructura_control(self, p):
        '''estructura_control : SI PAR_IZQ expr PAR_DER bloque
                              | SI PAR_IZQ expr PAR_DER bloque SINO bloque
                              | MIENTRAS PAR_IZQ expr PAR_DER bloque'''
        if p[1] == 'si':
            if len(p) == 6:  # if sin else
                p[0] = IfElse(p[3], p[5], None, p.lineno(1), self.find_column(p.slice[1]))
            else:             # if con else
                p[0] = IfElse(p[3], p[5], p[7], p.lineno(1), self.find_column(p.slice[1]))
        else:  # mientras
            p[0] = While(p[3], p[5], p.lineno(1), self.find_column(p.slice[1]))

    def p_bloque(self, p):
        '''bloque : LLAVE_IZQ sentencias LLAVE_DER'''
        p[0] = p[2]   # devuelve la lista de sentencias dentro del bloque

    def p_definicion_rubrica(self, p):
        '''definicion_rubrica : RUBRICA IDENT LLAVE_IZQ criterios LLAVE_DER'''
        p[0] = DefinicionRubrica(p[2], p[4], p.lineno(2), self.find_column(p.slice[2]))

    def p_criterios(self, p):
        '''criterios : criterio criterios
                     | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_criterio(self, p):
        '''criterio : CRITERIO IDENT PESO expr LLAVE_IZQ niveles LLAVE_DER PUNTO_Y_COMA'''
        p[0] = Criterio(p[2], p[4], p[6], p.lineno(2), self.find_column(p.slice[2]))

    def p_niveles(self, p):
        '''niveles : nivel niveles
                   | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_nivel(self, p):
        '''nivel : NIVEL CADENA expr PUNTO_Y_COMA'''
        p[0] = Nivel(p[2], p[3], p.lineno(1), self.find_column(p.slice[1]))

    # ---------- Reglas para expresiones (con precedencia integrada) ----------
    def p_expr(self, p):
        '''expr : expr_logica'''
        p[0] = p[1]

    def p_expr_logica_bin(self, p):
        '''expr_logica : expr_relacional IGUAL expr_relacional
                       | expr_relacional DISTINTO expr_relacional'''
        p[0] = BinOp(p[2], p[1], p[3])

    def p_expr_logica_simple(self, p):
        '''expr_logica : expr_relacional'''
        p[0] = p[1]

    def p_expr_relacional(self, p):
        '''expr_relacional : expr_aditiva
                           | expr_aditiva MENOR expr_aditiva
                           | expr_aditiva MAYOR expr_aditiva
                           | expr_aditiva MENOR_IGUAL expr_aditiva
                           | expr_aditiva MAYOR_IGUAL expr_aditiva'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(p[2], p[1], p[3])

    def p_expr_aditiva(self, p):
        '''expr_aditiva : expr_multiplicativa
                        | expr_aditiva MAS expr_multiplicativa
                        | expr_aditiva MENOS expr_multiplicativa'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(p[2], p[1], p[3])

    def p_expr_multiplicativa(self, p):
        '''expr_multiplicativa : expr_unaria
                               | expr_multiplicativa MULT expr_unaria
                               | expr_multiplicativa DIV expr_unaria'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(p[2], p[1], p[3])

    def p_expr_unaria(self, p):
        '''expr_unaria : MAS expr_unaria %prec UMENOS
                       | MENOS expr_unaria %prec UMENOS
                       | primaria'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = UnaryOp(p[1], p[2])

    def p_primaria(self, p):
        '''primaria : NUMERO
                    | DECIMAL
                    | CADENA
                    | IDENT
                    | PAR_IZQ expr PAR_DER'''
        if len(p) == 2:
            token_type = p.slice[1].type
            if token_type == 'NUMERO':
                p[0] = LiteralNum(p[1])
            elif token_type == 'DECIMAL':
                p[0] = LiteralDecimal(p[1])
            elif token_type == 'CADENA':
                p[0] = LiteralString(p[1])
            elif token_type == 'IDENT':
                p[0] = Variable(p[1], p.lineno(1), self.find_column(p.slice[1]))
            else:
                p[0] = p[1]
        else:
            p[0] = p[2]

    def p_empty(self, p):
        'empty :'
        pass

    # Manejo de errores sintácticos con bandera y recuperación (modo pánico)
    def p_error(self, p):
        self.hubo_error = True   # 🔥 marca que hubo error
        if p:
            col = self.find_column(p)
            print(f"Error sintáctico [línea {p.lineno}, columna {col}]: token inesperado '{p.value}'")
            # Sincronización: avanzar hasta encontrar ';', '}' o palabra reservada
            while True:
                tok = lexer.token()
                if not tok:
                    break
                if tok.type in ('PUNTO_Y_COMA', 'LLAVE_DER', 'RUBRICA', 'SI', 'MIENTRAS'):
                    break
        else:
            print("Error sintáctico: fin de archivo inesperado")

    # Helper para calcular columna a partir de la posición del token
    def find_column(self, token):
        last_cr = lexer.lexdata.rfind('\n', 0, token.lexpos)
        if last_cr < 0:
            last_cr = 0
        return token.lexpos - last_cr + 1
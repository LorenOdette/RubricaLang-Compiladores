# ast.py
# Definición de todos los nodos del AST

class ASTNode:
    pass

class Programa(ASTNode):
    def __init__(self, sentencias):
        self.sentencias = sentencias

class DeclaracionVar(ASTNode):
    def __init__(self, tipo, nombre, expr, linea, columna):
        self.tipo = tipo      # 'numero', 'decimal', 'cadena'
        self.nombre = nombre
        self.expr = expr      # puede ser None
        self.linea = linea
        self.columna = columna

class Asignacion(ASTNode):
    def __init__(self, nombre, expr, linea, columna):
        self.nombre = nombre
        self.expr = expr
        self.linea = linea
        self.columna = columna

class IfElse(ASTNode):
    def __init__(self, condicion, bloque_if, bloque_else, linea, columna):
        self.condicion = condicion
        self.bloque_if = bloque_if   # lista de sentencias
        self.bloque_else = bloque_else  # lista de sentencias o None
        self.linea = linea
        self.columna = columna

class While(ASTNode):
    def __init__(self, condicion, bloque, linea, columna):
        self.condicion = condicion
        self.bloque = bloque   # lista de sentencias
        self.linea = linea
        self.columna = columna

class DefinicionRubrica(ASTNode):
    def __init__(self, nombre, criterios, linea, columna):
        self.nombre = nombre
        self.criterios = criterios   # lista de Criterio
        self.linea = linea
        self.columna = columna

class Criterio(ASTNode):
    def __init__(self, nombre, peso, niveles, linea, columna):
        self.nombre = nombre
        self.peso = peso        # expresión (debe evaluarse a número)
        self.niveles = niveles  # lista de Nivel
        self.linea = linea
        self.columna = columna

class Nivel(ASTNode):
    def __init__(self, descripcion, puntuacion, linea, columna):
        self.descripcion = descripcion  # string (ya procesado)
        self.puntuacion = puntuacion    # expresión numérica
        self.linea = linea
        self.columna = columna

# Nodos para expresiones
class BinOp(ASTNode):
    def __init__(self, op, izquierda, derecha):
        self.op = op
        self.izquierda = izquierda
        self.derecha = derecha

class UnaryOp(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class LiteralNum(ASTNode):
    def __init__(self, valor):
        self.valor = int(valor)

class LiteralDecimal(ASTNode):
    def __init__(self, valor):
        self.valor = float(valor)

class LiteralString(ASTNode):
    def __init__(self, valor):
        self.valor = valor

class Variable(ASTNode):
    def __init__(self, nombre, linea, columna):
        self.nombre = nombre
        self.linea = linea
        self.columna = columna
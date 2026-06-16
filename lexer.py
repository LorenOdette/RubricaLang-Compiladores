# lexer.py
import ply.lex as lex

# Lista de todos los tokens
tokens = [
    # Palabras reservadas del DSL
    'RUBRICA', 'CRITERIO', 'PESO', 'NIVEL', 'TOTAL', 'DESCRIPCION',
    # Estructuras de control
    'SI', 'SINO', 'MIENTRAS',
    # Tipos
    'TIPO_NUMERO', 'TIPO_DECIMAL', 'TIPO_CADENA',
    # Literales
    'NUMERO', 'DECIMAL', 'CADENA', 'IDENT',
    # Operadores aritméticos
    'MAS', 'MENOS', 'MULT', 'DIV',
    # Operadores relacionales
    'MENOR', 'MAYOR', 'MENOR_IGUAL', 'MAYOR_IGUAL', 'IGUAL', 'DISTINTO',
    # Asignación
    'ASIGN',
    # Delimitadores
    'PAR_IZQ', 'PAR_DER', 'LLAVE_IZQ', 'LLAVE_DER', 'PUNTO_Y_COMA', 'COMA', 'DOS_PUNTOS',
]

# Palabras reservadas
reserved = {
    'rubrica': 'RUBRICA',
    'criterio': 'CRITERIO',
    'peso': 'PESO',
    'nivel': 'NIVEL',
    'total': 'TOTAL',
    'descripcion': 'DESCRIPCION',
    'si': 'SI',
    'sino': 'SINO',
    'mientras': 'MIENTRAS',
    'numero': 'TIPO_NUMERO',
    'decimal': 'TIPO_DECIMAL',
    'cadena': 'TIPO_CADENA',
}

# Expresiones regulares para tokens simples
t_MAS = r'\+'
t_MENOS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_MENOR = r'<'
t_MAYOR = r'>'
t_MENOR_IGUAL = r'<='
t_MAYOR_IGUAL = r'>='
t_IGUAL = r'=='
t_DISTINTO = r'!='
t_ASIGN = r'='
t_PAR_IZQ = r'\('
t_PAR_DER = r'\)'
t_LLAVE_IZQ = r'\{'
t_LLAVE_DER = r'\}'
t_PUNTO_Y_COMA = r';'
t_COMA = r','
t_DOS_PUNTOS = r':'

# Identificadores y palabras reservadas
def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t

# Literales numéricos (decimal antes que entero para que no confunda)
def t_DECIMAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Cadenas con escapes (soporte básico)
def t_CADENA(t):
    r'\"([^\\\n]|(\\.))*?\"'
    # Eliminar comillas y procesar escapes
    s = t.value[1:-1]
    # Procesar escapes comunes
    escapes = {
        '\\n': '\n',
        '\\t': '\t',
        '\\"': '"',
        '\\\\': '\\'
    }
    for esc, ch in escapes.items():
        s = s.replace(esc, ch)
    t.value = s
    return t

# Comentarios de línea
def t_COMENTARIO_LINEA(t):
    r'//.*'
    pass  # ignorar

# Comentarios de bloque (soportan anidamiento simple, pero no es necesario)
def t_COMENTARIO_BLOQUE(t):
    r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'
    # No se necesita procesar el contenido, solo ignorar
    pass

# Caracteres ignorados
t_ignore = ' \t'

# Control de líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Almacenamiento de errores léxicos
errores_lexicos = []

def t_error(t):
    # Calcular columna
    last_nl = t.lexer.lexdata.rfind('\n', 0, t.lexpos)
    if last_nl < 0:
        col = t.lexpos + 1
    else:
        col = t.lexpos - last_nl
    errores_lexicos.append(f"Error léxico [línea {t.lineno}, columna {col}]: carácter inesperado '{t.value[0]}'")
    t.lexer.skip(1)

# Construir el lexer (instancia global)
lexer = lex.lex()
# semantic.py
from ast import *

class Simbolo:
    def __init__(self, nombre, tipo, inicializada=False, linea=None, columna=None):
        self.nombre = nombre
        self.tipo = tipo        # 'numero', 'decimal', 'cadena'
        self.inicializada = inicializada
        self.linea = linea
        self.columna = columna

class TablaSimbolos:
    def __init__(self):
        self.scopes = [{}]   # pila de diccionarios: cada ámbito es un dict
        self.errores = []

    def entrar_ambito(self):
        self.scopes.append({})

    def salir_ambito(self):
        self.scopes.pop()

    def declarar(self, nombre, tipo, linea, columna, inicializada=False):
        if nombre in self.scopes[-1]:
            self.errores.append(f"Error semántico [línea {linea}, columna {columna}]: variable '{nombre}' ya declarada en este ámbito")
            return False
        self.scopes[-1][nombre] = Simbolo(nombre, tipo, inicializada, linea, columna)
        return True

    def buscar(self, nombre):
        # Buscar desde el ámbito más interno hacia afuera
        for scope in reversed(self.scopes):
            if nombre in scope:
                return scope[nombre]
        return None

    def actualizar_inicializacion(self, nombre, linea, columna):
        sym = self.buscar(nombre)
        if sym:
            sym.inicializada = True
        else:
            self.errores.append(f"Error semántico [línea {linea}, columna {columna}]: variable '{nombre}' no declarada")

    def verificar_usada(self, nombre, linea, columna):
        sym = self.buscar(nombre)
        if not sym:
            self.errores.append(f"Error semántico [línea {linea}, columna {columna}]: variable '{nombre}' no declarada")
            return False
        if not sym.inicializada:
            self.errores.append(f"Error semántico [línea {linea}, columna {columna}]: variable '{nombre}' usada antes de ser inicializada")
            return False
        return True

class AnalizadorSemantico:
    def __init__(self):
        self.ts = TablaSimbolos()
        self.current_rubrica = None   # para acumular pesos

    def analizar(self, ast):
        self.visitar(ast)
        return self.ts.errores

    def visitar(self, nodo):
        # Busca un método llamado visitar_NombreClase y lo ejecuta
        metodo = f'visitar_{type(nodo).__name__}'
        if hasattr(self, metodo):
            getattr(self, metodo)(nodo)
        else:
            # Si no hay visitador específico, recorre recursivamente los hijos
            for attr in dir(nodo):
                if not attr.startswith('_'):
                    hijo = getattr(nodo, attr)
                    if isinstance(hijo, list):
                        for item in hijo:
                            if isinstance(item, ASTNode):
                                self.visitar(item)
                    elif isinstance(hijo, ASTNode):
                        self.visitar(hijo)

    # Visitadores específicos -------------------------------------------------
    def visitar_Programa(self, nodo):
        for s in nodo.sentencias:
            self.visitar(s)

    def visitar_DeclaracionVar(self, nodo):
        tipo_expr = None
        if nodo.expr:
            tipo_expr = self.obtener_tipo_expr(nodo.expr)
            if tipo_expr != nodo.tipo:
                self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: tipo incompatible en inicialización de '{nodo.nombre}': se espera '{nodo.tipo}', se obtiene '{tipo_expr}'")
        self.ts.declarar(nodo.nombre, nodo.tipo, nodo.linea, nodo.columna, inicializada=(nodo.expr is not None))

    def visitar_Asignacion(self, nodo):
        sym = self.ts.buscar(nodo.nombre)
        if not sym:
            self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: variable '{nodo.nombre}' no declarada")
        else:
            tipo_expr = self.obtener_tipo_expr(nodo.expr)
            if tipo_expr != sym.tipo:
                self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: asignación incompatible: '{nodo.nombre}' es '{sym.tipo}', la expresión es '{tipo_expr}'")
            sym.inicializada = True

    def visitar_Variable(self, nodo):
        self.ts.verificar_usada(nodo.nombre, nodo.linea, nodo.columna)
        sym = self.ts.buscar(nodo.nombre)
        return sym.tipo if sym else None

    def visitar_IfElse(self, nodo):
        tipo_cond = self.obtener_tipo_expr(nodo.condicion)
        if tipo_cond not in ('numero', 'decimal'):
            self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: la condición del 'si' debe ser numérica, se obtuvo '{tipo_cond}'")
        self.ts.entrar_ambito()
        for s in nodo.bloque_if:
            self.visitar(s)
        self.ts.salir_ambito()
        if nodo.bloque_else:
            self.ts.entrar_ambito()
            for s in nodo.bloque_else:
                self.visitar(s)
            self.ts.salir_ambito()

    def visitar_While(self, nodo):
        tipo_cond = self.obtener_tipo_expr(nodo.condicion)
        if tipo_cond not in ('numero', 'decimal'):
            self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: la condición del 'mientras' debe ser numérica, se obtuvo '{tipo_cond}'")
        self.ts.entrar_ambito()
        for s in nodo.bloque:
            self.visitar(s)
        self.ts.salir_ambito()

    def visitar_DefinicionRubrica(self, nodo):
        self.ts.entrar_ambito()   # las variables dentro de la rúbrica no afectan afuera
        self.current_rubrica = {
            'nombre': nodo.nombre,
            'peso_total': 0,
        }
        for c in nodo.criterios:
            self.visitar(c)
        # Regla 1: suma de pesos == 100
        if self.current_rubrica['peso_total'] != 100:
            self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: la suma de pesos de los criterios es {self.current_rubrica['peso_total']}, debe ser 100")
        self.ts.salir_ambito()
        self.current_rubrica = None

    def visitar_Criterio(self, nodo):
        peso_val = self.evaluar_constante(nodo.peso)
        if peso_val is not None:
            # Regla 2: peso > 0
            if peso_val <= 0:
                self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: el peso del criterio '{nodo.nombre}' debe ser mayor que 0 (es {peso_val})")
            else:
                if self.current_rubrica:
                    self.current_rubrica['peso_total'] += peso_val
        else:
            self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: el peso debe ser una constante numérica")
        # Regla 3: al menos un nivel
        if len(nodo.niveles) == 0:
            self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: el criterio '{nodo.nombre}' debe tener al menos un nivel")
        for nivel in nodo.niveles:
            self.visitar(nivel)

    def visitar_Nivel(self, nodo):
        punt_val = self.evaluar_constante(nodo.puntuacion)
        if punt_val is None:
            self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: la puntuación del nivel debe ser una constante numérica")
        elif not isinstance(punt_val, (int, float)):
            self.ts.errores.append(f"Error semántico [línea {nodo.linea}, columna {nodo.columna}]: la puntuación debe ser numérica")

    # Funciones auxiliares para tipo y constantes ---------------------------------
    def obtener_tipo_expr(self, expr):
        if isinstance(expr, LiteralNum):
            return 'numero'
        elif isinstance(expr, LiteralDecimal):
            return 'decimal'
        elif isinstance(expr, LiteralString):
            return 'cadena'
        elif isinstance(expr, Variable):
            sym = self.ts.buscar(expr.nombre)
            return sym.tipo if sym else None
        elif isinstance(expr, BinOp):
            ti = self.obtener_tipo_expr(expr.izquierda)
            td = self.obtener_tipo_expr(expr.derecha)
            if ti is None or td is None:
                return None
            if expr.op in ('+', '-', '*', '/'):
                if ti == td and ti in ('numero', 'decimal'):
                    return ti
                if (ti == 'numero' and td == 'decimal') or (ti == 'decimal' and td == 'numero'):
                    return 'decimal'
                self.ts.errores.append(f"Error semántico: tipos incompatibles en operación '{expr.op}' entre {ti} y {td}")
                return None
            else:  # relacional
                if ti == td or (ti in ('numero','decimal') and td in ('numero','decimal')):
                    return 'numero'
                self.ts.errores.append(f"Error semántico: comparación incompatible entre {ti} y {td}")
                return None
        elif isinstance(expr, UnaryOp):
            return self.obtener_tipo_expr(expr.expr)
        return None

    def evaluar_constante(self, expr):
        """Retorna el valor numérico si la expresión es una constante aritmética, None si depende de variables."""
        if isinstance(expr, LiteralNum):
            return expr.valor
        if isinstance(expr, LiteralDecimal):
            return expr.valor
        if isinstance(expr, BinOp):
            izq = self.evaluar_constante(expr.izquierda)
            der = self.evaluar_constante(expr.derecha)
            if izq is None or der is None:
                return None
            if expr.op == '+':
                return izq + der
            if expr.op == '-':
                return izq - der
            if expr.op == '*':
                return izq * der
            if expr.op == '/':
                return izq / der
        if isinstance(expr, UnaryOp):
            val = self.evaluar_constante(expr.expr)
            if val is None:
                return None
            return -val if expr.op == '-' else val
        return None
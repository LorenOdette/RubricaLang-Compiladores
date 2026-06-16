# main.py
import sys
import os
from lexer import lexer, errores_lexicos
from parser import RubricaParser
from semantic import AnalizadorSemantico

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py archivo.rub")
        sys.exit(1)

    archivo = sys.argv[1]
    if not os.path.exists(archivo):
        print(f"Error: archivo '{archivo}' no encontrado")
        sys.exit(1)

    with open(archivo, 'r', encoding='utf-8') as f:
        codigo = f.read()

    # ---------- FASE 1: LÉXICO ----------
    print("=== ANÁLISIS LÉXICO ===")
    lexer.input(codigo)
    # Consumir todos los tokens para llenar errores_lexicos
    while lexer.token():
        pass
    if errores_lexicos:
        for err in errores_lexicos:
            print(err)
        print("\n[ERROR] El programa contiene errores léxicos. No se procede al análisis sintáctico.")
        sys.exit(1)
    else:
        print("No se encontraron errores léxicos.\n")

    # ---------- FASE 2: SINTÁCTICO (construye AST) ----------
    print("=== ANÁLISIS SINTÁCTICO ===")
    # Reiniciamos el lexer porque ya lo consumimos
    lexer.lineno = 1
    lexer.lexpos = 0
    lexer.input(codigo)
    parser = RubricaParser()
    try:
        ast = parser.parse(codigo)
        if ast is None:
            print("El programa contiene errores sintácticos. No se procede al análisis semántico.")
            sys.exit(1)
        else:
            print("El análisis sintáctico se completó con éxito. AST construido.\n")
    except Exception as e:
        print(f"Error inesperado durante el parsing: {e}")
        sys.exit(1)

    # ---------- FASE 3: SEMÁNTICO ----------
    print("=== ANÁLISIS SEMÁNTICO ===")
    sem = AnalizadorSemantico()
    errores_sem = sem.analizar(ast)
    if errores_sem:
        for err in errores_sem:
            print(err)
        print("\n[ERROR] El programa contiene errores semánticos.")
        sys.exit(1)
    else:
        print("No se encontraron errores semánticos. El programa es válido.")

if __name__ == '__main__':
    main()
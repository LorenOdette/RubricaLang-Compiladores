# RubricaLang - Analizador de rúbricas

## Requisitos
- Python 3.6+
- Instalar PLY: `pip install ply`

## Ejecución
python main.py archivo.rub

## Estructura del proyecto
- lexer.py: analizador léxico
- parser.py: analizador sintáctico (AST)
- semantic.py: analizador semántico
- main.py: programa principal

## Pruebas incluidas
- valida.txt: programa correcto
- error_sintactico.txt: error sintáctico (falta '{')
- error_semantico.txt: suma de pesos != 100
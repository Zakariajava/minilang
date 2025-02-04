# Compilador de MiniLang

Este proyecto es un compilador para **MiniLang**, un lenguaje de programación sencillo diseñado para enseñar los conceptos fundamentales de compiladores. El compilador incluye análisis léxico, sintáctico y semántico, generando un Árbol de Sintaxis Abstracta (AST).

## Características
- **Análisis léxico**: Convierte el código fuente en tokens.
- **Análisis sintáctico**: Valida la estructura gramatical y construye el AST.
- **Análisis semántico**: Verifica reglas de tipos, alcance y consistencia del código.
- **Estructura basada en PLY**: Usa `ply.lex` y `ply.yacc` para definir las reglas de análisis.
- **Soporte para constantes, variables y subrutinas**.
- **Subrutina principal `main` en minúsculas y de tipo `VOID`**.
- **Llamadas a subrutinas tanto en expresiones como en sentencias**.

## Archivos del Proyecto
- `compilador_minilang.py`: Código fuente principal del compilador.
- `informe_minilang.pdf`: Documento con la descripción detallada del compilador y sus decisiones de diseño.
- `parser.out`: Archivo generado con información del parser.
- `parsetab.py`: Tabla de parsing generada automáticamente por PLY.
- `README.txt`: Documento con información básica sobre el proyecto.
- `ejemplos/`: Contiene varios ejemplos de código MiniLang.
    - `ejemplo_dificil1_valido.minilang`, `ejemplo_dificil2_valido.minilang`, `ejemplo_dificil3_valido.minilang`: Ejemplos válidos con estructuras complejas.
    - `ejemplo_facil_valido.minilang`: Ejemplo válido sencillo.
    - `ejemplo_no_valido1.minilang`, `ejemplo_no_valido2.minilang`: Ejemplos de código con errores para probar la detección de fallos.

## Requisitos
- Python 3.11 o superior.
- Librería `ply` instalada. Puedes instalarla con:
  ```sh
  pip install ply
  ```

## Ejemplo de Uso
1. Ejecutar el compilador con un archivo de ejemplo:
    ```sh
    python compilador_minilang.py ejemplos/ejemplo_dificil3_valido.minilang
    ```
2. Para probar con otro archivo `.minilang`, agrégalo al directorio `ejemplos/` y ejecútalo de la misma manera:
    ```sh
    python compilador_minilang.py ejemplos/tu_archivo.minilang
    ```

## Estructura del Código
El compilador sigue un proceso en tres fases:
1. **Análisis Léxico**: Define los tokens y reconoce palabras clave, identificadores, operadores, etc.
2. **Análisis Sintáctico**: Usa una gramática basada en `ply.yacc` para construir el AST.
3. **Análisis Semántico**: Valida tipos de datos, alcances y restricciones del lenguaje.

## Licencia
Este proyecto se distribuye bajo la licencia MIT.

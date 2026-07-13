from django.shortcuts import render

PLANETA_COLUMNS = ["nombre", "dist", "radio", "grav", "días", "años", "temp", "anillo"]
PLANETA_ROWS = [
    ["Mercurio", 0.39, 0.38, 2.8, 58.646, 0.241, 440, "false"],
    ["Venus", 0.72, 0.95, 8.9, -243.019, 0.615, 730, "false"],
    ["Tierra", 1.00, 1.00, 9.8, 0.997, 1.000, 288, "false"],
    ["Marte", 1.52, 0.53, 3.7, 1.026, 1.880, 186, "false"],
    ["Júpiter", 5.20, 10.97, 22.9, 0.414, 11.862, 152, "true"],
    ["Saturno", 9.54, 9.14, 9.1, 0.444, 29.447, 134, "true"],
    ["Urano", 19.19, 3.98, 7.8, -0.719, 84.017, 76, "true"],
    ["Neptuno", 30.07, 3.86, 11.0, 0.671, 164.791, 53, "true"],
]

SATELITE_ROWS = [
    ["Calisto", "Júpiter", "Galileo Galilei", 1610],
    ["Europa", "Júpiter", "Galileo Galilei", 1610],
    ["Ganímedes", "Júpiter", "Galileo Galilei", 1610],
    ["Ío", "Júpiter", "Galileo Galilei", 1610],
    ["Luna", "Tierra", "-", "-"],
    ["Titán", "Saturno", "Christiaan Huygens", 1655],
    ["Tritón", "Neptuno", "William Lassell", 1846],
]

ATERRIZAJE_ROWS = [
    ["Viking 1", "Marte", "EEUU", 1976],
    ["Beagle 2", "Marte", "ESA", 2003],
    ["Galileo", "Júpiter", "EEUU", 2003],
    ["Mars 2 Lander", "Marte", "URRS", 1971],
    ["Messenger", "Mercurio", "EEUU", 2015],
    ["Pioneer", "Venus", "EEUU", 1978],
    ["Venera 3", "Venus", "URRS", 1966],
]

OPERATORS = {
    "SELECT": {
        "slug": "SELECT",
        "label": "SELECT",
        "description": "El operador SELECT permite elegir qué columnas se desean obtener desde una tabla.",
        "syntax": "SELECT columna1, columna2\nFROM nombre_tabla;",
        "question": "Obtenga el nombre y la distancia de todos los planetas.",
        "columns": PLANETA_COLUMNS,
        "rows": PLANETA_ROWS,
        "answer_sql": "SELECT nombre, dist\nFROM planeta;",
        "answer_columns": ["nombre", "dist"],
        "answer_rows": [
            ["Mercurio", 0.39],
            ["Venus", 0.72],
            ["Tierra", 1.00],
            ["Marte", 1.52],
            ["Júpiter", 5.20],
            ["Saturno", 9.54],
            ["Urano", 19.19],
            ["Neptuno", 30.07],
        ],
    },

    "WHERE": {
        "slug": "WHERE",
        "label": "WHERE",
        "description": "El operador WHERE permite filtrar filas según una condición lógica.",
        "syntax": "SELECT columna1, columna2\nFROM nombre_tabla\nWHERE condición;",
        "question": "Obtenga la gravedad y la temperatura de Venus.",
        "columns": PLANETA_COLUMNS,
        "rows": PLANETA_ROWS,
        "answer_sql": "SELECT grav, temp\nFROM planeta\nWHERE nombre = 'Venus';",
        "answer_columns": ["grav", "temp"],
        "answer_rows": [
            [8.9, 730],
        ],
    },

    "ALIAS": {
        "slug": "ALIAS",
        "label": "ALIAS",
        "description": (
            "El operador ALIAS permite asignar un nombre temporal a una columna, "
            "a una expresión o a una tabla dentro de una consulta. "
            "Se usa con la palabra clave AS."
        ),
        "syntax": "SELECT columna AS alias_columna\nFROM nombre_tabla;",
        "question": "Obtenga el nombre de los planetas bajo el alias splaneta desde la tabla satelite, tal que dichos planetas aparezcan también en la tabla aterrizaje.",
        "columns": ["tabla", "nombre", "planeta", "descubridor", "año", "nave", "país"],
        "rows": [
            ["satelite", "Calisto", "Júpiter", "Galileo Galilei", 1610, "-", "-"],
            ["satelite", "Europa", "Júpiter", "Galileo Galilei", 1610, "-", "-"],
            ["satelite", "Ganímedes", "Júpiter", "Galileo Galilei", 1610, "-", "-"],
            ["satelite", "Ío", "Júpiter", "Galileo Galilei", 1610, "-", "-"],
            ["satelite", "Luna", "Tierra", "-", "-", "-", "-"],
            ["satelite", "Titán", "Saturno", "Christiaan Huygens", 1655, "-", "-"],
            ["satelite", "Tritón", "Neptuno", "William Lassell", 1846, "-", "-"],
            ["aterrizaje", "-", "Marte", "-", 1976, "Viking 1", "EEUU"],
            ["aterrizaje", "-", "Marte", "-", 2003, "Beagle 2", "ESA"],
            ["aterrizaje", "-", "Júpiter", "-", 2003, "Galileo", "EEUU"],
            ["aterrizaje", "-", "Marte", "-", 1971, "Mars 2 Lander", "URRS"],
            ["aterrizaje", "-", "Mercurio", "-", 2015, "Messenger", "EEUU"],
            ["aterrizaje", "-", "Venus", "-", 1978, "Pioneer", "EEUU"],
            ["aterrizaje", "-", "Venus", "-", 1966, "Venera 3", "URRS"],
        ],
        "answer_sql": "SELECT S.planeta AS splaneta\nFROM satelite S, aterrizaje A\nWHERE S.planeta = A.planeta;",
        "answer_columns": ["splaneta"],
        "answer_rows": [
            ["Júpiter"],
            ["Júpiter"],
            ["Júpiter"],
            ["Júpiter"],
        ],
    },

    "UNION": {
        "slug": "UNION",
        "label": "UNION",
        "description": (
            "El operador UNION permite combinar los resultados de dos consultas SELECT. "
            "Ambas consultas deben devolver la misma cantidad de columnas y tipos compatibles. "
            "Por defecto, UNION elimina filas duplicadas."
        ),
        "syntax": "SELECT columna1, columna2\nFROM tabla1\nUNION\nSELECT columna1, columna2\nFROM tabla2;",
        "question": "Obtenga la unión de los nombres desdes las tablas planeta y satelite.",
        "columns": ["tabla", "nombre", "dist", "radio", "grav", "días", "años", "temp", "anillo", "planeta", "descubridor", "año"],
        "rows": [
            ["planeta", "Mercurio", 0.39, 0.38, 2.8, 58.646, 0.241, 440, "false", "-", "-", "-"],
            ["planeta", "Venus", 0.72, 0.95, 8.9, -243.019, 0.615, 730, "false", "-", "-", "-"],
            ["planeta", "Tierra", 1.00, 1.00, 9.8, 0.997, 1.000, 288, "false", "-", "-", "-"],
            ["planeta", "Marte", 1.52, 0.53, 3.7, 1.026, 1.880, 186, "false", "-", "-", "-"],
            ["planeta", "Júpiter", 5.20, 10.97, 22.9, 0.414, 11.862, 152, "true", "-", "-", "-"],
            ["planeta", "Saturno", 9.54, 9.14, 9.1, 0.444, 29.447, 134, "true", "-", "-", "-"],
            ["planeta", "Urano", 19.19, 3.98, 7.8, -0.719, 84.017, 76, "true", "-", "-", "-"],
            ["planeta", "Neptuno", 30.07, 3.86, 11.0, 0.671, 164.791, 53, "true", "-", "-", "-"],
            ["satelite", "Calisto", "-", "-", "-", "-", "-", "-", "-", "Júpiter", "Galileo Galilei", 1610],
            ["satelite", "Europa", "-", "-", "-", "-", "-", "-", "-", "Júpiter", "Galileo Galilei", 1610],
            ["satelite", "Ganímedes", "-", "-", "-", "-", "-", "-", "-", "Júpiter", "Galileo Galilei", 1610],
            ["satelite", "Ío", "-", "-", "-", "-", "-", "-", "-", "Júpiter", "Galileo Galilei", 1610],
            ["satelite", "Luna", "-", "-", "-", "-", "-", "-", "-", "Tierra", "-", "-"],
            ["satelite", "Titán", "-", "-", "-", "-", "-", "-", "-", "Saturno", "Christiaan Huygens", 1655],
            ["satelite", "Tritón", "-", "-", "-", "-", "-", "-", "-", "Neptuno", "William Lassell", 1846],
        ],
        "answer_sql": (
            "SELECT nombre\n"
            "FROM planeta\n"
            "UNION\n"
            "SELECT nombre\n"
            "FROM satelite;"
        ),
        "answer_columns": ["nombre"],
        "answer_rows": [
            ["Mercurio"],
            ["Venus"],
            ["Tierra"],
            ["Marte"],
            ["Júpiter"],
            ["Saturno"],
            ["Urano"],
            ["Neptuno"],
            ["Luna"],
            ["Ganímedes"],
            ["Calisto"],
            ["Europa"],
            ["Ío"],
            ["Titán"],
            ["Tritón"],
        ],
    },

    "EXCEPT": {
        "slug": "EXCEPT",
        "label": "EXCEPT",
        "description": (
            "El operador EXCEPT devuelve las filas que aparecen en la primera consulta, "
            "pero no aparecen en la segunda. Se puede entender como una resta entre conjuntos."
        ),
        "syntax": "SELECT columna1, columna2\nFROM tabla1\nEXCEPT\nSELECT columna1, columna2\nFROM tabla2;",
        "question": "Obtenga los nombres de los planetas con distancia mayor a 1.00, y que no estén en la tabla de satelites.",
        "columns": ["tabla", "nombre", "dist", "radio", "grav", "días", "años", "temp", "anillo", "planeta", "descubridor", "año"],
        "rows": [
            ["planeta", "Mercurio", 0.39, 0.38, 2.8, 58.646, 0.241, 440, "false", "-", "-", "-"],
            ["planeta", "Venus", 0.72, 0.95, 8.9, -243.019, 0.615, 730, "false", "-", "-", "-"],
            ["planeta", "Tierra", 1.00, 1.00, 9.8, 0.997, 1.000, 288, "false", "-", "-", "-"],
            ["planeta", "Marte", 1.52, 0.53, 3.7, 1.026, 1.880, 186, "false", "-", "-", "-"],
            ["planeta", "Júpiter", 5.20, 10.97, 22.9, 0.414, 11.862, 152, "true", "-", "-", "-"],
            ["planeta", "Saturno", 9.54, 9.14, 9.1, 0.444, 29.447, 134, "true", "-", "-", "-"],
            ["planeta", "Urano", 19.19, 3.98, 7.8, -0.719, 84.017, 76, "true", "-", "-", "-"],
            ["planeta", "Neptuno", 30.07, 3.86, 11.0, 0.671, 164.791, 53, "true", "-", "-", "-"],
            ["satelite", "Calisto", "-", "-", "-", "-", "-", "-", "-", "Júpiter", "Galileo Galilei", 1610],
            ["satelite", "Europa", "-", "-", "-", "-", "-", "-", "-", "Júpiter", "Galileo Galilei", 1610],
            ["satelite", "Ganímedes", "-", "-", "-", "-", "-", "-", "-", "Júpiter", "Galileo Galilei", 1610],
            ["satelite", "Ío", "-", "-", "-", "-", "-", "-", "-", "Júpiter", "Galileo Galilei", 1610],
            ["satelite", "Luna", "-", "-", "-", "-", "-", "-", "-", "Tierra", "-", "-"],
            ["satelite", "Titán", "-", "-", "-", "-", "-", "-", "-", "Saturno", "Christiaan Huygens", 1655],
            ["satelite", "Tritón", "-", "-", "-", "-", "-", "-", "-", "Neptuno", "William Lassell", 1846],
        ],
        "answer_sql": (
            "SELECT nombre as planeta\n"
            "FROM planeta\n"
            "WHERE dist > 1.00\n"
            "EXCEPT\n"
            "SELECT planeta\n"
            "FROM satelite;"
        ),
        "answer_columns": ["planeta"],
        "answer_rows": [
            ["Marte"],
            ["Urano"],
        ],
    },

    "BUSQUEDA&COMPARACION": {
        "slug": "BUSQUEDA&COMPARACION",
        "label": "Búsqueda y Comparación",
        "description": (
            "Los operadores de búsqueda y comparación permiten filtrar registros mediante condiciones. "
            "Algunos ejemplos son LIKE, IN, BETWEEN, =, <, >, <= y >=. "
            "LIKE se usa para buscar patrones en texto, IN para comparar contra un conjunto de valores "
            "y BETWEEN para filtrar rangos."
        ),
        "syntax": (
            "SELECT columna1, columna2\n"
            "FROM nombre_tabla\n"
            "WHERE columna LIKE patrón;\n\n"
            "SELECT columna1, columna2\n"
            "FROM nombre_tabla\n"
            "WHERE columna BETWEEN valor_inicial AND valor_final;\n\n"
            "SELECT columna1, columna2\n"
            "FROM nombre_tabla\n"
            "WHERE columna IN (valor1, valor2);"
        ),
        "question": "Obtenga el nombre de los planetas que comienzan con la letra M.",
        "columns": PLANETA_COLUMNS,
        "rows": PLANETA_ROWS,
        "answer_sql": "SELECT nombre\nFROM planeta\nWHERE nombre LIKE 'M%';",
        "answer_columns": ["nombre"],
        "answer_rows": [
            ["Mercurio"],
            ["Marte"],
        ],
    },

    "JOIN": {
        "slug": "JOIN",
        "label": "JOIN",
        "description": (
            "El operador JOIN permite combinar filas de dos tablas relacionadas. "
            "El INNER JOIN devuelve solo las filas que tienen coincidencia en ambas tablas."
        ),
        "syntax": "SELECT tabla1.columna, tabla2.columna\nFROM tabla1\nJOIN tabla2 ON tabla1.columna_comun = tabla2.columna_comun;",
        "question": "Obtenga el nombre del planeta, el año y la nave de los aterrizajes realizados en años igual o posterior al 2000, y en planetas con distancia mayor a 1.00.",
        "columns": ["tabla", "nombre", "dist", "radio", "grav", "días", "años", "temp", "anillo", "nave", "planeta", "país", "año"],
        "rows": [
            ["planeta", "Mercurio", 0.39, 0.38, 2.8, 58.646, 0.241, 440, "false", "-", "-", "-", "-"],
            ["planeta", "Venus", 0.72, 0.95, 8.9, -243.019, 0.615, 730, "false", "-", "-", "-", "-"],
            ["planeta", "Tierra", 1.00, 1.00, 9.8, 0.997, 1.000, 288, "false", "-", "-", "-", "-"],
            ["planeta", "Marte", 1.52, 0.53, 3.7, 1.026, 1.880, 186, "false", "-", "-", "-", "-"],
            ["planeta", "Júpiter", 5.20, 10.97, 22.9, 0.414, 11.862, 152, "true", "-", "-", "-", "-"],
            ["planeta", "Saturno", 9.54, 9.14, 9.1, 0.444, 29.447, 134, "true", "-", "-", "-", "-"],
            ["planeta", "Urano", 19.19, 3.98, 7.8, -0.719, 84.017, 76, "true", "-", "-", "-", "-"],
            ["planeta", "Neptuno", 30.07, 3.86, 11.0, 0.671, 164.791, 53, "true", "-", "-", "-", "-"],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Viking 1", "Marte", "EEUU", 1976],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Beagle 2", "Marte", "ESA", 2003],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Galileo", "Júpiter", "EEUU", 2003],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Mars 2 Lander", "Marte", "URRS", 1971],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Messenger", "Mercurio", "EEUU", 2015],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Pioneer", "Venus", "EEUU", 1978],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Venera 3", "Venus", "URRS", 1966],
        ],
        "answer_sql": (
            "SELECT nombre, año, nave\n"
            "FROM Planeta JOIN Aterrizaje\n"
            "ON nombre = planeta\n"
            "WHERE dist > 1.00\n"
            "AND año >= 2000"
        ),
        "answer_columns": ["nombre", "año", "nave"],
        "answer_rows": [
            ["Marte", 2003, "Beagle 2"],
            ["Júpiter", 2003, "Galileo"],
        ],
    },

    "LEFT&RIGHTJOIN": {
        "slug": "LEFT&RIGHTJOIN",
        "label": "LEFT & RIGHT JOIN",
        "description": (
            "LEFT JOIN devuelve todas las filas de la tabla izquierda y las coincidencias de la tabla derecha. "
            "Cuando no hay coincidencia, las columnas de la derecha aparecen como NULL. "
            "RIGHT JOIN hace lo mismo, pero conservando todas las filas de la tabla derecha."
        ),
        "syntax": (
            "SELECT tabla1.columna, tabla2.columna\n"
            "FROM tabla1\n"
            "LEFT JOIN tabla2 ON tabla1.columna_comun = tabla2.columna_comun;\n\n"
            "SELECT tabla1.columna, tabla2.columna\n"
            "FROM tabla1\n"
            "RIGHT JOIN tabla2 ON tabla1.columna_comun = tabla2.columna_comun;"
        ),
        "question": "Muestre todos los planetas y, si existe, la nave que aterrizó en ellos.",
        "columns": ["tabla", "nombre", "dist", "radio", "grav", "días", "años", "temp", "anillo", "nave", "planeta", "país", "año"],
        "rows": [
            ["planeta", "Mercurio", 0.39, 0.38, 2.8, 58.646, 0.241, 440, "false", "-", "-", "-", "-"],
            ["planeta", "Venus", 0.72, 0.95, 8.9, -243.019, 0.615, 730, "false", "-", "-", "-", "-"],
            ["planeta", "Tierra", 1.00, 1.00, 9.8, 0.997, 1.000, 288, "false", "-", "-", "-", "-"],
            ["planeta", "Marte", 1.52, 0.53, 3.7, 1.026, 1.880, 186, "false", "-", "-", "-", "-"],
            ["planeta", "Júpiter", 5.20, 10.97, 22.9, 0.414, 11.862, 152, "true", "-", "-", "-", "-"],
            ["planeta", "Saturno", 9.54, 9.14, 9.1, 0.444, 29.447, 134, "true", "-", "-", "-", "-"],
            ["planeta", "Urano", 19.19, 3.98, 7.8, -0.719, 84.017, 76, "true", "-", "-", "-", "-"],
            ["planeta", "Neptuno", 30.07, 3.86, 11.0, 0.671, 164.791, 53, "true", "-", "-", "-", "-"],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Viking 1", "Marte", "EEUU", 1976],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Beagle 2", "Marte", "ESA", 2003],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Galileo", "Júpiter", "EEUU", 2003],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Mars 2 Lander", "Marte", "URRS", 1971],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Messenger", "Mercurio", "EEUU", 2015],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Pioneer", "Venus", "EEUU", 1978],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Venera 3", "Venus", "URRS", 1966],
        ],
        "answer_sql": (
            "SELECT nave, nombre, dist, año\n"
            "FROM planeta LEFT JOIN aterrizaje\n"
            "ON nombre = planeta;"
        ),
        "answer_columns": ["nave", "nombre", "dist", "año"],
        "answer_rows": [
            ["Messenger", "Mercurio", 0.39, 2015],
            ["Venera 3", "Venus", 0.72, 1966],
            ["Pioneer", "Venus", 0.72, 1978],
            ["Mars 2 Lander", "Marte", 1.52, 1971],
            ["Viking 1", "Marte", 1.52, 1976],
            ["Beagle 2", "Marte", 1.52, 2003],
            ["Galileo", "Júpiter", 5.20, 2003],
            ["-", "Tierra", 1.00, "-"],
            ["-", "Saturno", 9.54, "-"],
            ["-", "Urano", 19.19, "-"],
            ["-", "Neptuno", 30.07, "-"],
        ],
    },

    "OUTER_JOIN": {
        "slug": "OUTER_JOIN",
        "label": "OUTER JOIN",
        "description": (
            "FULL OUTER JOIN devuelve todas las filas de ambas tablas. "
            "Cuando una fila no tiene coincidencia en la otra tabla, las columnas faltantes se muestran como NULL."
        ),
        "syntax": (
            "SELECT tabla1.columna, tabla2.columna\n"
            "FROM tabla1\n"
            "FULL OUTER JOIN tabla2 ON tabla1.columna_comun = tabla2.columna_comun;"
        ),
        "question": "Muestre todos los satelites y todos los aterrizajes, existan o no coincidencias entre sus planetas.",
        "columns": ["tabla", "nombre", "planeta", "descubridor", "año", "nave", "país"],
        "rows": [
            ["satelite", "Calisto", "Júpiter", "Galileo Galilei", 1610, "-", "-"],
            ["satelite", "Europa", "Júpiter", "Galileo Galilei", 1610, "-", "-"],
            ["satelite", "Ganímedes", "Júpiter", "Galileo Galilei", 1610, "-", "-"],
            ["satelite", "Ío", "Júpiter", "Galileo Galilei", 1610, "-", "-"],
            ["satelite", "Luna", "Tierra", "-", "-", "-", "-"],
            ["satelite", "Titán", "Saturno", "Christiaan Huygens", 1655, "-", "-"],
            ["satelite", "Tritón", "Neptuno", "William Lassell", 1846, "-", "-"],
            ["aterrizaje", "-", "Marte", "-", 1976, "Viking 1", "EEUU"],
            ["aterrizaje", "-", "Marte", "-", 2003, "Beagle 2", "ESA"],
            ["aterrizaje", "-", "Júpiter", "-", 2003, "Galileo", "EEUU"],
            ["aterrizaje", "-", "Marte", "-", 1971, "Mars 2 Lander", "URRS"],
            ["aterrizaje", "-", "Mercurio", "-", 2015, "Messenger", "EEUU"],
            ["aterrizaje", "-", "Venus", "-", 1978, "Pioneer", "EEUU"],
            ["aterrizaje", "-", "Venus", "-", 1966, "Venera 3", "URRS"],
        ],
        "answer_sql": (
            "SELECT planeta, nave, nombre AS\n"
            "satelite\n"
            "FROM satelite S FULL OUTER JOIN\n"
            "Aterrizaje A\n"
            "ON S.planeta = A.planeta"
        ),
        "answer_columns": ["planeta", "nave", "satelite"],
        "answer_rows": [
            ["Tierra", "-", "Luna"],
            ["Júpiter", "Galileo", "Ganímedes"],
            ["Júpiter", "Galileo", "Calipso"],
            ["Júpiter", "Galileo", "Europa"],
            ["Júpiter", "Galileo", "Ío"],
            ["Saturno", "-", "Titán"],
            ["Neptuno", "-", "Tritón"],
            ["Mercurio", "Mesenger", "-"],
            ["Venus", "Venera 3", "-"],
            ["Venus", "Pioneer", "-"],
            ["Marte", "Mars 2 lander", "-"],
            ["Marte", "Viking 1", "-"],
            ["Marte", "Beagle 2", "-"],
        ],
    },

    "NESTED_QUERYS": {
        "slug": "NESTED_QUERYS",
        "label": "NESTED QUERYS",
        "description": (
            "Las consultas anidadas permiten utilizar una consulta dentro de otra. "
            "Son útiles cuando el resultado de una consulta secundaria se usa como condición de la consulta principal."
        ),
        "syntax": "SELECT columna1, columna2\nFROM tabla1\nWHERE columna IN (\n    SELECT columna\n    FROM tabla2\n    WHERE condición\n);",
        "question": "Obtenga las naves y planetas de los aterrizajes realizados después del año 2000 en planetas con gravedad menor o igual a 9.8.",
        "columns": ["tabla", "nombre", "dist", "radio", "grav", "días", "años", "temp", "anillo", "nave", "planeta", "país", "año"],
        "rows": [
            ["planeta", "Mercurio", 0.39, 0.38, 2.8, 58.646, 0.241, 440, "false", "-", "-", "-", "-"],
            ["planeta", "Venus", 0.72, 0.95, 8.9, -243.019, 0.615, 730, "false", "-", "-", "-", "-"],
            ["planeta", "Tierra", 1.00, 1.00, 9.8, 0.997, 1.000, 288, "false", "-", "-", "-", "-"],
            ["planeta", "Marte", 1.52, 0.53, 3.7, 1.026, 1.880, 186, "false", "-", "-", "-", "-"],
            ["planeta", "Júpiter", 5.20, 10.97, 22.9, 0.414, 11.862, 152, "true", "-", "-", "-", "-"],
            ["planeta", "Saturno", 9.54, 9.14, 9.1, 0.444, 29.447, 134, "true", "-", "-", "-", "-"],
            ["planeta", "Urano", 19.19, 3.98, 7.8, -0.719, 84.017, 76, "true", "-", "-", "-", "-"],
            ["planeta", "Neptuno", 30.07, 3.86, 11.0, 0.671, 164.791, 53, "true", "-", "-", "-", "-"],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Viking 1", "Marte", "EEUU", 1976],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Beagle 2", "Marte", "ESA", 2003],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Galileo", "Júpiter", "EEUU", 2003],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Mars 2 Lander", "Marte", "URRS", 1971],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Messenger", "Mercurio", "EEUU", 2015],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Pioneer", "Venus", "EEUU", 1978],
            ["aterrizaje", "-", "-", "-", "-", "-", "-", "-", "-", "Venera 3", "Venus", "URRS", 1966],
        ],
        "answer_sql": (
            "SELECT nave, planeta\n"
            "FROM aterrizaje\n"
            "WHERE planeta NOT IN\n"
            "    ( SELECT nombre\n"
            "    FROM planeta\n"
            "    WHERE grav > 9.8 )\n"
            "AND año > 2000;"
        ),
        "answer_columns": ["nave", "planeta"],
        "answer_rows": [
            ["Beagle 2", "Marte"],
            ["Messenger", "Mercurio"],
        ],
    },

    "AGREGATIONS": {
        "slug": "AGREGATIONS",
        "label": "AGREGACIONES",
        "description": (
            "Las funciones de agregación permiten calcular valores resumidos a partir de varias filas. "
            "Algunas funciones comunes son COUNT, SUM, AVG, MAX y MIN. "
            "Normalmente se combinan con GROUP BY cuando se desea obtener un resumen por grupo."
        ),
        "syntax": (
            "SELECT columna_grupo, FUNCION_AGREGACION(columna) AS alias\n"
            "FROM nombre_tabla\n"
            "GROUP BY columna_grupo;"
        ),
        "question": "Calcule la cantidad de aterrizajes registrados cada cada planeta.",
        "columns": ["nave", "planeta", "país", "año"],
        "rows": ATERRIZAJE_ROWS,
        "answer_sql": (
            "SELECT planeta, COUNT(*) AS conteo\n"
            "FROM aterrizaje\n"
            "GROUP BY planeta;"
        ),
        "answer_columns": ["planeta", "conteo"],
        "answer_rows": [
            ["Mercurio", 1],
            ["Venus", 2],
            ["Marte", 3],
            ["Júpiter", 1],
        ],
    },
}


def home(request):
    return render(request, 'home.html', {
        "operators": OPERATORS.values()
    })


def select_view(request):
    operator = OPERATORS["SELECT"]
    return render(request, 'select.html', {
        "operator": operator
    })


def where_view(request):
    operator = OPERATORS["WHERE"]
    return render(request, 'where.html', {
        "operator": operator
    })


def alias_view(request):
    operator = OPERATORS["ALIAS"]
    return render(request, 'alias.html', {
        "operator": operator
    })


def union_view(request):
    operator = OPERATORS["UNION"]
    return render(request, 'union.html', {
        "operator": operator
    })


def except_view(request):
    operator = OPERATORS["EXCEPT"]
    return render(request, 'except.html', {
        "operator": operator
    })


def busqueda_view(request):
    operator = OPERATORS["BUSQUEDA&COMPARACION"]
    return render(request, 'seach&comparison.html', {
        "operator": operator
    })


def join_view(request):
    operator = OPERATORS["JOIN"]
    return render(request, 'join.html', {
        "operator": operator
    })


def left_right_join_view(request):
    operator = OPERATORS["LEFT&RIGHTJOIN"]
    return render(request, 'left_right_join.html', {
        "operator": operator
    })


def outer_join_view(request):
    operator = OPERATORS["OUTER_JOIN"]
    return render(request, 'outer_join.html', {
        "operator": operator
    })


def nested_querys_view(request):
    operator = OPERATORS["NESTED_QUERYS"]
    return render(request, 'nested_querys.html', {
        "operator": operator
    })


def agregaciones_view(request):
    operator = OPERATORS["AGREGATIONS"]
    return render(request, 'agregations.html', {
        "operator": operator
    })

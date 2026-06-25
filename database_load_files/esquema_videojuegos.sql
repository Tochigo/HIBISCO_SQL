-- =========================
-- TABLAS PRINCIPALES
-- =========================


DROP SCHEMA IF EXISTS videojuegos CASCADE;
CREATE SCHEMA videojuegos;

SET search_path TO videojuegos;

-- =========================
-- TABLAS PRINCIPALES
-- =========================

CREATE TABLE IF NOT EXISTS jugadores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    alias VARCHAR(50) NOT NULL UNIQUE,
    pais VARCHAR(50) NOT NULL,
    nivel INTEGER NOT NULL CHECK (nivel BETWEEN 1 AND 100)
);

CREATE TABLE IF NOT EXISTS consolas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    fabricante VARCHAR(80) NOT NULL,
    generacion INTEGER NOT NULL,
    tipo VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS videojuegos (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    genero VARCHAR(50) NOT NULL,
    clasificacion VARCHAR(10) NOT NULL,
    lanzamiento INTEGER NOT NULL,
    precio INTEGER NOT NULL CHECK (precio >= 0)
);

-- =========================
-- TABLAS DE RELACIONES
-- =========================

CREATE TABLE IF NOT EXISTS jugador_consola (
    jugador_id INTEGER NOT NULL REFERENCES jugadores(id) ON DELETE CASCADE,
    consola_id INTEGER NOT NULL REFERENCES consolas(id) ON DELETE CASCADE,
    fecha_compra DATE NOT NULL,
    PRIMARY KEY (jugador_id, consola_id)
);

CREATE TABLE IF NOT EXISTS videojuego_consola (
    videojuego_id INTEGER NOT NULL REFERENCES videojuegos(id) ON DELETE CASCADE,
    consola_id INTEGER NOT NULL REFERENCES consolas(id) ON DELETE CASCADE,
    disponible_desde DATE NOT NULL,
    PRIMARY KEY (videojuego_id, consola_id)
);

CREATE TABLE IF NOT EXISTS jugador_videojuego (
    jugador_id INTEGER NOT NULL REFERENCES jugadores(id) ON DELETE CASCADE,
    videojuego_id INTEGER NOT NULL REFERENCES videojuegos(id) ON DELETE CASCADE,
    horas_jugadas INTEGER NOT NULL CHECK (horas_jugadas >= 0),
    completado BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (jugador_id, videojuego_id)
);

-- =========================
-- DATOS: CONSOLAS
-- =========================

INSERT INTO consolas (nombre, fabricante, generacion, tipo) VALUES
('Nebula Play 5', 'Orion Systems', 9, 'Sobremesa'),
('Pocket Nova', 'LumaTech', 8, 'Portátil'),
('Titan Box X', 'AstraWorks', 9, 'Sobremesa');

-- =========================
-- DATOS: VIDEOJUEGOS
-- =========================

INSERT INTO videojuegos (titulo, genero, clasificacion, lanzamiento, precio) VALUES
('Crónicas de Auralia', 'RPG', 'T', 2021, 39990),
('Circuito Fantasma', 'Carreras', 'E', 2020, 29990),
('Sombras de Neón', 'Acción', 'M', 2022, 44990),
('Granja Estelar', 'Simulación', 'E', 2019, 24990),
('Arena de Titanes', 'Lucha', 'T', 2023, 49990),
('Islas del Eco', 'Aventura', 'E10+', 2021, 34990),
('Código Abisal', 'Puzzle', 'E', 2020, 19990),
('Reinos Fragmentados', 'Estrategia', 'T', 2022, 39990),
('Furia Mecánica', 'Acción', 'M', 2024, 52990),
('Melodía Lunar', 'Ritmo', 'E', 2018, 17990),
('Guardianes del Prisma', 'RPG', 'T', 2023, 45990),
('Velocidad Horizonte', 'Carreras', 'E', 2022, 36990),
('Bosque de Cristal', 'Aventura', 'E', 2019, 21990),
('Torre Infinita', 'Roguelike', 'T', 2021, 27990),
('Planeta Minúsculo', 'Simulación', 'E', 2020, 23990),
('Batalla de Órbitas', 'Estrategia', 'T', 2024, 48990),
('Eco del Dragón', 'RPG', 'T', 2018, 32990),
('Distrito Cero', 'Acción', 'M', 2023, 46990),
('Ruta Pixel', 'Plataformas', 'E', 2021, 18990),
('Archivo Estelar', 'Puzzle', 'E10+', 2022, 25990);

-- =========================
-- DATOS: JUGADORES
-- =========================

INSERT INTO jugadores (nombre, alias, pais, nivel) VALUES
('Valerio Naranjo', 'NexoLince', 'Chile', 42),
('Mara Cifuentes', 'PixelMara', 'Chile', 57),
('Elian Rojas', 'RayoNorte', 'Perú', 33),
('Sofía Aravena', 'LunaByte', 'Chile', 76),
('Tomás Beltrán', 'TomoQuest', 'Argentina', 21),
('Isidora Lagos', 'IsiNova', 'Chile', 88),
('Bruno Salvatierra', 'Bruzzer', 'Uruguay', 64),
('Camila Fuentes', 'CamiCircuit', 'Chile', 49),
('Renato Pizarro', 'RenPixel', 'México', 37),
('Antonia Valle', 'AntoSpark', 'Chile', 95),
('Damián Vera', 'DamiánZero', 'Colombia', 18),
('Martina Solís', 'MartyCloud', 'Chile', 52),
('Lucas Montoya', 'LukoDash', 'Argentina', 67),
('Emilia Rivas', 'EmiPrisma', 'Chile', 44),
('Gabriel León', 'GaboFénix', 'Perú', 72),
('Josefa Mora', 'JotaMoon', 'Chile', 39),
('Matías Carrasco', 'MatiRift', 'Chile', 81),
('Agustina Bravo', 'AguStar', 'Uruguay', 26),
('Nicolás Farías', 'NicoForge', 'Chile', 58),
('Florencia Vega', 'FlorArcade', 'México', 63),
('Cristóbal Sáez', 'CrisVector', 'Chile', 47),
('Amanda Quiroz', 'Amanita', 'Colombia', 34),
('Benjamín Soto', 'BenjiWarp', 'Chile', 69),
('Catalina Ponce', 'CataQuest', 'Argentina', 54),
('Ignacio Muñoz', 'NachoNova', 'Chile', 92),
('Fernanda Díaz', 'FerPixel', 'Perú', 41),
('Sebastián Cortés', 'SebaDrift', 'Chile', 73),
('Trinidad Herrera', 'TriniLoop', 'Chile', 29),
('Vicente Molina', 'VichoCore', 'Uruguay', 61),
('Paula Godoy', 'PauNebula', 'Chile', 85),
('Joaquín Tapia', 'JoacoBit', 'México', 36),
('Constanza Reyes', 'ConiRay', 'Chile', 78),
('Diego Paredes', 'DekoStorm', 'Argentina', 23),
('Javiera Peña', 'JaviBloom', 'Chile', 59),
('Felipe Olivares', 'PipeArc', 'Colombia', 66),
('Rocío Medina', 'RociGlow', 'Chile', 31),
('Samuel Navarro', 'SamuraiSam', 'Perú', 74),
('Valentina Espinoza', 'ValeHex', 'Chile', 48),
('Maximiliano Araya', 'MaxOrbit', 'Chile', 90),
('Daniela Sepúlveda', 'DaniWave', 'Uruguay', 55),
('Álvaro Campos', 'AlvaCode', 'Chile', 27),
('Francisca Ibáñez', 'FranNova', 'México', 62),
('Hugo Gallardo', 'HugoTank', 'Chile', 71),
('Belén Acuña', 'BelenQuest', 'Argentina', 38),
('Esteban Salinas', 'EsteRacer', 'Chile', 84),
('Maite Figueroa', 'MaiPixel', 'Perú', 46),
('Pablo Henríquez', 'PabloFlux', 'Chile', 53),
('Laura Sandoval', 'LauSpark', 'Colombia', 68),
('Rodrigo Bustos', 'RodoX', 'Chile', 32),
('Claudia Mella', 'ClauBit', 'Chile', 79);

-- =========================
-- RELACIÓN: VIDEOJUEGOS DISPONIBLES EN CONSOLAS
-- Cada juego queda disponible en una o más consolas.
-- =========================

INSERT INTO videojuego_consola (videojuego_id, consola_id, disponible_desde)
SELECT id, 1, DATE '2021-01-10' + (id * INTERVAL '12 days')
FROM videojuegos
WHERE id IN (1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 16, 17, 18, 20);

INSERT INTO videojuego_consola (videojuego_id, consola_id, disponible_desde)
SELECT id, 2, DATE '2020-03-15' + (id * INTERVAL '10 days')
FROM videojuegos
WHERE id IN (1, 4, 6, 7, 10, 13, 15, 17, 19, 20);

INSERT INTO videojuego_consola (videojuego_id, consola_id, disponible_desde)
SELECT id, 3, DATE '2022-05-20' + (id * INTERVAL '8 days')
FROM videojuegos
WHERE id IN (2, 3, 5, 8, 9, 11, 12, 14, 16, 18, 19);

-- =========================
-- RELACIÓN: JUGADORES Y CONSOLAS
-- Cada jugador tiene al menos una consola.
-- Algunos tienen dos o tres.
-- =========================

INSERT INTO jugador_consola (jugador_id, consola_id, fecha_compra)
SELECT id, ((id - 1) % 3) + 1, DATE '2021-01-01' + (id * INTERVAL '9 days')
FROM jugadores;

INSERT INTO jugador_consola (jugador_id, consola_id, fecha_compra)
SELECT id, (id % 3) + 1, DATE '2022-02-01' + (id * INTERVAL '7 days')
FROM jugadores
WHERE id % 2 = 0;

INSERT INTO jugador_consola (jugador_id, consola_id, fecha_compra)
SELECT id, ((id + 1) % 3) + 1, DATE '2023-03-01' + (id * INTERVAL '5 days')
FROM jugadores
WHERE id % 5 = 0
ON CONFLICT DO NOTHING;

-- =========================
-- RELACIÓN: JUGADORES Y VIDEOJUEGOS
-- Cada jugador posee varios videojuegos.
-- =========================

INSERT INTO jugador_videojuego (jugador_id, videojuego_id, horas_jugadas, completado)
SELECT
    j.id,
    ((j.id + n.numero - 2) % 20) + 1 AS videojuego_id,
    ((j.id * 7 + n.numero * 13) % 180) + 1 AS horas_jugadas,
    ((j.id + n.numero) % 4 = 0) AS completado
FROM jugadores j
CROSS JOIN generate_series(1, 4) AS n(numero);

-- Algunos jugadores tienen juegos extra.
INSERT INTO jugador_videojuego (jugador_id, videojuego_id, horas_jugadas, completado)
SELECT
    j.id,
    ((j.id * 3) % 20) + 1 AS videojuego_id,
    ((j.id * 11) % 220) + 5 AS horas_jugadas,
    (j.id % 3 = 0) AS completado
FROM jugadores j
WHERE j.id % 3 = 0
ON CONFLICT DO NOTHING;

-- =========================
-- CONSULTAS DE VERIFICACIÓN
-- =========================

SELECT 'jugadores' AS tabla, COUNT(*) AS total FROM videojuegos.jugadores
UNION ALL
SELECT 'videojuegos', COUNT(*) FROM videojuegos.videojuegos
UNION ALL
SELECT 'consolas', COUNT(*) FROM videojuegos.consolas
UNION ALL
SELECT 'jugador_consola', COUNT(*) FROM videojuegos.jugador_consola
UNION ALL
SELECT 'videojuego_consola', COUNT(*) FROM videojuegos.videojuego_consola
UNION ALL
SELECT 'jugador_videojuego', COUNT(*) FROM videojuegos.jugador_videojuego;
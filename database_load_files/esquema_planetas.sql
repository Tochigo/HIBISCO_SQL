-- Esquema de ejemplo: planetas
-- Versión compatible con PostgreSQL para HIBISCO SQL.
-- OJO: esta línea elimina el esquema planetas si ya existe.
DROP SCHEMA IF EXISTS planetas CASCADE;

CREATE SCHEMA planetas;
SET search_path TO planetas;

CREATE TABLE planeta (
    nombre VARCHAR(50) PRIMARY KEY,
    dist NUMERIC(5,2),
    radio NUMERIC(5,2),
    grav NUMERIC(4,1),
    dias NUMERIC(8,3),
    años NUMERIC(8,3),
    temp INTEGER,
    anillo BOOLEAN
);

CREATE TABLE aterrizaje (
    nave VARCHAR(50) PRIMARY KEY,
    planeta VARCHAR(50) REFERENCES planeta(nombre),
    pais VARCHAR(50),
    año INTEGER
);

CREATE TABLE satelite (
    nombre VARCHAR(50) PRIMARY KEY,
    planeta VARCHAR(50) REFERENCES planeta(nombre),
    descubridor VARCHAR(50),
    año INTEGER
);

INSERT INTO planeta (nombre, dist, radio, grav, dias, años, temp, anillo) VALUES
    ('Júpiter', 5.20, 10.97, 22.9, 0.414, 11.862, 152, TRUE),
    ('Marte', 1.52, 0.53, 3.7, 1.026, 1.880, 186, FALSE),
    ('Mercurio', 0.39, 0.38, 2.8, 58.646, 0.241, 440, FALSE),
    ('Neptuno', 30.07, 3.86, 11.0, 0.671, 164.791, 53, TRUE),
    ('Saturno', 9.54, 9.14, 9.1, 0.444, 29.447, 134, TRUE),
    ('Tierra', 1.00, 1.00, 9.8, 0.997, 1.000, 288, FALSE),
    ('Urano', 19.19, 3.98, 7.8, -0.719, 84.017, 76, TRUE),
    ('Venus', 0.72, 0.95, 8.9, -243.019, 0.615, 730, FALSE);

INSERT INTO aterrizaje (nave, planeta, pais, año) VALUES
    ('Viking 1', 'Marte', 'EEUU', 1976),
    ('Beagle 2', 'Marte', 'ESA', 2003),
    ('Galileo', 'Júpiter', 'EEUU', 2003),
    ('Mars 2 Lander', 'Marte', 'URRS', 1971),
    ('Messenger', 'Mercurio', 'EEUU', 2015),
    ('Pioneer', 'Venus', 'EEUU', 1978),
    ('Venera 3', 'Venus', 'URRS', 1966);

INSERT INTO satelite (nombre, planeta, descubridor, año) VALUES
    ('Calisto', 'Júpiter', 'Galileo Galile', 1610),
    ('Europa', 'Júpiter', 'Galileo Galile', 1610),
    ('Ganímedes', 'Júpiter', 'Galileo Galilei', 1610),
    ('Ío', 'Júpiter', 'Galileo Galile', 1610),
    ('Luna', 'Tierra', NULL, NULL),
    ('Titán', 'Saturno', 'Christiaan Huygens', 1655),
    ('Tritón', 'Neptuno', 'William Lassell', 1846);

-- Permisos de solo lectura para el usuario de la aplicación.
-- Ajusta sqlmemoria_user si tu usuario de base de datos tiene otro nombre.
GRANT USAGE ON SCHEMA planetas TO sqlmemoria_user;
GRANT SELECT ON ALL TABLES IN SCHEMA planetas TO sqlmemoria_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA planetas GRANT SELECT ON TABLES TO sqlmemoria_user;

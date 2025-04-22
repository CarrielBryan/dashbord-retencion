import sqlite3
import random
from faker import Faker # type: ignore
from datetime import datetime, timedelta

# Inicializar Faker
fake = Faker()

# Conectar a la base de datos SQLite
conn = sqlite3.connect("retencion.db")
cursor = conn.cursor()

# Crear tablas
cursor.executescript('''
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS contratos;
DROP TABLE IF EXISTS cancelaciones;
DROP TABLE IF EXISTS llamadas_retencion;

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    email TEXT,
    region TEXT,
    fecha_alta DATE
);

CREATE TABLE contratos (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER,
    tipo_plan TEXT,
    fecha_inicio DATE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE cancelaciones (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER,
    fecha_cancelacion DATE,
    motivo TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE llamadas_retencion (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER,
    fecha_llamada DATE,
    resultado TEXT,
    notas TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);
''')

# Funciones auxiliares
planes = ['Prepago', 'Postpago', 'Familiar', 'Empresarial']
regiones = ['Norte', 'Sur', 'Centro', 'Este', 'Oeste']
motivos_cancelacion = ['Precio', 'Mala atención', 'Cambio de compañía', 'Cobertura', 'Problemas técnicos']
resultados_llamada = ['Retenido', 'No Retenido', 'No respondió']

# Insertar datos ficticios
for i in range(1, 201):
    nombre = fake.name()
    email = fake.email()
    region = random.choice(regiones)
    fecha_alta = fake.date_between(start_date='-3y', end_date='-6m')

    # Insertar cliente
    cursor.execute("INSERT INTO clientes (id, nombre, email, region, fecha_alta) VALUES (?, ?, ?, ?, ?)",
                   (i, nombre, email, region, fecha_alta))

    # Insertar contrato
    tipo_plan = random.choice(planes)
    cursor.execute("INSERT INTO contratos (cliente_id, tipo_plan, fecha_inicio) VALUES (?, ?, ?)",
                   (i, tipo_plan, fecha_alta))

    # Probabilidad de cancelación (40%)
    if random.random() < 0.4:
        fecha_cancelacion = fake.date_between(start_date=fecha_alta, end_date='today')
        motivo = random.choice(motivos_cancelacion)
        cursor.execute("INSERT INTO cancelaciones (cliente_id, fecha_cancelacion, motivo) VALUES (?, ?, ?)",
                       (i, fecha_cancelacion, motivo))

    # Probabilidad de llamada de retención (50%)
    if random.random() < 0.5:
        fecha_llamada = fake.date_between(start_date=fecha_alta, end_date='today')
        resultado = random.choice(resultados_llamada)
        notas = fake.sentence()
        cursor.execute("INSERT INTO llamadas_retencion (cliente_id, fecha_llamada, resultado, notas) VALUES (?, ?, ?, ?)",
                       (i, fecha_llamada, resultado, notas))

# Guardar cambios y cerrar
conn.commit()
conn.close()

print("Base de datos 'retencion.db' creada con éxito.")
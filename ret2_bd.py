import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Conexión a la base de datos
conn = sqlite3.connect("retencion.db")

# Cargar tablas en DataFrames
clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
contratos = pd.read_sql_query("SELECT * FROM contratos", conn)
cancelaciones = pd.read_sql_query("SELECT * FROM cancelaciones", conn)
llamadas = pd.read_sql_query("SELECT * FROM llamadas_retencion", conn)

# Cierre de conexión (ya no es necesaria)
conn.close()

# Mostrar info general
print("Clientes:", clientes.shape)
print("Contratos:", contratos.shape)
print("Cancelaciones:", cancelaciones.shape)
print("Llamadas:", llamadas.shape)

# Unir datos relevantes
df = clientes.merge(contratos, left_on='id', right_on='cliente_id', how='left')\
             .merge(cancelaciones, left_on='id', right_on='cliente_id', how='left', suffixes=('', '_cancel'))\
             .merge(llamadas, left_on='id', right_on='cliente_id', how='left', suffixes=('', '_llamada'))

# Crear una columna "cancelado"
df['cancelado'] = df['fecha_cancelacion'].notnull()

# Tasa de cancelación
cancel_rate = df['cancelado'].mean() * 100
print(f"\nTasa de cancelación: {cancel_rate:.2f}%")

# Cancels por región
cancel_por_region = df.groupby('region')['cancelado'].mean().sort_values() * 100

# Visualización
sns.set(style="whitegrid")
plt.figure(figsize=(8, 5))
sns.barplot(x=cancel_por_region.index, y=cancel_por_region.values, palette="coolwarm")
plt.ylabel("Tasa de cancelación (%)")
plt.title("Tasa de cancelación por región")
plt.show()
# --- Tasa de cancelación por tipo de plan ---
cancel_por_plan = df.groupby('tipo_plan')['cancelado'].mean().sort_values() * 100

plt.figure(figsize=(8, 5))
sns.barplot(x=cancel_por_plan.index, y=cancel_por_plan.values, palette="viridis")
plt.ylabel("Tasa de cancelación (%)")
plt.title("Tasa de cancelación por tipo de plan")
plt.show()

# --- Motivos de cancelación más frecuentes ---
motivos = df[df['cancelado']]['motivo'].value_counts()

plt.figure(figsize=(8, 5))
sns.barplot(x=motivos.index, y=motivos.values, palette="magma")
plt.ylabel("Cantidad")
plt.title("Motivos de cancelación más frecuentes")
plt.xticks(rotation=45)
plt.show()

# --- Efectividad de llamadas de retención ---
llamadas_filtradas = df[df['resultado'].notnull()]
efectividad = llamadas_filtradas['resultado'].value_counts(normalize=True) * 100 
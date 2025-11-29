"""
Script para verificar los tipos de evento en la base de datos
"""
import pymysql
from datetime import datetime

# Configuración de conexión (usando las credenciales del bootstrap.sql)
config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'app_catalogo',
    'password': 'Catalogo_2025',
    'database': 'ev_catalogo',
    'charset': 'utf8mb4'
}

try:
    # Conectar a la base de datos
    conn = pymysql.connect(**config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Consultar los últimos 10 tipos de evento
    query = """
        SELECT id, nombre, descripcion, status, created_at, updated_at
        FROM tipo_evento
        WHERE is_deleted = 0
        ORDER BY created_at DESC
        LIMIT 10
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n" + "="*80)
    print("TIPOS DE EVENTO EN LA BASE DE DATOS (Últimos 10)")
    print("="*80 + "\n")
    
    if not results:
        print("❌ No se encontraron tipos de evento en la base de datos.\n")
    else:
        for idx, row in enumerate(results, 1):
            print(f"#{idx}")
            print(f"  ID:          {row['id']}")
            print(f"  Nombre:      {row['nombre']}")
            print(f"  Descripción: {row['descripcion'] if row['descripcion'] else '❌ NULL/VACÍO'}")
            print(f"  Status:      {row['status']}")
            print(f"  Creado:      {row['created_at']}")
            print(f"  Actualizado: {row['updated_at'] if row['updated_at'] else 'N/A'}")
            print("-" * 80)
    
    # Contar tipos con descripción vacía o NULL
    cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN descripcion IS NULL OR descripcion = '' THEN 1 ELSE 0 END) as sin_descripcion
        FROM tipo_evento
        WHERE is_deleted = 0
    """)
    stats = cursor.fetchone()
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"  Total tipos de evento: {stats['total']}")
    print(f"  Sin descripción:       {stats['sin_descripcion']}")
    print(f"  Con descripción:       {stats['total'] - stats['sin_descripcion']}")
    print("="*80 + "\n")
    
    cursor.close()
    conn.close()
    
except pymysql.Error as e:
    print(f"\n❌ Error de base de datos: {e}\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")

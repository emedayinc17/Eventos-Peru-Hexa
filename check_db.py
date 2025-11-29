"""
Script simplificado para verificar tipos de evento
"""
import pymysql

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'app_catalogo',
    'password': 'Catalogo_2025',
    'database': 'ev_catalogo',
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Consultar los últimos 5 tipos de evento
    query = """
        SELECT id, nombre, descripcion, status, created_at
        FROM tipo_evento
        WHERE is_deleted = 0
        ORDER BY created_at DESC
        LIMIT 5
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n=== ULTIMOS 5 TIPOS DE EVENTO ===\n")
    
    for row in results:
        desc = row['descripcion'] if row['descripcion'] else "*** SIN DESCRIPCION ***"
        print(f"ID: {row['id'][:8]}...")
        print(f"Nombre: {row['nombre']}")
        print(f"Descripcion: {desc}")
        print(f"Creado: {row['created_at']}")
        print("-" * 50)
    
    # Estadísticas
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN descripcion IS NULL OR descripcion = '' THEN 1 ELSE 0 END) as sin_desc
        FROM tipo_evento
        WHERE is_deleted = 0
    """)
    stats = cursor.fetchone()
    
    print(f"\nTOTAL: {stats['total']}")
    print(f"SIN DESCRIPCION: {stats['sin_desc']}")
    print(f"CON DESCRIPCION: {stats['total'] - stats['sin_desc']}\n")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")

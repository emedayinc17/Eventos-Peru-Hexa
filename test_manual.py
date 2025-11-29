"""
Script simplificado para probar directamente el servicio de catálogo
"""
import pymysql

print("Verificando tipos de evento en la BD...")

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
    
    # Contar total
    cursor.execute("SELECT COUNT(*) as total FROM tipo_evento WHERE is_deleted = 0")
    total_antes = cursor.fetchone()['total']
    print(f"\nTotal de tipos ANTES: {total_antes}")
    
    print("\n" + "="*60)
    print("INSTRUCCIONES:")
    print("="*60)
    print("1. Ve al navegador: http://localhost:5173/admin/tipos-evento")
    print("2. Crea un nuevo tipo de evento con:")
    print("   - Nombre: 'Prueba Final'")
    print("   - Descripción: 'Esta es una prueba final del fix'")
    print("3. Presiona ENTER aquí cuando hayas creado el tipo")
    print("="*60)
    
    input("\nPresiona ENTER después de crear el tipo de evento...")
    
    # Verificar después
    cursor.execute("SELECT COUNT(*) as total FROM tipo_evento WHERE is_deleted = 0")
    total_despues = cursor.fetchone()['total']
    
    print(f"\nTotal de tipos DESPUÉS: {total_despues}")
    
    if total_despues > total_antes:
        print(f"✅ Se creó {total_despues - total_antes} nuevo(s) tipo(s)")
        
        # Mostrar el último creado
        cursor.execute("""
            SELECT id, nombre, descripcion, created_at
            FROM tipo_evento
            WHERE is_deleted = 0
            ORDER BY created_at DESC
            LIMIT 1
        """)
        ultimo = cursor.fetchone()
        
        print(f"\n📋 Último tipo creado:")
        print(f"   Nombre: {ultimo['nombre']}")
        print(f"   Descripción: {ultimo['descripcion'] if ultimo['descripcion'] else '❌ VACÍO'}")
        print(f"   Creado: {ultimo['created_at']}")
        
        if ultimo['descripcion']:
            print("\n🎉 ¡ÉXITO! La descripción se guardó correctamente en la BD")
        else:
            print("\n❌ FALLO: La descripción NO se guardó en la BD")
    else:
        print("❌ No se detectó ningún nuevo tipo de evento")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

from backend.extensions import db
from backend.app import create_app
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            queries = [
                "ALTER TABLE pages ADD COLUMN color_card VARCHAR(7) DEFAULT '#ffffff'",
                "ALTER TABLE pages ADD COLUMN color_border VARCHAR(7) DEFAULT '#dee2e6'",
                "ALTER TABLE pages ADD COLUMN color_accent VARCHAR(7) DEFAULT '#667eea'",
                "ALTER TABLE pages ADD COLUMN font_family VARCHAR(50) DEFAULT 'Arial'",
                "ALTER TABLE pages ADD COLUMN font_size INT DEFAULT 16",
                "ALTER TABLE pages ADD COLUMN border_radius INT DEFAULT 10"
            ]
            
            for query in queries:
                try:
                    conn.execute(text(query))
                    conn.commit()
                    print(f"✓ Ejecutado: {query[:50]}...")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print(f"⊗ Columna ya existe: {query[:50]}...")
                    else:
                        print(f"✗ Error: {e}")
            
            update_query = """
                UPDATE pages 
                SET 
                    color_card = COALESCE(color_card, '#ffffff'),
                    color_border = COALESCE(color_border, '#dee2e6'),
                    color_accent = COALESCE(color_accent, '#667eea'),
                    font_family = COALESCE(font_family, 'Arial'),
                    font_size = COALESCE(font_size, 16),
                    border_radius = COALESCE(border_radius, 10)
            """
            conn.execute(text(update_query))
            conn.commit()
            print("✓ Valores actualizados correctamente")
            
        print("\n¡Campos agregados exitosamente!")
        
    except Exception as e:
        print(f"Error: {e}")


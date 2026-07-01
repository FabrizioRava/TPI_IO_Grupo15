import sqlite3
import os
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_path="database/inventario.db"):
        # Crear carpeta database si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.crear_tablas()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def crear_tablas(self):
        """Crea la tabla de artículos SIN SKU"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de artículos - SIN columna sku
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articulos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                demanda INTEGER NOT NULL,
                costo_unitario REAL NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ============ OPERACIONES CRUD ============
    
    def insertar_articulo(self, nombre: str, demanda: int, costo_unitario: float) -> int:
        """Inserta un nuevo artículo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO articulos (nombre, demanda, costo_unitario) VALUES (?, ?, ?)",
                (nombre, demanda, costo_unitario)
            )
            conn.commit()
            articulo_id = cursor.lastrowid
            return articulo_id
        except sqlite3.IntegrityError:
            # Si el nombre ya existe
            return -1
        finally:
            conn.close()
    
    def obtener_articulos(self) -> List[Tuple]:
        """Obtiene todos los artículos ordenados por nombre"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, demanda, costo_unitario FROM articulos ORDER BY nombre")
        datos = cursor.fetchall()
        conn.close()
        return datos
    
    def obtener_articulo_por_id(self, articulo_id: int) -> Optional[Tuple]:
        """Obtiene un artículo por su ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, demanda, costo_unitario FROM articulos WHERE id = ?", (articulo_id,))
        dato = cursor.fetchone()
        conn.close()
        return dato
    
    def obtener_articulo_por_nombre(self, nombre: str) -> Optional[Tuple]:
        """Obtiene un artículo por su nombre"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, demanda, costo_unitario FROM articulos WHERE nombre = ?", (nombre,))
        dato = cursor.fetchone()
        conn.close()
        return dato
    
    def actualizar_articulo(self, articulo_id: int, nombre: str, demanda: int, costo_unitario: float) -> bool:
        """Actualiza los datos de un artículo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE articulos SET nombre = ?, demanda = ?, costo_unitario = ? WHERE id = ?",
                (nombre, demanda, costo_unitario, articulo_id)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Si el nombre ya existe en otro registro
            return False
        finally:
            conn.close()
    
    def eliminar_articulo(self, articulo_id: int):
        """Elimina un artículo por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM articulos WHERE id = ?", (articulo_id,))
        conn.commit()
        conn.close()
    
    def eliminar_todos_articulos(self):
        """Elimina todos los artículos (útil para reiniciar)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM articulos")
        conn.commit()
        conn.close()
    
    def cargar_datos_iniciales(self):
        """Carga los 10 productos del caso de estudio SIN SKU"""
        productos = [
            ("Producto SKU-22", 950, 100.00),
            ("Producto SKU-68", 1500, 50.00),
            ("Producto SKU-27", 500, 50.00),
            ("Producto SKU-03", 1000, 15.00),
            ("Producto SKU-82", 260, 50.00),
            ("Producto SKU-54", 250, 30.00),
            ("Producto SKU-36", 150, 10.00),
            ("Producto SKU-19", 400, 2.00),
            ("Producto SKU-23", 85, 5.00),
            ("Producto SKU-41", 45, 5.00)
        ]
        
        for nombre, demanda, costo in productos:
            self.insertar_articulo(nombre, demanda, costo)
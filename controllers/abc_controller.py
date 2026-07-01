import pandas as pd
import numpy as np
from database import Database

class ABCController:
    def __init__(self, db: Database):
        self.db = db
    
    def calcular_analisis_abc(self):
        """
        Calcula el análisis ABC para todos los artículos
        Retorna: DataFrame con los resultados ordenados
        """
        # Obtener artículos de la base de datos
        articulos = self.db.obtener_articulos()
        
        if not articulos:
            return None
        
        # Crear DataFrame
        data = []
        for articulo in articulos:
            id_art, nombre, demanda, costo = articulo
            capital = demanda * costo
            data.append({
                'id': id_art,
                'nombre': nombre,
                'demanda': demanda,
                'costo_unitario': costo,
                'capital': capital
            })
        
        df = pd.DataFrame(data)
        
        # Ordenar por capital de mayor a menor
        df = df.sort_values('capital', ascending=False).reset_index(drop=True)
        
        # Calcular capital total
        capital_total = df['capital'].sum()
        
        # Calcular porcentaje individual y acumulado
        df['porcentaje_individual'] = (df['capital'] / capital_total * 100).round(2)
        df['porcentaje_acumulado'] = df['porcentaje_individual'].cumsum().round(2)
        
        # Calcular porcentaje de artículos acumulado
        df['porcentaje_articulos'] = ((df.index + 1) / len(df) * 100).round(2)
        
        # Clasificación por cantidad de productos (20-30-50)
        n = len(df)
        n_a = int(n * 0.20)  # 20% de los productos
        n_b = int(n * 0.30)  # 30% de los productos
        
        df['grupo'] = 'C'  # Por defecto
        
        # Asignar Grupo A (primer 20%)
        for i in range(min(n_a, n)):
            df.at[i, 'grupo'] = 'A'
        
        # Asignar Grupo B (siguiente 30%)
        for i in range(n_a, min(n_a + n_b, n)):
            df.at[i, 'grupo'] = 'B'
        
        return df
    
    def generar_recomendaciones(self, df):
        """
        Genera recomendaciones basadas en el análisis ABC
        """
        if df is None or df.empty:
            return ["No hay datos para analizar"]
        
        recomendaciones = []
        
        # Productos Grupo A
        grupo_a = df[df['grupo'] == 'A']
        if not grupo_a.empty:
            productos_a = ', '.join(grupo_a['nombre'].tolist())
            porcentaje_productos_a = (len(grupo_a) / len(df) * 100)
            pct_capital_a = grupo_a['porcentaje_individual'].sum()
            recomendaciones.append(
                f"🔴 GRUPO A - Control Exhaustivo: Los productos {productos_a} representan el "
                f"{porcentaje_productos_a:.1f}% de los artículos y el "
                f"{pct_capital_a:.1f}% del capital total. "
                f"Se recomienda mantener un control riguroso del inventario, realizar conteos frecuentes, "
                f"negociar precios con proveedores y priorizar su disponibilidad."
            )
        
        # Productos Grupo B
        grupo_b = df[df['grupo'] == 'B']
        if not grupo_b.empty:
            productos_b = ', '.join(grupo_b['nombre'].tolist())
            porcentaje_productos_b = (len(grupo_b) / len(df) * 100)
            pct_capital_b = grupo_b['porcentaje_individual'].sum()
            recomendaciones.append(
                f"🟡 GRUPO B - Control Estándar: Los productos {productos_b} representan el "
                f"{porcentaje_productos_b:.1f}% de los artículos y el "
                f"{pct_capital_b:.1f}% del capital. Se recomienda un control periódico y "
                f"monitoreo regular de su rotación."
            )
        
        # Productos Grupo C
        grupo_c = df[df['grupo'] == 'C']
        if not grupo_c.empty:
            productos_c = ', '.join(grupo_c['nombre'].tolist())
            porcentaje_productos_c = (len(grupo_c) / len(df) * 100)
            pct_capital_c = grupo_c['porcentaje_individual'].sum()
            recomendaciones.append(
                f"🟢 GRUPO C - Control Simplificado: Los productos {productos_c} representan el "
                f"{porcentaje_productos_c:.1f}% de los artículos y solo el "
                f"{pct_capital_c:.1f}% del capital. Se recomienda simplificar los procesos de control, "
                f"realizar pedidos menos frecuentes y mantener stocks de seguridad más bajos."
            )
        
        # Recomendación general
        if not grupo_a.empty:
            porcentaje_productos_a = (len(grupo_a) / len(df) * 100)
            pct_capital_a = grupo_a['porcentaje_individual'].sum()
            recomendaciones.append(
                f"📊 CONCLUSIÓN: El {porcentaje_productos_a:.1f}% de los productos (Grupo A) concentran el "
                f"{pct_capital_a:.1f}% del capital invertido. "
                f"Se sugiere enfocar los esfuerzos de gestión en estos productos para maximizar "
                f"la eficiencia del inventario."
            )
        
        return recomendaciones
    
    def obtener_productos_grupo_a(self, df):
        """Obtiene solo los productos del Grupo A para análisis adicional"""
        if df is None:
            return None
        return df[df['grupo'] == 'A'].copy()
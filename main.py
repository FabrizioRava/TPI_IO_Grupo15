import customtkinter as ctk
from database import Database
from views import App
import sys

def main():
    # Configurar CustomTkinter - TEMA CLARO
    ctk.set_appearance_mode("Light")  # Cambiado a "Light"
    ctk.set_default_color_theme("blue")
    
    # Configurar fuente más grande para TODA la aplicación
    ctk.set_widget_scaling(1.4)
    ctk.set_window_scaling(1.4)
    
    # Inicializar base de datos
    db = Database()
    
    # Cargar datos si no existen
    if not db.obtener_articulos():
        print("📦 Cargando datos iniciales...")
        db.cargar_datos_iniciales()
    
    # Crear y ejecutar app
    app = App(db)
    
    # Manejar el cierre limpio para evitar errores
    def on_closing():
        app.quit()
        app.destroy()
        sys.exit(0)
    
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
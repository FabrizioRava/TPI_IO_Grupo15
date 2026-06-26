import customtkinter as ctk
from views.inventario_tab import InventarioTab
from views.analisis_tab import AnalisisABCTab

class App(ctk.CTk):
    def __init__(self, db):
        super().__init__()
        
        self.db = db
        self.title("Sistema de Gestión de Inventarios - Análisis ABC")
        self.geometry("1400x900")  # Más grande para pantalla completa
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Pestañas - SIN el argumento font (no es soportado)
        self.tabview = ctk.CTkTabview(
            self.main_frame,
            width=1300,
            height=800
        )
        self.tabview.grid(row=0, column=0, sticky="nsew")
        
        # Agregar pestañas
        self.tabview.add("📋 Inventario")
        self.tabview.add("📊 Análisis ABC")
        
        # Configurar el tamaño de fuente de las pestañas después de crearlas
        # (usando el widget interno de tkinter)
        try:
            # Intentar cambiar el tamaño de fuente de las pestañas
            style = ctk.CTkStyle(self)
            style.configure("TButton", font=("Arial", 18, "bold"))
        except:
            pass
        
        # Inicializar pestañas
        self.tab_inventario = InventarioTab(self.tabview.tab("📋 Inventario"), self.db)
        self.tab_analisis = AnalisisABCTab(self.tabview.tab("📊 Análisis ABC"), self.db)
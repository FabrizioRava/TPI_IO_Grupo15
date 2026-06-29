import customtkinter as ctk
from views.inventario_tab import InventarioTab
from views.analisis_tab import AnalisisABCTab
from views.produccion_tab import ProduccionTab

class App(ctk.CTk):
    def __init__(self, db):
        super().__init__()
        
        self.db = db
        self.title("Sistema de Gestión de Inventarios - Análisis ABC")
        self.geometry("1400x900")
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Pestañas
        self.tabview = ctk.CTkTabview(
            self.main_frame,
            width=1300,
            height=800
        )
        self.tabview.grid(row=0, column=0, sticky="nsew")
        
        # Agregar pestañas
        self.tabview.add("📋 Inventario")
        self.tabview.add("📊 Análisis ABC")
        self.tabview.add("🏭 Producción")  # NUEVA PESTAÑA
        
        # Inicializar pestañas
        self.tab_inventario = InventarioTab(self.tabview.tab("📋 Inventario"), self.db)
        self.tab_analisis = AnalisisABCTab(self.tabview.tab("📊 Análisis ABC"), self.db)
        self.tab_produccion = ProduccionTab(self.tabview.tab("🏭 Producción"), self.db)
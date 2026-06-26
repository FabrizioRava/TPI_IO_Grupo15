import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from controllers.abc_controller import ABCController
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import numpy as np
from scipy.interpolate import CubicSpline
matplotlib.use('TkAgg')

class AnalisisABCTab:
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.controller = ABCController(db)
        self.df_resultados = None
        
        # Frame principal con scroll
        self.main_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="📊 Análisis ABC - Clasificación de Inventario",
            font=("Arial", 28, "bold")
        )
        titulo.pack(pady=(0, 15))
        
        # Botón para ejecutar el análisis
        self.btn_analizar = ctk.CTkButton(
            self.main_frame,
            text="🔍 Ejecutar Análisis ABC",
            command=self.ejecutar_analisis,
            height=50,
            font=("Arial", 18, "bold"),
            fg_color="#1565C0",
            hover_color="#0D47A1"
        )
        self.btn_analizar.pack(pady=15)
        
        # Frame para resultados (inicialmente oculto)
        self.resultados_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # Tabla de resultados
        self.tabla_frame = ctk.CTkFrame(self.resultados_frame, corner_radius=10)
        self.tabla_frame.pack(fill="both", expand=True, pady=10)
        
        self.crear_tabla_resultados()
        
        # Frame para recomendaciones - SIN SCROLL
        self.recomendaciones_frame = ctk.CTkFrame(self.resultados_frame, corner_radius=10)
        self.recomendaciones_frame.pack(fill="x", pady=10)
        
        self.recomendaciones_label = ctk.CTkLabel(
            self.recomendaciones_frame,
            text="",
            font=("Segoe UI", 16),
            wraplength=1100,
            justify="left",
            anchor="w"
        )
        self.recomendaciones_label.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Frame para el gráfico
        self.grafico_frame = ctk.CTkFrame(self.resultados_frame, corner_radius=10)
        self.grafico_frame.pack(fill="both", expand=True, pady=10)
        
        # Label para el gráfico (placeholder)
        self.label_grafico = ctk.CTkLabel(
            self.grafico_frame,
            text="El gráfico se mostrará aquí después del análisis",
            font=("Arial", 18)
        )
        self.label_grafico.pack(expand=True, pady=20)
    
    def crear_tabla_resultados(self):
        """Crea la tabla para mostrar los resultados del análisis ABC"""
        scroll_frame = ctk.CTkFrame(self.tabla_frame, corner_radius=10)
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Resultados.Treeview",
            background="#FFFFFF",
            foreground="#000000",
            rowheight=45,
            fieldbackground="#FFFFFF",
            font=("Segoe UI", 14),
            borderwidth=1,
            relief="solid"
        )
        
        style.configure(
            "Resultados.Treeview.Heading",
            background="#2C3E50",
            foreground="#FFFFFF",
            font=("Segoe UI", 15, "bold"),
            borderwidth=2,
            relief="solid"
        )
        
        style.map(
            "Resultados.Treeview",
            background=[("selected", "#1565C0")],
            foreground=[("selected", "#FFFFFF")]
        )
        
        self.tree_resultados = ttk.Treeview(
            scroll_frame,
            columns=("Producto", "Demanda", "Costo", "Capital", "Porcentaje", "Grupo"),
            show="headings",
            height=10,
            style="Resultados.Treeview"
        )
        
        self.tree_resultados.heading("Producto", text="Producto", anchor="w")
        self.tree_resultados.heading("Demanda", text="Demanda", anchor="center")
        self.tree_resultados.heading("Costo", text="Costo Unit.", anchor="center")
        self.tree_resultados.heading("Capital", text="Capital Total ($)", anchor="center")
        self.tree_resultados.heading("Porcentaje", text="% del Capital", anchor="center")
        self.tree_resultados.heading("Grupo", text="Grupo", anchor="center")
        
        self.tree_resultados.column("Producto", width=150, anchor="w")
        self.tree_resultados.column("Demanda", width=120, anchor="center")
        self.tree_resultados.column("Costo", width=130, anchor="center")
        self.tree_resultados.column("Capital", width=160, anchor="center")
        self.tree_resultados.column("Porcentaje", width=140, anchor="center")
        self.tree_resultados.column("Grupo", width=100, anchor="center")
        
        self.tree_resultados.tag_configure('A', background='#FFCDD2')
        self.tree_resultados.tag_configure('B', background='#FFF9C4')
        self.tree_resultados.tag_configure('C', background='#C8E6C9')
        
        scrollbar = ttk.Scrollbar(
            scroll_frame,
            orient="vertical",
            command=self.tree_resultados.yview
        )
        self.tree_resultados.configure(yscrollcommand=scrollbar.set)
        
        self.tree_resultados.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def ejecutar_analisis(self):
        articulos = self.db.obtener_articulos()
        if not articulos:
            messagebox.showwarning("Advertencia", "No hay productos en el inventario. Agrega algunos productos primero.")
            return
        
        self.resultados_frame.pack(fill="both", expand=True, pady=10)
        
        self.df_resultados = self.controller.calcular_analisis_abc()
        
        if self.df_resultados is None:
            messagebox.showerror("Error", "No se pudo realizar el análisis")
            return
        
        self.cargar_tabla_resultados()
        self.cargar_recomendaciones()
        self.generar_grafico()
    
    def cargar_tabla_resultados(self):
        for item in self.tree_resultados.get_children():
            self.tree_resultados.delete(item)
        
        for _, row in self.df_resultados.iterrows():
            grupo = row['grupo']
            self.tree_resultados.insert("", "end", values=(
                row['sku'],
                row['demanda'],
                f"${row['costo_unitario']:,.2f}",
                f"${row['capital']:,.2f}",
                f"{row['porcentaje_individual']:.1f}%",
                grupo
            ), tags=(grupo,))
    
    def cargar_recomendaciones(self):
        recomendaciones = self.controller.generar_recomendaciones(self.df_resultados)
        texto_completo = "\n\n".join(recomendaciones)
        self.recomendaciones_label.configure(text=texto_completo)
    
    def generar_grafico(self):
        """Genera el gráfico de Pareto del análisis ABC estilo imagen con bloques por grupo"""
        # Limpiar frame del gráfico
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()
        
        # Crear un frame contenedor para centrar el gráfico
        container_frame = ctk.CTkFrame(self.grafico_frame, fg_color="transparent")
        container_frame.pack(fill="both", expand=True)
        
        # Crear figura con tamaño más angosto
        fig, ax1 = plt.subplots(figsize=(8, 7))
        
        # Datos
        df = self.df_resultados
        
        # Calcular porcentaje de artículos y valor por grupo
        grupos = ['A', 'B', 'C']
        colores = ['#D32F2F', '#F57C00', '#388E3C']
        
        # Calcular estadísticas por grupo
        stats_grupos = []
        pos_actual = 0
        
        for grupo in grupos:
            df_grupo = df[df['grupo'] == grupo]
            if not df_grupo.empty:
                pct_articulos = (len(df_grupo) / len(df) * 100)
                pct_valor_individual = df_grupo['porcentaje_individual'].sum()
                pct_valor_acumulado = df_grupo['porcentaje_acumulado'].max()
                pos_media = pos_actual + pct_articulos / 2
                stats_grupos.append({
                    'grupo': grupo,
                    'pct_articulos': pct_articulos,
                    'pct_valor_individual': pct_valor_individual,
                    'pct_valor_acumulado': pct_valor_acumulado,
                    'pos_inicio': pos_actual,
                    'pos_fin': pos_actual + pct_articulos,
                    'pos_media': pos_media
                })
                pos_actual += pct_articulos
        
        # Dibujar bloques para cada grupo
        for i, stat in enumerate(stats_grupos):
            rect = plt.Rectangle(
                (stat['pos_inicio'], 0), 
                stat['pct_articulos'], 
                stat['pct_valor_acumulado'],
                facecolor=colores[i],
                alpha=0.7,
                edgecolor='black',
                linewidth=1.5
            )
            ax1.add_patch(rect)
            
            ax1.text(
                stat['pos_media'], 
                3,
                f"Grupo {stat['grupo']}\n{stat['pct_valor_individual']:.1f}%",
                ha='center', 
                va='bottom', 
                fontsize=14, 
                fontweight='bold',
                color='white',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.6)
            )
        
        # Configurar eje izquierdo
        ax1.set_xlabel('Porcentaje de Artículos (%)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Porcentaje del Valor Monetario (%)', fontsize=14, fontweight='bold')
        ax1.set_xlim(0, 105)
        ax1.set_ylim(0, 105)
        ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        ax1.set_xticks(range(0, 101, 10))
        ax1.set_xticklabels([f"{i}%" for i in range(0, 101, 10)], fontsize=12)
        
        ax1.set_yticks(range(0, 101, 10))
        ax1.set_yticklabels([f"{i}%" for i in range(0, 101, 10)], fontsize=12)
        
        # Curva acumulada
        porcentaje_articulos = df['porcentaje_articulos'].tolist()
        porcentaje_acumulado = df['porcentaje_acumulado'].tolist()
        
        x_curva = [0] + porcentaje_articulos
        y_curva = [0] + porcentaje_acumulado
        
        x_smooth = np.linspace(0, 100, 200)
        cs = CubicSpline(x_curva, y_curva, bc_type='natural')
        y_smooth = cs(x_smooth)
        
        ax1.plot(x_smooth, y_smooth, color='#1565C0', linewidth=3, label='Curva Acumulada')
        ax1.plot(porcentaje_articulos, porcentaje_acumulado, 'o', color='#0D47A1', markersize=8)
        
        ax1.axhline(y=80, color='red', linestyle='--', alpha=0.5, linewidth=2)
        ax1.axhline(y=95, color='orange', linestyle='--', alpha=0.5, linewidth=2)
        
        ax1.text(2, 82, '80%', color='red', fontsize=12, fontweight='bold')
        ax1.text(2, 97, '95%', color='orange', fontsize=12, fontweight='bold')
        
        ax1.set_title('Análisis ABC - Clasificación de Inventario', fontsize=16, fontweight='bold', pad=20)
        
        # Leyenda ELIMINADA
        
        fig.tight_layout()
        
        # Incrustar en Tkinter - centrado
        canvas = FigureCanvasTkAgg(fig, master=container_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True)
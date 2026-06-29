import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from controllers.produccion_controller import ProduccionController
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import numpy as np
matplotlib.use('TkAgg')

class ProduccionTab:
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.controller = ProduccionController(db)
        self.producto_seleccionado = None
        self.productos_grupo_a = []
        self.ultimo_resultado = None
        self.ultimo_texto = ""
        
        # Frame principal con scroll
        self.main_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="🏭 Análisis de Producción - Modelo EPQ",
            font=("Arial", 28, "bold")
        )
        titulo.pack(pady=(0, 15))
        
        # Subtítulo
        subtitulo = ctk.CTkLabel(
            self.main_frame,
            text="Seleccione un producto del Grupo A para analizar su estrategia de producción óptima",
            font=("Arial", 16)
        )
        subtitulo.pack(pady=(0, 15))
        
        # Frame para selección de producto
        self.seleccion_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.seleccion_frame.pack(fill="x", pady=10)
        
        self.label_producto = ctk.CTkLabel(
            self.seleccion_frame,
            text="Producto del Grupo A:",
            font=("Arial", 16)
        )
        self.label_producto.pack(side="left", padx=10, pady=10)
        
        self.combo_productos = ctk.CTkComboBox(
            self.seleccion_frame,
            values=["Cargando..."],
            width=350,
            height=40,
            font=("Arial", 14)
        )
        self.combo_productos.pack(side="left", padx=10, pady=10)
        
        self.btn_cargar = ctk.CTkButton(
            self.seleccion_frame,
            text="🔄 Cargar Productos Grupo A",
            command=self.cargar_productos_grupo_a,
            height=40,
            font=("Arial", 14)
        )
        self.btn_cargar.pack(side="left", padx=10, pady=10)
        
        # Frame para entrada de parámetros - EPQ
        self.parametros_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.parametros_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            self.parametros_frame,
            text="📐 Parámetros del Modelo EPQ",
            font=("Arial", 18, "bold")
        ).pack(pady=(10, 5))
        
        self.grid_parametros = ctk.CTkFrame(self.parametros_frame, fg_color="transparent")
        self.grid_parametros.pack(fill="x", padx=10, pady=5)
        
        # Costo de preparación (Co)
        ctk.CTkLabel(
            self.grid_parametros,
            text="Costo de preparación ($/lote):",
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.entry_co = ctk.CTkEntry(
            self.grid_parametros,
            width=180,
            height=40,
            font=("Arial", 14),
            placeholder_text="Ej: 500"
        )
        self.entry_co.grid(row=0, column=1, padx=5, pady=5)
        
        # Tasa de producción (p)
        ctk.CTkLabel(
            self.grid_parametros,
            text="Tasa de producción (unidades/año):",
            font=("Arial", 14)
        ).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        self.entry_p = ctk.CTkEntry(
            self.grid_parametros,
            width=180,
            height=40,
            font=("Arial", 14),
            placeholder_text="Ej: 5000"
        )
        self.entry_p.grid(row=0, column=3, padx=5, pady=5)
        
        # Costo de mantenimiento (Ch)
        ctk.CTkLabel(
            self.grid_parametros,
            text="Costo de mantenimiento ($/unidad/año):",
            font=("Arial", 14)
        ).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.entry_ch = ctk.CTkEntry(
            self.grid_parametros,
            width=180,
            height=40,
            font=("Arial", 14),
            placeholder_text="Ej: 10"
        )
        self.entry_ch.grid(row=1, column=1, padx=5, pady=5)
        
        # Costo por faltante (Cb) - OPCIONAL
        ctk.CTkLabel(
            self.grid_parametros,
            text="Costo por faltante ($/unidad/año):",
            font=("Arial", 14)
        ).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        self.entry_cb = ctk.CTkEntry(
            self.grid_parametros,
            width=180,
            height=40,
            font=("Arial", 14),
            placeholder_text="Opcional: dejar vacío"
        )
        self.entry_cb.grid(row=1, column=3, padx=5, pady=5)
        
        # Frame para entrada de parámetros - Stock de Seguridad y PR
        self.ss_pr_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.ss_pr_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            self.ss_pr_frame,
            text="🛡️ Stock de Seguridad y Punto de Reorden",
            font=("Arial", 18, "bold")
        ).pack(pady=(10, 5))
        
        self.grid_ss_pr = ctk.CTkFrame(self.ss_pr_frame, fg_color="transparent")
        self.grid_ss_pr.pack(fill="x", padx=10, pady=5)
        
        # Nivel de Servicio (NS)
        ctk.CTkLabel(
            self.grid_ss_pr,
            text="Nivel de servicio (0-1):",
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.entry_ns = ctk.CTkEntry(
            self.grid_ss_pr,
            width=160,
            height=40,
            font=("Arial", 14),
            placeholder_text="Ej: 0.95"
        )
        self.entry_ns.grid(row=0, column=1, padx=5, pady=5)
        
        # Días operativos al año
        ctk.CTkLabel(
            self.grid_ss_pr,
            text="Días operativos al año (máx 365):",
            font=("Arial", 14)
        ).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        self.entry_dias = ctk.CTkEntry(
            self.grid_ss_pr,
            width=160,
            height=40,
            font=("Arial", 14),
            placeholder_text="Ej: 300"
        )
        self.entry_dias.grid(row=0, column=3, padx=5, pady=5)
        
        # Lead Time promedio (L)
        ctk.CTkLabel(
            self.grid_ss_pr,
            text="Tiempo de envío (días):",
            font=("Arial", 14)
        ).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.entry_L = ctk.CTkEntry(
            self.grid_ss_pr,
            width=160,
            height=40,
            font=("Arial", 14),
            placeholder_text="Ej: 5"
        )
        self.entry_L.grid(row=1, column=1, padx=5, pady=5)
        
        # Desvío estándar del lead time (σ_L) - OPCIONAL
        ctk.CTkLabel(
            self.grid_ss_pr,
            text="Desviación en tiempo de envío (días):",
            font=("Arial", 14)
        ).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        self.entry_sigma_L = ctk.CTkEntry(
            self.grid_ss_pr,
            width=160,
            height=40,
            font=("Arial", 14),
            placeholder_text="Opcional: 0 por defecto"
        )
        self.entry_sigma_L.grid(row=1, column=3, padx=5, pady=5)
        
        # Tipo de desviación de demanda
        ctk.CTkLabel(
            self.grid_ss_pr,
            text="Tipo de desviación de demanda:",
            font=("Arial", 14)
        ).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.combo_tipo_desviacion = ctk.CTkComboBox(
            self.grid_ss_pr,
            values=["Diaria (unidades/día)", "Durante el envío (unidades)"],
            width=180,
            height=40,
            font=("Arial", 14)
        )
        self.combo_tipo_desviacion.grid(row=2, column=1, padx=5, pady=5)
        self.combo_tipo_desviacion.set("Diaria (unidades/día)")
        
        # Desvío estándar de la demanda (σ_d)
        ctk.CTkLabel(
            self.grid_ss_pr,
            text="Desviación de la demanda:",
            font=("Arial", 14)
        ).grid(row=2, column=2, padx=5, pady=5, sticky="w")
        
        self.entry_sigma_d = ctk.CTkEntry(
            self.grid_ss_pr,
            width=160,
            height=40,
            font=("Arial", 14),
            placeholder_text="Opcional: 0 por defecto"
        )
        self.entry_sigma_d.grid(row=2, column=3, padx=5, pady=5)
        
        # Botón para calcular
        self.btn_calcular = ctk.CTkButton(
            self.main_frame,
            text="📊 Calcular Estrategia Óptima Completa",
            command=self.calcular_completo,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color="#1565C0",
            hover_color="#0D47A1"
        )
        self.btn_calcular.pack(pady=15)
        
        # ====== RECOMENDACIONES (sin scroll) ======
        self.recomendaciones_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.recomendaciones_frame.pack(fill="x", pady=10)
        
        self.recomendaciones_label = ctk.CTkLabel(
            self.recomendaciones_frame,
            text="",
            font=("Segoe UI", 14),
            wraplength=1200,
            justify="left",
            anchor="w"
        )
        self.recomendaciones_label.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Frame para gráficos
        self.graficos_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.graficos_frame.pack(fill="both", expand=True, pady=10)
        
        # Cargar productos automáticamente al iniciar
        self.cargar_productos_grupo_a()
    
    def cargar_productos_grupo_a(self):
        """Carga los productos del Grupo A en el combobox"""
        self.productos_grupo_a = self.controller.obtener_productos_grupo_a()
        
        if not self.productos_grupo_a:
            self.combo_productos.configure(values=["No hay productos en Grupo A"])
            self.combo_productos.set("No hay productos en Grupo A")
            return
        
        valores = [f"{p['sku']} - {p['nombre']} (D={p['demanda']})" for p in self.productos_grupo_a]
        self.combo_productos.configure(values=valores)
        self.combo_productos.set(valores[0])
        self.actualizar_demanda_seleccionada()
    
    def actualizar_demanda_seleccionada(self):
        """Actualiza el producto seleccionado"""
        seleccion = self.combo_productos.get()
        if not seleccion or seleccion.startswith("No hay"):
            self.producto_seleccionado = None
            return
        
        sku = seleccion.split(" - ")[0]
        for p in self.productos_grupo_a:
            if p['sku'] == sku:
                self.producto_seleccionado = p
                break
    
    def calcular_completo(self):
        """Calcula y muestra todos los resultados: EPQ + SS + PR + gráficos"""
        if not self.producto_seleccionado:
            messagebox.showerror("Error", "Seleccione un producto del Grupo A")
            return
        
        # Obtener valores de EPQ
        try:
            co = float(self.entry_co.get().strip())
            p = float(self.entry_p.get().strip())
            ch = float(self.entry_ch.get().strip())
            if co <= 0 or p <= 0 or ch <= 0:
                messagebox.showerror("Error", "Co, p y Ch deben ser > 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos para EPQ")
            return
        
        # Obtener valores de SS y PR
        try:
            nivel_servicio = float(self.entry_ns.get().strip())
            dias_operativos = float(self.entry_dias.get().strip())
            L = float(self.entry_L.get().strip())
            
            # Validar días operativos
            if dias_operativos > 365:
                messagebox.showerror("Error", "Los días operativos no pueden superar los 365 días por año")
                return
            if dias_operativos <= 0:
                messagebox.showerror("Error", "Los días operativos deben ser mayores a 0")
                return
            
            # Validar nivel de servicio
            if nivel_servicio < 0 or nivel_servicio > 1:
                messagebox.showerror("Error", "El nivel de servicio debe estar entre 0 y 1")
                return
            
            sigma_L_text = self.entry_sigma_L.get().strip()
            sigma_d_text = self.entry_sigma_d.get().strip()
            sigma_L = float(sigma_L_text) if sigma_L_text else 0
            sigma_d = float(sigma_d_text) if sigma_d_text else 0
            
            if L <= 0 or sigma_L < 0 or sigma_d < 0:
                messagebox.showerror("Error", "Todos los valores deben ser positivos")
                return
            
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos para SS/PR")
            return
        
        # Obtener tipo de desviación
        tipo_desviacion = 'diaria' if self.combo_tipo_desviacion.get() == "Diaria (unidades/día)" else 'lead_time'
        
        # Leer Cb (opcional)
        cb_text = self.entry_cb.get().strip()
        cb = None
        if cb_text:
            try:
                cb = float(cb_text)
                if cb <= 0:
                    messagebox.showerror("Error", "Cb debe ser > 0")
                    return
            except ValueError:
                messagebox.showerror("Error", "Cb debe ser un valor numérico")
                return
        
        demanda = self.producto_seleccionado['demanda']
        sku = self.producto_seleccionado['sku']
        costo_unitario = self.producto_seleccionado['costo_unitario']
        
        # Validaciones
        advertencias = self.controller.validar_datos(nivel_servicio, dias_operativos)
        if advertencias:
            mensaje = "\n\n".join(advertencias)
            if "ERROR" in mensaje:
                messagebox.showerror("Error de validación", mensaje)
                return
            else:
                messagebox.showwarning("Advertencia", mensaje)
        
        # Calcular EPQ
        resultado_epq = self.controller.calcular_epq(demanda, co, p, ch, cb)
        if resultado_epq.get('error', False):
            messagebox.showerror("Error", resultado_epq['mensaje'])
            return
        
        # Obtener S* para SS/PR
        s_optima = resultado_epq.get('s_optima', 0)
        
        # ============================================================
        # CALCULAR SS Y PR - PASANDO CH PARA EL COSTO DEL SS
        # ============================================================
        resultado_ss_pr = self.controller.calcular_ss_pr(
            demanda=demanda,
            dias_operativos=dias_operativos,
            L=L,
            sigma_L=sigma_L,
            sigma_d=sigma_d,
            nivel_servicio=nivel_servicio,
            s_optima=s_optima,
            tipo_desviacion=tipo_desviacion,
            ch=ch
        )
        
        # Obtener costo_ss del resultado (ya calculado como SS × Ch)
        costo_ss = resultado_ss_pr['costo_ss']
        
        # Calcular costo total incluyendo SS
        ct = resultado_epq['ct']
        ct_con_ss = ct + costo_ss
        
        # ============================================================
        # CALCULAR VALORES EN DÍAS PARA COMPARAR
        # ============================================================
        t_dias = resultado_epq['t'] * dias_operativos
        tp_dias = resultado_epq['tp'] * dias_operativos
        td_dias = resultado_epq['td'] * dias_operativos
        
        # ============================================================
        # COMPARAR CON RESULTADO ANTERIOR PARA DETECTAR CAMBIOS
        # ============================================================
        resultado_actual = {
            # Variables principales del EPQ
            'q_optima': resultado_epq['q_optima'],
            'cp': resultado_epq['cp'],
            'cm': resultado_epq['cm'],
            'ct': resultado_epq['ct'],
            'imax': resultado_epq['imax'],                    # <--- NUEVO
            'n': resultado_epq['n'],
            
            # Variables de tiempos
            't_dias': t_dias,
            'tp_dias': tp_dias,
            'td_dias': td_dias,                               # <--- NUEVO
            
            # Variables de stock
            'ss_redondeado': resultado_ss_pr['ss_redondeado'],
            'pr_redondeado': resultado_ss_pr['pr_redondeado'],
            
            # Variables de costos con stock de seguridad
            'costo_ss': costo_ss,
            'ct_con_ss': ct_con_ss,
            
            # Variables específicas si hay faltantes
            's_optima': resultado_epq.get('s_optima', 0),      # <--- NUEVO
            'ct_f': resultado_epq.get('ct_f', 0),              # <--- NUEVO
        }
        
        cambios = self.controller.comparar_con_anterior(resultado_actual)
        self.controller.ultimo_resultado = resultado_actual
        
        # Generar texto de cambios si existen
        texto_cambios = ""
        if cambios:
            texto_cambios = "\n\n📊 CAMBIOS DETECTADOS RESPECTO AL ANÁLISIS ANTERIOR:\n"
            for clave, cambio in cambios.items():
                simbolo = cambio['simbolo']
                # Mostrar con 2 decimales para valores monetarios
                if 'costo' in clave or 'ct' in clave:
                    texto_cambios += f"   {simbolo} {cambio['nombre']}: ${cambio['valor_anterior']:.2f} → ${cambio['valor_nuevo']:.2f} "
                else:
                    texto_cambios += f"   {simbolo} {cambio['nombre']}: {cambio['valor_anterior']:.2f} → {cambio['valor_nuevo']:.2f} "
                if cambio['cambio'] == 'aumento':
                    texto_cambios += f"(aumentó en {cambio['diferencia']:.2f})\n"
                else:
                    texto_cambios += f"(disminuyó en {cambio['diferencia']:.2f})\n"
        
        # Generar recomendaciones
        recomendaciones = self.controller.generar_recomendaciones(
            demanda=demanda,
            q_optima=resultado_epq['q_optima'],
            cp=resultado_epq['cp'],
            cm=resultado_epq['cm'],
            ct=resultado_epq['ct'],
            t=resultado_epq['t'],
            tp=resultado_epq['tp'],
            td=resultado_epq['td'],
            imax=resultado_epq['imax'],
            n=resultado_epq['n'],
            ss=resultado_ss_pr['ss_redondeado'],
            pr=resultado_ss_pr['pr_redondeado'],
            nivel_servicio=nivel_servicio,
            tiene_faltantes=resultado_epq['tiene_faltantes'],
            s_optima=s_optima,
            cb=cb,
            cf=resultado_epq.get('cf'),
            ct_f=resultado_epq.get('ct_f'),
            dias_operativos=dias_operativos,
            L=L,
            sigma_L=sigma_L,
            sigma_d=sigma_d,
            tipo_desviacion=tipo_desviacion,
            costo_ss=costo_ss,
            costo_unitario=costo_unitario
        )
        
        # Agregar cambios al texto
        texto_final = recomendaciones
        if texto_cambios:
            texto_final += texto_cambios
        
        # Mostrar recomendaciones
        self.recomendaciones_label.configure(text=texto_final)
        self.ultimo_texto = texto_final
        
        # Graficar
        self.graficar(resultado_epq, resultado_ss_pr, demanda, co, ch, p, cb, dias_operativos)
    
    def graficar(self, resultado_epq, resultado_ss_pr, demanda, co, ch, p, cb=None, dias_operativos=300):
        """Genera los gráficos: sierra y costos con escala adaptada a días operativos"""
        for widget in self.graficos_frame.winfo_children():
            widget.destroy()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        q_optima = resultado_epq['q_optima']
        imax = resultado_epq['imax']
        t = resultado_epq['t']
        tp = resultado_epq['tp']
        tiene_faltantes = resultado_epq['tiene_faltantes']
        s_optima = resultado_epq.get('s_optima', 0)
        
        # ========== GRÁFICO 1: SIERRA ==========
        max_dias = dias_operativos
        tiempo_total = np.linspace(0, max_dias, 500)
        inventario = []
        
        for tiempo in tiempo_total:
            t_ciclo = tiempo % (t * dias_operativos)
            t_prod = tp * dias_operativos
            
            if t_ciclo <= t_prod:
                inv = (p - demanda) * (t_ciclo / dias_operativos)
            else:
                inv = imax - demanda * ((t_ciclo - t_prod) / dias_operativos)
            
            if tiene_faltantes:
                inv = max(inv, -s_optima)
            else:
                inv = max(inv, 0)
            inventario.append(inv)
        
        ax1.plot(tiempo_total, inventario, color='#1565C0', linewidth=2)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        if resultado_ss_pr['pr_redondeado'] > 0:
            ax1.axhline(y=resultado_ss_pr['pr_redondeado'], color='red', linestyle='--', 
                       linewidth=1.5, label=f'PR = {resultado_ss_pr["pr_redondeado"]}')
        if resultado_ss_pr['ss_redondeado'] > 0:
            ax1.axhline(y=resultado_ss_pr['ss_redondeado'], color='green', linestyle='--', 
                       linewidth=1.5, label=f'SS = {resultado_ss_pr["ss_redondeado"]}')
        
        ax1.set_xlabel('Tiempo (días)', fontsize=12)
        ax1.set_ylabel('Inventario (unidades)', fontsize=12)
        ax1.set_title('Gráfico de Sierra - Evolución del Inventario', fontsize=14)
        ax1.set_xlim(0, max_dias)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # ========== GRÁFICO 2: COSTOS ==========
        q_range = np.linspace(max(1, q_optima * 0.2), q_optima * 2.5, 100)
        cp_values = (demanda / q_range) * co
        cm_values = (q_range / 2) * ch * (1 - demanda / p)
        ct_values = cp_values + cm_values
        
        ax2.plot(q_range, cp_values, color='orange', linewidth=2, label='Costo de Producción (CP)')
        ax2.plot(q_range, cm_values, color='green', linewidth=2, label='Costo de Inventario (CI)')
        ax2.plot(q_range, ct_values, color='blue', linewidth=2.5, label='Costo Total (CT)')
        
        if tiene_faltantes and cb is not None and cb > 0:
            q_range_falt = np.linspace(max(1, q_optima * 0.2), q_optima * 2.5, 100)
            cp_falt = (demanda / q_range_falt) * co
            cm_falt = (q_range_falt / 2) * ch * (1 - demanda / p)
            ct_falt_values = cp_falt + cm_falt + ((q_range_falt * (ch/(ch+cb))**2 * cb) / (2 * (1 - demanda/p)))
            ax2.plot(q_range_falt, ct_falt_values, color='purple', linewidth=2, 
                    linestyle='--', label='CT con faltantes')
        
        ax2.scatter(q_optima, resultado_epq['ct'], color='red', s=100, zorder=5)
        ax2.annotate(f'Q* = {q_optima}', 
                    xy=(q_optima, resultado_epq['ct']),
                    xytext=(q_optima * 1.1, resultado_epq['ct'] * 0.9),
                    fontsize=11, fontweight='bold')
        
        ax2.set_xlabel('Tamaño del Lote (Q)', fontsize=12)
        ax2.set_ylabel('Costos ($/año)', fontsize=12)
        ax2.set_title('Análisis de Costos vs Tamaño de Lote', fontsize=14)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.graficos_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
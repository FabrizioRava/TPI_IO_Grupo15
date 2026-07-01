import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database

class InventarioTab:
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        
        # Frame principal con padding
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo = ctk.CTkLabel(
            self.frame, 
            text="📋 Gestión de Inventario", 
            font=("Arial", 28, "bold")
        )
        titulo.pack(pady=(0, 15))
        
        # Frame para la tabla
        self.tabla_frame = ctk.CTkFrame(self.frame, corner_radius=10)
        self.tabla_frame.pack(fill="both", expand=True, pady=10)
        
        # Crear la tabla
        self.crear_tabla()
        
        # Frame para botones
        self.botones_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.botones_frame.pack(fill="x", pady=10)
        
        # Botones con mejor estilo y fuente más grande
        self.btn_agregar = ctk.CTkButton(
            self.botones_frame, 
            text="➕ Agregar Producto", 
            command=self.agregar_producto,
            height=45,
            font=("Arial", 16)
        )
        self.btn_agregar.pack(side="left", padx=5)
        
        self.btn_eliminar = ctk.CTkButton(
            self.botones_frame, 
            text="🗑️ Eliminar Seleccionado", 
            command=self.eliminar_producto,
            height=45,
            font=("Arial", 16),
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        )
        self.btn_eliminar.pack(side="left", padx=5)
        
        self.btn_actualizar = ctk.CTkButton(
            self.botones_frame, 
            text="🔄 Actualizar", 
            command=self.cargar_datos,
            height=45,
            font=("Arial", 16),
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        )
        self.btn_actualizar.pack(side="left", padx=5)
        
        # Cargar datos
        self.cargar_datos()
    
    def crear_tabla(self):
        """Crea la tabla con Treeview mejorada con bordes y líneas"""
        # Frame para scroll
        self.scroll_frame = ctk.CTkFrame(self.tabla_frame, corner_radius=10)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Estilo para la tabla
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configurar estilo de la tabla con bordes visibles y FUENTE GRANDE
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#000000",
            rowheight=45,
            fieldbackground="#FFFFFF",
            font=("Segoe UI", 14),
            borderwidth=1,
            relief="solid"
        )
        
        # Configurar el estilo del heading (encabezados) con FUENTE GRANDE
        style.configure(
            "Treeview.Heading",
            background="#2C3E50",
            foreground="#FFFFFF",
            font=("Segoe UI", 15, "bold"),
            borderwidth=2,
            relief="solid"
        )
        
        # Mapa de colores para selección
        style.map(
            "Treeview",
            background=[("selected", "#1565C0")],
            foreground=[("selected", "#FFFFFF")]
        )
        
        # Treeview - SOLO 3 columnas: Producto, Demanda, Costo
        self.tree = ttk.Treeview(
            self.scroll_frame, 
            columns=("Producto", "Demanda", "Costo"), 
            show="headings",
            height=12,
            style="Treeview"
        )
        
        # Configurar columnas
        self.tree.heading("Producto", text="Producto", anchor="w")
        self.tree.heading("Demanda", text="Demanda Anual", anchor="center")
        self.tree.heading("Costo", text="Costo Unitario ($)", anchor="center")
        
        self.tree.column("Producto", width=300, anchor="w")
        self.tree.column("Demanda", width=200, anchor="center")
        self.tree.column("Costo", width=200, anchor="center")
        
        # Agregar tags para colores alternados
        self.tree.tag_configure('odd', background='#F5F5F5')
        self.tree.tag_configure('even', background='#FFFFFF')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.scroll_frame, 
            orient="vertical", 
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Eventos
        self.tree.bind("<Double-1>", self.on_double_click)
    
    def cargar_datos(self):
        """Carga los datos de la base de datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener datos
        articulos = self.db.obtener_articulos()
        
        # Insertar en la tabla - SOLO el nombre del producto
        for i, articulo in enumerate(articulos):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=(
                articulo[1],   # Nombre
                articulo[2],   # Demanda
                f"${articulo[3]:,.2f}"  # Costo
            ), tags=(tag,))
    
    def on_double_click(self, event):
        """Maneja el doble clic para editar una celda"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        column = self.tree.identify_column(event.x)
        
        # Convertir columna a índice (0, 1, 2)
        col_index = int(column.replace("#", "")) - 1
        
        # Solo permitir editar Demanda (col 1) y Costo (col 2)
        if col_index not in [1, 2]:
            return
        
        # El nombre está en la columna 0
        nombre = values[0]
        
        # Obtener el nombre de la columna
        col_name = ["Producto", "Demanda", "Costo"][col_index]
        
        # Crear ventana de edición
        self.mostrar_dialogo_edicion(nombre, col_index, col_name, values)
    
    def mostrar_dialogo_edicion(self, nombre, col_index, col_name, values):
        """Muestra un diálogo para editar el valor"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"Editar {col_name}")
        dialog.geometry("500x320")
        dialog.grab_set()
        dialog.transient(self.parent)
        dialog.focus_force()
        
        # Frame principal
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Información del artículo - Fuente más grande
        ctk.CTkLabel(
            frame, 
            text=f"Editando: {nombre}", 
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        # Obtener el artículo completo de la BD para tener el ID
        articulos = self.db.obtener_articulos()
        articulo_data = None
        for a in articulos:
            if a[1] == nombre:  # a[1] es el nombre
                articulo_data = a
                break
        
        if not articulo_data:
            messagebox.showerror("Error", "Artículo no encontrado")
            dialog.destroy()
            return
        
        articulo_id = articulo_data[0]
        valor_actual = values[col_index]
        if col_name == "Costo":
            valor_actual = valor_actual.replace("$", "").replace(",", "")
        
        # Entry para nuevo valor - Fuente más grande
        ctk.CTkLabel(frame, text=f"Valor actual: {valor_actual}", font=("Arial", 14)).pack(pady=5)
        ctk.CTkLabel(frame, text="Nuevo valor:", font=("Arial", 14)).pack(pady=5)
        
        entry = ctk.CTkEntry(frame, height=45, font=("Arial", 14))
        entry.insert(0, str(valor_actual))
        entry.pack(pady=5, fill="x")
        
        def guardar():
            try:
                nuevo_valor = entry.get().strip()
                
                # Obtener el artículo completo
                articulo = self.db.obtener_articulo_por_id(articulo_id)
                if not articulo:
                    messagebox.showerror("Error", "Artículo no encontrado")
                    return
                
                # Crear lista con los valores actuales
                valores_actuales = list(articulo)
                
                # Actualizar el valor correspondiente
                # El orden es: id, nombre, demanda, costo
                if col_index == 1:  # Demanda
                    valores_actuales[2] = int(nuevo_valor)
                elif col_index == 2:  # Costo
                    valores_actuales[3] = float(nuevo_valor)
                
                # Actualizar en la base de datos
                self.db.actualizar_articulo(
                    articulo_id,
                    valores_actuales[1],  # nombre
                    valores_actuales[2],  # demanda
                    valores_actuales[3]   # costo
                )
                
                dialog.destroy()
                self.cargar_datos()
                messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa un valor numérico válido")
        
        # Frame para botones - Fuente más grande
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(
            btn_frame, 
            text="💾 Guardar", 
            command=guardar, 
            height=40,
            font=("Arial", 14)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="❌ Cancelar", 
            command=dialog.destroy, 
            height=40,
            font=("Arial", 14)
        ).pack(side="left", padx=5)
    
    def agregar_producto(self):
        """Abre un diálogo para agregar un nuevo producto - SIN SKU"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Agregar Nuevo Producto")
        dialog.geometry("500x400")  # Más pequeño porque ya no tiene SKU
        dialog.grab_set()
        dialog.transient(self.parent)
        dialog.focus_force()
        
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título - Fuente más grande
        ctk.CTkLabel(
            frame, 
            text="➕ Nuevo Producto", 
            font=("Arial", 20, "bold")
        ).pack(pady=10)
        
        # Campos - Fuente más grande (SIN SKU)
        campos = [
            ("Nombre del Producto:", "entry_nombre"),
            ("Demanda Anual:", "entry_demanda"),
            ("Costo Unitario ($):", "entry_costo")
        ]
        
        entries = {}
        for label, key in campos:
            ctk.CTkLabel(frame, text=label, font=("Arial", 14)).pack(pady=(10, 2))
            entry = ctk.CTkEntry(frame, height=40, font=("Arial", 14))
            entry.pack(pady=(0, 5), fill="x")
            entries[key] = entry
        
        def guardar():
            try:
                nombre = entries["entry_nombre"].get().strip()
                demanda = int(entries["entry_demanda"].get().strip())
                costo = float(entries["entry_costo"].get().strip())
                
                if not nombre:
                    messagebox.showerror("Error", "El nombre es obligatorio")
                    return
                
                # Insertar en la base de datos (SIN SKU)
                resultado = self.db.insertar_articulo(nombre, demanda, costo)
                
                if resultado == -1:
                    messagebox.showerror("Error", f"El producto '{nombre}' ya existe")
                else:
                    dialog.destroy()
                    self.cargar_datos()
                    messagebox.showinfo("Éxito", "Producto agregado correctamente")
                    
            except ValueError:
                messagebox.showerror("Error", "Demanda y Costo deben ser valores numéricos")
        
        ctk.CTkButton(
            frame, 
            text="💾 Guardar", 
            command=guardar, 
            height=40,
            font=("Arial", 14)
        ).pack(pady=15)
        
        ctk.CTkButton(
            frame, 
            text="❌ Cancelar", 
            command=dialog.destroy, 
            height=40,
            font=("Arial", 14)
        ).pack()
    
    def eliminar_producto(self):
        """Elimina el producto seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un producto para eliminar")
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        nombre = values[0]  # Ahora es el nombre del producto
        
        # Obtener el ID del artículo desde la BD
        articulos = self.db.obtener_articulos()
        articulo_id = None
        for a in articulos:
            if a[1] == nombre:
                articulo_id = a[0]
                break
        
        if not articulo_id:
            messagebox.showerror("Error", "Producto no encontrado")
            return
        
        # Confirmar
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar el producto '{nombre}'?"):
            self.db.eliminar_articulo(articulo_id)
            self.cargar_datos()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
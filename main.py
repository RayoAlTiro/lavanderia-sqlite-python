import tkinter as tk
from tkinter import ttk, messagebox
from app.models.customer import Customer
from app.models.service import Service 
# Asegúrate de que tus modelos Order y Payment existan y estén en la ruta app.models
# from app.models.order import Order 
# from app.models.payment import Payment 

class LavanderiaApp(tk.Tk):
    """Clase principal de la aplicación GUI con Tkinter."""
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Lavandería")
        self.geometry("1000x600") 
        
        # Configurar Estilo Ttk para una apariencia moderna
        self.style = ttk.Style(self)
        self.style.theme_use('clam') 

        # Contenedor de pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Crear y añadir todas las pestañas
        self.create_customer_tab()
        self.create_service_tab()
        self.create_order_tab()
        self.create_payment_tab()

    # =======================================================
    # MÓDULO: CLIENTES (CRUD COMPLETO) 👥
    # =======================================================

    def create_customer_tab(self):
        """Configura el frame (pestaña) de gestión de Clientes."""
        self.customer_frame = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.notebook.add(self.customer_frame, text='Clientes 👥')
        
        ttk.Label(self.customer_frame, text="Gestión de Clientes", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        self.customer_list_container = ttk.Frame(self.customer_frame)
        self.customer_list_container.pack(fill='both', expand=True, pady=10)

        self.customer_button_frame = ttk.Frame(self.customer_frame)
        self.customer_button_frame.pack(fill='x', pady=5)

        ttk.Button(self.customer_button_frame, text="Recargar", command=self.load_customer_data).pack(side='left', padx=5)
        ttk.Button(self.customer_button_frame, text="Alta Nuevo Cliente", command=self.open_create_customer_window).pack(side='left', padx=5)
        ttk.Button(self.customer_button_frame, text="Modificar Cliente", command=self.open_edit_customer_window).pack(side='left', padx=5)
        ttk.Button(self.customer_button_frame, text="Eliminar Cliente", command=self.delete_customer).pack(side='left', padx=5)
        
        self.load_customer_data()
        
    def load_customer_data(self):
        """Carga y muestra la lista de clientes en el Treeview."""
        for widget in self.customer_list_container.winfo_children():
            widget.destroy()

        columns = ('id', 'name', 'phone', 'email')
        self.customer_tree = ttk.Treeview(self.customer_list_container, columns=columns, show='headings')
        self.customer_tree.pack(side='left', fill='both', expand=True)

        vsb = ttk.Scrollbar(self.customer_list_container, orient="vertical", command=self.customer_tree.yview)
        vsb.pack(side='right', fill='y')
        self.customer_tree.configure(yscrollcommand=vsb.set)

        self.customer_tree.heading('id', text='ID', anchor='center'); self.customer_tree.column('id', width=50, stretch=tk.NO, anchor='center')
        self.customer_tree.heading('name', text='Nombre', anchor='w'); self.customer_tree.column('name', width=150, stretch=tk.YES)
        self.customer_tree.heading('phone', text='Teléfono', anchor='w'); self.customer_tree.column('phone', width=100, stretch=tk.YES)
        self.customer_tree.heading('email', text='Email', anchor='w'); self.customer_tree.column('email', width=200, stretch=tk.YES)

        customers = Customer.all() 
        for c in customers:
            # c ahora es un diccionario gracias a la corrección en Customer.all()
            self.customer_tree.insert('', tk.END, values=(c['id'], c['name'], c['phone'], c['email']))
    
    # ALTA (CREATE)
    def open_create_customer_window(self):
        """Abre ventana emergente para Alta de cliente."""
        top = tk.Toplevel(self)
        top.title("Alta de Nuevo Cliente")
        top.geometry("350x250")
        top.transient(self); top.grab_set()

        labels = ["Nombre:", "Teléfono:", "Email:"]
        entries = {}; main_frame = ttk.Frame(top, padding="15"); main_frame.pack(fill='both', expand=True)

        for i, text in enumerate(labels):
            ttk.Label(main_frame, text=text).grid(row=i, column=0, sticky='w', pady=5, padx=5)
            entry = ttk.Entry(main_frame, width=30)
            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=5)
            entries[text] = entry
        
        button_frame = ttk.Frame(main_frame); button_frame.grid(row=len(labels), columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="Guardar", 
                   command=lambda: self.save_new_customer(top, entries)).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Cancelar", command=top.destroy).pack(side='left', padx=10)
        main_frame.grid_columnconfigure(1, weight=1)

    def save_new_customer(self, top_level, entries):
        """Guarda los datos del nuevo cliente."""
        name = entries["Nombre:"].get().strip()
        phone = entries["Teléfono:"].get().strip()
        email = entries["Email:"].get().strip()

        if not name:
            messagebox.showerror("Error de Validación", "El campo Nombre no puede estar vacío.")
            return
        try:
            new_id = Customer.create(name, phone, email) 
            messagebox.showinfo("Éxito", f"Cliente '{name}' creado con ID: {new_id}")
            top_level.destroy()
            self.load_customer_data()
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al guardar: {e}")

    # MODIFICACIÓN (UPDATE)
    def open_edit_customer_window(self):
        """Abre la ventana emergente para modificar el cliente seleccionado."""
        selected_item = self.customer_tree.focus()
        
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Debes seleccionar un cliente de la lista para modificar.")
            return

        values = self.customer_tree.item(selected_item, 'values')
        customer_id = values[0]
        cliente = Customer.get_by_id(customer_id) 

        top = tk.Toplevel(self)
        top.title(f"Modificar Cliente ID: {customer_id}")
        top.geometry("350x250")
        top.transient(self); top.grab_set()

        labels = ["Nombre:", "Teléfono:", "Email:"]
        entries = {}; main_frame = ttk.Frame(top, padding="15"); main_frame.pack(fill='both', expand=True)

        # Acceso por atributo (cliente.name), ya que Customer.get_by_id retorna una instancia de Customer
        initial_data = {"Nombre:": cliente.name, "Teléfono:": cliente.phone, "Email:": cliente.email}

        for i, text in enumerate(labels):
            ttk.Label(main_frame, text=text).grid(row=i, column=0, sticky='w', pady=5, padx=5)
            entry = ttk.Entry(main_frame, width=30)
            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=5)
            entries[text] = entry
            entry.insert(0, initial_data.get(text, ''))
        
        button_frame = ttk.Frame(main_frame); button_frame.grid(row=len(labels), columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="Guardar Cambios", 
                   command=lambda: self.update_existing_customer(top, cliente, entries)).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Cancelar", command=top.destroy).pack(side='left', padx=10)
        main_frame.grid_columnconfigure(1, weight=1)

    def update_existing_customer(self, top_level, cliente_instance, entries):
        """Actualiza la instancia del cliente y guarda los cambios en la BD."""
        name = entries["Nombre:"].get().strip()
        phone = entries["Teléfono:"].get().strip()
        email = entries["Email:"].get().strip()

        if not name:
            messagebox.showerror("Error de Validación", "El campo Nombre no puede estar vacío.")
            return
        
        try:
            cliente_instance.name = name
            cliente_instance.phone = phone
            cliente_instance.email = email
            cliente_instance.update()
            
            messagebox.showinfo("Éxito", f"Cliente {name} modificado correctamente.")
            top_level.destroy()
            self.load_customer_data()
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al actualizar: {e}")
            
    # BAJA (DELETE)
    def delete_customer(self):
        """Elimina el cliente seleccionado en la tabla."""
        selected_item = self.customer_tree.focus()
        
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Debes seleccionar un cliente de la lista para eliminar.")
            return

        values = self.customer_tree.item(selected_item, 'values')
        customer_id = values[0]
        customer_name = values[1]

        confirm = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Estás seguro de que deseas eliminar al cliente: {customer_name} (ID: {customer_id})?"
        )

        if confirm:
            try:
                cliente = Customer.get_by_id(customer_id) 
                cliente.delete()
                
                messagebox.showinfo("Éxito", f"Cliente {customer_name} eliminado correctamente.")
                self.load_customer_data()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el cliente: {e}")

    # =======================================================
    # MÓDULO: SERVICIOS (CRUD COMPLETO) 🧺 - AJUSTADO A MODELO ESTÁTICO
    # =======================================================

    def create_service_tab(self):
        """Configura el frame (pestaña) de gestión de Servicios."""
        self.service_frame = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.notebook.add(self.service_frame, text='Servicios 🧺')
        
        ttk.Label(self.service_frame, text="Gestión de Servicios", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        self.service_list_container = ttk.Frame(self.service_frame)
        self.service_list_container.pack(fill='both', expand=True, pady=10)

        self.service_button_frame = ttk.Frame(self.service_frame)
        self.service_button_frame.pack(fill='x', pady=5)

        ttk.Button(self.service_button_frame, text="Recargar", command=self.load_service_data).pack(side='left', padx=5)
        ttk.Button(self.service_button_frame, text="Alta Nuevo Servicio", command=self.open_create_service_window).pack(side='left', padx=5)
        ttk.Button(self.service_button_frame, text="Modificar Servicio", command=self.open_edit_service_window).pack(side='left', padx=5)
        ttk.Button(self.service_button_frame, text="Eliminar Servicio", command=self.delete_service).pack(side='left', padx=5)
        
        self.load_service_data()

    def load_service_data(self):
        """Carga y muestra la lista de servicios en el Treeview."""
        for widget in self.service_list_container.winfo_children():
            widget.destroy()

        columns = ('id', 'name', 'price')
        self.service_tree = ttk.Treeview(self.service_list_container, columns=columns, show='headings')
        self.service_tree.pack(side='left', fill='both', expand=True)

        vsb = ttk.Scrollbar(self.service_list_container, orient="vertical", command=self.service_tree.yview)
        vsb.pack(side='right', fill='y')
        self.service_tree.configure(yscrollcommand=vsb.set)

        self.service_tree.heading('id', text='ID', anchor='center'); self.service_tree.column('id', width=50, stretch=tk.NO, anchor='center')
        self.service_tree.heading('name', text='Nombre', anchor='w'); self.service_tree.column('name', width=200, stretch=tk.YES)
        self.service_tree.heading('price', text='Precio ($)', anchor='e'); self.service_tree.column('price', width=100, stretch=tk.YES, anchor='e')

        # CORRECCIÓN: Usamos Service.get_all() 
        services = Service.get_all() 
        for s in services:
            # s es un diccionario
            price_formatted = f"${s['price']:.2f}"
            self.service_tree.insert('', tk.END, values=(s['id'], s['name'], price_formatted))

    # ALTA (CREATE) DE SERVICIO
    def open_create_service_window(self):
        """Abre ventana emergente para Alta de Servicio."""
        top = tk.Toplevel(self)
        top.title("Alta de Nuevo Servicio")
        top.geometry("350x200")
        top.transient(self); top.grab_set()

        labels = ["Nombre:", "Precio:"]
        entries = {}; main_frame = ttk.Frame(top, padding="15"); main_frame.pack(fill='both', expand=True)

        for i, text in enumerate(labels):
            ttk.Label(main_frame, text=text).grid(row=i, column=0, sticky='w', pady=5, padx=5)
            entry = ttk.Entry(main_frame, width=30)
            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=5)
            entries[text] = entry
        
        button_frame = ttk.Frame(main_frame); button_frame.grid(row=len(labels), columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="Guardar", 
                   command=lambda: self.save_new_service(top, entries)).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Cancelar", command=top.destroy).pack(side='left', padx=10)
        main_frame.grid_columnconfigure(1, weight=1)

    def save_new_service(self, top_level, entries):
        """Guarda los datos del nuevo servicio."""
        name = entries["Nombre:"].get().strip()
        price_str = entries["Precio:"].get().strip()
        
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Error de Validación", "El precio debe ser un número válido.")
            return

        if not name or price <= 0:
            messagebox.showerror("Error de Validación", "Nombre no puede estar vacío y Precio debe ser positivo.")
            return
        
        try:
            Service.create(name, price)
            messagebox.showinfo("Éxito", f"Servicio '{name}' creado.")
            top_level.destroy()
            self.load_service_data()
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al guardar: {e}")

    # MODIFICACIÓN (UPDATE) DE SERVICIO
    def open_edit_service_window(self):
        """Abre la ventana emergente para modificar el servicio seleccionado."""
        selected_item = self.service_tree.focus()
        
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Debes seleccionar un servicio de la lista para modificar.")
            return

        values = self.service_tree.item(selected_item, 'values')
        service_id = values[0]
        
        # Obtenemos los datos como diccionario
        servicio_data = Service.get_by_id(service_id)
        
        if not servicio_data:
            messagebox.showerror("Error", "Servicio no encontrado.")
            return

        top = tk.Toplevel(self)
        top.title(f"Modificar Servicio ID: {service_id}")
        top.geometry("350x200")
        top.transient(self); top.grab_set()

        labels = ["Nombre:", "Precio:"]
        entries = {}; main_frame = ttk.Frame(top, padding="15"); main_frame.pack(fill='both', expand=True)

        # Acceso por clave de diccionario (servicio_data['name'])
        initial_data = {"Nombre:": servicio_data['name'], "Precio:": str(servicio_data['price'])}

        for i, text in enumerate(labels):
            ttk.Label(main_frame, text=text).grid(row=i, column=0, sticky='w', pady=5, padx=5)
            entry = ttk.Entry(main_frame, width=30)
            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=5)
            entries[text] = entry
            entry.insert(0, initial_data.get(text, ''))
        
        button_frame = ttk.Frame(main_frame); button_frame.grid(row=len(labels), columnspan=2, pady=15)
        
        # Pasamos service_id al método de actualización
        ttk.Button(button_frame, text="Guardar Cambios", 
                   command=lambda: self.update_existing_service(top, service_id, entries)).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Cancelar", command=top.destroy).pack(side='left', padx=10)
        main_frame.grid_columnconfigure(1, weight=1)

    def update_existing_service(self, top_level, service_id, entries):
        """Actualiza el servicio usando el método estático Service.update()."""
        name = entries["Nombre:"].get().strip()
        price_str = entries["Precio:"].get().strip()

        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Error de Validación", "El precio debe ser un número válido.")
            return
        
        if not name or price <= 0:
            messagebox.showerror("Error de Validación", "Nombre no puede estar vacío y Precio debe ser positivo.")
            return
        
        try:
            # Llama directamente al método estático con el ID
            Service.update(service_id, name, price)
            
            messagebox.showinfo("Éxito", f"Servicio {name} modificado correctamente.")
            top_level.destroy()
            self.load_service_data()
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al actualizar: {e}")

    # BAJA (DELETE) DE SERVICIO
    def delete_service(self):
        """Elimina el servicio seleccionado en la tabla."""
        selected_item = self.service_tree.focus()
        
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Debes seleccionar un servicio de la lista para eliminar.")
            return

        values = self.service_tree.item(selected_item, 'values')
        service_id = values[0]
        service_name = values[1]

        confirm = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Estás seguro de que deseas eliminar el servicio: {service_name} (ID: {service_id})?"
        )

        if confirm:
            try:
                # Llama directamente al método estático Service.delete()
                Service.delete(service_id)
                
                messagebox.showinfo("Éxito", f"Servicio {service_name} eliminado correctamente.")
                self.load_service_data()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el servicio: {e}")


    # =======================================================
    # MÓDULOS EN CONSTRUCCIÓN
    # =======================================================

    def create_order_tab(self):
        order_frame = ttk.Frame(self.notebook)
        self.notebook.add(order_frame, text='Pedidos/Órdenes 📄')
        ttk.Label(order_frame, text="Módulo de Pedidos - En Construcción", font=("Helvetica", 14)).pack(pady=50)

    def create_payment_tab(self):
        payment_frame = ttk.Frame(self.notebook)
        self.notebook.add(payment_frame, text='Pagos 💵')
        ttk.Label(payment_frame, text="Módulo de Pagos - En Construcción", font=("Helvetica", 14)).pack(pady=50)


# --- EJECUCIÓN ---
if __name__ == "__main__":
    app = LavanderiaApp()
    app.mainloop()
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime
import uuid

# --- 1. CLASES DE MODELO (MOCK DATA) ---
# Hemos simulado tus clases Customer, Service, Order y Payment para que
# operen sobre listas de datos en memoria (data = []) y el código sea ejecutable.

class Customer:
    data = []
    @staticmethod
    def create(name, phone):
        new_id = len(Customer.data) + 1
        Customer.data.append({"id": new_id, "name": name, "phone": phone})
        return new_id
    @staticmethod
    def get_all():
        return Customer.data
    @staticmethod
    def get_by_id(customer_id):
        return next((c for c in Customer.data if c['id'] == customer_id), None)
    @staticmethod
    def update(customer_id, name, phone):
        customer = Customer.get_by_id(customer_id)
        if customer:
            customer.update({"name": name, "phone": phone})
            return True
        return False
    @staticmethod
    def delete(customer_id):
        global data
        Customer.data = [c for c in Customer.data if c['id'] != customer_id]

Customer.create("Raymundo Landa", "5512345678")
Customer.create("Ana García", "5587654321")


class Service:
    data = []
    @staticmethod
    def create(name, price):
        new_id = len(Service.data) + 1
        Service.data.append({"id": new_id, "name": name, "price": price})
        return new_id
    @staticmethod
    def get_all():
        return Service.data
    @staticmethod
    def get_by_id(service_id):
        return next((s for s in Service.data if s['id'] == service_id), None)
    @staticmethod
    def update(service_id, name, price):
        service = Service.get_by_id(service_id)
        if service:
            service.update({"name": name, "price": price})
            return True
        return False
    @staticmethod
    def delete(service_id):
        global data
        Service.data = [s for s in Service.data if s['id'] != service_id]

Service.create("Lavado y Secado (Kg)", 15.0)
Service.create("Planchado (Unidad)", 5.0)


class Order:
    """Modelo adaptado para operar en memoria (Mocks)."""
    data = []
    
    @staticmethod
    def create(customer_id, items, total_amount, status="Pendiente"):
        new_id = len(Order.data) + 1
        Order.data.append({
            "id": new_id,
            "customer_id": customer_id,
            "items": items,  # Lista de {'service_id': X, 'quantity': Y, 'price': Z}
            "total": total_amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": status,
            "paid": 0.0 # Cantidad pagada
        })
        return new_id

    @staticmethod
    def get_all():
        return Order.data

    @staticmethod
    def get_by_id(order_id):
        return next((o for o in Order.data if o['id'] == order_id), None)

    @staticmethod
    def update_status(order_id, new_status):
        order = Order.get_by_id(order_id)
        if order:
            order["status"] = new_status
            return True
        return False
        
    @staticmethod
    def update_payment(order_id, amount):
        order = Order.get_by_id(order_id)
        if order:
            order["paid"] += amount
            if order["paid"] >= order["total"]:
                 order["status"] = "Pagado y Terminado"
            return True
        return False
    
    @staticmethod
    def delete(order_id):
        global data
        Order.data = [o for o in Order.data if o['id'] != order_id]

class Payment:
    """Modelo adaptado para operar en memoria (Mocks)."""
    data = []
    
    @staticmethod
    def create(order_id, amount, method="Efectivo"):
        new_id = str(uuid.uuid4())[:8]
        Payment.data.append({
            "id": new_id,
            "order_id": order_id,
            "amount": amount,
            "method": method,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        # Actualizar el estado de la orden al registrar el pago
        Order.update_payment(order_id, amount)
        return new_id

    @staticmethod
    def all():
        return Payment.data


# --- 2. APLICACIÓN TKINTER ---

class LavanderiaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Lavandería")
        self.geometry("1000x650")
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Inicialización de las pestañas
        self.create_customer_tab()
        self.create_service_tab()
        # Estas son las funciones corregidas/completadas:
        self.create_order_tab() 
        self.create_payment_tab()

        # Almacenamiento temporal para el carrito de Pedidos
        self.current_order_items = []
        self.current_order_customer_id = None
        
        # Configuración de estilo
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        style.configure("Treeview", font=('Helvetica', 10))

    # -----------------------------
    # MÉTODOS DE CLIENTES (Ejemplo de CRUD previo)
    # -----------------------------
    def create_customer_tab(self):
        self.customer_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.customer_frame, text='Clientes 👥')
        ttk.Label(self.customer_frame, text="Gestión de Clientes", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Botonera
        btn_frame = ttk.Frame(self.customer_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Nuevo Cliente", command=lambda: self.open_customer_window("new")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Modificar Cliente", command=lambda: self.open_customer_window("edit")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Eliminar Cliente", command=self.delete_customer).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Recargar", command=self.load_customer_data).pack(side='left', padx=5)

        # Tabla (Treeview)
        self.customer_tree = ttk.Treeview(self.customer_frame, columns=("ID", "Nombre", "Teléfono"), show='headings')
        self.customer_tree.heading("ID", text="ID")
        self.customer_tree.heading("Nombre", text="Nombre")
        self.customer_tree.heading("Teléfono", text="Teléfono")
        self.customer_tree.column("ID", width=50, anchor="center")
        self.customer_tree.column("Nombre", width=250)
        self.customer_tree.column("Teléfono", width=150, anchor="center")
        self.customer_tree.pack(fill='both', expand=True)
        self.load_customer_data()

    def load_customer_data(self):
        """Carga datos de clientes en el Treeview."""
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
            
        customers = Customer.get_all()
        for c in customers:
            self.customer_tree.insert('', 'end', values=(c['id'], c['name'], c['phone']))

    def open_customer_window(self, mode):
        """Abre ventana modal para crear o editar cliente."""
        selected_item = self.customer_tree.focus()
        customer_id = None
        customer_data = {"name": "", "phone": ""}

        if mode == "edit" and selected_item:
            values = self.customer_tree.item(selected_item, 'values')
            customer_id = int(values[0])
            customer_data = Customer.get_by_id(customer_id)
            if not customer_data:
                messagebox.showerror("Error", "Cliente no encontrado.")
                return
        elif mode == "edit" and not selected_item:
            messagebox.showinfo("Información", "Seleccione un cliente para modificar.")
            return

        window = tk.Toplevel(self)
        window.title(f"{'Modificar' if mode == 'edit' else 'Nuevo'} Cliente")
        window.geometry("300x150")

        ttk.Label(window, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        name_entry = ttk.Entry(window, width=30)
        name_entry.insert(0, customer_data["name"])
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(window, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        phone_entry = ttk.Entry(window, width=30)
        phone_entry.insert(0, customer_data["phone"])
        phone_entry.grid(row=1, column=1, padx=5, pady=5)

        save_btn = ttk.Button(window, text="Guardar", command=lambda: self.save_customer(window, mode, customer_id, name_entry.get(), phone_entry.get()))
        save_btn.grid(row=2, column=1, padx=5, pady=10, sticky='e')

    def save_customer(self, window, mode, customer_id, name, phone):
        if not name or not phone:
            messagebox.showerror("Error de Validación", "Todos los campos son obligatorios.")
            return

        if mode == "new":
            Customer.create(name, phone)
        elif mode == "edit":
            Customer.update(customer_id, name, phone)
            
        window.destroy()
        self.load_customer_data()
        messagebox.showinfo("Éxito", "Cliente guardado correctamente.")

    def delete_customer(self):
        selected_item = self.customer_tree.focus()
        if not selected_item:
            messagebox.showinfo("Información", "Seleccione un cliente para eliminar.")
            return
            
        values = self.customer_tree.item(selected_item, 'values')
        customer_id = int(values[0])
        
        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar al cliente ID {customer_id}?"):
            Customer.delete(customer_id)
            self.load_customer_data()
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")

    # -----------------------------
    # MÉTODOS DE SERVICIOS (Ejemplo de CRUD previo)
    # -----------------------------
    def create_service_tab(self):
        self.service_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.service_frame, text='Servicios 🧺')
        ttk.Label(self.service_frame, text="Catálogo de Servicios", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Botonera
        btn_frame = ttk.Frame(self.service_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Nuevo Servicio", command=lambda: self.open_service_window("new")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Modificar Servicio", command=lambda: self.open_service_window("edit")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Eliminar Servicio", command=self.delete_service).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Recargar", command=self.load_service_data).pack(side='left', padx=5)

        # Tabla (Treeview)
        self.service_tree = ttk.Treeview(self.service_frame, columns=("ID", "Nombre", "Precio"), show='headings')
        self.service_tree.heading("ID", text="ID")
        self.service_tree.heading("Nombre", text="Nombre")
        self.service_tree.heading("Precio", text="Precio ($)")
        self.service_tree.column("ID", width=50, anchor="center")
        self.service_tree.column("Nombre", width=250)
        self.service_tree.column("Precio", width=100, anchor="center")
        self.service_tree.pack(fill='both', expand=True)
        self.load_service_data()

    def load_service_data(self):
        """Carga datos de servicios en el Treeview."""
        for item in self.service_tree.get_children():
            self.service_tree.delete(item)
            
        services = Service.get_all()
        for s in services:
            self.service_tree.insert('', 'end', values=(s['id'], s['name'], f"{s['price']:.2f}"))

    def open_service_window(self, mode):
        """Abre ventana modal para crear o editar servicio."""
        selected_item = self.service_tree.focus()
        service_id = None
        service_data = {"name": "", "price": 0.0}

        if mode == "edit" and selected_item:
            values = self.service_tree.item(selected_item, 'values')
            service_id = int(values[0])
            service_data_raw = Service.get_by_id(service_id)
            if service_data_raw:
                service_data = service_data_raw
            else:
                messagebox.showerror("Error", "Servicio no encontrado.")
                return
        elif mode == "edit" and not selected_item:
            messagebox.showinfo("Información", "Seleccione un servicio para modificar.")
            return

        window = tk.Toplevel(self)
        window.title(f"{'Modificar' if mode == 'edit' else 'Nuevo'} Servicio")
        window.geometry("300x150")

        ttk.Label(window, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        name_entry = ttk.Entry(window, width=30)
        name_entry.insert(0, service_data["name"])
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(window, text="Precio ($):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        price_entry = ttk.Entry(window, width=30)
        price_entry.insert(0, service_data["price"])
        price_entry.grid(row=1, column=1, padx=5, pady=5)

        save_btn = ttk.Button(window, text="Guardar", command=lambda: self.save_service(window, mode, service_id, name_entry.get(), price_entry.get()))
        save_btn.grid(row=2, column=1, padx=5, pady=10, sticky='e')

    def save_service(self, window, mode, service_id, name, price_str):
        if not name or not price_str:
            messagebox.showerror("Error de Validación", "Todos los campos son obligatorios.")
            return

        try:
            price = float(price_str)
            if price <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error de Validación", "El precio debe ser un número positivo.")
            return

        if mode == "new":
            Service.create(name, price)
        elif mode == "edit":
            Service.update(service_id, name, price)
            
        window.destroy()
        self.load_service_data()
        messagebox.showinfo("Éxito", "Servicio guardado correctamente.")

    def delete_service(self):
        selected_item = self.service_tree.focus()
        if not selected_item:
            messagebox.showinfo("Información", "Seleccione un servicio para eliminar.")
            return
            
        values = self.service_tree.item(selected_item, 'values')
        service_id = int(values[0])
        
        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar el servicio ID {service_id}?"):
            Service.delete(service_id)
            self.load_service_data()
            messagebox.showinfo("Éxito", "Servicio eliminado correctamente.")


    # -----------------------------
    # 3. MÉTODOS DE PEDIDOS/ÓRDENES (CORREGIDOS Y COMPLETADOS)
    # -----------------------------
    def create_order_tab(self):
        """Configura el frame (pestaña) de gestión de Pedidos."""
        self.order_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.order_frame, text='Pedidos/Órdenes 📄')
        
        ttk.Label(self.order_frame, text="Gestión de Pedidos", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # --- Botonera ---
        self.order_button_frame = ttk.Frame(self.order_frame)
        self.order_button_frame.pack(fill='x', pady=5)
        
        ttk.Button(self.order_button_frame, text="Recargar", command=self.load_order_data).pack(side='left', padx=5)
        # ESTE MÉTODO FALTABA Y CAUSABA EL ERROR:
        ttk.Button(self.order_button_frame, text="Nuevo Pedido", command=self.open_create_order_window).pack(side='left', padx=5)
        ttk.Button(self.order_button_frame, text="Cambiar Estado", command=self.change_order_status).pack(side='left', padx=5)
        ttk.Button(self.order_button_frame, text="Eliminar Pedido", command=self.delete_order).pack(side='left', padx=5)
        
        # --- Tabla ---
        self.order_list_container = ttk.Frame(self.order_frame)
        self.order_list_container.pack(fill='both', expand=True, pady=10)
        
        self.order_tree = ttk.Treeview(self.order_list_container, 
                                       columns=("ID", "Cliente", "Total", "Fecha", "Estado", "Pagado"), 
                                       show='headings')
        self.order_tree.heading("ID", text="ID")
        self.order_tree.heading("Cliente", text="Cliente")
        self.order_tree.heading("Total", text="Total ($)")
        self.order_tree.heading("Fecha", text="Fecha")
        self.order_tree.heading("Estado", text="Estado")
        self.order_tree.heading("Pagado", text="Pagado ($)")
        
        self.order_tree.column("ID", width=50, anchor="center")
        self.order_tree.column("Cliente", width=200)
        self.order_tree.column("Total", width=100, anchor="center")
        self.order_tree.column("Fecha", width=150, anchor="center")
        self.order_tree.column("Estado", width=150, anchor="center")
        self.order_tree.column("Pagado", width=100, anchor="center")
        
        self.order_tree.pack(fill='both', expand=True)
        self.load_order_data()

    def load_order_data(self):
        """Carga datos de pedidos en el Treeview de Pedidos."""
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
            
        orders = Order.get_all()
        for o in orders:
            # Obtener nombre del cliente
            customer = Customer.get_by_id(o['customer_id'])
            customer_name = customer['name'] if customer else "N/A"
            
            # Insertar datos
            self.order_tree.insert('', 'end', values=(
                o['id'], 
                customer_name, 
                f"{o['total']:.2f}", 
                o['date'], 
                o['status'],
                f"{o['paid']:.2f}"
            ))

    def open_create_order_window(self):
        """Abre la ventana modal para crear un nuevo pedido (con carrito)."""
        self.current_order_items = []
        self.current_order_customer_id = None
        
        window = tk.Toplevel(self)
        window.title("Crear Nuevo Pedido")
        window.geometry("700x500")
        
        main_frame = ttk.Frame(window, padding="10")
        main_frame.pack(fill='both', expand=True)

        # --- Parte 1: Selección de Cliente ---
        customer_frame = ttk.LabelFrame(main_frame, text="Cliente")
        customer_frame.pack(fill='x', pady=5)
        
        ttk.Label(customer_frame, text="Seleccionar Cliente:").pack(side='left', padx=5)
        
        customer_names = [f"{c['id']} - {c['name']}" for c in Customer.get_all()]
        self.customer_var = tk.StringVar(window)
        
        # Usar OptionMenu si hay clientes, si no, usar un Label
        if customer_names:
            self.customer_var.set(customer_names[0])
            self.customer_option_menu = ttk.OptionMenu(customer_frame, self.customer_var, customer_names[0], *customer_names)
            self.customer_option_menu.pack(side='left', padx=5, fill='x', expand=True)
        else:
            ttk.Label(customer_frame, text="No hay clientes registrados.").pack(side='left', padx=5)

        # --- Parte 2: Agregar Servicios (Carrito) ---
        service_frame = ttk.LabelFrame(main_frame, text="Agregar Servicio")
        service_frame.pack(fill='x', pady=5)
        
        services = Service.get_all()
        service_names = [f"{s['id']} - {s['name']} (${s['price']:.2f})" for s in services]
        self.service_var = tk.StringVar(window)
        self.service_var.set(service_names[0] if service_names else "No hay servicios")
        
        ttk.Label(service_frame, text="Servicio:").grid(row=0, column=0, padx=5, pady=5)
        self.service_option_menu = ttk.OptionMenu(service_frame, self.service_var, self.service_var.get(), *service_names)
        self.service_option_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(service_frame, text="Cantidad/Peso:").grid(row=0, column=2, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(service_frame, width=10)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(service_frame, text="Añadir al Pedido", command=self.add_item_to_cart).grid(row=0, column=4, padx=5, pady=5)
        
        service_frame.grid_columnconfigure(1, weight=1)

        # --- Parte 3: Carrito de la Orden ---
        cart_frame = ttk.LabelFrame(main_frame, text="Detalle del Pedido")
        cart_frame.pack(fill='both', expand=True, pady=5)
        
        self.cart_tree = ttk.Treeview(cart_frame, columns=("Servicio", "Cantidad", "Subtotal"), show='headings')
        self.cart_tree.heading("Servicio", text="Servicio")
        self.cart_tree.heading("Cantidad", text="Cant.")
        self.cart_tree.heading("Subtotal", text="Subtotal ($)")
        self.cart_tree.column("Servicio", width=300)
        self.cart_tree.column("Cantidad", width=80, anchor="center")
        self.cart_tree.column("Subtotal", width=100, anchor="center")
        self.cart_tree.pack(fill='both', expand=True)

        self.total_var = tk.StringVar(window, value="Total: $0.00")
        ttk.Label(main_frame, textvariable=self.total_var, font=("Helvetica", 12, "bold")).pack(pady=5, anchor='e')

        # --- Parte 4: Botón de Guardar ---
        ttk.Button(main_frame, text="Guardar Pedido", command=lambda: self.save_new_order(window)).pack(pady=10, side='right')
        
        self.update_cart_tree() # Inicializar el carrito

    def add_item_to_cart(self):
        """Añade un servicio seleccionado al carrito temporal."""
        try:
            selected_service_str = self.service_var.get()
            service_id = int(selected_service_str.split(' - ')[0])
            quantity = float(self.quantity_entry.get())
            
            if quantity <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a cero.")
                return

            service = Service.get_by_id(service_id)
            if service:
                item_subtotal = service['price'] * quantity
                # Buscar si el item ya existe para sumarle la cantidad
                found = False
                for item in self.current_order_items:
                    if item['service_id'] == service_id:
                        item['quantity'] += quantity
                        item['subtotal'] += item_subtotal
                        found = True
                        break
                
                if not found:
                    self.current_order_items.append({
                        'service_id': service_id,
                        'name': service['name'],
                        'price': service['price'],
                        'quantity': quantity,
                        'subtotal': item_subtotal
                    })
                
                self.quantity_entry.delete(0, tk.END)
                self.quantity_entry.insert(0, "1")
                self.update_cart_tree()
        
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad válida.")
        except IndexError:
            messagebox.showerror("Error", "No hay servicios seleccionados.")

    def update_cart_tree(self):
        """Actualiza el Treeview del carrito con los ítems temporales y el total."""
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        total_order = 0.0
        for item in self.current_order_items:
            self.cart_tree.insert('', 'end', values=(
                item['name'], 
                f"{item['quantity']:.2f}", 
                f"{item['subtotal']:.2f}"
            ))
            total_order += item['subtotal']
            
        self.total_var.set(f"Total: ${total_order:.2f}")

    def save_new_order(self, window):
        """Guarda la orden en el modelo de datos."""
        if not self.current_order_items:
            messagebox.showerror("Error", "El pedido no puede estar vacío.")
            return

        try:
            # Obtener ID del cliente seleccionado
            selected_customer_str = self.customer_var.get()
            customer_id = int(selected_customer_str.split(' - ')[0])
            
            # Calcular el total
            total_amount = sum(item['subtotal'] for item in self.current_order_items)
            
            # Preparar ítems para guardar (simplificado para el modelo mock)
            items_to_save = [
                {'service_id': i['service_id'], 'quantity': i['quantity'], 'price': i['price']} 
                for i in self.current_order_items
            ]
            
            # Guardar la orden
            Order.create(customer_id, items_to_save, total_amount, status="Pendiente")
            
            messagebox.showinfo("Éxito", f"Pedido creado con total de ${total_amount:.2f}")
            window.destroy()
            self.load_order_data()
            
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"Ocurrió un error: {e}")

    def change_order_status(self):
        """Permite cambiar el estado de un pedido seleccionado."""
        selected_item = self.order_tree.focus()
        if not selected_item:
            messagebox.showinfo("Información", "Seleccione un pedido para cambiar su estado.")
            return
            
        order_id = int(self.order_tree.item(selected_item, 'values')[0])
        current_status = self.order_tree.item(selected_item, 'values')[4]
        
        new_status = simpledialog.askstring("Cambiar Estado", 
                                            f"Nuevo estado para Pedido {order_id} (Actual: {current_status}):\n"
                                            "Opciones: Pendiente, Listo, Entregado, Cancelado", 
                                            parent=self)
        
        if new_status and new_status in ["Pendiente", "Listo", "Entregado", "Cancelado"]:
            Order.update_status(order_id, new_status)
            self.load_order_data()
            messagebox.showinfo("Éxito", f"Estado de Pedido {order_id} actualizado a {new_status}.")
        elif new_status:
            messagebox.showerror("Error", "Estado no válido.")

    def delete_order(self):
        """Elimina un pedido seleccionado."""
        selected_item = self.order_tree.focus()
        if not selected_item:
            messagebox.showinfo("Información", "Seleccione un pedido para eliminar.")
            return
            
        values = self.order_tree.item(selected_item, 'values')
        order_id = int(values[0])
        
        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar el Pedido ID {order_id}? (Esta acción no se puede deshacer)"):
            Order.delete(order_id)
            self.load_order_data()
            messagebox.showinfo("Éxito", "Pedido eliminado correctamente.")

    # -----------------------------
    # 4. MÉTODOS DE PAGOS (CORREGIDOS Y COMPLETADOS)
    # -----------------------------
    def create_payment_tab(self):
        """Configura el frame (pestaña) de gestión de Pagos."""
        self.payment_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.payment_frame, text='Pagos 💵')
        
        ttk.Label(self.payment_frame, text="Registro de Pagos", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Botonera
        btn_frame = ttk.Frame(self.payment_frame)
        btn_frame.pack(fill='x', pady=5)
        
        # ESTE MÉTODO FALTABA Y CAUSABA EL ERROR:
        ttk.Button(btn_frame, text="Recargar", command=self.load_payment_data).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Registrar Nuevo Pago", command=self.open_create_payment_window).pack(side='left', padx=5)

        # Tabla
        self.payment_list_container = ttk.Frame(self.payment_frame)
        self.payment_list_container.pack(fill='both', expand=True, pady=10)
        
        self.payment_tree = ttk.Treeview(self.payment_list_container, 
                                         columns=("ID", "Orden ID", "Monto", "Método", "Fecha"), 
                                         show='headings')
        self.payment_tree.heading("ID", text="Transacción ID")
        self.payment_tree.heading("Orden ID", text="Orden ID")
        self.payment_tree.heading("Monto", text="Monto ($)")
        self.payment_tree.heading("Método", text="Método")
        self.payment_tree.heading("Fecha", text="Fecha")
        
        self.payment_tree.column("ID", width=100, anchor="center")
        self.payment_tree.column("Orden ID", width=100, anchor="center")
        self.payment_tree.column("Monto", width=100, anchor="center")
        self.payment_tree.column("Método", width=150)
        self.payment_tree.column("Fecha", width=150, anchor="center")
        
        self.payment_tree.pack(fill='both', expand=True)
        self.load_payment_data()

    def load_payment_data(self):
        """Carga datos de pagos en el Treeview de Pagos."""
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
            
        payments = Payment.all()
        for p in payments:
            self.payment_tree.insert('', 'end', values=(
                p['id'], 
                p['order_id'], 
                f"{p['amount']:.2f}", 
                p['method'], 
                p['date']
            ))

    def open_create_payment_window(self):
        """Abre ventana modal para registrar un pago."""
        window = tk.Toplevel(self)
        window.title("Registrar Nuevo Pago")
        window.geometry("350x200")

        ttk.Label(window, text="Orden ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        order_entry = ttk.Entry(window, width=30)
        order_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(window, text="Monto ($):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        amount_entry = ttk.Entry(window, width=30)
        amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(window, text="Método:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        methods = ["Efectivo", "Tarjeta", "Transferencia"]
        method_var = tk.StringVar(window, value=methods[0])
        method_menu = ttk.OptionMenu(window, method_var, methods[0], *methods)
        method_menu.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        save_btn = ttk.Button(window, text="Registrar Pago", command=lambda: self.save_payment(window, order_entry.get(), amount_entry.get(), method_var.get()))
        save_btn.grid(row=3, column=1, padx=5, pady=10, sticky='e')

    def save_payment(self, window, order_id_str, amount_str, method):
        """Guarda el pago y actualiza el estado de la orden."""
        try:
            order_id = int(order_id_str)
            amount = float(amount_str)
            
            if amount <= 0:
                messagebox.showerror("Error", "El monto debe ser positivo.")
                return
            
            order = Order.get_by_id(order_id)
            if not order:
                messagebox.showerror("Error", f"La Orden ID {order_id} no existe.")
                return

            # --- VALIDACIÓN CRÍTICA ---
            remaining = order['total'] - order['paid']
            if amount > remaining:
                if not messagebox.askyesno("Advertencia", f"El pago excede el monto restante (${remaining:.2f}). ¿Desea continuar?"):
                    return
            # --- FIN VALIDACIÓN ---

            Payment.create(order_id, amount, method)
            
            window.destroy()
            self.load_payment_data()
            self.load_order_data() # Recargar pedidos para ver el estado de pago actualizado
            messagebox.showinfo("Éxito", f"Pago de ${amount:.2f} registrado para Orden {order_id}.")
            
        except ValueError:
            messagebox.showerror("Error de Validación", "El ID de Orden y el Monto deben ser números válidos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el pago: {e}")


# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Crear algunas órdenes de prueba para probar las pestañas
    Order.create(customer_id=1, items=[{'service_id': 1, 'quantity': 5, 'price': 15.0}], total_amount=75.0, status="Pendiente")
    Order.create(customer_id=2, items=[{'service_id': 2, 'quantity': 10, 'price': 5.0}], total_amount=50.0, status="Listo")
    
    # Crear la aplicación
    app = LavanderiaApp()
    app.mainloop()
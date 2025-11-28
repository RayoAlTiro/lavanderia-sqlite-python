import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime
from app.database import db 


class Customer:
    """Modelo Cliente conectado a SQLite."""
    @staticmethod
    def create(name, phone):
        query = "INSERT INTO customers (name, phone) VALUES (?, ?)"
        return db.execute(query, (name, phone))

    @staticmethod
    def get_all():
        query = "SELECT * FROM customers ORDER BY name ASC"
        return db.fetch(query)

    @staticmethod
    def get_by_id(customer_id):
        query = "SELECT * FROM customers WHERE id = ?"
        results = db.fetch(query, (customer_id,))
        return results[0] if results else None

    @staticmethod
    def update(customer_id, name, phone):
        query = "UPDATE customers SET name = ?, phone = ? WHERE id = ?"
        db.execute(query, (name, phone, customer_id))
        return True

    @staticmethod
    def delete(customer_id):
        query = "DELETE FROM customers WHERE id = ?"
        db.execute(query, (customer_id,))
        return True

class Service:
    """Modelo Servicio conectado a SQLite."""
    @staticmethod
    def create(name, price):
        query = "INSERT INTO services (name, price) VALUES (?, ?)"
        return db.execute(query, (name, price))

    @staticmethod
    def get_all():
        query = "SELECT * FROM services ORDER BY name ASC"
        return db.fetch(query)

    @staticmethod
    def get_by_id(service_id):
        query = "SELECT * FROM services WHERE id = ?"
        results = db.fetch(query, (service_id,))
        return results[0] if results else None

    @staticmethod
    def update(service_id, name, price):
        query = "UPDATE services SET name = ?, price = ? WHERE id = ?"
        db.execute(query, (name, price, service_id))
        return True

    @staticmethod
    def delete(service_id):
        query = "DELETE FROM services WHERE id = ?"
        db.execute(query, (service_id,))
        return True

class Order:
    """Modelo Pedido conectado a SQLite."""
    @staticmethod
    def create(customer_id, items, total_amount, status="Pendiente"):
        # Nota: En este esquema simple no guardamos el detalle de los ítems en una tabla aparte,
        # solo guardamos el total de la orden.
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        query = """
            INSERT INTO orders (customer_id, total, date, status, paid) 
            VALUES (?, ?, ?, ?, ?)
        """
        return db.execute(query, (customer_id, total_amount, date_str, status, 0.0))

    @staticmethod
    def get_all():
        query = "SELECT * FROM orders ORDER BY id DESC"
        return db.fetch(query)

    @staticmethod
    def get_by_id(order_id):
        query = "SELECT * FROM orders WHERE id = ?"
        results = db.fetch(query, (order_id,))
        return results[0] if results else None

    @staticmethod
    def update_status(order_id, new_status):
        query = "UPDATE orders SET status = ? WHERE id = ?"
        db.execute(query, (new_status, order_id))
        return True

    @staticmethod
    def delete(order_id):
        # Primero borramos pagos asociados para mantener integridad (si no hay CASCADE)
        db.execute("DELETE FROM payments WHERE order_id = ?", (order_id,))
        db.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        return True

class Payment:
    """Modelo Pago conectado a SQLite."""
    @staticmethod
    def create(order_id, amount, method="Efectivo"):
        # 1. Registrar el pago
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        query_insert = """
            INSERT INTO payments (order_id, amount, method, date) 
            VALUES (?, ?, ?, ?)
        """
        payment_id = db.execute(query_insert, (order_id, amount, method, date_str))

        # 2. Actualizar el saldo pagado de la orden
        # Primero obtenemos la orden actual para ver totales
        order = Order.get_by_id(order_id)
        if order:
            new_paid = order['paid'] + amount
            new_status = order['status']
            
            # Si ya se cubrió el total, cambiamos estado
            if new_paid >= order['total']:
                new_status = "Pagado y Terminado"
            
            query_update = "UPDATE orders SET paid = ?, status = ? WHERE id = ?"
            db.execute(query_update, (new_paid, new_status, order_id))
            
        return payment_id

    @staticmethod
    def all():
        query = "SELECT * FROM payments ORDER BY id DESC"
        return db.fetch(query)


# =======================================================
# 2. APLICACIÓN TKINTER (GUI)
# =======================================================

class LavanderiaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Lavandería (BD SQLite)")
        self.geometry("1100x700")
        
        # Configuración de estilo
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        self.style.configure("Treeview", font=('Helvetica', 10), rowheight=25)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Variables temporales para el carrito
        self.current_order_items = []
        
        # Inicialización de las pestañas
        self.create_customer_tab()
        self.create_service_tab()
        self.create_order_tab() 
        self.create_payment_tab()

    # -----------------------------
    # PESTAÑA CLIENTES
    # -----------------------------
    def create_customer_tab(self):
        self.customer_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.customer_frame, text='Clientes 👥')
        
        ttk.Label(self.customer_frame, text="Gestión de Clientes", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        # Botonera
        btn_frame = ttk.Frame(self.customer_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Nuevo Cliente", command=lambda: self.open_customer_window("new")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Modificar", command=lambda: self.open_customer_window("edit")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_customer).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Actualizar Lista", command=self.load_customer_data).pack(side='left', padx=5)

        # Tabla
        columns = ("ID", "Nombre", "Teléfono")
        self.customer_tree = ttk.Treeview(self.customer_frame, columns=columns, show='headings')
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=100 if col == "ID" else 200)
            
        self.customer_tree.pack(fill='both', expand=True)
        self.load_customer_data()

    def load_customer_data(self):
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        customers = Customer.get_all()
        for c in customers:
            self.customer_tree.insert('', 'end', values=(c['id'], c['name'], c['phone']))

    def open_customer_window(self, mode):
        selected = self.customer_tree.focus()
        customer_id = None
        data = {"name": "", "phone": ""}

        if mode == "edit":
            if not selected:
                messagebox.showwarning("Aviso", "Seleccione un cliente para modificar.")
                return
            values = self.customer_tree.item(selected, 'values')
            customer_id = values[0]
            # Consultamos a BD para tener datos frescos
            c_db = Customer.get_by_id(customer_id)
            if c_db: data = c_db

        win = tk.Toplevel(self)
        win.title(f"{'Nuevo' if mode == 'new' else 'Editar'} Cliente")
        win.geometry("300x180")

        ttk.Label(win, text="Nombre:").pack(pady=5)
        entry_name = ttk.Entry(win, width=30)
        entry_name.pack()
        entry_name.insert(0, data['name'])

        ttk.Label(win, text="Teléfono:").pack(pady=5)
        entry_phone = ttk.Entry(win, width=30)
        entry_phone.pack()
        entry_phone.insert(0, data['phone'])

        def save():
            name = entry_name.get().strip()
            phone = entry_phone.get().strip()
            if not name:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            
            if mode == "new":
                Customer.create(name, phone)
            else:
                Customer.update(customer_id, name, phone)
            
            win.destroy()
            self.load_customer_data()
            messagebox.showinfo("Éxito", "Cliente guardado.")

        ttk.Button(win, text="Guardar", command=save).pack(pady=15)

    def delete_customer(self):
        selected = self.customer_tree.focus()
        if not selected:
            return
        cid = self.customer_tree.item(selected, 'values')[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar cliente?"):
            Customer.delete(cid)
            self.load_customer_data()

    # -----------------------------
    # PESTAÑA SERVICIOS
    # -----------------------------
    def create_service_tab(self):
        self.service_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.service_frame, text='Servicios 🧺')
        
        ttk.Label(self.service_frame, text="Catálogo de Servicios", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        btn_frame = ttk.Frame(self.service_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Nuevo Servicio", command=lambda: self.open_service_window("new")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Modificar", command=lambda: self.open_service_window("edit")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_service).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Actualizar Lista", command=self.load_service_data).pack(side='left', padx=5)

        self.service_tree = ttk.Treeview(self.service_frame, columns=("ID", "Nombre", "Precio"), show='headings')
        self.service_tree.heading("ID", text="ID"); self.service_tree.column("ID", width=50)
        self.service_tree.heading("Nombre", text="Nombre"); self.service_tree.column("Nombre", width=200)
        self.service_tree.heading("Precio", text="Precio ($)"); self.service_tree.column("Precio", width=100)
        self.service_tree.pack(fill='both', expand=True)
        self.load_service_data()

    def load_service_data(self):
        for item in self.service_tree.get_children():
            self.service_tree.delete(item)
        services = Service.get_all()
        for s in services:
            self.service_tree.insert('', 'end', values=(s['id'], s['name'], f"${s['price']:.2f}"))

    def open_service_window(self, mode):
        selected = self.service_tree.focus()
        service_id = None
        data = {"name": "", "price": 0.0} # Inicializar price como float o string vacío
        
        if mode == "edit":
            if not selected: 
                messagebox.showwarning("Aviso", "Seleccione un servicio para modificar.")
                return
            values = self.service_tree.item(selected, 'values')
            service_id = values[0]
            s_db = Service.get_by_id(service_id)
            if s_db: data = s_db

        win = tk.Toplevel(self)
        win.title(f"{'Nuevo' if mode == 'new' else 'Editar'} Servicio")
        win.geometry("300x180")

        ttk.Label(win, text="Nombre:").pack(pady=5)
        entry_name = ttk.Entry(win, width=30)
        entry_name.pack(); entry_name.insert(0, data['name'])

        ttk.Label(win, text="Precio:").pack(pady=5)
        entry_price = ttk.Entry(win, width=30)
        entry_price.pack(); entry_price.insert(0, str(data['price']))

        def save():
            name = entry_name.get()
            try:
                price = float(entry_price.get())
                if price < 0: raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Precio inválido")
                return
            
            if mode == "new": Service.create(name, price)
            else: Service.update(service_id, name, price)
            win.destroy(); self.load_service_data()

        ttk.Button(win, text="Guardar", command=save).pack(pady=15)

    def delete_service(self):
        selected = self.service_tree.focus()
        if selected and messagebox.askyesno("Confirmar", "¿Eliminar servicio?"):
            sid = self.service_tree.item(selected, 'values')[0]
            Service.delete(sid)
            self.load_service_data()

    # -----------------------------
    # PESTAÑA PEDIDOS (ÓRDENES)
    # -----------------------------
    def create_order_tab(self):
        self.order_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.order_frame, text='Pedidos 📄')
        
        ttk.Label(self.order_frame, text="Gestión de Pedidos", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        btn_frame = ttk.Frame(self.order_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Nuevo Pedido", command=self.open_create_order_window).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cambiar Estado", command=self.change_order_status).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_order).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Actualizar Lista", command=self.load_order_data).pack(side='left', padx=5)
        
        cols = ("ID", "Cliente", "Total", "Pagado", "Fecha", "Estado")
        self.order_tree = ttk.Treeview(self.order_frame, columns=cols, show='headings')
        for c in cols:
            self.order_tree.heading(c, text=c)
            self.order_tree.column(c, width=100 if c != "Cliente" else 200, anchor="center")
        
        self.order_tree.pack(fill='both', expand=True)
        # Cargamos datos al inicio de la pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if "Pedidos" in selected_tab:
            self.load_order_data()
        elif "Clientes" in selected_tab:
            self.load_customer_data()
        elif "Servicios" in selected_tab:
            self.load_service_data()
        elif "Pagos" in selected_tab:
            self.load_payment_data()

    def load_order_data(self):
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        orders = Order.get_all()
        for o in orders:
            # Recuperar nombre del cliente para mostrar en la tabla
            customer = Customer.get_by_id(o['customer_id'])
            c_name = customer['name'] if customer else "Desconocido"
            
            self.order_tree.insert('', 'end', values=(
                o['id'], c_name, f"${o['total']:.2f}", f"${o['paid']:.2f}", 
                o['date'], o['status']
            ))

    def open_create_order_window(self):
        self.current_order_items = []
        win = tk.Toplevel(self)
        win.title("Nuevo Pedido")
        win.geometry("700x550")

        # 1. Seleccionar Cliente
        frame_cust = ttk.LabelFrame(win, text="1. Seleccionar Cliente", padding=10)
        frame_cust.pack(fill='x', padx=10, pady=5)
        
        customers = Customer.get_all()
        if not customers:
            ttk.Label(frame_cust, text="No hay clientes registrados. Cree uno primero.").pack()
            return
        
        cust_options = [f"{c['id']} - {c['name']}" for c in customers]
        self.var_customer = tk.StringVar(value=cust_options[0])
        ttk.OptionMenu(frame_cust, self.var_customer, cust_options[0], *cust_options).pack(fill='x')

        # 2. Agregar Servicios
        frame_serv = ttk.LabelFrame(win, text="2. Agregar Servicios", padding=10)
        frame_serv.pack(fill='x', padx=10, pady=5)
        
        services = Service.get_all()
        if not services:
            ttk.Label(frame_serv, text="No hay servicios registrados.").pack()
        else:
            # Creamos un diccionario para mapear ID a Servicio fácilmente
            self.service_map = {s['id']: s for s in services}
            serv_options = [f"{s['id']} - {s['name']} (${s['price']:.2f})" for s in services]
            
            self.var_service = tk.StringVar(value=serv_options[0])
            ttk.OptionMenu(frame_serv, self.var_service, serv_options[0], *serv_options).grid(row=0, column=0, sticky="ew")
            
            ttk.Label(frame_serv, text="Cant:").grid(row=0, column=1, padx=5)
            self.entry_qty = ttk.Entry(frame_serv, width=5)
            self.entry_qty.insert(0, "1")
            self.entry_qty.grid(row=0, column=2)
            
            ttk.Button(frame_serv, text="Agregar (+)", command=self.add_item_to_cart).grid(row=0, column=3, padx=10)

        # 3. Carrito Visual
        self.tree_cart = ttk.Treeview(win, columns=("Servicio", "Cant", "Subtotal"), show='headings', height=6)
        self.tree_cart.heading("Servicio", text="Servicio"); self.tree_cart.heading("Cant", text="Cant"); self.tree_cart.heading("Subtotal", text="Subtotal")
        self.tree_cart.column("Servicio", width=300); self.tree_cart.column("Cant", width=50); self.tree_cart.column("Subtotal", width=100)
        self.tree_cart.pack(fill='x', padx=10, pady=5)

        self.lbl_total = ttk.Label(win, text="Total: $0.00", font=("Arial", 12, "bold"))
        self.lbl_total.pack(pady=5, padx=10, anchor='e')

        ttk.Button(win, text="GUARDAR PEDIDO", command=lambda: self.save_new_order(win)).pack(pady=10)

    def add_item_to_cart(self):
        try:
            qty = float(self.entry_qty.get())
            if qty <= 0: raise ValueError("Cantidad debe ser positiva")
            
            s_str = self.var_service.get()
            s_id = int(s_str.split(' - ')[0])
            service = self.service_map.get(s_id)
            
            subtotal = service['price'] * qty
            
            self.current_order_items.append({
                "service_id": s_id, "name": service['name'], 
                "price": service['price'], "qty": qty, "subtotal": subtotal
            })
            
            # Actualizar tabla y total
            self.tree_cart.insert('', 'end', values=(service['name'], qty, f"{subtotal:.2f}"))
            total = sum(i['subtotal'] for i in self.current_order_items)
            self.lbl_total.config(text=f"Total: ${total:.2f}")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al añadir ítem: {e}")


    def save_new_order(self, win):
        if not self.current_order_items:
            messagebox.showerror("Error", "El carrito está vacío")
            return
        
        c_str = self.var_customer.get()
        c_id = int(c_str.split(' - ')[0])
        total = sum(i['subtotal'] for i in self.current_order_items)
        
        # Guardamos en BD
        Order.create(c_id, self.current_order_items, total)
        
        win.destroy()
        self.load_order_data()
        messagebox.showinfo("Éxito", "Pedido registrado en base de datos.")

    def change_order_status(self):
        sel = self.order_tree.focus()
        if not sel: 
            messagebox.showwarning("Aviso", "Seleccione una orden.")
            return

        # Obtenemos el ID del Treeview
        oid = self.order_tree.item(sel, 'values')[0] 
        
        # Muestra el estado actual y pide el nuevo
        current_status = self.order_tree.item(sel, 'values')[5]
        
        status = simpledialog.askstring(
            "Cambiar Estado", 
            f"ID {oid} (Actual: {current_status})\nNuevo estado (Pendiente, Listo, Entregado, Cancelado):",
            parent=self.order_frame
        )
        if status:
            Order.update_status(oid, status)
            self.load_order_data()

    def delete_order(self):
        sel = self.order_tree.focus()
        if sel and messagebox.askyesno("Confirmar", "¿Eliminar Pedido y sus pagos? Esta acción es permanente."):
            oid = self.order_tree.item(sel, 'values')[0]
            Order.delete(oid)
            self.load_order_data()

    # -----------------------------
    # PESTAÑA PAGOS
    # -----------------------------
    def create_payment_tab(self):
        self.payment_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.payment_frame, text='Pagos 💵')
        
        ttk.Label(self.payment_frame, text="Registro de Pagos", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        btn_frame = ttk.Frame(self.payment_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Registrar Pago", command=self.open_create_payment_window).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Actualizar Lista", command=self.load_payment_data).pack(side='left', padx=5)
        
        cols = ("ID", "ID Orden", "Monto", "Método", "Fecha")
        self.payment_tree = ttk.Treeview(self.payment_frame, columns=cols, show='headings')
        for c in cols:
            self.payment_tree.heading(c, text=c)
            self.payment_tree.column(c, width=120, anchor="center")
        self.payment_tree.pack(fill='both', expand=True)
        # La carga inicial está cubierta por on_tab_change, pero la llamamos por si acaso
        self.load_payment_data() 

    def load_payment_data(self):
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        payments = Payment.all()
        for p in payments:
            # CORRECCIÓN: Usamos .get() con valores por defecto para TODAS las claves
            # que podrían faltar en registros antiguos, incluyendo 'method' y 'date'.
            
            # Recuperación robusta de datos
            id_val = p.get('id', 'N/A')
            order_id_val = p.get('order_id', 'N/A')
            amount_val = p.get('amount', 0.0) # 0.0 para poder formatear
            method_val = p.get('method', 'N/A')
            date_val = p.get('date', 'Fecha Desconocida')
            
            self.payment_tree.insert('', 'end', values=(
                id_val, 
                order_id_val, 
                f"${amount_val:.2f}", # Formatear el monto
                method_val, 
                date_val
            ))

    def open_create_payment_window(self):
        win = tk.Toplevel(self)
        win.title("Registrar Pago")
        win.geometry("300x250")

        ttk.Label(win, text="ID Orden:").pack(pady=5)
        entry_oid = ttk.Entry(win); entry_oid.pack()

        ttk.Label(win, text="Monto ($):").pack(pady=5)
        entry_amount = ttk.Entry(win); entry_amount.pack()

        ttk.Label(win, text="Método:").pack(pady=5)
        combo_method = ttk.Combobox(win, values=["Efectivo", "Tarjeta", "Transferencia"], state="readonly")
        combo_method.pack(); combo_method.current(0)

        def save():
            try:
                oid = int(entry_oid.get())
                amt = float(entry_amount.get())
                met = combo_method.get()

                if amt <= 0:
                    messagebox.showerror("Error", "El monto debe ser positivo.")
                    return
                
                # Validar existencia orden
                order = Order.get_by_id(oid)
                if not order:
                    messagebox.showerror("Error", f"ID de Orden {oid} no existe.")
                    return
                
                # Advertencia si excede total
                remaining = order['total'] - order['paid']
                if amt > remaining and remaining > 0.01:
                    if not messagebox.askyesno("Alerta", f"El pago excede el restante (${remaining:.2f}). ¿Continuar?"):
                        return

                Payment.create(oid, amt, met)
                win.destroy()
                self.load_payment_data()
                self.load_order_data() # Refrescar estado de órdenes
                messagebox.showinfo("Éxito", "Pago registrado. ¡Estado de la orden actualizado!")
                
            except ValueError:
                messagebox.showerror("Error", "Asegúrese de que el ID y el Monto sean números válidos.")

        ttk.Button(win, text="Guardar Pago", command=save).pack(pady=15)

# --- EJECUCIÓN ---
if __name__ == "__main__":
    app = LavanderiaApp()
    app.mainloop()
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
import sqlite3
import json
import os
from datetime import datetime
import threading
import time
from plyer import camera, gps, accelerometer

# Configuración de la base de datos
class DatabaseManager:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Inicializa las tablas de la base de datos y fuerza la reinicialización si es necesario"""
        db_path = 'computer_store.db'
        if os.path.exists(db_path):
            # Opcional: Forzar reinicialización eliminando la base de datos existente
            os.remove(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tabla productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                precio REAL NOT NULL,
                descripcion TEXT,
                stock INTEGER DEFAULT 0,
                codigo_barras TEXT,
                imagen_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla carrito
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carrito (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                cantidad INTEGER DEFAULT 1,
                precio_unitario REAL,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')
        
        # Tabla pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total REAL NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                direccion TEXT,
                ubicacion_gps TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla detalles pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalles_pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER,
                producto_id INTEGER,
                cantidad INTEGER,
                precio_unitario REAL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')
        
        # Insertar datos de ejemplo si no existen
        cursor.execute('SELECT COUNT(*) FROM productos')
        if cursor.fetchone()[0] == 0:
            productos_ejemplo = [
                ('AMD Ryzen 9 7950X', 'Procesadores', 2480000.00, 'Procesador 16 núcleos, 32 hilos, 4.5GHz base', 8, '1234567890123', 'ryzen_9_7950x.jpg'),
                ('Intel Core i9-13900K', 'Procesadores', 2715000.00, 'Procesador 24 núcleos, 32 hilos, hasta 5.8GHz', 12, '1234567890124', 'intel_i9_13900k.jpg'),
                ('AMD Ryzen 7 7700X', 'Procesadores', 1269000.10, 'Procesador 8 núcleos, 16 hilos, 4.5GHz base', 15, '1234567890125', 'ryzen_7_7700x.jpg'),
                ('NVIDIA RTX 4090', 'Tarjetas Gráficas', 13693374.36, 'GPU de alta gama, 24GB GDDR6X', 5, '1234567890126', 'rtx_4090.jpg'),
                ('AMD RX 7900 XTX', 'Tarjetas Gráficas', 4500000.14, 'GPU potente, 24GB GDDR6', 7, '1234567890127', 'rx_7900_xtx.jpg'),
                ('NVIDIA RTX 4070', 'Tarjetas Gráficas', 4991750.14, 'GPU gaming, 12GB GDDR6X', 10, '1234567890128', 'rtx_4070.jpg'),
                ('Corsair Vengeance DDR5 32GB', 'Memorias RAM', 975620.25, 'Kit 2x16GB DDR5-5600MHz RGB', 20, '1234567890129', 'corsair_ddr5_32gb.jpg'),
                ('G.Skill Trident Z5 RGB 16GB', 'Memorias RAM', 520000.25, 'Kit 2x8GB DDR5-6000MHz', 25, '1234567890130', 'gskill_ddr5_16gb.jpg'),
                ('Kingston Fury Beast 64GB', 'Memorias RAM', 107143.45, 'Kit 4x16GB DDR4-3200MHz', 8, '1234567890131', 'kingston_64gb.jpg'),
                ('ASUS ROG Strix X670E-E', 'Motherboards', 2105900.25, 'Placa AM5, WiFi 6E, PCIe 5.0', 6, '1234567890132', 'asus_x670e.jpg'),
                ('MSI MAG B550 Tomahawk', 'Motherboards', 749000.14, 'Placa AM4, PCIe 4.0, USB-C', 12, '1234567890133', 'msi_b550.jpg'),
                ('Gigabyte Z790 AORUS Elite', 'Motherboards', 13150000.24, 'Placa LGA1700, DDR5, WiFi 6', 9, '1234567890134', 'gigabyte_z790.jpg'),
                ('Samsung 980 PRO 2TB', 'Almacenamiento', 415000.58, 'SSD NVMe M.2, 7000MB/s lectura', 15, '1234567890135', 'samsung_980_pro.jpg'),
                ('WD Black SN850X 1TB', 'Almacenamiento', 2273400.25, 'SSD NVMe gaming, 7300MB/s', 20, '1234567890136', 'wd_black_sn850x.jpg'),
                ('Seagate IronWolf 4TB', 'Almacenamiento', 998500.69, 'HDD NAS, 5400RPM, CMR', 18, '1234567890137', 'seagate_ironwolf.jpg'),
                ('Corsair RM850x', 'Fuentes de Poder', 930252.85, '850W 80+ Gold modular', 12, '1234567890138', 'corsair_rm850x.jpg'),
                ('EVGA SuperNOVA 1000W', 'Fuentes de Poder', 187520.65, '1000W 80+ Platinum modular', 8, '1234567890139', 'evga_1000w.jpg'),
                ('Seasonic Focus GX-650', 'Fuentes de Poder', 584000.35, '650W 80+ Gold semi-modular', 15, '1234567890140', 'seasonic_650w.jpg'),
            ]
            cursor.executemany('''
                INSERT INTO productos (nombre, categoria, precio, descripcion, stock, codigo_barras, imagen_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', productos_ejemplo)
        
        conn.commit()
        conn.close()
    
    def get_productos(self, categoria=None, busqueda=None):
        """Obtiene productos con filtros opcionales"""
        conn = sqlite3.connect('computer_store.db')
        cursor = conn.cursor()
        
        query = 'SELECT * FROM productos WHERE 1=1'
        params = []
        
        if categoria and categoria != 'Todos':
            query += ' AND categoria = ?'
            params.append(categoria)
        
        if busqueda:
            query += ' AND (nombre LIKE ? OR descripcion LIKE ?)'
            params.extend([f'%{busqueda}%', f'%{busqueda}%'])
        
        cursor.execute(query, params)
        productos = cursor.fetchall()
        conn.close()
        return productos
    
    def get_producto_por_codigo(self, codigo):
        """Busca producto por código de barras"""
        conn = sqlite3.connect('computer_store.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos WHERE codigo_barras = ?', (codigo,))
        producto = cursor.fetchone()
        conn.close()
        return producto
    
    def agregar_al_carrito(self, producto_id, cantidad=1):
        """Agrega producto al carrito"""
        conn = sqlite3.connect('computer_store.db')
        cursor = conn.cursor()
        
        # Verificar si el producto ya está en el carrito
        cursor.execute('SELECT * FROM carrito WHERE producto_id = ?', (producto_id,))
        item_existente = cursor.fetchone()
        
        if item_existente:
            # Actualizar cantidad
            nueva_cantidad = item_existente[2] + cantidad
            cursor.execute('UPDATE carrito SET cantidad = ? WHERE producto_id = ?', 
                         (nueva_cantidad, producto_id))
        else:
            # Obtener precio del producto
            cursor.execute('SELECT precio FROM productos WHERE id = ?', (producto_id,))
            precio = cursor.fetchone()[0]
            
            # Insertar nuevo item
            cursor.execute('''
                INSERT INTO carrito (producto_id, cantidad, precio_unitario)
                VALUES (?, ?, ?)
            ''', (producto_id, cantidad, precio))
        
        conn.commit()
        conn.close()
    
    def get_carrito(self):
        """Obtiene items del carrito con información del producto"""
        conn = sqlite3.connect('computer_store.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, p.nombre, c.cantidad, c.precio_unitario, 
                   (c.cantidad * c.precio_unitario) as subtotal, p.id as producto_id
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
        ''')
        items = cursor.fetchall()
        conn.close()
        return items
    
    def limpiar_carrito(self):
        """Limpia el carrito de compras"""
        conn = sqlite3.connect('computer_store.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM carrito')
        conn.commit()
        conn.close()
    
    def crear_pedido(self, total, direccion, ubicacion_gps):
        """Crea un nuevo pedido"""
        conn = sqlite3.connect('computer_store.db')
        cursor = conn.cursor()
        
        # Crear pedido
        cursor.execute('''
            INSERT INTO pedidos (total, direccion, ubicacion_gps)
            VALUES (?, ?, ?)
        ''', (total, direccion, ubicacion_gps))
        
        pedido_id = cursor.lastrowid
        
        # Agregar detalles del pedido
        items_carrito = self.get_carrito()
        for item in items_carrito:
            cursor.execute('''
                INSERT INTO detalles_pedidos (pedido_id, producto_id, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
            ''', (pedido_id, item[5], item[2], item[3]))
        
        conn.commit()
        conn.close()
        return pedido_id

# Clase para manejo de GPS real
class GPSManager:
    def __init__(self):
        self.current_location = {"lat": 10.4236, "lon": -75.5378}  # Valor por defecto
        if platform == 'android':
            self.configure_gps()
    
    def configure_gps(self):
        """Configura el GPS usando plyer"""
        try:
            gps.configure(on_location=self.on_location)
            gps.start(minTime=1000, minDistance=1)
        except NotImplementedError:
            print("GPS no soportado en esta plataforma")
    
    def on_location(self, **kwargs):
        """Actualiza la ubicación cuando se recibe nueva data"""
        self.current_location = {"lat": kwargs.get('lat', 10.4236), "lon": kwargs.get('lon', -75.5378)}
    
    def get_current_location(self):
        """Obtiene la ubicación actual"""
        return self.current_location
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calcula distancia entre dos puntos"""
        import math
        R = 6371  # Radio de la Tierra en km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        return distance

# Clase para manejo del acelerómetro
class AccelerometerManager:
    def __init__(self):
        self.shake_threshold = 2.5
        self.last_shake_time = 0
        self.shake_callback = None
        self.enabled = False
    
    def start_monitoring(self, callback):
        """Inicia monitoreo del acelerómetro"""
        self.shake_callback = callback
        try:
            accelerometer.enable()
            self.enabled = True
            Clock.schedule_interval(self.check_accelerometer, 0.1)
        except NotImplementedError:
            print("Acelerómetro no soportado")
    
    def check_accelerometer(self, dt):
        """Verifica si hay un shake"""
        if not self.enabled:
            return
        try:
            accel_data = accelerometer.acceleration
            if accel_data:
                x, y, z = accel_data[:3]
                magnitude = (x**2 + y**2 + z**2)**0.5
                current_time = time.time()
                if magnitude > self.shake_threshold and current_time - self.last_shake_time > 2:
                    self.last_shake_time = current_time
                    if self.shake_callback:
                        self.shake_callback()
        except Exception:
            pass
    
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        if self.enabled:
            accelerometer.disable()
            self.enabled = False

# Pantalla principal con catálogo
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header con búsqueda
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        self.search_input = TextInput(
            hint_text='Buscar productos...',
            multiline=False,
            size_hint_x=0.7
        )
        self.search_input.bind(text=self.on_search)
        
        search_btn = Button(text='Buscar', size_hint_x=0.3)
        search_btn.bind(on_press=self.search_products)
        
        header_layout.add_widget(self.search_input)
        header_layout.add_widget(search_btn)
        
        # Filtros de categoría
        category_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=5)
        categorias = ['Todos', 'Procesadores', 'Tarjetas Gráficas', 'Memorias RAM', 'Motherboards', 'Almacenamiento', 'Fuentes de Poder', 'Refrigeración', 'Cases']
        
        for categoria in categorias:
            btn = Button(text=categoria, size_hint_x=1/len(categorias), font_size=10)
            btn.bind(on_press=lambda x, cat=categoria: self.filter_by_category(cat))
            category_layout.add_widget(btn)
        
        # Lista de productos
        self.productos_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.productos_layout.bind(minimum_height=self.productos_layout.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.productos_layout)
        
        # Navegación inferior
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=10)
        
        carrito_btn = Button(text='Carrito')
        carrito_btn.bind(on_press=self.go_to_cart)
        
        scanner_btn = Button(text='Scanner')
        scanner_btn.bind(on_press=self.go_to_scanner)
        
        mapa_btn = Button(text='Tiendas')
        mapa_btn.bind(on_press=self.go_to_map)
        
        nav_layout.add_widget(carrito_btn)
        nav_layout.add_widget(scanner_btn)
        nav_layout.add_widget(mapa_btn)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(category_layout)
        main_layout.add_widget(scroll)
        main_layout.add_widget(nav_layout)
        
        self.add_widget(main_layout)
        self.load_products()  # Asegurar recarga inicial
    
    def load_products(self, categoria=None, busqueda=None):
        """Carga productos en la interfaz"""
        self.productos_layout.clear_widgets()
        productos = self.db.get_productos(categoria, busqueda)
        
        for producto in productos:
            product_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, padding=5)
            product_layout.canvas.before.clear()
            
            # Información del producto
            info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
            
            nombre_label = Label(text=producto[1], font_size=14, bold=True, text_size=(250, None), halign='left')
            categoria_label = Label(text=f"📦 {producto[2]}", font_size=11, text_size=(250, None), halign='left')
            precio_label = Label(text=f"💲 ${producto[3]:,.2f}", font_size=13, bold=True, color=[0, 0.7, 0, 1])
            stock_label = Label(text=f"📊 Stock: {producto[5]} unidades", font_size=11, text_size=(250, None), halign='left')
            
            info_layout.add_widget(nombre_label)
            info_layout.add_widget(categoria_label)
            info_layout.add_widget(precio_label)
            info_layout.add_widget(stock_label)
            
            # Botón agregar al carrito
            add_btn = Button(text='Agregar\nal Carrito', size_hint_x=0.3)
            add_btn.bind(on_press=lambda x, pid=producto[0]: self.add_to_cart(pid))
            
            product_layout.add_widget(info_layout)
            product_layout.add_widget(add_btn)
            
            self.productos_layout.add_widget(product_layout)
    
    def on_search(self, instance, text):
        """Búsqueda en tiempo real"""
        if len(text) >= 3 or text == '':
            self.load_products(busqueda=text)
    
    def search_products(self, instance):
        """Búsqueda manual"""
        busqueda = self.search_input.text
        self.load_products(busqueda=busqueda)
    
    def filter_by_category(self, categoria):
        """Filtra productos por categoría"""
        self.load_products(categoria=categoria)
    
    def add_to_cart(self, producto_id):
        """Agrega producto al carrito"""
        self.db.agregar_al_carrito(producto_id)
        self.show_popup("Producto agregado al carrito exitosamente")
    
    def show_popup(self, message):
        """Muestra mensaje popup"""
        popup = Popup(title='Información', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()
    
    def go_to_cart(self, instance):
        """Navega al carrito"""
        self.manager.current = 'cart'
    
    def go_to_scanner(self, instance):
        """Navega al scanner"""
        self.manager.current = 'scanner'
    
    def go_to_map(self, instance):
        """Navega al mapa"""
        self.manager.current = 'map'

# Pantalla del carrito
class CartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.accel = AccelerometerManager()
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        back_btn = Button(text='← Volver', size_hint_x=0.3)
        back_btn.bind(on_press=self.go_back)
        
        title_label = Label(text='Carrito de Compras', font_size=20, bold=True)
        
        clear_btn = Button(text='Limpiar', size_hint_x=0.3)
        clear_btn.bind(on_press=self.clear_cart)
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(title_label)
        header_layout.add_widget(clear_btn)
        
        # Lista de items del carrito
        self.cart_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.cart_layout.bind(minimum_height=self.cart_layout.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.cart_layout)
        
        # Total y checkout
        bottom_layout = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=10)
        
        self.total_label = Label(text='Total: $0.00', font_size=18, bold=True)
        
        checkout_btn = Button(text='Proceder al Pago', size_hint_y=0.6)
        checkout_btn.bind(on_press=self.checkout)
        
        # Instrucción para shake
        shake_label = Label(text='Agita el dispositivo para limpiar el carrito', font_size=12)
        shake_btn = Button(text='Simular Shake', size_hint_y=0.4)
        shake_btn.bind(on_press=lambda x: self.accel.simulate_shake())
        
        bottom_layout.add_widget(self.total_label)
        bottom_layout.add_widget(checkout_btn)
        bottom_layout.add_widget(shake_label)
        bottom_layout.add_widget(shake_btn)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(scroll)
        main_layout.add_widget(bottom_layout)
        
        self.add_widget(main_layout)
        
        # Configurar acelerómetro
        self.accel.start_monitoring(self.on_shake_detected)
    
    def on_enter(self):
        """Se ejecuta cuando se entra a la pantalla"""
        self.load_cart_items()
    
    def load_cart_items(self):
        """Carga los items del carrito"""
        self.cart_layout.clear_widgets()
        items = self.db.get_carrito()
        total = 0
        
        for item in items:
            item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, padding=5)
            
            # Información del item
            info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
            
            nombre_label = Label(text=item[1], font_size=14, bold=True)
            cantidad_label = Label(text=f"Cantidad: {item[2]}")
            precio_label = Label(text=f"${item[3]:,.2f} c/u")
            subtotal_label = Label(text=f"Subtotal: ${item[4]:,.2f}", bold=True)
            
            info_layout.add_widget(nombre_label)
            info_layout.add_widget(cantidad_label)
            info_layout.add_widget(precio_label)
            info_layout.add_widget(subtotal_label)
            
            # Botón eliminar
            remove_btn = Button(text='Eliminar', size_hint_x=0.3)
            remove_btn.bind(on_press=lambda x, iid=item[0]: self.remove_item(iid))
            
            item_layout.add_widget(info_layout)
            item_layout.add_widget(remove_btn)
            
            self.cart_layout.add_widget(item_layout)
            total += item[4]
        
        self.total_label.text = f'Total: ${total:,.2f}'
        
        if len(items) == 0:
            empty_label = Label(text='El carrito está vacío', font_size=16)
            self.cart_layout.add_widget(empty_label)
    
    def remove_item(self, item_id):
        """Elimina item del carrito"""
        conn = sqlite3.connect('computer_store.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM carrito WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        self.load_cart_items()
    
    def clear_cart(self, instance):
        """Limpia el carrito"""
        self.db.limpiar_carrito()
        self.load_cart_items()
        self.show_popup("Carrito limpiado")
    
    def on_shake_detected(self):
        """Se ejecuta cuando se detecta shake"""
        self.clear_cart(None)
    
    def checkout(self, instance):
        """Procede al checkout"""
        items = self.db.get_carrito()
        if not items:
            self.show_popup("El carrito está vacío")
            return
        
        total = sum(item[4] for item in items)
        
        # Usar GPS real para ubicación
        gps = GPSManager()
        location = gps.get_current_location()
        ubicacion_gps = f"{location['lat']},{location['lon']}"
        
        # Crear pedido
        pedido_id = self.db.crear_pedido(total, "Dirección de envío", ubicacion_gps)
        
        # Limpiar carrito
        self.db.limpiar_carrito()
        
        self.show_popup(f"Pedido #{pedido_id} creado exitosamente!\nTotal: ${total:,.2f}")
        self.load_cart_items()
    
    def show_popup(self, message):
        """Muestra mensaje popup"""
        popup = Popup(title='Información', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()
    
    def go_back(self, instance):
        """Vuelve a la pantalla anterior"""
        self.manager.current = 'home'

# Pantalla del scanner con cámara real
class ScannerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        back_btn = Button(text='← Volver', size_hint_x=0.3)
        back_btn.bind(on_press=self.go_back)
        
        title_label = Label(text='Scanner de Códigos', font_size=20, bold=True)
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(title_label)
        header_layout.add_widget(Label(size_hint_x=0.3))  # Espaciador
        
        # Área de la cámara
        camera_layout = BoxLayout(orientation='vertical', size_hint_y=0.6)
        
        try:
            self.camera = Camera(resolution=(640, 480), play=True)
            self.camera.bind(on_texture=self.update_camera)
        except Exception as e:
            self.camera = Label(
                text=f'[Cámara no disponible]\nError: {str(e)}\nEnfoca el código de barras',
                font_size=16,
                halign='center'
            )
        
        capture_btn = Button(text='📸 Capturar Código', size_hint_y=0.2)
        capture_btn.bind(on_press=self.capture_code)
        camera_layout.add_widget(self.camera)
        camera_layout.add_widget(capture_btn)
        
        # Área de entrada manual
        manual_layout = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=10)
        
        manual_label = Label(text='O ingresa el código manualmente:', font_size=14)
        
        input_layout = BoxLayout(orientation='horizontal', spacing=10)
        
        self.code_input = TextInput(
            hint_text='Código de barras...',
            multiline=False,
            size_hint_x=0.7
        )
        
        scan_btn = Button(text='Buscar', size_hint_x=0.3)
        scan_btn.bind(on_press=self.search_by_code)
        
        input_layout.add_widget(self.code_input)
        input_layout.add_widget(scan_btn)
        
        manual_layout.add_widget(manual_label)
        manual_layout.add_widget(input_layout)
        
        # Botones de códigos de ejemplo
        examples_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=5)
        
        example_codes = ['1234567890123', '1234567890124', '1234567890125']
        for code in example_codes:
            btn = Button(text=f'Código: {code[-3:]}')
            btn.bind(on_press=lambda x, c=code: self.scan_example_code(c))
            examples_layout.add_widget(btn)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(camera_layout)
        main_layout.add_widget(manual_layout)
        main_layout.add_widget(examples_layout)
        
        self.add_widget(main_layout)
    
    def update_camera(self, *args):
        """Actualiza la vista de la cámara (opcional)"""
        pass
    
    def capture_code(self, instance):
        """Captura una imagen y procesa el código"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            photo_path = f"barcode_{timestamp}.jpg"
            camera.take_picture(filename=photo_path, on_complete=self.on_picture_taken)
        except NotImplementedError:
            self.show_popup("📷 Cámara no soportada en esta plataforma")
    
    def on_picture_taken(self, photo_path):
        """Procesa la imagen capturada (simulado por ahora)"""
        # Simulación: usa un código fijo para pruebas
        code = "1234567890123"  # Reemplazar con decodificación real (ver notas)
        self.scan_code(code)
    
    def search_by_code(self, instance):
        """Busca producto por código"""
        code = self.code_input.text.strip()
        if not code:
            self.show_popup("Ingresa un código de barras")
            return
        
        self.scan_code(code)
    
    def scan_example_code(self, code):
        """Escanea código de ejemplo"""
        self.code_input.text = code
        self.scan_code(code)
    
    def scan_code(self, code):
        """Procesa el código escaneado"""
        producto = self.db.get_producto_por_codigo(code)
        
        if producto:
            # Mostrar información del producto
            info = f"Producto encontrado:\n\n"
            info += f"Nombre: {producto[1]}\n"
            info += f"Categoría: {producto[2]}\n"
            info += f"Precio: ${producto[3]:,.2f}\n"
            info += f"Stock: {producto[5]}\n\n"
            info += "¿Deseas agregarlo al carrito?"
            
            popup_layout = BoxLayout(orientation='vertical', spacing=10)
            
            info_label = Label(text=info, text_size=(300, None), halign='center')
            
            buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
            
            add_btn = Button(text='Agregar al Carrito')
            add_btn.bind(on_press=lambda x: self.add_and_close_popup(producto[0]))
            
            cancel_btn = Button(text='Cancelar')
            cancel_btn.bind(on_press=lambda x: self.popup.dismiss())
            
            buttons_layout.add_widget(add_btn)
            buttons_layout.add_widget(cancel_btn)
            
            popup_layout.add_widget(info_label)
            popup_layout.add_widget(buttons_layout)
            
            self.popup = Popup(
                title='Producto Encontrado',
                content=popup_layout,
                size_hint=(0.9, 0.7)
            )
            self.popup.open()
        else:
            self.show_popup(f"No se encontró producto con código: {code}")
    
    def add_and_close_popup(self, producto_id):
        """Agrega producto al carrito y cierra popup"""
        self.db.agregar_al_carrito(producto_id)
        self.popup.dismiss()
        self.show_popup("Producto agregado al carrito")
        self.code_input.text = ""
    
    def show_popup(self, message):
        """Muestra mensaje popup"""
        popup = Popup(title='Información', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()
    
    def go_back(self, instance):
        """Vuelve a la pantalla anterior"""
        self.manager.current = 'home'

# Pantalla del mapa con GPS real
class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps = GPSManager()
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        back_btn = Button(text='← Volver', size_hint_x=0.3)
        back_btn.bind(on_press=self.go_back)
        
        title_label = Label(text='Tiendas Cercanas', font_size=20, bold=True)
        
        location_btn = Button(text='Mi Ubicación', size_hint_x=0.3)
        location_btn.bind(on_press=self.get_location)
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(title_label)
        header_layout.add_widget(location_btn)
        
        # Área del mapa (simulada)
        map_layout = BoxLayout(orientation='vertical', size_hint_y=0.6)
        
        self.map_placeholder = Label(
            text='🗺 [Mapa GPS]\nCargando ubicación...',
            font_size=14,
            halign='center',
            text_size=(None, None)
        )
        map_layout.add_widget(self.map_placeholder)
        
        # Lista de tiendas
        stores_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=10)
        
        stores_label = Label(text='Tiendas Disponibles:', font_size=16, bold=True, size_hint_y=0.2)
        
        self.stores_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.stores_list.bind(minimum_height=self.stores_list.setter('height'))
        
        scroll_stores = ScrollView()
        scroll_stores.add_widget(self.stores_list)
        
        stores_layout.add_widget(stores_label)
        stores_layout.add_widget(scroll_stores)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(map_layout)
        main_layout.add_widget(stores_layout)
        
        self.add_widget(main_layout)
        self.load_stores()
    
    def load_stores(self):
        """Carga lista de tiendas cercanas"""
        self.stores_list.clear_widgets()
        current_location = self.gps.get_current_location()
        lat1, lon1 = current_location['lat'], current_location['lon']
        
        tiendas = [
            {"nombre": "Computerworking", "direccion": "Calle 32 #25-45", "lat": 10.4250, "lon": -75.5390, "telefono": "300-123-4567", "especialidad": "Procesadores y GPUs"},
            {"nombre": "Compulago", "direccion": "Av. Pedro de Heredia #85-12", "lat": 10.4300, "lon": -75.5340, "telefono": "300-234-5678", "especialidad": "RAM y Almacenamiento"},
            {"nombre": "Computo Segunda mano", "direccion": "Cra 17 #45-23", "lat": 10.4150, "lon": -75.5450, "telefono": "300-345-6789", "especialidad": "Motherboards y Fuentes"},
            {"nombre": "Celuclock", "direccion": "Centro Comercial la castellana", "lat": 10.4100, "lon": -75.5500, "telefono": "300-456-7890", "especialidad": "Celulares y Accesorios"},
        ]
        
        for tienda in tiendas:
            distancia = self.gps.calculate_distance(lat1, lon1, tienda['lat'], tienda['lon'])
            tienda['distancia'] = round(distancia, 1)
            store_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, padding=5)
            
            # Información de la tienda
            info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
            
            nombre_label = Label(text=f"🔧 {tienda['nombre']}", font_size=14, bold=True)
            direccion_label = Label(text=tienda["direccion"], font_size=12)
            distancia_label = Label(text=f"📍 {tienda['distancia']} km", font_size=12)
            especialidad_label = Label(text=f"⚡ {tienda['especialidad']}", font_size=11, color=[0, 0.7, 0, 1])
            telefono_label = Label(text=f"📞 {tienda['telefono']}", font_size=12)
            
            info_layout.add_widget(nombre_label)
            info_layout.add_widget(direccion_label)
            info_layout.add_widget(distancia_label)
            info_layout.add_widget(especialidad_label)
            
            # Botón de navegación
            nav_btn = Button(text='Cómo\nLlegar', size_hint_x=0.3)
            nav_btn.bind(on_press=lambda x, t=tienda: self.navigate_to_store(t))
            
            store_layout.add_widget(info_layout)
            store_layout.add_widget(nav_btn)
            
            self.stores_list.add_widget(store_layout)
    
    def get_location(self, instance):
        """Obtiene ubicación actual"""
        location = self.gps.get_current_location()
        self.map_placeholder.text = f"🗺 [Mapa GPS]\n📍 Tu ubicación: Lat {location['lat']}, Lon {location['lon']}\n\n🏪 Tiendas cercanas cargadas"
        self.show_popup(f"Ubicación actual:\nLatitud: {location['lat']}\nLongitud: {location['lon']}")
        self.load_stores()
    
    def navigate_to_store(self, tienda):
        """Simula navegación a la tienda"""
        message = f"🗺 Navegando a {tienda['nombre']}\n\n"
        message += f"Dirección: {tienda['direccion']}\n"
        message += f"Distancia: {tienda['distancia']} km\n"
        message += f"Tiempo estimado: {int(tienda['distancia'] * 3)} minutos"
        
        self.show_popup(message)
    
    def show_popup(self, message):
        """Muestra mensaje popup"""
        popup = Popup(title='Información GPS', content=Label(text=message), size_hint=(0.8, 0.6))
        popup.open()
    
    def go_back(self, instance):
        """Vuelve a la pantalla anterior"""
        self.manager.current = 'home'

# Aplicación principal
class ComputerStoreApp(App):
    def build(self):
        # Configurar ventana
        Window.size = (400, 700)  # Simular tamaño móvil
        
        # Crear screen manager
        sm = ScreenManager()
        
        # Agregar pantallas
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(CartScreen(name='cart'))
        sm.add_widget(ScannerScreen(name='scanner'))
        sm.add_widget(MapScreen(name='map'))
        
        return sm

if __name__ == '__main__':
    ComputerStoreApp().run()
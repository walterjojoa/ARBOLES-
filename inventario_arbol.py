"""
Taller Árboles - Inventario de Droguería con Árbol Binario de Búsqueda (ABB)
Estructuras de Datos · Universidad Cooperativa de Colombia

Caso de estudio: una droguería necesita encontrar sus productos rápidamente por
código. En vez de recorrer una lista completa (estructura lineal), los productos
se guardan en un Árbol Binario de Búsqueda ordenado por código: en cada nodo se
decide ir a la izquierda (código menor) o a la derecha (código mayor).

Ejecutar:  python inventario_arbol.py
Requisitos: solo Python 3 (Tkinter viene incluido).
"""

import tkinter as tk
from tkinter import ttk, messagebox


# =============================================================================
#  MODELO: ÁRBOL BINARIO DE BÚSQUEDA
# =============================================================================

UMBRAL_STOCK_BAJO = 10


class Nodo:
    def __init__(self, codigo, nombre, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.izquierda = None
        self.derecha = None


class ArbolInventario:
    """ABB ordenado por código de producto.

    Criterio para duplicados: si se inserta un código que ya existe, no se crea
    un nodo nuevo, se actualizan los datos del producto (igual que la agenda
    telefónica vista en clase).
    """

    def __init__(self):
        self.raiz = None

    # ---------------- Insertar ----------------
    def insertar(self, codigo, nombre, precio, stock):
        """Retorna True si se creó un nodo nuevo, False si se actualizó."""
        if self.raiz is None:
            self.raiz = Nodo(codigo, nombre, precio, stock)
            return True
        return self._insertar_recursivo(self.raiz, codigo, nombre, precio, stock)

    def _insertar_recursivo(self, actual, codigo, nombre, precio, stock):
        if codigo < actual.codigo:
            if actual.izquierda is None:
                actual.izquierda = Nodo(codigo, nombre, precio, stock)
                return True
            return self._insertar_recursivo(actual.izquierda, codigo, nombre, precio, stock)
        if codigo > actual.codigo:
            if actual.derecha is None:
                actual.derecha = Nodo(codigo, nombre, precio, stock)
                return True
            return self._insertar_recursivo(actual.derecha, codigo, nombre, precio, stock)
        actual.nombre, actual.precio, actual.stock = nombre, precio, stock
        return False

    # ---------------- Buscar ----------------
    def buscar(self, codigo):
        """Retorna (nodo, camino). El camino son los nodos visitados desde la raíz."""
        camino = []
        actual = self.raiz
        while actual is not None:
            camino.append(actual)
            if codigo == actual.codigo:
                return actual, camino
            actual = actual.izquierda if codigo < actual.codigo else actual.derecha
        return None, camino

    # ---------------- Eliminar ----------------
    def eliminar(self, codigo):
        self.raiz, eliminado = self._eliminar_recursivo(self.raiz, codigo)
        return eliminado

    def _eliminar_recursivo(self, nodo, codigo):
        if nodo is None:
            return None, False
        if codigo < nodo.codigo:
            nodo.izquierda, ok = self._eliminar_recursivo(nodo.izquierda, codigo)
            return nodo, ok
        if codigo > nodo.codigo:
            nodo.derecha, ok = self._eliminar_recursivo(nodo.derecha, codigo)
            return nodo, ok

        # Caso 1 (hoja) y caso 2 (un solo hijo): el hijo ocupa su lugar
        if nodo.izquierda is None:
            return nodo.derecha, True
        if nodo.derecha is None:
            return nodo.izquierda, True

        # Caso 3 (dos hijos): se reemplaza por el sucesor inorden
        # (el menor del subárbol derecho) y luego se elimina ese sucesor.
        sucesor = nodo.derecha
        while sucesor.izquierda is not None:
            sucesor = sucesor.izquierda
        codigo_sucesor = sucesor.codigo
        nodo.codigo, nodo.nombre = sucesor.codigo, sucesor.nombre
        nodo.precio, nodo.stock = sucesor.precio, sucesor.stock
        nodo.derecha, _ = self._eliminar_recursivo(nodo.derecha, codigo_sucesor)
        return nodo, True

    # ---------------- Recorridos ----------------
    def inorden(self):
        resultado = []

        def visitar(n):
            if n is not None:
                visitar(n.izquierda)
                resultado.append(n)
                visitar(n.derecha)

        visitar(self.raiz)
        return resultado

    def preorden(self):
        resultado = []

        def visitar(n):
            if n is not None:
                resultado.append(n)
                visitar(n.izquierda)
                visitar(n.derecha)

        visitar(self.raiz)
        return resultado

    def postorden(self):
        resultado = []

        def visitar(n):
            if n is not None:
                visitar(n.izquierda)
                visitar(n.derecha)
                resultado.append(n)

        visitar(self.raiz)
        return resultado

    # ---------------- Propiedades del árbol ----------------
    def altura(self, nodo="raiz"):
        """Número de niveles (la raíz está en el nivel 1, como en la clase)."""
        if nodo == "raiz":
            nodo = self.raiz
        if nodo is None:
            return 0
        return 1 + max(self.altura(nodo.izquierda), self.altura(nodo.derecha))

    def peso(self):
        """Cantidad total de nodos."""
        return len(self.inorden())

    def hojas(self):
        return [n for n in self.inorden() if self.grado(n) == 0]

    def grado(self, nodo):
        """Número de hijos de un nodo."""
        return (nodo.izquierda is not None) + (nodo.derecha is not None)

    def grado_arbol(self):
        return max((self.grado(n) for n in self.inorden()), default=0)

    def nivel(self, codigo):
        nodo, camino = self.buscar(codigo)
        return len(camino) if nodo else None

    def padre(self, codigo):
        nodo, camino = self.buscar(codigo)
        return camino[-2] if nodo and len(camino) > 1 else None

    def tipo(self, nodo):
        if nodo is self.raiz:
            return "Raíz"
        return "Hoja" if self.grado(nodo) == 0 else "Rama"

    def valor_total(self):
        return sum(n.precio * n.stock for n in self.inorden())

    def stock_bajo(self):
        return [n for n in self.inorden() if n.stock < UMBRAL_STOCK_BAJO]

    # ---------------- Balancear ----------------
    def balancear(self):
        """Reconstruye el árbol tomando siempre el elemento del medio del
        recorrido inorden como raíz (idea base de los árboles AVL)."""
        datos = [(n.codigo, n.nombre, n.precio, n.stock) for n in self.inorden()]

        def construir(inicio, fin):
            if inicio > fin:
                return None
            medio = (inicio + fin) // 2
            nodo = Nodo(*datos[medio])
            nodo.izquierda = construir(inicio, medio - 1)
            nodo.derecha = construir(medio + 1, fin)
            return nodo

        self.raiz = construir(0, len(datos) - 1)

    def vaciar(self):
        self.raiz = None


# =============================================================================
#  VISTA: INTERFAZ GRÁFICA (Tkinter)
# =============================================================================

FUENTE = "Segoe UI"

AZUL_OSCURO = "#25306B"
AZUL = "#537BFF"
NARANJA = "#FF7333"
AMBAR = "#FFB020"
MORADO = "#92278F"
VERDE = "#2FA36B"
ROJO = "#E5484D"
FONDO = "#F3F5FB"
TARJETA = "#FFFFFF"
BORDE = "#E3E7F1"
TEXTO = "#1E2547"
TENUE = "#7A82A6"

# relleno, borde  (mismos colores que las diapositivas: raíz amarilla, rama azul, hoja verde)
COLORES_NODO = {
    "Raíz": ("#FFC83D", "#C98F00"),
    "Rama": ("#CFE0FA", "#4A6FB3"),
    "Hoja": ("#9AD873", "#4E8F2C"),
}

RADIO = 25
SEP_X = 70
SEP_Y = 88
Y_INICIAL = 56

DATOS_EJEMPLO = [
    (500, "Acetaminofén 500mg", 3500, 120),
    (250, "Ibuprofeno 400mg", 6200, 45),
    (750, "Amoxicilina 500mg", 18900, 8),
    (120, "Loratadina 10mg", 4800, 60),
    (380, "Omeprazol 20mg", 9500, 30),
    (620, "Vitamina C 1g", 12000, 75),
    (880, "Suero oral", 5400, 5),
    (60, "Alcohol antiséptico", 7800, 40),
    (180, "Gasas estériles", 3200, 90),
    (300, "Diclofenaco gel", 15600, 12),
    (450, "Losartán 50mg", 11200, 25),
    (700, "Jarabe para la tos", 16500, 6),
    (950, "Termómetro digital", 28000, 9),
    (820, "Tapabocas x50", 22000, 3),
]


def moneda(valor):
    return "$" + f"{valor:,.0f}".replace(",", ".")


def recortar(texto, maximo):
    return texto if len(texto) <= maximo else texto[: maximo - 1] + "…"


def oscurecer(color, factor=0.86):
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return "#{:02x}{:02x}{:02x}".format(int(r * factor), int(g * factor), int(b * factor))


class Boton(tk.Label):
    """Botón plano con efecto hover."""

    def __init__(self, master, texto, comando, color=AZUL, color_texto="white", **kw):
        super().__init__(master, text=texto, bg=color, fg=color_texto, cursor="hand2",
                         font=(FUENTE, 10, "bold"), padx=14, pady=8, **kw)
        self.comando = comando
        self.cambiar_color(color, color_texto)
        self.bind("<Enter>", lambda e: self.config(bg=self.color_hover))
        self.bind("<Leave>", lambda e: self.config(bg=self.color))
        self.bind("<Button-1>", lambda e: self.comando())

    def cambiar_color(self, color, color_texto="white"):
        self.color, self.color_hover = color, oscurecer(color)
        self.config(bg=color, fg=color_texto)


def tarjeta(master, titulo=None, subtitulo=None):
    marco = tk.Frame(master, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1)
    if titulo:
        encabezado = tk.Frame(marco, bg=TARJETA)
        encabezado.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(encabezado, text=titulo, bg=TARJETA, fg=TEXTO,
                 font=(FUENTE, 12, "bold")).pack(side="left")
        if subtitulo:
            tk.Label(encabezado, text=subtitulo, bg=TARJETA, fg=TENUE,
                     font=(FUENTE, 9)).pack(side="right")
    return marco


class AplicacionInventario(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventario Droguería · Árbol Binario de Búsqueda")
        self.geometry("1440x900")
        self.minsize(1200, 760)
        self.configure(bg=FONDO)
        try:
            self.state("zoomed")
        except tk.TclError:
            pass

        self.arbol = ArbolInventario()
        self.tipo_recorrido = "Inorden"
        # (códigos resaltados del camino, código encontrado, código del paso actual)
        self.resaltado = (set(), None, None)
        self.animando = False
        self._id_aviso = None

        self._configurar_estilos()
        self._crear_encabezado()
        self._crear_barra_estado()
        cuerpo = tk.Frame(self, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=18, pady=(12, 0))
        self._crear_panel_lateral(cuerpo)
        self._crear_panel_principal(cuerpo)

        self.cargar_ejemplo(silencioso=True)

    # ------------------------------------------------------------------ estilos
    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Inv.Treeview", background=TARJETA, fieldbackground=TARJETA,
                         foreground=TEXTO, rowheight=28, font=(FUENTE, 10), borderwidth=0)
        estilo.configure("Inv.Treeview.Heading", background=AZUL_OSCURO, foreground="white",
                         font=(FUENTE, 10, "bold"), relief="flat", padding=6)
        estilo.map("Inv.Treeview.Heading", background=[("active", AZUL)])
        estilo.map("Inv.Treeview", background=[("selected", AZUL)],
                   foreground=[("selected", "white")])
        for orientacion in ("Vertical", "Horizontal"):
            estilo.configure(f"{orientacion}.TScrollbar", background="#D5DBEA",
                             troughcolor=FONDO, bordercolor=FONDO, arrowcolor=TENUE,
                             lightcolor="#D5DBEA", darkcolor="#D5DBEA")

    # ------------------------------------------------------------------ encabezado
    def _crear_encabezado(self):
        barra = tk.Frame(self, bg=AZUL_OSCURO)
        barra.pack(fill="x")
        izquierda = tk.Frame(barra, bg=AZUL_OSCURO)
        izquierda.pack(side="left", padx=24, pady=10)

        tk.Label(izquierda, text="  TALLER · ESTRUCTURAS JERÁRQUICAS  ", bg=AMBAR, fg="white",
                 font=(FUENTE, 8, "bold")).pack(anchor="w")
        tk.Label(izquierda, text="Inventario de Droguería", bg=AZUL_OSCURO, fg="white",
                 font=(FUENTE, 18, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Label(izquierda, text="Productos organizados en un Árbol Binario de Búsqueda por código",
                 bg=AZUL_OSCURO, fg="#B8C3F0", font=(FUENTE, 10)).pack(anchor="w")

        leyenda = tk.Frame(barra, bg=AZUL_OSCURO)
        leyenda.pack(side="right", padx=24)
        elementos = [
            ("Raíz", *COLORES_NODO["Raíz"]),
            ("Rama", *COLORES_NODO["Rama"]),
            ("Hoja", *COLORES_NODO["Hoja"]),
            ("Camino de búsqueda", AZUL_OSCURO, NARANJA),
            ("Encontrado", MORADO, "#5E1A5C"),
            ("Stock bajo", ROJO, ROJO),
        ]
        for texto, relleno, borde in elementos:
            item = tk.Frame(leyenda, bg=AZUL_OSCURO)
            item.pack(side="left", padx=8)
            punto = tk.Canvas(item, width=18, height=18, bg=AZUL_OSCURO, highlightthickness=0)
            punto.create_oval(2, 2, 16, 16, fill=relleno, outline=borde, width=3 if borde == NARANJA else 2)
            punto.pack(side="left")
            tk.Label(item, text=texto, bg=AZUL_OSCURO, fg="white",
                     font=(FUENTE, 9)).pack(side="left", padx=(4, 0))

    # ------------------------------------------------------------------ barra de estado
    def _crear_barra_estado(self):
        self.barra_estado = tk.Label(self, text="Listo", anchor="w", bg=AZUL_OSCURO, fg="white",
                                     font=(FUENTE, 10), padx=20, pady=6)
        self.barra_estado.pack(side="bottom", fill="x")

    def aviso(self, mensaje, tipo="info"):
        colores = {"ok": VERDE, "error": ROJO, "info": AZUL, "alerta": NARANJA}
        self.barra_estado.config(text="  " + mensaje, bg=colores.get(tipo, AZUL))
        if self._id_aviso:
            self.after_cancel(self._id_aviso)
        self._id_aviso = self.after(5000, lambda: self.barra_estado.config(text="Listo", bg=AZUL_OSCURO))

    # ------------------------------------------------------------------ panel lateral
    def _crear_panel_lateral(self, master):
        lateral = tk.Frame(master, bg=FONDO, width=330)
        lateral.pack(side="left", fill="y", padx=(0, 16), pady=(0, 12))
        lateral.pack_propagate(False)

        # --- Formulario
        form = tarjeta(lateral, "Producto")
        form.pack(fill="x")
        cuerpo = tk.Frame(form, bg=TARJETA)
        cuerpo.pack(fill="x", padx=16, pady=(0, 14))

        self.campos = {}
        # (clave, texto, fila, columna, columnas que ocupa)
        etiquetas = [("codigo", "Código", 0, 0, 1), ("nombre", "Nombre del producto", 0, 1, 2),
                     ("precio", "Precio (COP)", 1, 0, 2), ("stock", "Stock", 1, 2, 1)]
        for clave, texto, fila, columna, ocupa in etiquetas:
            contenedor = tk.Frame(cuerpo, bg=TARJETA)
            contenedor.grid(row=fila, column=columna, columnspan=ocupa, sticky="ew",
                            padx=(0 if columna == 0 else 4, 0 if columna + ocupa == 3 else 4), pady=3)
            tk.Label(contenedor, text=texto, bg=TARJETA, fg=TENUE,
                     font=(FUENTE, 9, "bold")).pack(anchor="w")
            entrada = tk.Entry(contenedor, font=(FUENTE, 11), bg=FONDO, fg=TEXTO, relief="flat",
                               highlightthickness=1, highlightbackground=BORDE,
                               highlightcolor=AZUL, insertbackground=TEXTO, width=6)
            entrada.pack(fill="x", ipady=4, pady=(2, 0))
            self.campos[clave] = entrada
        for i in range(3):
            cuerpo.columnconfigure(i, weight=1, uniform="campos")
        self.campos["codigo"].bind("<Return>", lambda e: self.buscar())

        botones = tk.Frame(cuerpo, bg=TARJETA)
        botones.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        for i in range(3):
            botones.columnconfigure(i, weight=1, uniform="botones")
        Boton(botones, "＋  Agregar / Actualizar", self.agregar, VERDE).grid(
            row=0, column=0, columnspan=3, sticky="ew", pady=(0, 6))
        Boton(botones, "Buscar", self.buscar, AZUL).grid(row=1, column=0, sticky="ew", padx=(0, 3))
        Boton(botones, "Eliminar", self.eliminar, ROJO).grid(row=1, column=1, sticky="ew", padx=3)
        Boton(botones, "Limpiar", self.limpiar_formulario, "#E8EDFB", AZUL_OSCURO).grid(
            row=1, column=2, sticky="ew", padx=(3, 0))

        # --- Acciones sobre el árbol
        acciones = tarjeta(lateral, "Árbol")
        acciones.pack(fill="x", pady=10)
        cuerpo_acc = tk.Frame(acciones, bg=TARJETA)
        cuerpo_acc.pack(fill="x", padx=16, pady=(0, 12))
        for i in range(3):
            cuerpo_acc.columnconfigure(i, weight=1, uniform="acciones")
        Boton(cuerpo_acc, "Balancear", self.balancear, MORADO).grid(row=0, column=0, sticky="ew", padx=(0, 3))
        Boton(cuerpo_acc, "Ejemplo", self.cargar_ejemplo, NARANJA).grid(row=0, column=1, sticky="ew", padx=3)
        Boton(cuerpo_acc, "Vaciar", self.vaciar, "#E8EDFB", AZUL_OSCURO).grid(
            row=0, column=2, sticky="ew", padx=(3, 0))

        # --- Detalle del nodo seleccionado (los datos del producto ya están en el formulario)
        detalle = tarjeta(lateral, "Detalle del nodo")
        detalle.pack(fill="both", expand=True)
        cuerpo_det = tk.Frame(detalle, bg=TARJETA)
        cuerpo_det.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.detalle = {}
        claves = ["Tipo de nodo", "Nivel", "Grado", "Padre", "Hijos", "Stock", "Camino"]
        for fila, clave in enumerate(claves):
            tk.Label(cuerpo_det, text=clave, bg=TARJETA, fg=TENUE, font=(FUENTE, 9),
                     anchor="w").grid(row=fila, column=0, sticky="w", pady=2)
            valor = tk.Label(cuerpo_det, text="—", bg=TARJETA, fg=TEXTO,
                             font=(FUENTE, 10, "bold"), anchor="e")
            valor.grid(row=fila, column=1, sticky="e", pady=2)
            self.detalle[clave] = valor
        cuerpo_det.columnconfigure(1, weight=1)
        self.detalle["Camino"].config(fg=NARANJA)

    # ------------------------------------------------------------------ panel principal
    def _crear_panel_principal(self, master):
        principal = tk.Frame(master, bg=FONDO)
        principal.pack(side="left", fill="both", expand=True, pady=(0, 14))

        # --- Tarjetas de estadísticas
        fila_stats = tk.Frame(principal, bg=FONDO)
        fila_stats.pack(fill="x")
        self.estadisticas = {}
        definiciones = [
            ("peso", "Peso (nodos)", AZUL),
            ("altura", "Altura (niveles)", MORADO),
            ("hojas", "Hojas", VERDE),
            ("grado", "Grado del árbol", AMBAR),
            ("valor", "Valor inventario", AZUL_OSCURO),
            ("bajo", "Stock bajo", ROJO),
        ]
        for i, (clave, titulo, color) in enumerate(definiciones):
            caja = tk.Frame(fila_stats, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1)
            caja.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0))
            fila_stats.columnconfigure(i, weight=1, uniform="stats")
            tk.Frame(caja, bg=color, width=5).pack(side="left", fill="y")
            interior = tk.Frame(caja, bg=TARJETA)
            interior.pack(side="left", fill="both", expand=True, padx=12, pady=10)
            tk.Label(interior, text=titulo.upper(), bg=TARJETA, fg=TENUE,
                     font=(FUENTE, 8, "bold")).pack(anchor="w")
            valor = tk.Label(interior, text="0", bg=TARJETA, fg=TEXTO, font=(FUENTE, 18, "bold"))
            valor.pack(anchor="w")
            self.estadisticas[clave] = valor

        # --- Tarjeta principal con dos vistas: Árbol / Tabla
        vista = tk.Frame(principal, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1)
        vista.pack(fill="both", expand=True, pady=(12, 0))

        encabezado = tk.Frame(vista, bg=TARJETA)
        encabezado.pack(fill="x", padx=16, pady=(12, 6))
        self.titulo_vista = tk.Label(encabezado, text="", bg=TARJETA, fg=TEXTO,
                                     font=(FUENTE, 12, "bold"))
        self.titulo_vista.pack(side="left")
        self.botones_vista = {}
        for nombre in ("Tabla", "Árbol"):
            boton = Boton(encabezado, nombre, lambda n=nombre: self.cambiar_vista(n), "#E8EDFB", AZUL_OSCURO)
            boton.config(padx=18, pady=4)
            boton.pack(side="right", padx=(6, 0))
            self.botones_vista[nombre] = boton
        self.pista = tk.Label(encabezado, text="", bg=TARJETA, fg=TENUE, font=(FUENTE, 9))
        self.pista.pack(side="right", padx=12)

        # Pie con los recorridos (visible en ambas vistas)
        pie = tk.Frame(vista, bg="#F7F9FE", highlightbackground=BORDE, highlightthickness=1)
        pie.pack(side="bottom", fill="x")
        selector = tk.Frame(pie, bg="#F7F9FE")
        selector.pack(fill="x", padx=16, pady=(10, 0))
        tk.Label(selector, text="Recorrido:", bg="#F7F9FE", fg=TENUE,
                 font=(FUENTE, 9, "bold")).pack(side="left", padx=(0, 8))
        self.botones_recorrido = {}
        for nombre in ("Inorden", "Preorden", "Postorden"):
            boton = Boton(selector, nombre, lambda n=nombre: self.cambiar_recorrido(n), "#E8EDFB", AZUL_OSCURO)
            boton.config(padx=12, pady=3)
            boton.pack(side="left", padx=(0, 6))
            self.botones_recorrido[nombre] = boton
        self.explicacion = tk.Label(selector, text="", bg="#F7F9FE", fg=TENUE, font=(FUENTE, 9))
        self.explicacion.pack(side="left", padx=8)
        self.secuencia = tk.Label(pie, text="", bg="#F7F9FE", fg=AZUL_OSCURO, anchor="w",
                                  justify="left", font=("Consolas", 10))
        self.secuencia.pack(fill="x", padx=16, pady=(6, 10))
        pie.bind("<Configure>", lambda e: self.secuencia.config(wraplength=e.width - 40))

        # Páginas apiladas (se muestra una u otra)
        paginas = tk.Frame(vista, bg=TARJETA)
        paginas.pack(fill="both", expand=True)
        self.paginas = {"Árbol": tk.Frame(paginas, bg=TARJETA), "Tabla": tk.Frame(paginas, bg=TARJETA)}
        for pagina in self.paginas.values():
            pagina.place(relx=0, rely=0, relwidth=1, relheight=1)

        # --- Página: tabla
        contenedor_tabla = tk.Frame(self.paginas["Tabla"], bg=TARJETA)
        contenedor_tabla.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        columnas = ("codigo", "nombre", "precio", "stock", "valor", "tipo", "nivel")
        self.tabla = ttk.Treeview(contenedor_tabla, columns=columnas, show="headings",
                                  style="Inv.Treeview")
        encabezados = {"codigo": ("Código", 80), "nombre": ("Producto", 220),
                       "precio": ("Precio", 110), "stock": ("Stock", 80),
                       "valor": ("Valor total", 130), "tipo": ("Tipo de nodo", 110),
                       "nivel": ("Nivel", 70)}
        for columna in columnas:
            texto, ancho = encabezados[columna]
            self.tabla.heading(columna, text=texto)
            self.tabla.column(columna, width=ancho, anchor="w" if columna == "nombre" else "center")
        self.tabla.tag_configure("par", background="#F7F9FE")
        self.tabla.tag_configure("bajo", background="#FFECEC", foreground="#B42318")
        barra_tabla = ttk.Scrollbar(contenedor_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra_tabla.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra_tabla.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

        # --- Página: lienzo del árbol
        contenedor = tk.Frame(self.paginas["Árbol"], bg=TARJETA)
        contenedor.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.canvas = tk.Canvas(contenedor, bg=TARJETA, highlightthickness=0)
        barra_x = ttk.Scrollbar(contenedor, orient="horizontal", command=self.canvas.xview)
        barra_y = ttk.Scrollbar(contenedor, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=barra_x.set, yscrollcommand=barra_y.set)
        barra_y.pack(side="right", fill="y")
        barra_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.dibujar())
        self.canvas.bind("<MouseWheel>",
                         lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))
        self.canvas.bind("<Shift-MouseWheel>",
                         lambda e: self.canvas.xview_scroll(int(-e.delta / 120), "units"))

        self.cambiar_recorrido("Inorden")
        self.cambiar_vista("Árbol")

    def cambiar_vista(self, nombre):
        self.paginas[nombre].tkraise()
        textos = {"Árbol": ("Estructura del árbol", "Haz clic en un nodo para ver su detalle"),
                  "Tabla": ("Productos", "Haz clic en una fila para ubicarla en el árbol")}
        titulo, pista = textos[nombre]
        self.titulo_vista.config(text=titulo)
        self.pista.config(text=pista)
        for clave, boton in self.botones_vista.items():
            if clave == nombre:
                boton.cambiar_color(AZUL_OSCURO)
            else:
                boton.cambiar_color("#E8EDFB", AZUL_OSCURO)

    # ================================================================== DIBUJO
    def dibujar(self):
        c = self.canvas
        c.delete("all")
        ancho_vis = max(c.winfo_width(), 300)
        alto_vis = max(c.winfo_height(), 200)

        if self.arbol.raiz is None:
            c.create_text(ancho_vis / 2, alto_vis / 2 - 12, text="El árbol está vacío",
                          font=(FUENTE, 15, "bold"), fill=TEXTO)
            c.create_text(ancho_vis / 2, alto_vis / 2 + 16,
                          text="Agrega un producto o carga los datos de ejemplo",
                          font=(FUENTE, 10), fill=TENUE)
            c.configure(scrollregion=(0, 0, ancho_vis, alto_vis))
            return

        # Posición x = orden inorden (así el árbol queda ordenado de izquierda a derecha)
        # Posición y = profundidad del nodo
        orden = self.arbol.inorden()
        indice = {n.codigo: i for i, n in enumerate(orden)}
        ancho_arbol = (len(orden) - 1) * SEP_X
        x_inicial = max(100, (ancho_vis - ancho_arbol) / 2)
        posiciones = {}

        def ubicar(nodo, profundidad):
            if nodo is not None:
                posiciones[nodo.codigo] = (x_inicial + indice[nodo.codigo] * SEP_X,
                                           Y_INICIAL + profundidad * SEP_Y)
                ubicar(nodo.izquierda, profundidad + 1)
                ubicar(nodo.derecha, profundidad + 1)

        ubicar(self.arbol.raiz, 0)
        altura = self.arbol.altura()
        ancho_total = max(ancho_vis, x_inicial + ancho_arbol + 60)
        alto_total = max(alto_vis, Y_INICIAL + (altura - 1) * SEP_Y + 70)

        # Guías de nivel (como en la diapositiva de altura y nivel)
        for k in range(altura):
            y = Y_INICIAL + k * SEP_Y
            c.create_line(16, y, ancho_total - 16, y, fill="#E9ECF5", dash=(6, 4))
            c.create_text(20, y - 13, text=f"Nivel {k + 1}", anchor="w",
                          font=(FUENTE, 9, "bold"), fill="#A3AAC7")

        resaltados, encontrado, actual = self.resaltado

        # Aristas
        for nodo in orden:
            for hijo in (nodo.izquierda, nodo.derecha):
                if hijo is not None:
                    x1, y1 = posiciones[nodo.codigo]
                    x2, y2 = posiciones[hijo.codigo]
                    activa = nodo.codigo in resaltados and hijo.codigo in resaltados
                    c.create_line(x1, y1, x2, y2, fill=NARANJA if activa else "#BAC4DE",
                                  width=4 if activa else 2, capstyle="round")

        # Nodos
        for nodo in orden:
            x, y = posiciones[nodo.codigo]
            relleno, borde = COLORES_NODO[self.arbol.tipo(nodo)]
            color_texto = TEXTO
            grosor = 2
            if nodo.codigo == encontrado:
                relleno, borde, color_texto = MORADO, "#5E1A5C", "white"
            if nodo.codigo in resaltados:
                borde, grosor = NARANJA, 4
            etiqueta = f"nodo_{nodo.codigo}"

            if nodo.codigo == actual:
                c.create_oval(x - RADIO - 9, y - RADIO - 9, x + RADIO + 9, y + RADIO + 9,
                              outline=NARANJA, width=2, dash=(4, 3))
            c.create_oval(x - RADIO + 2, y - RADIO + 4, x + RADIO + 2, y + RADIO + 4,
                          fill="#DFE4F0", outline="")
            c.create_oval(x - RADIO, y - RADIO, x + RADIO, y + RADIO, fill=relleno,
                          outline=borde, width=grosor, tags=(etiqueta,))
            c.create_text(x, y, text=str(nodo.codigo), font=(FUENTE, 10, "bold"),
                          fill=color_texto, tags=(etiqueta,))
            nombre = c.create_text(x, y + RADIO + 12, text=recortar(nodo.nombre, 14),
                                   font=(FUENTE, 8), fill=TENUE, tags=(etiqueta,))
            x1, y1, x2, y2 = c.bbox(nombre)
            fondo = c.create_rectangle(x1 - 3, y1, x2 + 3, y2, fill=TARJETA, outline="", tags=(etiqueta,))
            c.tag_lower(fondo, nombre)
            if nodo.stock < UMBRAL_STOCK_BAJO:
                c.create_oval(x + RADIO - 10, y - RADIO - 2, x + RADIO + 2, y - RADIO + 10,
                              fill=ROJO, outline="white", width=2, tags=(etiqueta,))

            c.tag_bind(etiqueta, "<Button-1>", lambda e, cod=nodo.codigo: self.seleccionar_nodo(cod))
            c.tag_bind(etiqueta, "<Enter>", lambda e: c.config(cursor="hand2"))
            c.tag_bind(etiqueta, "<Leave>", lambda e: c.config(cursor=""))

        c.configure(scrollregion=(0, 0, ancho_total, alto_total))

    def animar_camino(self, camino, encontrado, al_terminar=None):
        """Recorre el camino nodo por nodo para mostrar cómo baja la búsqueda."""
        self.animando = True
        codigos = [n.codigo for n in camino]

        def paso(i):
            self.resaltado = (set(codigos[:i + 1]), None, codigos[i])
            self.dibujar()
            if i + 1 < len(codigos):
                self.after(420, paso, i + 1)
            else:
                self.after(420, finalizar)

        def finalizar():
            self.resaltado = (set(codigos), encontrado, None)
            self.dibujar()
            self.animando = False
            if al_terminar:
                al_terminar()

        if codigos:
            paso(0)
        else:
            finalizar()

    # ================================================================== ACTUALIZACIÓN
    def refrescar(self):
        self.dibujar()
        self._refrescar_tabla()
        self._refrescar_estadisticas()

    def _refrescar_estadisticas(self):
        a = self.arbol
        bajos = len(a.stock_bajo())
        self.estadisticas["peso"].config(text=str(a.peso()))
        self.estadisticas["altura"].config(text=str(a.altura()))
        self.estadisticas["hojas"].config(text=str(len(a.hojas())))
        self.estadisticas["grado"].config(text=str(a.grado_arbol()))
        self.estadisticas["valor"].config(text=moneda(a.valor_total()))
        self.estadisticas["bajo"].config(text=str(bajos), fg=ROJO if bajos else TEXTO)

    def _refrescar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        recorridos = {"Inorden": self.arbol.inorden, "Preorden": self.arbol.preorden,
                      "Postorden": self.arbol.postorden}
        nodos = recorridos[self.tipo_recorrido]()
        for i, n in enumerate(nodos):
            etiqueta = "bajo" if n.stock < UMBRAL_STOCK_BAJO else ("par" if i % 2 else "")
            self.tabla.insert("", "end", iid=str(n.codigo), tags=(etiqueta,), values=(
                n.codigo, n.nombre, moneda(n.precio), n.stock, moneda(n.precio * n.stock),
                self.arbol.tipo(n), self.arbol.nivel(n.codigo)))
        explicacion = {"Inorden": "izquierda → raíz → derecha (queda ordenado por código)",
                       "Preorden": "raíz → izquierda → derecha",
                       "Postorden": "izquierda → derecha → raíz"}
        self.explicacion.config(text=explicacion[self.tipo_recorrido])
        self.secuencia.config(text="  →  ".join(str(n.codigo) for n in nodos) or "(vacío)")

    def cambiar_recorrido(self, nombre):
        self.tipo_recorrido = nombre
        for clave, boton in self.botones_recorrido.items():
            if clave == nombre:
                boton.cambiar_color(AZUL)
            else:
                boton.cambiar_color("#E8EDFB", AZUL_OSCURO)
        self._refrescar_tabla()

    def mostrar_detalle(self, nodo):
        if nodo is None:
            for clave, etiqueta in self.detalle.items():
                etiqueta.config(text="—", fg=NARANJA if clave == "Camino" else TEXTO)
            return
        _, camino = self.arbol.buscar(nodo.codigo)
        padre = camino[-2] if len(camino) > 1 else None
        hijos = [str(h.codigo) for h in (nodo.izquierda, nodo.derecha) if h is not None]
        tipo = self.arbol.tipo(nodo)
        valores = {
            "Tipo de nodo": (tipo, COLORES_NODO[tipo][1]),
            "Nivel": (str(len(camino)), TEXTO),
            "Grado": (f"{self.arbol.grado(nodo)} hijo(s)", TEXTO),
            "Padre": (str(padre.codigo) if padre else "Ninguno (es la raíz)", TEXTO),
            "Hijos": (", ".join(hijos) if hijos else "Ninguno (es hoja)", TEXTO),
            "Stock": (f"{nodo.stock} und" + ("  · bajo" if nodo.stock < UMBRAL_STOCK_BAJO else ""),
                      ROJO if nodo.stock < UMBRAL_STOCK_BAJO else TEXTO),
            "Camino": (" → ".join(str(n.codigo) for n in camino), NARANJA),
        }
        for clave, (texto, color) in valores.items():
            self.detalle[clave].config(text=texto, fg=color)

    def seleccionar_nodo(self, codigo):
        if self.animando:
            return
        nodo, camino = self.arbol.buscar(codigo)
        if nodo is None:
            return
        self.resaltado = ({n.codigo for n in camino}, codigo, None)
        self._llenar_formulario(nodo)
        self.mostrar_detalle(nodo)
        self.dibujar()
        if self.tabla.exists(str(codigo)):
            self.tabla.selection_set(str(codigo))
            self.tabla.see(str(codigo))

    def _al_seleccionar_fila(self, _evento):
        seleccion = self.tabla.selection()
        if seleccion and not self.animando and self.resaltado[1] != int(seleccion[0]):
            self.seleccionar_nodo(int(seleccion[0]))

    # ================================================================== FORMULARIO
    def _llenar_formulario(self, nodo):
        for clave, valor in (("codigo", nodo.codigo), ("nombre", nodo.nombre),
                             ("precio", nodo.precio), ("stock", nodo.stock)):
            self.campos[clave].delete(0, "end")
            self.campos[clave].insert(0, str(valor))

    def limpiar_formulario(self):
        for entrada in self.campos.values():
            entrada.delete(0, "end")
        self.resaltado = (set(), None, None)
        self.mostrar_detalle(None)
        self.tabla.selection_remove(*self.tabla.selection())
        self.dibujar()
        self.campos["codigo"].focus_set()

    def _leer_codigo(self):
        texto = self.campos["codigo"].get().strip()
        if not texto.isdigit() or int(texto) <= 0:
            raise ValueError("El código debe ser un número entero positivo.")
        return int(texto)

    def _leer_producto(self):
        codigo = self._leer_codigo()
        nombre = self.campos["nombre"].get().strip()
        if not nombre:
            raise ValueError("Escribe el nombre del producto.")
        try:
            precio = float(self.campos["precio"].get().strip().replace(".", "").replace(",", "."))
        except ValueError:
            raise ValueError("El precio debe ser un número.")
        stock_texto = self.campos["stock"].get().strip()
        if not stock_texto.isdigit():
            raise ValueError("El stock debe ser un número entero (0 o más).")
        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        return codigo, nombre, precio, int(stock_texto)

    # ================================================================== ACCIONES
    def agregar(self):
        if self.animando:
            return
        try:
            codigo, nombre, precio, stock = self._leer_producto()
        except ValueError as error:
            self.aviso(str(error), "error")
            return
        es_nuevo = self.arbol.insertar(codigo, nombre, precio, stock)
        self._refrescar_tabla()
        self._refrescar_estadisticas()
        nodo, camino = self.arbol.buscar(codigo)

        def terminar():
            self.mostrar_detalle(nodo)
            if es_nuevo:
                self.aviso(f"Producto {codigo} insertado en el nivel {len(camino)} "
                           f"(recorrió {len(camino) - 1} nodo(s) para ubicarse).", "ok")
            else:
                self.aviso(f"El código {codigo} ya existía: se actualizaron sus datos.", "info")

        self.animar_camino(camino, codigo, terminar)

    def buscar(self):
        if self.animando:
            return
        try:
            codigo = self._leer_codigo()
        except ValueError as error:
            self.aviso(str(error), "error")
            return
        nodo, camino = self.arbol.buscar(codigo)

        def terminar():
            if nodo:
                self._llenar_formulario(nodo)
                self.mostrar_detalle(nodo)
                self.tabla.selection_set(str(codigo))
                self.tabla.see(str(codigo))
                self.aviso(f"Encontrado: {nodo.nombre} · {len(camino)} comparación(es) "
                           f"de {self.arbol.peso()} productos.", "ok")
            else:
                self.mostrar_detalle(None)
                self.aviso(f"El código {codigo} no existe (se revisaron {len(camino)} nodo(s)).", "error")

        self.animar_camino(camino, codigo if nodo else None, terminar)

    def eliminar(self):
        if self.animando:
            return
        try:
            codigo = self._leer_codigo()
        except ValueError as error:
            self.aviso(str(error), "error")
            return
        nodo, _ = self.arbol.buscar(codigo)
        if nodo is None:
            self.aviso(f"El código {codigo} no existe en el inventario.", "error")
            return
        casos = {0: "Caso 1: era una hoja, se quitó directamente.",
                 1: "Caso 2: tenía un hijo, el hijo ocupó su lugar.",
                 2: "Caso 3: tenía dos hijos, se reemplazó por su sucesor inorden."}
        caso = casos[self.arbol.grado(nodo)]
        if not messagebox.askyesno("Eliminar producto", f"¿Eliminar '{nodo.nombre}' ({codigo})?"):
            return
        self.arbol.eliminar(codigo)
        self.limpiar_formulario()
        self.refrescar()
        self.aviso(f"Producto {codigo} eliminado. {caso}", "alerta")

    def balancear(self):
        if self.animando or self.arbol.raiz is None:
            return
        antes = self.arbol.altura()
        self.arbol.balancear()
        self.resaltado = (set(), None, None)
        self.mostrar_detalle(None)
        self.refrescar()
        self.aviso(f"Árbol balanceado: la altura pasó de {antes} a {self.arbol.altura()} niveles.", "ok")

    def cargar_ejemplo(self, silencioso=False):
        if self.animando:
            return
        self.arbol.vaciar()
        for producto in DATOS_EJEMPLO:
            self.arbol.insertar(*producto)
        self.resaltado = (set(), None, None)
        self.mostrar_detalle(None)
        self.refrescar()
        if not silencioso:
            self.aviso(f"Se cargaron {len(DATOS_EJEMPLO)} productos de ejemplo.", "info")

    def vaciar(self):
        if self.animando or self.arbol.raiz is None:
            return
        if not messagebox.askyesno("Vaciar árbol", "¿Eliminar todos los productos del inventario?"):
            return
        self.arbol.vaciar()
        self.limpiar_formulario()
        self.refrescar()
        self.aviso("El inventario quedó vacío.", "alerta")


if __name__ == "__main__":
    AplicacionInventario().mainloop()

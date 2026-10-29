# Inventario de Droguería — Árbol Binario de Búsqueda

Taller de **Árboles** · Estructuras de Datos · Universidad Cooperativa de Colombia

## Caso de estudio

Una droguería necesita encontrar sus productos rápidamente por código. En lugar de
recorrer una lista completa (estructura lineal), los productos se guardan en un
**Árbol Binario de Búsqueda (ABB)** ordenado por código: en cada nodo se decide ir a
la izquierda (código menor) o a la derecha (código mayor), así que la búsqueda solo
recorre un camino desde la raíz.

## Ejecutar

```bash
python inventario_arbol.py
```

Solo requiere Python 3 (Tkinter viene incluido).

## Funcionalidades

- **Agregar / actualizar** productos (código, nombre, precio, stock). Si el código ya existe, se actualizan sus datos.
- **Buscar** por código con animación del camino recorrido desde la raíz.
- **Eliminar** cubriendo los 3 casos: nodo hoja, nodo con un hijo y nodo con dos hijos (sucesor inorden).
- **Recorridos** inorden, preorden y postorden.
- **Balancear** el árbol (idea base de los árboles AVL), mostrando la altura antes y después.
- **Estadísticas**: peso, altura, número de hojas, grado del árbol, valor del inventario y productos con stock bajo.
- **Detalle de cada nodo**: tipo (raíz, rama u hoja), nivel, grado, padre, hijos y camino desde la raíz.

## Estructura del código

| Parte | Descripción |
|---|---|
| `Nodo` | Producto con referencias `izquierda` y `derecha` |
| `ArbolInventario` | Lógica del ABB: insertar, buscar, eliminar, recorridos, altura, peso, hojas, grado, balancear |
| `AplicacionInventario` | Interfaz gráfica en Tkinter: formulario, árbol dibujado, tabla y estadísticas |

Colores del árbol (igual que en la clase): raíz amarilla, ramas azules y hojas verdes.

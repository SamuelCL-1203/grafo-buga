# GrafoBuga — Rutas Optimas en Grafos

Aplicacion web en Python/Streamlit que implementa los algoritmos de Dijkstra, Euler (Hierholzer) y Hamilton (Held-Karp DP) para calcular rutas optimas en un grafo de nodos inspirado en la ciudad de Guadalajara de Buga, Colombia.

---

## Ejecucion local

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/grafo-buga.git
cd grafo-buga
```

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicacion
```bash
streamlit run app.py
```

La app se abrira automaticamente en `http://localhost:8501`.

---

## Funcionalidades

| Pestana | Algoritmo | Descripcion |
|---|---|---|
| Dijkstra - Ruta corta | Dijkstra + Min-Heap | Camino mas corto entre dos nodos |
| Euler - Ciclo de aristas | Hierholzer | Recorre todas las aristas exactamente una vez |
| Hamilton - Ciclo de vertices | Held-Karp DP | Visita todos los vertices exactamente una vez (TSP) |
| Pruebas de rendimiento | — | Benchmarks con 5, 10 y 20 nodos |

---

## Complejidades algoritmicas

| Algoritmo | Tiempo | Espacio |
|---|---|---|
| Dijkstra | O((V + E) log V) | O(V) |
| Euler (Hierholzer) | O(E) | O(E) |
| Hamilton (Held-Karp) | O(n2 * 2n) | O(n * 2n) |

---

## Formato de entrada de grafos

Para ingresar un grafo manualmente, usa el formato:
```
NodoA NodoB peso
NodoB NodoC peso
...
```

Ejemplo:
```
Plaza Hospital 5
Hospital Basilica 3
Basilica Terminal 4
Terminal Plaza 8
Plaza Basilica 6
Hospital Terminal 7
```

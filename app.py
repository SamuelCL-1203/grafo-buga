import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import heapq
import time
import random
from functools import lru_cache
import pandas as pd

st.set_page_config(page_title="GrafoBuga", page_icon="🗺️", layout="wide")

st.title("🗺️ GrafoBuga — Rutas Óptimas")
st.caption("Teoría de Grafos aplicada a Guadalajara de Buga")

GRAFO_BUGA = {
    "Plaza_Central":  {"Barrio_Paraiso": 3, "Hospital": 5, "Terminal": 8},
    "Barrio_Paraiso": {"Plaza_Central": 3,  "Parque": 2,   "Terminal": 6},
    "Hospital":       {"Plaza_Central": 5,  "Parque": 4,   "Basilica": 3},
    "Parque":         {"Barrio_Paraiso": 2, "Hospital": 4, "Basilica": 1, "Terminal": 5},
    "Basilica":       {"Hospital": 3,       "Parque": 1,   "Terminal": 4},
    "Terminal":       {"Plaza_Central": 8,  "Barrio_Paraiso": 6, "Parque": 5, "Basilica": 4},
}


def dijkstra(grafo, origen, destino):
    dist = {nodo: float('inf') for nodo in grafo}
    dist[origen] = 0
    prev = {nodo: None for nodo in grafo}
    heap = [(0, origen)]

    while heap:
        costo, u = heapq.heappop(heap)
        if costo > dist[u]:
            continue
        for v, peso in grafo[u].items():
            if dist[u] + peso < dist[v]:
                dist[v] = dist[u] + peso
                prev[v] = u
                heapq.heappush(heap, (dist[v], v))

    camino = []
    nodo = destino
    while nodo is not None:
        camino.append(nodo)
        nodo = prev[nodo]
    camino.reverse()

    if not camino or camino[0] != origen:
        return None, float('inf')
    return camino, dist[destino]


def tiene_ciclo_euler(G):
    if not nx.is_connected(G):
        return False, "El grafo no es conexo."
    impares = [n for n in G.nodes() if G.degree(n) % 2 != 0]
    if impares:
        return False, f"Nodos con grado impar: {impares}"
    return True, "OK"


def ciclo_euler(G, inicio):
    g_copy = nx.MultiGraph(G)
    pila = [inicio]
    circuito = []
    while pila:
        v = pila[-1]
        if g_copy.degree(v) > 0:
            u = list(g_copy.neighbors(v))[0]
            pila.append(u)
            g_copy.remove_edge(v, u)
        else:
            circuito.append(pila.pop())
    return circuito


def ciclo_hamiltoniano(grafo):
    nodos = list(grafo.keys())
    n = len(nodos)
    idx = {nodo: i for i, nodo in enumerate(nodos)}
    INF = float('inf')

    dist_m = [[INF] * n for _ in range(n)]
    for u in grafo:
        for v, w in grafo[u].items():
            dist_m[idx[u]][idx[v]] = w

    FULL = (1 << n) - 1

    @lru_cache(maxsize=None)
    def dp(mask, pos):
        if mask == FULL:
            return dist_m[pos][0] if dist_m[pos][0] < INF else INF
        best = INF
        for nxt in range(n):
            if mask & (1 << nxt) or dist_m[pos][nxt] == INF:
                continue
            val = dist_m[pos][nxt] + dp(mask | (1 << nxt), nxt)
            if val < best:
                best = val
        return best

    costo = dp(1, 0)
    dp.cache_clear()
    if costo == INF:
        return None, INF

    camino = [nodos[0]]
    mask, pos = 1, 0
    for _ in range(n - 1):
        mejor_nxt, mejor_val = -1, INF
        for nxt in range(n):
            if mask & (1 << nxt) or dist_m[pos][nxt] == INF:
                continue
            val = dist_m[pos][nxt] + dp(mask | (1 << nxt), nxt)
            if val < mejor_val:
                mejor_val = val
                mejor_nxt = nxt
        if mejor_nxt == -1:
            break
        camino.append(nodos[mejor_nxt])
        mask |= (1 << mejor_nxt)
        pos = mejor_nxt

    camino.append(nodos[0])
    dp.cache_clear()
    return camino, costo


def dibujar_grafo(G, camino=None):
    fig, ax = plt.subplots(figsize=(7, 5))
    pos = nx.spring_layout(G, seed=42)

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#aaa', width=1.5)

    if camino and len(camino) > 1:
        aristas = list(zip(camino[:-1], camino[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=aristas, ax=ax,
                               edge_color='#e63946', width=3)

    colores = ['#457b9d' if (camino and n in camino) else '#a8dadc' for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colores, node_size=600)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_weight='bold')
    pesos = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos, ax=ax, font_size=7)

    ax.axis('off')
    plt.tight_layout()
    return fig


def grafo_a_nx(grafo):
    G = nx.Graph()
    for u, vecinos in grafo.items():
        for v, w in vecinos.items():
            G.add_edge(u, v, weight=w)
    return G


def grafo_aleatorio(n):
    random.seed(42)
    nodos = [f"N{i}" for i in range(n)]
    g = {n: {} for n in nodos}
    for i in range(n - 1):
        w = random.randint(1, 20)
        g[nodos[i]][nodos[i+1]] = w
        g[nodos[i+1]][nodos[i]] = w
    for i in range(n):
        for j in range(i + 2, n):
            if random.random() < 0.5:
                w = random.randint(1, 20)
                g[nodos[i]][nodos[j]] = w
                g[nodos[j]][nodos[i]] = w
    return g


G = grafo_a_nx(GRAFO_BUGA)
nodos = sorted(GRAFO_BUGA.keys())

tab1, tab2, tab3, tab4 = st.tabs([
    "Dijkstra — Ruta corta",
    "Euler — Ciclo de aristas",
    "Hamilton — Ciclo de vértices",
    "Pruebas de rendimiento"
])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ruta más corta entre dos puntos")
        origen  = st.selectbox("Nodo origen", nodos)
        destino = st.selectbox("Nodo destino", nodos, index=1)
        if st.button("Calcular ruta"):
            if origen == destino:
                st.warning("El origen y el destino son el mismo nodo.")
            else:
                t0 = time.perf_counter()
                camino, costo = dijkstra(GRAFO_BUGA, origen, destino)
                t1 = time.perf_counter()
                if camino is None:
                    st.error("No existe ruta entre esos nodos.")
                else:
                    st.success(f"Ruta: {' → '.join(camino)}")
                    st.info(f"Costo total: {costo} | Tiempo: {(t1-t0)*1000:.3f} ms")
                    st.session_state['camino_dijk'] = camino
    with col2:
        fig = dibujar_grafo(G, st.session_state.get('camino_dijk', []))
        st.pyplot(fig)
        plt.close(fig)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ciclo que recorre todas las aristas")
        inicio = st.selectbox("Nodo de inicio", nodos)
        if st.button("Buscar ciclo de Euler"):
            valido, msg = tiene_ciclo_euler(G)
            if not valido:
                st.error(f"No existe ciclo de Euler: {msg}")
                st.info("Todos los nodos deben tener grado par.")
            else:
                t0 = time.perf_counter()
                ciclo = ciclo_euler(G, inicio)
                t1 = time.perf_counter()
                st.success(f"Ciclo: {' → '.join(ciclo)}")
                st.info(f"Aristas recorridas: {len(ciclo)-1} | Tiempo: {(t1-t0)*1000:.3f} ms")
                st.session_state['camino_euler'] = ciclo

        st.markdown("**Grados de los nodos:**")
        df_grados = pd.DataFrame(
            [(n, G.degree(n), "Par" if G.degree(n) % 2 == 0 else "Impar")
             for n in nodos],
            columns=["Nodo", "Grado", "Estado"]
        )
        st.dataframe(df_grados, hide_index=True)
    with col2:
        fig = dibujar_grafo(G, st.session_state.get('camino_euler', []))
        st.pyplot(fig)
        plt.close(fig)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ciclo que visita todos los vértices")
        st.caption(f"Nodos en el grafo: {len(nodos)}")
        if st.button("Calcular ciclo hamiltoniano"):
            with st.spinner("Calculando..."):
                t0 = time.perf_counter()
                ciclo_h, costo_h = ciclo_hamiltoniano(GRAFO_BUGA)
                t1 = time.perf_counter()
            if ciclo_h is None:
                st.error("No existe ciclo hamiltoniano.")
            else:
                st.success(f"Ciclo: {' → '.join(ciclo_h)}")
                st.info(f"Costo: {costo_h} | Tiempo: {(t1-t0)*1000:.2f} ms")
                st.session_state['camino_ham'] = ciclo_h
    with col2:
        fig = dibujar_grafo(G, st.session_state.get('camino_ham', []))
        st.pyplot(fig)
        plt.close(fig)

with tab4:
    st.subheader("Pruebas de rendimiento con grafos aleatorios")
    if st.button("Ejecutar pruebas"):
        resultados = []
        for n in [5, 10, 20]:
            g = grafo_aleatorio(n)
            ns = list(g.keys())

            t0 = time.perf_counter()
            dijkstra(g, ns[0], ns[-1])
            t_dijk = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            ciclo_hamiltoniano(g)
            t_ham = (time.perf_counter() - t0) * 1000

            resultados.append({
                "Nodos": n,
                "Dijkstra (ms)": f"{t_dijk:.4f}",
                "Hamilton (ms)": f"{t_ham:.2f}",
            })

        st.dataframe(pd.DataFrame(resultados), hide_index=True)

"""
salida.py — Módulo de Salida y Reportes
Proyecto: Particionamiento Óptimo de Sistemas Distribuidos
Autor: Isa

Este módulo recibe la solución del algoritmo de particionamiento
y genera reportes detallados con métricas, aristas cortadas y resultados.
"""

import time
import csv
import os
from typing import List, Dict, Tuple


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL: calcular el costo de corte de una partición
# ─────────────────────────────────────────────────────────────

def calcular_corte(matriz: List[List[float]], particion: List[int]) -> float:
    """
    Calcula el costo total de corte de una partición dada.

    Parámetros:
        matriz    -- Matriz de dependencias n×n (lista de listas)
        particion -- Lista donde particion[i] indica el grupo del componente i
                     Ejemplo: [0, 0, 1, 1] = componentes 0 y 1 en grupo 0,
                                              componentes 2 y 3 en grupo 1

    Retorna:
        El costo total (suma de pesos de aristas entre grupos distintos)
    """
    n = len(matriz)
    costo = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            if particion[i] != particion[j]:
                costo += matriz[i][j]
    return costo


# ─────────────────────────────────────────────────────────────
# FUNCIÓN: obtener las aristas cortadas (los pares entre grupos)
# ─────────────────────────────────────────────────────────────

def obtener_aristas_cortadas(
    matriz: List[List[float]],
    particion: List[int],
    nombres: List[str] = None
) -> List[Dict]:
    """
    Obtiene la lista detallada de aristas que cruzan entre particiones.

    Parámetros:
        matriz    -- Matriz de dependencias n×n
        particion -- Lista de asignaciones de grupo por componente
        nombres   -- Nombres opcionales de los componentes (ej: ["A", "B", "C"])

    Retorna:
        Lista de diccionarios con claves: componente_i, componente_j, grupo_i, grupo_j, peso
    """
    n = len(matriz)
    if nombres is None:
        nombres = [f"C{i}" for i in range(n)]

    aristas = []
    for i in range(n):
        for j in range(i + 1, n):
            if particion[i] != particion[j] and matriz[i][j] > 0:
                aristas.append({
                    "componente_i": nombres[i],
                    "componente_j": nombres[j],
                    "grupo_i":      particion[i],
                    "grupo_j":      particion[j],
                    "peso":         matriz[i][j]
                })

    # Ordenar de mayor a menor peso para ver primero las conexiones más costosas
    aristas.sort(key=lambda x: x["peso"], reverse=True)
    return aristas


# ─────────────────────────────────────────────────────────────
# FUNCIÓN: agrupar componentes por partición
# ─────────────────────────────────────────────────────────────

def agrupar_componentes(
    particion: List[int],
    nombres: List[str] = None
) -> Dict[int, List[str]]:
    """
    Organiza los componentes en un diccionario {grupo: [lista de componentes]}.

    Parámetros:
        particion -- Lista de asignaciones de grupo
        nombres   -- Nombres opcionales de los componentes

    Retorna:
        Diccionario {número_de_grupo: [nombres de componentes en ese grupo]}
    """
    n = len(particion)
    if nombres is None:
        nombres = [f"C{i}" for i in range(n)]

    grupos = {}
    for i, grupo in enumerate(particion):
        if grupo not in grupos:
            grupos[grupo] = []
        grupos[grupo].append(nombres[i])

    return grupos


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL: generar reporte completo en consola
# ─────────────────────────────────────────────────────────────

def generar_reporte(
    matriz: List[List[float]],
    particion: List[int],
    nombres: List[str] = None,
    tiempo_ejecucion: float = None,
    nombre_algoritmo: str = "Algoritmo",
    k: int = None
):
    """
    Imprime en consola un reporte completo con todos los resultados.

    Parámetros:
        matriz            -- Matriz de dependencias n×n
        particion         -- Lista de asignaciones de grupo
        nombres           -- Nombres de los componentes (opcional)
        tiempo_ejecucion  -- Tiempo en segundos que tardó el algoritmo (opcional)
        nombre_algoritmo  -- Nombre del algoritmo usado (para el reporte)
        k                 -- Número de particiones (se infiere si no se pasa)
    """
    n = len(matriz)
    if nombres is None:
        nombres = [f"C{i}" for i in range(n)]
    if k is None:
        k = max(particion) + 1

    separador = "=" * 60

    print(separador)
    print(f"  REPORTE DE PARTICIONAMIENTO ÓPTIMO")
    print(f"  Algoritmo: {nombre_algoritmo}")
    print(separador)

    # ── 1. Información general ──────────────────────────────
    print(f"\n📊 INFORMACIÓN GENERAL")
    print(f"   Número de componentes : {n}")
    print(f"   Número de particiones : {k}")
    if tiempo_ejecucion is not None:
        print(f"   Tiempo de ejecución   : {tiempo_ejecucion:.6f} segundos")

    # ── 2. Partición encontrada ─────────────────────────────
    print(f"\n📦 PARTICIÓN ENCONTRADA")
    grupos = agrupar_componentes(particion, nombres)
    for g in sorted(grupos.keys()):
        componentes_str = ", ".join(grupos[g])
        print(f"   Grupo {g + 1}: {{ {componentes_str} }}")

    # ── 3. Función de corte ─────────────────────────────────
    costo = calcular_corte(matriz, particion)
    print(f"\n✂️  FUNCIÓN DE CORTE")
    print(f"   Costo total del corte : {costo:.2f}")

    # ── 4. Aristas cortadas ─────────────────────────────────
    aristas = obtener_aristas_cortadas(matriz, particion, nombres)
    print(f"\n🔗 ARISTAS CORTADAS ({len(aristas)} aristas entre grupos distintos)")
    if aristas:
        print(f"   {'Componente A':<14} {'Componente B':<14} {'Grupo A':>7} {'Grupo B':>7} {'Peso':>8}")
        print(f"   {'-'*14} {'-'*14} {'-'*7} {'-'*7} {'-'*8}")
        for a in aristas:
            print(
                f"   {a['componente_i']:<14} {a['componente_j']:<14} "
                f"{a['grupo_i'] + 1:>7} {a['grupo_j'] + 1:>7} {a['peso']:>8.2f}"
            )
    else:
        print("   (Ninguna — todos los componentes están en el mismo grupo)")

    print(f"\n{separador}\n")


# ─────────────────────────────────────────────────────────────
# FUNCIÓN: guardar resultados en CSV
# ─────────────────────────────────────────────────────────────

def guardar_resultados_csv(
    matriz: List[List[float]],
    particion: List[int],
    nombres: List[str] = None,
    tiempo_ejecucion: float = None,
    nombre_algoritmo: str = "Algoritmo",
    ruta_salida: str = "resultados.csv"
):
    """
    Guarda los resultados del particionamiento en un archivo CSV.

    Parámetros:
        matriz            -- Matriz de dependencias n×n
        particion         -- Lista de asignaciones de grupo
        nombres           -- Nombres de los componentes (opcional)
        tiempo_ejecucion  -- Tiempo en segundos
        nombre_algoritmo  -- Nombre del algoritmo
        ruta_salida       -- Ruta del archivo CSV a generar
    """
    n = len(matriz)
    if nombres is None:
        nombres = [f"C{i}" for i in range(n)]

    costo = calcular_corte(matriz, particion)
    aristas = obtener_aristas_cortadas(matriz, particion, nombres)

    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Encabezado de resumen
        writer.writerow(["=== RESUMEN ==="])
        writer.writerow(["Algoritmo", nombre_algoritmo])
        writer.writerow(["Componentes", n])
        writer.writerow(["Particiones (k)", max(particion) + 1])
        writer.writerow(["Costo de corte", f"{costo:.2f}"])
        if tiempo_ejecucion is not None:
            writer.writerow(["Tiempo (s)", f"{tiempo_ejecucion:.6f}"])
        writer.writerow([])

        # Partición
        writer.writerow(["=== PARTICIÓN ==="])
        writer.writerow(["Componente", "Grupo asignado"])
        for i, g in enumerate(particion):
            writer.writerow([nombres[i], g + 1])
        writer.writerow([])

        # Aristas cortadas
        writer.writerow(["=== ARISTAS CORTADAS ==="])
        writer.writerow(["Componente A", "Componente B", "Grupo A", "Grupo B", "Peso"])
        for a in aristas:
            writer.writerow([
                a["componente_i"], a["componente_j"],
                a["grupo_i"] + 1, a["grupo_j"] + 1,
                f"{a['peso']:.2f}"
            ])

    print(f"✅ Resultados guardados en: {ruta_salida}")


# ─────────────────────────────────────────────────────────────
# FUNCIÓN: comparar múltiples algoritmos (para resultados experimentales)
# ─────────────────────────────────────────────────────────────

def comparar_algoritmos(resultados: List[Dict]):
    """
    Muestra una tabla comparativa de múltiples algoritmos ejecutados sobre el mismo dataset.

    Parámetros:
        resultados -- Lista de diccionarios, cada uno con:
                      { "algoritmo": str, "costo": float, "tiempo": float,
                        "particion": list, "es_optimo": bool (opcional) }
    """
    print("=" * 70)
    print("  COMPARACIÓN DE ALGORITMOS")
    print("=" * 70)
    print(f"  {'Algoritmo':<25} {'Costo de corte':>15} {'Tiempo (s)':>12} {'Óptimo':>8}")
    print(f"  {'-'*25} {'-'*15} {'-'*12} {'-'*8}")

    mejor_costo = min(r["costo"] for r in resultados)

    for r in resultados:
        es_optimo = "✓" if abs(r["costo"] - mejor_costo) < 1e-9 else " "
        tiempo_str = f"{r['tiempo']:.6f}" if r.get("tiempo") is not None else "N/A"
        print(
            f"  {r['algoritmo']:<25} {r['costo']:>15.2f} {tiempo_str:>12} {es_optimo:>8}"
        )

    print("=" * 70)
    print(f"\n  Mejor costo encontrado: {mejor_costo:.2f}\n")


# ─────────────────────────────────────────────────────────────
# EJEMPLO DE USO — puedes ejecutar este archivo directamente
# para ver cómo funciona con un dataset de ejemplo
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # Dataset de ejemplo: 6 componentes, matriz 6×6
    # (Simulando un sistema con microservicios A, B, C, D, E, F)
    nombres_ejemplo = ["A", "B", "C", "D", "E", "F"]

    matriz_ejemplo = [
        # A    B    C    D    E    F
        [0,   10,   2,   0,   0,   1],   # A
        [10,   0,   8,   1,   0,   0],   # B
        [2,    8,   0,   0,   3,   0],   # C
        [0,    1,   0,   0,   9,   7],   # D
        [0,    0,   3,   9,   0,  12],   # E
        [1,    0,   0,   7,  12,   0],   # F
    ]

    # Partición óptima encontrada por el algoritmo de tu compañero
    # (A,B,C en grupo 0) y (D,E,F en grupo 1)
    particion_ejemplo = [0, 0, 0, 1, 1, 1]

    # Simular tiempo de ejecución
    inicio = time.time()
    tiempo = time.time() - inicio + 0.003412  # simulado

    # ── Generar reporte en consola ──
    generar_reporte(
        matriz=matriz_ejemplo,
        particion=particion_ejemplo,
        nombres=nombres_ejemplo,
        tiempo_ejecucion=tiempo,
        nombre_algoritmo="Búsqueda exhaustiva",
        k=2
    )

    # ── Guardar en CSV ──
    guardar_resultados_csv(
        matriz=matriz_ejemplo,
        particion=particion_ejemplo,
        nombres=nombres_ejemplo,
        tiempo_ejecucion=tiempo,
        nombre_algoritmo="Búsqueda exhaustiva",
        ruta_salida="resultados_ejemplo.csv"
    )

    # ── Comparar con otra partición (heurística) ──
    particion_heuristica = [0, 0, 1, 1, 1, 0]
    costo_heuristica = calcular_corte(matriz_ejemplo, particion_heuristica)

    comparar_algoritmos([
        {"algoritmo": "Búsqueda exhaustiva",  "costo": calcular_corte(matriz_ejemplo, particion_ejemplo), "tiempo": 0.003412},
        {"algoritmo": "Heurística greedy",    "costo": costo_heuristica,                                 "tiempo": 0.000521},
    ])
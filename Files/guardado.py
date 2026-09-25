import json
import os

from Files.entidades import Jugador, Monstruo
from Files.objetos import generar_objeto

ARCHIVO_GUARDADO = "partida_guardada.json"

def serializar_monstruo(monstruo):
    return {
        "nombre": monstruo.nombre,
        "vida_max": monstruo.vida_max,
        "vida_actual": monstruo.vida_actual,
        "ataque_base": monstruo.ataque_base,
        "reflejos": monstruo.reflejos,
        "velocidad_base": monstruo.velocidad_base,
        "etiquetas": monstruo.etiquetas,
        "habilidades": monstruo.habilidades
    }

def deserializar_monstruo(datos):
    monstruo = Monstruo(
        nombre=datos["nombre"],
        vida=datos["vida_max"],
        ataque_base=datos["ataque_base"],
        reflejos=datos["reflejos"],
        velocidad=datos["velocidad_base"],
        etiquetas=datos["etiquetas"],
        habilidades=datos.get("habilidades", [])
    )
    monstruo.vida_actual = datos["vida_actual"]
    return monstruo

def serializar_inventario(inventario):
    return [
        item.nombre if hasattr(item, "nombre") else item
        for item in inventario
    ]

def guardar_partida(jugador):
    print("\n[Guardando partida...]")

    equipo_nombres = {}
    for slot, item in jugador.equipo.items():
        equipo_nombres[slot] = item.nombre if item else None

    datos_guardado = {
        "jugador": {
            "nombre": jugador.nombre,
            "aliados_obtenidos": jugador.aliados_obtenidos,
            "equipo_aliado": [serializar_monstruo(m) for m in jugador.equipo_aliado],
            "caja_aliados": [serializar_monstruo(m) for m in jugador.caja_aliados],
            "inventario": serializar_inventario(jugador.inventario),
            "eventos_desbloqueados": jugador.eventos_desbloqueados,
            "equipo": equipo_nombres
        }
    }

    ruta = os.path.join(os.path.dirname(__file__), ARCHIVO_GUARDADO)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos_guardado, archivo, indent=4, ensure_ascii=False)

    print("¡Partida guardada con éxito!")

def cargar_partida():
    ruta = os.path.join(os.path.dirname(__file__), ARCHIVO_GUARDADO)
    if not os.path.exists(ruta):
        print("\nNo se encontró ninguna partida guardada.")
        return None

    print("\n[Cargando partida...]")
    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    datos_jugador = datos["jugador"]

    jugador = Jugador(datos_jugador["nombre"])
    jugador.aliados_obtenidos = datos_jugador.get("aliados_obtenidos", [])
    jugador.eventos_desbloqueados = datos_jugador.get("eventos_desbloqueados", [])

    jugador.inventario = []
    for nombre in datos_jugador.get("inventario", []):
        if isinstance(nombre, str):
            obj = generar_objeto(nombre)
            if obj is not None:
                jugador.inventario.append(obj)

    if "equipo" in datos_jugador:
        for slot, nombre_item in datos_jugador["equipo"].items():
            if nombre_item:
                jugador.equipo[slot] = generar_objeto(nombre_item)
            else:
                jugador.equipo[slot] = None

    jugador.actualizar_stats()

    jugador.equipo_aliado = [deserializar_monstruo(m) for m in datos_jugador.get("equipo_aliado", [])]
    jugador.caja_aliados = [deserializar_monstruo(m) for m in datos_jugador.get("caja_aliados", [])]

    print("¡Partida cargada con éxito!")
    return jugador
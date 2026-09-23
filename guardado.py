import json
import os
from entidades import Jugador, Monstruo

ARCHIVO_GUARDADO = "partida_guardada.json"

def serializar_monstruo(monstruo):
    """Convierte un objeto Monstruo en un diccionario simple para el JSON"""
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
    """Convierte un diccionario JSON de vuelta a un objeto Monstruo"""
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

def guardar_partida(jugador):
    print("\n[Guardando partida...]")
    datos_guardado = {
        "jugador": {
            "nombre": jugador.nombre,
            "aliados_obtenidos": jugador.aliados_obtenidos,
            "equipo_aliado": [serializar_monstruo(m) for m in jugador.equipo_aliado],
            "caja_aliados": [serializar_monstruo(m) for m in jugador.caja_aliados]
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
    
    # Recreamos al jugador
    jugador = Jugador(datos_jugador["nombre"])
    jugador.aliados_obtenidos = datos_jugador.get("aliados_obtenidos", [])
    
    # Recreamos a sus monstruos con las stats exactas
    jugador.equipo_aliado = [deserializar_monstruo(m) for m in datos_jugador.get("equipo_aliado", [])]
    jugador.caja_aliados = [deserializar_monstruo(m) for m in datos_jugador.get("caja_aliados", [])]
    
    print("¡Partida cargada con éxito!")
    return jugador
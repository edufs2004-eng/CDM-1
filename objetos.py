import json
import os

class Objeto:
    def __init__(self, nombre, tipo_slot, bonos_stats=None):
        self.nombre = nombre
        self.tipo_slot = tipo_slot
        self.bonos_stats = bonos_stats or {}

def cargar_objetos():
    ruta = os.path.join(os.path.dirname(__file__), "data", "datos_objetos.json")
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {}

def generar_objeto(nombre_objeto):
    datos = cargar_objetos()
    if not datos:
        return None

    if nombre_objeto not in datos:
        return None

    item = datos[nombre_objeto]
    return Objeto(
        nombre=item.get("nombre", nombre_objeto),
        tipo_slot=item.get("tipo_slot", "Extra"),
        bonos_stats=item.get("bonos_stats", {})
    )
import json
import os

def cargar_base_objetos():
    ruta = os.path.join(os.path.dirname(__file__), 'datos_objetos.json')
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print("Error: No se encontró datos_objetos.json")
        return {}

OBJETOS_DB = cargar_base_objetos()

class Equipamiento:
    def __init__(self, nombre, tipo_slot, bonos_stats):
        self.nombre = nombre
        self.tipo_slot = tipo_slot
        self.bonos_stats = bonos_stats

def generar_objeto(nombre_objeto):
    """Busca el objeto en la DB y retorna una instancia de Equipamiento"""
    if nombre_objeto not in OBJETOS_DB:
        return None
        
    datos = OBJETOS_DB[nombre_objeto]
    return Equipamiento(nombre_objeto, datos["tipo"], datos["bonos"])
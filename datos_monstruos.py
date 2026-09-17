import random
import json
import os
from entidades import Monstruo

def cargar_base_datos():
    """Lee el archivo JSON y lo carga en memoria"""
    ruta_archivo = os.path.join(os.path.dirname(__file__), 'datos_monstruos.json')
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print("Error: No se encontró el archivo datos_monstruos.json")
        return {}

# Cargamos la base de datos al iniciar el módulo
MONSTRUOS_DB = cargar_base_datos()

def generar_monstruo(nombre_monstruo):
    """Busca al monstruo en el JSON y crea una instancia con stats aleatorios"""
    if nombre_monstruo not in MONSTRUOS_DB:
        print(f"Error: El monstruo '{nombre_monstruo}' no existe en la base de datos.")
        return None
        
    datos = MONSTRUOS_DB[nombre_monstruo]
    
    vida_aleatoria = random.randint(datos["vida"][0], datos["vida"][1])
    ataque_aleatorio = random.randint(datos["ataque"][0], datos["ataque"][1])
    reflejos_aleatorios = random.randint(datos["reflejos"][0], datos["reflejos"][1])
    vel_aleatoria = random.randint(datos["velocidad"][0], datos["velocidad"][1])
    
    nuevo_monstruo = Monstruo(
        nombre=nombre_monstruo,
        vida=vida_aleatoria,
        ataque_base=ataque_aleatorio,
        reflejos=reflejos_aleatorios,
        velocidad=vel_aleatoria,
        etiquetas=datos["etiquetas"].copy(),
        habilidades=datos["habilidades"].copy()
    )
    
    return nuevo_monstruo
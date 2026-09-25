import json
import os
import random
from Files.entidades import Monstruo

def cargar_base_monstruos():
    ruta = os.path.join(os.path.dirname(__file__), 'datos_monstruos.json')
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print("Error: No se encontró datos_monstruos.json")
        return {}

MONSTRUOS_DB = cargar_base_monstruos()

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
    
    # Generamos su personalidad única (porcentajes fijos para este individuo)
    ia_generada = {}
    if "probabilidades_ia" in datos:
        for hab, intervalo in datos["probabilidades_ia"].items():
            ia_generada[hab] = random.randint(intervalo[0], intervalo[1])
    
    nuevo_monstruo = Monstruo(
        nombre=nombre_monstruo,
        vida=vida_aleatoria,
        ataque_base=ataque_aleatorio,
        reflejos=reflejos_aleatorios,
        velocidad=vel_aleatoria,
        etiquetas=datos["etiquetas"].copy(),
        habilidades=datos.get("habilidades", []).copy(),
        probabilidades_ia=ia_generada
    )
    
    return nuevo_monstruo
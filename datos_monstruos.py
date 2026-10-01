import json
import os
import random
from entidades import Monstruo

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
    armadura_aleatoria = random.randint(*datos.get("armadura", [0, 0]))
    
    # Cada monstruo conserva sus probabilidades IA sorteadas al nacer.
    ia_generada = {}
    if "probabilidades_ia" in datos:
        for hab, intervalo in datos["probabilidades_ia"].items():
            minimo, maximo = map(float, intervalo)
            if maximo > 1:
                minimo /= 100
                maximo /= 100
            ia_generada[hab] = random.uniform(minimo, maximo)

    etiquetas = datos["etiquetas"].copy()
    if "Gigante" not in etiquetas and "Titánico" not in etiquetas and "Normal" not in etiquetas:
        etiquetas.append("Normal")
    
    nuevo_monstruo = Monstruo(
        nombre=nombre_monstruo,
        vida=vida_aleatoria,
        ataque_base=ataque_aleatorio,
        reflejos=reflejos_aleatorios,
        velocidad=vel_aleatoria,
        etiquetas=etiquetas,
        habilidades=datos.get("habilidades", []).copy(),
        probabilidades_ia=ia_generada,
        armadura=armadura_aleatoria,
        peligrosidad=datos.get("peligrosidad"),
        datos_fase=datos.get("fases", {}).copy(),
        terreno=datos.get("terreno")
    )
    
    return nuevo_monstruo
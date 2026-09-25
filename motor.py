import math
import random
import time
from habilidades import avanzar_estado_combate, reducir_cooldowns

def calcular_orden_turnos(combatientes, estado_combate=None):
    print("\n--- CALCULANDO ORDEN DE TURNOS ---")
    time.sleep(0.5)
    
    # Solo tomamos a los vivos y NO aturdidos para el cálculo
    activos = [c for c in combatientes if c.vida_actual > 0]
    
    if not activos:
        return [] # Si todos están aturdidos/muertos, no hay acciones

    avanzar_estado_combate(estado_combate)
    for combatiente in activos:
        combatiente.vida_turno_anterior = combatiente.vida_actual
        reiniciar_contadores = getattr(combatiente, "reiniciar_contadores_ronda", None)
        if reiniciar_contadores:
            reiniciar_contadores()
    reducir_cooldowns(activos)
    for combatiente in activos:
        procesar_estados = getattr(combatiente, "procesar_estados_ronda", None)
        if procesar_estados:
            procesar_estados()
    
    # Usamos velocidad_actual en vez de la base
    min_vel = min(c.velocidad_actual for c in activos)
    if min_vel <= 0: min_vel = 1 # Seguridad matemática
    
    acciones_turno = []
    
    for personaje in activos:
        vel_actual = personaje.velocidad_actual
        
        acciones_turno.append({
            "nombre": personaje.nombre, 
            "iniciativa": vel_actual,
            "objeto": personaje
        })
        
        while True:
            vel_actual = math.ceil(vel_actual / 2) 
            
            if vel_actual <= min_vel:
                break
                
            acciones_turno.append({
                "nombre": personaje.nombre, 
                "iniciativa": vel_actual,
                "objeto": personaje
            })

    acciones_turno.sort(
        key=lambda x: (x["iniciativa"], x["objeto"].reflejos, random.random()),
        reverse=True
    )
    return acciones_turno
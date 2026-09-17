import math
import random
import time

def calcular_orden_turnos(combatientes):
    print("\n--- CALCULANDO ORDEN DE TURNOS ---")
    time.sleep(0.5)
    
    # Solo tomamos a los vivos y NO aturdidos para el cálculo
    activos = [c for c in combatientes if c.vida_actual > 0 and getattr(c, 'aturdido_turnos', 0) <= 0]
    
    if not activos:
        return [] # Si todos están aturdidos/muertos, no hay acciones
    
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

    acciones_turno.sort(key=lambda x: (x["iniciativa"], random.random()), reverse=True)
    return acciones_turno
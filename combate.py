import time
import random
from motor import calcular_orden_turnos

def filtrar_objetivos_validos(posibles_objetivos):
    vivos = [obj for obj in posibles_objetivos if obj.vida_actual > 0]
    if not vivos: return []
    
    cuerpo_a_cuerpo = [obj for obj in vivos if "Ataque a distancia" not in obj.etiquetas]
    if len(cuerpo_a_cuerpo) > 0: return cuerpo_a_cuerpo
    else: return vivos

def turno_jugador_o_aliado(atacante, enemigos_vivos, estado_combate):
    while True:
        print(f"\n¿Qué hará {atacante.nombre}? (Terreno: {estado_combate['terreno']})")
        print("1. Atacar")
        print("2. Habilidad")
        print("3. Pasar turno")
        
        opcion = input("Elige una opción (1-3): ")
        
        if opcion == "1":
            objetivos_validos = filtrar_objetivos_validos(enemigos_vivos)
            print("\nSelecciona un objetivo:")
            for i, enemigo in enumerate(objetivos_validos):
                print(f"{i + 1}. {enemigo.nombre} (Vida: {enemigo.vida_actual}/{enemigo.vida_max})")
            
            try:
                seleccion = int(input("Número del objetivo: ")) - 1
                if 0 <= seleccion < len(objetivos_validos):
                    objetivo = objetivos_validos[seleccion]
                    atacante.atacar(objetivo)
                    break
                else: print("Selección inválida.")
            except ValueError: print("Ingresa un número.")
            
        elif opcion == "2":
            if not atacante.habilidades:
                print(f"{atacante.nombre} no tiene habilidades activas.")
                continue
                
            print("\nHabilidades disponibles:")
            for i, hab in enumerate(atacante.habilidades):
                print(f"{i + 1}. {hab}")
            print(f"{len(atacante.habilidades) + 1}. Cancelar")
            
            try:
                sel_hab = int(input("Selecciona habilidad: ")) - 1
                if sel_hab == len(atacante.habilidades): continue
                
                habilidad_elegida = atacante.habilidades[sel_hab]
                
                # LÓGICA DE HABILIDAD: TSUNAMI
                if habilidad_elegida == "Tsunami":
                    print(f"\n¡{atacante.nombre} invoca un TSUNAMI!")
                    print("¡El terreno de combate ha cambiado a HÍBRIDO!")
                    estado_combate["terreno"] = "Híbrido"
                    # Eliminamos la habilidad para que sea de uso único
                    atacante.habilidades.remove("Tsunami")
                    time.sleep(1)
                    break
                else:
                    print("Esta habilidad es pasiva o instantánea. No se activa manualmente.")
            except ValueError: print("Ingresa un número.")
            
        elif opcion == "3":
            print(f"{atacante.nombre} pasa su turno.")
            time.sleep(1)
            break

def turno_ia(atacante, bando_jugador_vivos):
    print(f"\n[{atacante.nombre} está decidiendo su acción...]")
    time.sleep(1.5)
    
    # Simplificado: La IA del tutorial solo ataca
    objetivos_validos = filtrar_objetivos_validos(bando_jugador_vivos)
    if objetivos_validos:
        objetivo = random.choice(objetivos_validos)
        atacante.atacar(objetivo)

def iniciar_combate(jugador, aliados, enemigos, terreno="Tierra"):
    print("\n" + "="*40)
    print(f" ¡COMBATE INICIADO! | TERRENO: {terreno}")
    print("="*40)
    time.sleep(1)

    bando_jugador = [jugador] + aliados
    estado_combate = {"terreno": terreno}
    ronda = 1

    while True:
        vivos_jugador = [p for p in bando_jugador if p.vida_actual > 0]
        vivos_enemigos = [e for e in enemigos if e.vida_actual > 0]

        if not vivos_jugador:
            print("\n¡HAS SIDO DERROTADO! Fin del combate...")
            return False
        if not vivos_enemigos:
            print("\n¡VICTORIA! Has derrotado al enemigo.")
            return True

        print(f"\n{'='*15} RONDA {ronda} {'='*15}")
        time.sleep(1)
        
        # Reducir contadores de aturdimiento y restaurar velocidad
        for combatiente in vivos_jugador + vivos_enemigos:
            if combatiente.aturdido_turnos > 0:
                combatiente.aturdido_turnos -= 1
                if combatiente.aturdido_turnos == 0:
                    combatiente.velocidad_actual = combatiente.velocidad_base
                    print(f"[!] {combatiente.nombre} ya no está aturdido y recupera su velocidad.")

        combatientes_vivos = vivos_jugador + vivos_enemigos
        orden_turnos = calcular_orden_turnos(combatientes_vivos)

        for accion in orden_turnos:
            atacante = accion["objeto"]
            if atacante.vida_actual <= 0 or atacante.aturdido_turnos > 0:
                continue
            if len([e for e in enemigos if e.vida_actual > 0]) == 0 or len([p for p in bando_jugador if p.vida_actual > 0]) == 0:
                break 

            print(f"\n>>> Turno de: {atacante.nombre} (Iniciativa: {accion['iniciativa']})")
            time.sleep(1)

            if atacante in bando_jugador:
                turno_jugador_o_aliado(atacante, vivos_enemigos, estado_combate)
            else:
                turno_ia(atacante, vivos_jugador)

        ronda += 1
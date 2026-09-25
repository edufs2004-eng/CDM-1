import time
import random
from motor import calcular_orden_turnos
from habilidades import (
    HABILIDADES_DB,
    ejecutar_habilidad_activa,
    puede_usar_habilidad,
    ataque_permitido,
)

def filtrar_objetivos_validos(posibles_objetivos, atacante=None, estado_combate=None):
    vivos = [
        obj for obj in posibles_objetivos
        if obj.puede_ser_objetivo()
        and (atacante is None or ataque_permitido(atacante, obj, estado_combate))
    ]
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
            objetivos_validos = filtrar_objetivos_validos(enemigos_vivos, atacante, estado_combate)
            print("\nSelecciona un objetivo:")
            for i, enemigo in enumerate(objetivos_validos):
                print(f"{i + 1}. {enemigo.nombre} (Vida: {enemigo.vida_actual}/{enemigo.vida_max})")
            
            try:
                seleccion = int(input("Número del objetivo: ")) - 1
                if 0 <= seleccion < len(objetivos_validos):
                    objetivo = objetivos_validos[seleccion]
                    atacante.atacar(objetivo, estado_combate)
                    break
                else: print("Selección inválida.")
            except ValueError: print("Ingresa un número.")
            
        elif opcion == "2":
            # Filtramos solo las habilidades activas que aún tengan usos
            habs_activas = []
            for h in atacante.habilidades:
                if h in HABILIDADES_DB and puede_usar_habilidad(atacante, h):
                    habs_activas.append(h)
            
            if not habs_activas:
                print(f"\n{atacante.nombre} no tiene habilidades activas disponibles en este momento.")
                time.sleep(1)
                continue
                
            print("\nHabilidades disponibles:")
            for i, hab in enumerate(habs_activas):
                print(f"{i + 1}. {hab}")
            print(f"{len(habs_activas) + 1}. Cancelar")
            
            try:
                sel_hab = int(input("Selecciona habilidad: ")) - 1
                if sel_hab == len(habs_activas): continue
                
                habilidad_elegida = habs_activas[sel_hab]
                
                # --- EJECUCIÓN MODULAR ---
                ejecutar_habilidad_activa(habilidad_elegida, atacante, None, estado_combate)
                break # Rompe el while y gasta el turno
                
            except ValueError: 
                print("Ingresa un número.")
            
        elif opcion == "3":
            print(f"{atacante.nombre} pasa su turno.")
            time.sleep(1)
            break
        else:
            print("Opción incorrecta.")

def turno_ia(atacante, bando_jugador_vivos, estado_combate):
    print(f"\n[{atacante.nombre} está decidiendo su acción...]")
    time.sleep(1.5)
    
    objetivos_validos = filtrar_objetivos_validos(bando_jugador_vivos, atacante, estado_combate)
    if objetivos_validos:
        objetivo = random.choice(objetivos_validos)
        atacante.atacar(objetivo, estado_combate)

def iniciar_combate(jugador, aliados, enemigos, terreno="Tierra", aliados_reserva=None):
    print("\n" + "="*40)
    print(f" ¡COMBATE INICIADO! | TERRENO: {terreno}")
    print("="*40)
    time.sleep(1)

    bando_jugador = aliados.copy()
    if jugador is not None:
        bando_jugador.insert(0, jugador)
        jugador.guardianes = aliados.copy()
        
    estado_combate = {
        "terreno": terreno,
        "equipo_enemigo": enemigos,
        "nuevos_combatientes": [],
        "jugador": jugador,
        "aliados_inactivos": list(aliados_reserva or []),
    }

    def actualizar_combatientes():
        jugador_actual = estado_combate["jugador"]
        if jugador_actual is not None and jugador_actual not in bando_jugador:
            if terreno_valido(jugador_actual, estado_combate["terreno"]):
                bando_jugador.insert(0, jugador_actual)

        for aliado in estado_combate["aliados_inactivos"][:]:
            if terreno_valido(aliado, estado_combate["terreno"]):
                bando_jugador.append(aliado)
                estado_combate["aliados_inactivos"].remove(aliado)

        if jugador_actual is not None:
            jugador_actual.guardianes = [
                aliado for aliado in bando_jugador if aliado is not jugador_actual
            ]

    estado_combate["actualizar_combatientes"] = actualizar_combatientes
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
        
        combatientes_vivos = vivos_jugador + vivos_enemigos
        orden_turnos = calcular_orden_turnos(combatientes_vivos, estado_combate)

        for accion in orden_turnos:
            atacante = accion["objeto"]
            
            if atacante.vida_actual <= 0:
                continue
            
            if len([e for e in enemigos if e.vida_actual > 0]) == 0 or len([p for p in bando_jugador if p.vida_actual > 0]) == 0:
                break 

            print(f"\n>>> Turno de: {atacante.nombre} (Iniciativa: {accion['iniciativa']})")
            time.sleep(1)

            # AQUÍ COBRAMOS EL ATURDIMIENTO
            if atacante.aturdido_turnos > 0:
                print(f"¡{atacante.nombre} está aturdido y pierde esta acción!")
                atacante.aturdido_turnos -= 1
                time.sleep(1)
                continue # Saltamos el turno

            if atacante in bando_jugador:
                turno_jugador_o_aliado(atacante, vivos_enemigos, estado_combate)
            else:
                turno_ia(atacante, [e for e in enemigos if e.vida_actual > 0], estado_combate)

        enemigos.extend(estado_combate.pop("nuevos_combatientes", []))

        ronda += 1


def terreno_valido(entidad, terreno):
    if terreno == "Agua":
        return "Acuático" in entidad.etiquetas or "Híbrido" in entidad.etiquetas or "Barca" in entidad.etiquetas
    if terreno == "Tierra":
        return hasattr(entidad, "equipo") or "Terrestre" in entidad.etiquetas or "Híbrido" in entidad.etiquetas
    return True
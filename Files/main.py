import time
from Files.entidades import Jugador
from Files.mapa import menu_exploracion
from Files.guardado import guardar_partida, cargar_partida
from Files.objetos import generar_objeto

def gestionar_equipo(jugador):
    while True:
        print("\n" + "="*30)
        print("      GESTIÓN DE EQUIPO      ")
        print("="*30)
        
        print("\n[EQUIPO ACTIVO] (Máx 4)")
        if not jugador.equipo_aliado:
            print("  (Vacío)")
        else:
            for i, aliado in enumerate(jugador.equipo_aliado):
                print(f"  {i + 1}. {aliado.nombre} (Vida: {aliado.vida_max}, Ataque: {aliado.ataque_base}, Vel: {aliado.velocidad_base})")
                
        print("\n[RESERVA / CAJA]")
        if not jugador.caja_aliados:
            print("  (Vacío)")
        else:
            for i, aliado in enumerate(jugador.caja_aliados):
                print(f"  {i + len(jugador.equipo_aliado) + 1}. {aliado.nombre} (Vida: {aliado.vida_max}, Ataque: {aliado.ataque_base}, Vel: {aliado.velocidad_base})")

        print("\nOpciones:")
        print("1. Enviar monstruo activo a la reserva")
        print("2. Mover monstruo de la reserva al equipo activo")
        print("3. Volver al Menú de Juego")
        
        opcion = input("Elige una opción (1-3): ")
        
        if opcion == "1":
            if not jugador.equipo_aliado:
                print("No tienes monstruos en tu equipo activo.")
                time.sleep(1)
                continue
            try:
                idx = int(input("Número del monstruo a retirar: ")) - 1
                if 0 <= idx < len(jugador.equipo_aliado):
                    monstruo_movido = jugador.equipo_aliado.pop(idx)
                    jugador.caja_aliados.append(monstruo_movido)
                    print(f"\n{monstruo_movido.nombre} fue enviado a la reserva.")
                else: print("Número inválido.")
            except ValueError: print("Ingresa un número.")
            
        elif opcion == "2":
            if len(jugador.equipo_aliado) >= 4:
                print("Tu equipo ya está lleno (Máximo 4). Retira uno primero.")
                time.sleep(1.5)
                continue
            if not jugador.caja_aliados:
                print("No tienes monstruos en tu reserva.")
                time.sleep(1)
                continue
                
            try:
                idx_visual = int(input("Número del monstruo a equipar: ")) - 1
                idx_real = idx_visual - len(jugador.equipo_aliado)
                
                if 0 <= idx_real < len(jugador.caja_aliados):
                    monstruo_movido = jugador.caja_aliados.pop(idx_real)
                    jugador.equipo_aliado.append(monstruo_movido)
                    print(f"\n{monstruo_movido.nombre} se ha unido a tu equipo activo.")
                else: print("Número inválido.")
            except ValueError: print("Ingresa un número.")
            
        elif opcion == "3":
            break
        else:
            print("Opción incorrecta.")
        time.sleep(1)

def gestionar_equipamiento_jugador(jugador):
    while True:
        print("\n" + "="*30)
        print("[STATS DEL PERSONAJE]")
        print(f"Nombre: {jugador.nombre}")
        print(f"Vida: {jugador.vida_max} | Ataque Base: {jugador.ataque_base} (±{jugador.varianza_ataque}) | Vel: {jugador.velocidad_base} | Reflejos: {jugador.reflejos}")
        
        print("\n[EQUIPAMIENTO]")
        for slot, item in jugador.equipo.items():
            nombre_item = item.nombre if item else "Vacío"
            print(f"- {slot}: {nombre_item}")
        
        print("\n[INVENTARIO DE OBJETOS]")
        if not jugador.inventario:
            print(" (Vacío)")
        else:
            for i, obj in enumerate(jugador.inventario):
                print(f" {i+1}. {obj}")
                
        print("\nOpciones:")
        print("1. Equipar objeto del inventario")
        print("2. Desequipar objeto")
        print("3. Volver")
        
        opc = input("Elige una opción (1-3): ")
        if opc == "1":
            if not jugador.inventario:
                print("No tienes objetos para equipar.")
                time.sleep(1)
                continue
            try:
                idx = int(input("Número del objeto a equipar: ")) - 1
                if 0 <= idx < len(jugador.inventario):
                    nombre_obj = jugador.inventario[idx]
                    nuevo_item = generar_objeto(nombre_obj)
                    slot = nuevo_item.tipo_slot
                    
                    if jugador.equipo[slot] is not None:
                        jugador.inventario.append(jugador.equipo[slot].nombre)
                        
                    jugador.equipo[slot] = nuevo_item
                    jugador.inventario.pop(idx)
                    jugador.actualizar_stats()
                    print(f"\n¡Te has equipado: {nombre_obj} en el slot {slot}!")
                else:
                    print("Número inválido.")
            except ValueError:
                print("Ingresa un número.")
                
        elif opc == "2":
            slots_ocupados = [s for s, i in jugador.equipo.items() if i is not None]
            if not slots_ocupados:
                print("No tienes nada equipado para quitarte.")
                time.sleep(1)
                continue
            
            print("\nSlots ocupados:")
            for i, s in enumerate(slots_ocupados):
                print(f"{i+1}. {s} ({jugador.equipo[s].nombre})")
                
            try:
                idx = int(input("Número del slot a desequipar: ")) - 1
                if 0 <= idx < len(slots_ocupados):
                    slot_elegido = slots_ocupados[idx]
                    item_removido = jugador.equipo[slot_elegido].nombre
                    jugador.inventario.append(item_removido)
                    jugador.equipo[slot_elegido] = None
                    jugador.actualizar_stats()
                    print(f"\nTe has desequipado: {item_removido}.")
                else:
                    print("Número inválido.")
            except ValueError:
                print("Ingresa un número.")
                
        elif opc == "3":
            break
        else:
            print("Opción inválida.")

def menu_juego(jugador):
    while True:
        print("\n" + "="*30)
        print(f"      MENÚ DE {jugador.nombre.upper()}      ")
        print("="*30)
        print("1. Explorar Zonas (Mapa)")
        print("2. Gestionar Equipo de Monstruos")
        print("3. Ver Stats y Gestionar Equipamiento")
        print("4. Guardar Partida")
        print("5. Salir al Menú Principal")
        
        opcion = input("Elige una opción: ")
        
        if opcion == "1":
            menu_exploracion(jugador)
        elif opcion == "2":
            gestionar_equipo(jugador)
        elif opcion == "3":
            gestionar_equipamiento_jugador(jugador)
        elif opcion == "4":
            guardar_partida(jugador)
            time.sleep(1)
        elif opcion == "5":
            break
        else:
            print("Opción inválida.")

def menu_principal():
    while True:
        print("\n" + "="*40)
        print("      RPG: EL ORIGEN DEL PESCADOR     ")
        print("="*40)
        print("1. Nueva Partida")
        print("2. Continuar Partida")
        print("3. Salir")
        
        opcion = input("Elige una opción: ")
        
        if opcion == "1":
            nombre = input("\nIngresa tu nombre: ")
            if not nombre.strip(): nombre = "Pescador Joven"
            prota = Jugador(nombre)
            print(f"\n¡Bienvenido, {prota.nombre}! Tu aventura comienza...")
            time.sleep(1)
            menu_juego(prota)
        elif opcion == "2":
            prota = cargar_partida()
            if prota:
                time.sleep(1)
                menu_juego(prota)
            else:
                time.sleep(1)
        elif opcion == "3":
            print("Saliendo del juego...")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu_principal()
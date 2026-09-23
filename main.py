import time
from entidades import Jugador
from mapa import menu_exploracion
from guardado import guardar_partida, cargar_partida

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

def menu_juego(jugador):
    while True:
        print("\n" + "="*30)
        print(f"      MENÚ DE {jugador.nombre.upper()}      ")
        print("="*30)
        print("1. Explorar Zonas (Mapa)")
        print("2. Gestionar Equipo de Monstruos")
        print("3. Ver Stats y Equipamiento")
        print("4. Guardar Partida")
        print("5. Salir al Menú Principal")
        
        opcion = input("Elige una opción: ")
        
        if opcion == "1":
            menu_exploracion(jugador)
        elif opcion == "2":
            gestionar_equipo(jugador)
        elif opcion == "3":
            print("\n[STATS DEL PERSONAJE]")
            print(f"Nombre: {jugador.nombre}")
            print(f"Vida: {jugador.vida_max} | Ataque Base: {jugador.ataque_base} | Vel: {jugador.velocidad_base}")
            print("\n[EQUIPAMIENTO]")
            for slot, item in jugador.equipo.items():
                nombre_item = item.nombre if item else "Vacío"
                print(f"- {slot}: {nombre_item}")
            input("\nPresiona Enter para volver...")
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
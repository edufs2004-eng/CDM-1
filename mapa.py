import time
from datos_monstruos import generar_monstruo
from combate import iniciar_combate

# Diccionario con las zonas y los monstruos que habitan en ellas (y su terreno de combate)
ZONAS = {
    "Playa": {
        "Pulpo Inteligente": "Híbrido",
        "Tiburón": "Agua",
        "Serpiente Marina": "Agua"
    },
    "Bosque": {
        # Aquí agregaremos monstruos terrestres a futuro
    }
}

# Diccionario para guardar los monstruos generados que aún no has derrotado
monstruos_activos = {}

def verificar_restricciones_terreno(aliados, terreno_combate):
    """Filtra los aliados que pueden entrar al combate según el terreno."""
    aliados_validos = []
    for aliado in aliados:
        if terreno_combate == "Agua":
            if "Acuático" in aliado.etiquetas or "Híbrido" in aliado.etiquetas or "Barca" in aliado.etiquetas:
                aliados_validos.append(aliado)
        elif terreno_combate == "Tierra":
            if "Terrestre" in aliado.etiquetas or "Híbrido" in aliado.etiquetas:
                aliados_validos.append(aliado)
        else: # Si el terreno es Híbrido, entran todos
            aliados_validos.append(aliado)
            
    return aliados_validos

def procesar_captura(jugador, monstruo):
    """Verifica si el monstruo se captura o solo muere."""
    if monstruo.nombre not in jugador.aliados_obtenidos:
        print(f"\n¡Has capturado a {monstruo.nombre}!")
        print(f"Stats guardados: Vida {monstruo.vida_max}, Ataque {monstruo.ataque_base}, Vel {monstruo.velocidad_base}")
        # Lo añadimos a la lista de nombres obtenidos
        jugador.aliados_obtenidos.append(monstruo.nombre)
        # Añadimos la instancia exacta al inventario/equipo (por ahora directo al equipo aliado si hay espacio)
        if len(jugador.equipo_aliado) < 4:
            jugador.equipo_aliado.append(monstruo)
            print(f"{monstruo.nombre} ha sido añadido a tu equipo activo.")
        else:
            jugador.caja_aliados.append(monstruo)
            print(f"Tu equipo está lleno. {monstruo.nombre} fue enviado a tu Reserva.")
    else:
        print(f"\nYa tienes un {monstruo.nombre}. El monstruo ha sido derrotado y deja de existir.")

def menu_exploracion(jugador):
    while True:
        print("\n" + "="*30)
        print("         MAPA MUNDI          ")
        print("="*30)
        
        zonas_lista = list(ZONAS.keys())
        for i, zona in enumerate(zonas_lista):
            print(f"{i + 1}. {zona}")
        print(f"{len(zonas_lista) + 1}. Volver")
        
        try:
            opcion_zona = int(input("\nElige una zona: ")) - 1
            if opcion_zona == len(zonas_lista):
                break
            
            if 0 <= opcion_zona < len(zonas_lista):
                zona_elegida = zonas_lista[opcion_zona]
                menu_zona(jugador, zona_elegida)
            else:
                print("Opción inválida.")
        except ValueError:
            print("Ingresa un número.")

def menu_zona(jugador, nombre_zona):
    monstruos_zona = ZONAS[nombre_zona]
    nombres_monstruos = list(monstruos_zona.keys())
    
    while True:
        print(f"\n--- EXPLORANDO: {nombre_zona.upper()} ---")
        for i, nombre in enumerate(nombres_monstruos):
            terreno = monstruos_zona[nombre]
            estado = "[NUEVO]" if nombre not in monstruos_activos else f"[Vida: {monstruos_activos[nombre].vida_actual}/{monstruos_activos[nombre].vida_max}]"
            print(f"{i + 1}. {nombre} (Terreno: {terreno}) {estado}")
        print(f"{len(nombres_monstruos) + 1}. Volver")
        
        try:
            opcion = int(input("\n¿A quién te quieres enfrentar?: ")) - 1
            if opcion == len(nombres_monstruos):
                break
                
            if 0 <= opcion < len(nombres_monstruos):
                nombre_enemigo = nombres_monstruos[opcion]
                terreno_combate = monstruos_zona[nombre_enemigo]
                
                # 1. Sistema de Persistencia: Si no existe, lo generamos
                if nombre_enemigo not in monstruos_activos:
                    monstruos_activos[nombre_enemigo] = generar_monstruo(nombre_enemigo)
                
                enemigo = monstruos_activos[nombre_enemigo]
                
                # 2. Filtrar aliados por terreno
                equipo_valido = verificar_restricciones_terreno(jugador.equipo_aliado, terreno_combate)
                
                # Evaluamos si el jugador mismo puede entrar
                if not verificar_restricciones_terreno([jugador], terreno_combate):
                    print(f"\n[!] Tu personaje no tiene forma de pelear en terreno {terreno_combate}.")
                    # Si no tiene aliados válidos tampoco, no puede pelear
                    if not equipo_valido:
                        print("¡No tienes equipo válido para este combate! Vuelve cuando estés preparado.")
                        continue
                    else:
                        print("Solo tus aliados combatirán.")
                        jugador_combatira = None
                else:
                    jugador_combatira = jugador
                
                # 3. Iniciar Combate
                enemigos = [enemigo]
                victoria = iniciar_combate(jugador_combatira, equipo_valido, enemigos, terreno=terreno_combate)
                
                # 4. Resultados post-combate
                if victoria:
                    procesar_captura(jugador, enemigo)
                    del monstruos_activos[nombre_enemigo] # Eliminamos la instancia para que genere una nueva la próxima vez
                    # Restaurar vida de tu equipo
                    jugador.vida_actual = jugador.vida_max
                    for aliado in jugador.equipo_aliado: aliado.vida_actual = aliado.vida_max
                else:
                    print(f"\nHas huido o perdido. {enemigo.nombre} te estará esperando.")
                    # Recupera su vida, pero mantiene stats exactos
                    enemigo.vida_actual = enemigo.vida_max
                    jugador.vida_actual = jugador.vida_max # El jugador revive para seguir jugando
                    
        except ValueError:
            print("Ingresa un número.")
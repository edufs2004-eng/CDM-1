from objetos import generar_objeto

def evaluar_logros(jugador, enemigo, estado_combate):
    nuevos_logs = []

    if enemigo.nombre == "Pulpo Inteligente" and "derrota_pulpo" not in jugador.eventos_desbloqueados:
        jugador.eventos_desbloqueados.append("derrota_pulpo")
        nuevo_item = generar_objeto("Palo de madera con hojita")
        if nuevo_item:
            jugador.inventario.append(nuevo_item.nombre)
            nuevos_logs.append("🏆 LOGRO: ¡Has obtenido [Palo de madera con hojita] por tu primera victoria contra el Pulpo!")

    return nuevos_logs
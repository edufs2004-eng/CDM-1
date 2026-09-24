from objetos import generar_objeto

def evaluar_logros(jugador, enemigo, estado_combate):
    """
    Evalúa todas las condiciones al terminar un combate victorioso.
    Retorna una lista de textos con los logros y objetos obtenidos.
    """
    nuevos_logs = []
    
    # -----------------------------------------
    # HITOS DE PRIMERA VICTORIA
    # -----------------------------------------
    if enemigo.nombre == "Pulpo Inteligente" and "derrota_pulpo" not in jugador.eventos_desbloqueados:
        jugador.eventos_desbloqueados.append("derrota_pulpo")
        nuevo_item = generar_objeto("Palo de madera con hojita")
        if nuevo_item:
            jugador.inventario.append(nuevo_item)
            nuevos_logs.append("🏆 LOGRO: ¡Has obtenido [Palo de madera con hojita] por tu primera victoria contra el Pulpo!")

    # -----------------------------------------
    # HITOS CONDICIONALES (Ej. Ogro sin perder mucha vida)
    # -----------------------------------------
    # (Lo programaremos cuando lleguemos al Ogro)

    # -----------------------------------------
    # HITOS DE CACERÍA (Contadores 10 Tiburones/Megalodones)
    # -----------------------------------------
    # (Lo programaremos en el siguiente paso)

    return nuevos_logs
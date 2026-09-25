from Files.objetos import generar_objeto

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
            jugador.inventario.append(nuevo_item.nombre)
            nuevos_logs.append("🏆 LOGRO: ¡Has obtenido [Palo de madera con hojita] por tu primera victoria contra el Pulpo!")

    # -----------------------------------------
    # HITOS CONDICIONALES
    # -----------------------------------------
    # (Se implementarán según avance del diseño)

    # -----------------------------------------
    # HITOS DE CACERÍA
    # -----------------------------------------
    # (Se implementarán según avance del diseño)

    return nuevos_logs
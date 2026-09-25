RECOMPENSAS_EVENTOS = {
    "Pulpo Inteligente": ("recompensa_palo_pulpo", "Palo de madera con hojita"),
    "Nautilus": ("recompensa_linterna_nautilus", "Linterna de Nautilus"),
    "Capitán del Caleuche": ("recompensa_barco_caleuche", "Barco del Caleuche"),
}


def agregar_objeto_unico(jugador, nombre_objeto, evento):
    if evento in jugador.eventos_desbloqueados:
        return False
    jugador.inventario.append(nombre_objeto)
    jugador.eventos_desbloqueados.append(evento)
    return True


def evaluar_recompensas_victoria(jugador, enemigo):
    """Evalúa hitos deterministas después de una victoria."""
    logs = []
    nombre = enemigo.nombre
    jugador.contadores_eventos[nombre] = jugador.contadores_eventos.get(nombre, 0) + 1

    recompensa = RECOMPENSAS_EVENTOS.get(nombre)
    if recompensa:
        evento, objeto = recompensa
        if agregar_objeto_unico(jugador, objeto, evento):
            logs.append(f"¡Recompensa obtenida: {objeto}!")

    if nombre == "Ogro de Fuego" and jugador.vida_actual < jugador.vida_max / 2:
        if agregar_objeto_unico(jugador, "Hacha de fuego", "recompensa_hacha_ogro"):
            logs.append("¡Recompensa obtenida: Hacha de fuego!")

    if nombre == "Tiburón" and jugador.contadores_eventos[nombre] >= 10:
        if agregar_objeto_unico(jugador, "Corona de dientes de tiburón", "recompensa_10_tiburones"):
            logs.append("¡Recompensa obtenida: Corona de dientes de tiburón!")

    if nombre == "Megalodón" and jugador.contadores_eventos[nombre] >= 10:
        if agregar_objeto_unico(jugador, "Armadura de dientes de megalodón", "recompensa_10_megalodones"):
            logs.append("¡Recompensa obtenida: Armadura de dientes de megalodón!")

    aliados_acuaticos = sum(
        1 for aliado in jugador.equipo_aliado
        if "Acuático" in aliado.etiquetas or "Híbrido" in aliado.etiquetas
    )
    if aliados_acuaticos >= 3:
        if agregar_objeto_unico(jugador, "Caña de pescar de experto", "recompensa_equipo_acuatico"):
            logs.append("¡Recompensa obtenida: Caña de pescar de experto!")

    if jugador.aliados_revividos_ronda >= 4:
        if agregar_objeto_unico(jugador, "Espada del capitán", "recompensa_4_revividos"):
            logs.append("¡Recompensa obtenida: Espada del capitán!")

    return logs

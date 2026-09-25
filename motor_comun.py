from motor import calcular_orden_turnos
from normalizacion import normalizar_terreno

def ejecutar_combate(jugador, aliados, enemigos, terreno, turno_jugador, turno_ia, mostrar_turno=None):
    terreno = normalizar_terreno(terreno)
    estado = {"terreno": terreno}

    bando_jugador = list(aliados)
    if jugador is not None:
        bando_jugador.insert(0, jugador)

    ronda = 1

    while True:
        vivos_jugador = [e for e in bando_jugador if getattr(e, "vida_actual", 0) > 0]
        vivos_enemigos = [e for e in enemigos if getattr(e, "vida_actual", 0) > 0]

        if jugador is not None and getattr(jugador, "vida_actual", 0) <= 0:
            return False

        if not vivos_enemigos:
            return True

        if not vivos_jugador:
            return False

        if mostrar_turno is not None:
            mostrar_turno(ronda)

        orden = calcular_orden_turnos(vivos_jugador + vivos_enemigos)

        for accion in orden:
            atacante = accion["objeto"]

            if getattr(atacante, "vida_actual", 0) <= 0:
                continue

            if atacante in bando_jugador:
                if getattr(jugador, "vida_actual", 0) <= 0:
                    return False
                if not vivos_enemigos:
                    return True
                turno_jugador(atacante, vivos_enemigos, estado)
            else:
                if not vivos_jugador:
                    return False
                turno_ia(atacante, vivos_jugador, estado)

        for entidad in vivos_jugador + vivos_enemigos:
            if getattr(entidad, "aturdido_turnos", 0) > 0:
                entidad.aturdido_turnos -= 1

            entidad.gestionar_cooldowns()

        ronda += 1
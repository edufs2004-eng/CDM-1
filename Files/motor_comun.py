from Files.motor import calcular_orden_turnos
from Files.normalizacion import normalizar_terreno

def ejecutar_combate(jugador, aliados, enemigos, terreno, turno_jugador, turno_ia, mostrar_turno=None):
    terreno = normalizar_terreno(terreno)
    estado = {"terreno": terreno}

    bando_jugador = list(aliados)
    if jugador is not None:
        bando_jugador.insert(0, jugador)

    ronda = 1

    while True:
        vivos_jugador = [entidad for entidad in bando_jugador if entidad.vida_actual > 0]
        vivos_enemigos = [entidad for entidad in enemigos if entidad.vida_actual > 0]

        if jugador is not None and jugador.vida_actual <= 0:
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

            if atacante.vida_actual <= 0:
                continue

            if atacante in bando_jugador:
                if jugador is not None and jugador.vida_actual <= 0:
                    return False
                if not vivos_enemigos:
                    return True
                turno_jugador(atacante, vivos_enemigos, estado)
            else:
                if not vivos_jugador:
                    return False
                turno_ia(atacante, vivos_jugador, estado)

        ronda += 1
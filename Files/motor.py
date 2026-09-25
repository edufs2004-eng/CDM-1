import random

def calcular_orden_turnos(combatientes):
    vivos = [c for c in combatientes if getattr(c, "vida_actual", 0) > 0]
    if not vivos:
        return []

    vel_min = min(max(getattr(c, "velocidad_actual", 1), 1) for c in vivos)
    turnos = []

    for combatiente in vivos:
        acciones = max(1, getattr(combatiente, "velocidad_actual", 1) // vel_min)

        for _ in range(acciones):
            turnos.append({
                "objeto": combatiente,
                "nombre": getattr(combatiente, "nombre", "Entidad"),
                "velocidad": getattr(combatiente, "velocidad_actual", 0),
                "reflejos": getattr(combatiente, "reflejos", 0),
                "iniciativa": random.random(),
            })

    turnos.sort(
        key=lambda turno: (
            turno["velocidad"],
            turno["reflejos"],
            turno["iniciativa"],
        ),
        reverse=True,
    )

    return turnos
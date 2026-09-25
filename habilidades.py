import random
import time

# ==========================================
# DICCIONARIO MAESTRO DE HABILIDADES
# ==========================================
HABILIDADES_DB = {
    "Cachetada": {
        "tipo": "instantanea",
        "trigger": "al_atacar",
        "probabilidad": 0.30,
        "umbral_dano_porcentaje": 0.10,
        "texto": "\n¡{usuario} activó CACHETADA!",
        "efectos": [
            {"accion": "aturdir", "turnos": 1, "texto": "¡{objetivo} ha sido aturdido (perderá su próxima acción)!"}
        ]
    },
    "Tácticas de escape": {
        "tipo": "pasiva",
        "trigger": "al_recibir_dano_letal",
        "usos_maximos": 1, # Solo 1 vez por combate
        "texto": "\n¡{usuario} usó TÁCTICAS DE ESCAPE!\n{usuario} sobrevivió con 1 HP y lanzó un chorro de tinta.",
        "efectos": [
            {"accion": "sobrevivir", "hp": 1},
            {"accion": "reducir_velocidad", "objetivo_efecto": "atacante", "porcentaje": 0.25, "texto": "¡La velocidad de {objetivo} bajó en {cantidad} puntos!"}
        ]
    },
    "Tsunami": {
        "tipo": "activa",
        "usos_maximos": 1,
        "texto": "\n¡{usuario} invoca un TSUNAMI!",
        "efectos": [
            {"accion": "cambiar_terreno", "terreno": "Híbrido", "texto": "¡El terreno de combate ha cambiado a HÍBRIDO!"}
        ]
    },
    "Puños en llamas": {
        "tipo": "instantanea",
        "trigger": "al_atacar",
        "probabilidad": 0.25,
        "texto": "¡{usuario} prende sus puños y aplica quemadura!",
        "efectos": [
            {"accion": "aplicar_quemadura", "cargas": 1}
        ]
    },
    "Chorro de agua": {
        "tipo": "activa",
        "texto": "¡{usuario} se purifica con un chorro de agua!",
        "efectos": [
            {"accion": "purificar_quemadura", "objetivo_efecto": "usuario"}
        ]
    },
    "Círculo de fuego": {
        "tipo": "ia",
        "cooldown": 8,
        "efectos": [
            {"accion": "crear_circulo_fuego", "turnos": 2}
        ]
    },
    "Gran mordisco": {
        "tipo": "activa",
        "cooldown": 5,
        "texto": "¡{usuario} ejecuta Gran mordisco!",
        "efectos": [
            {
                "accion": "ataque_especial",
                "multiplicador": 1.5,
                "ignora_penalizacion_gigante": True
            }
        ]
    },
    "No muerto": {
        "tipo": "pasiva",
        "trigger": "al_recibir_dano_letal",
        "probabilidad": 0.30,
        "texto": "¡{usuario} se niega a morir!",
        "efectos": [
            {"accion": "revivir_vida_anterior"}
        ]
    },
    "Mejor amigo": {
        "tipo": "pasiva"
    },
    "Tripulación fantasma": {
        "tipo": "ia",
        "usos_maximos": 1,
        "efectos": [
            {"accion": "crear_fantasmas"}
        ]
    },
    "Furia del mar": {
        "tipo": "pasiva",
        "trigger": "al_recibir_dano_letal",
        "usos_maximos": 1,
        "efectos": [
            {"accion": "transicionar_fase"}
        ]
    }
}


def puede_usar_habilidad(usuario, nombre):
    """Comprueba usos y cooldowns sin depender de la interfaz."""
    datos = HABILIDADES_DB.get(nombre)
    if not datos or datos.get("tipo") not in ("activa", "ia"):
        return False

    usos_maximos = datos.get("usos_maximos")
    usos_actuales = usuario.habilidades_usadas.get(nombre, 0)
    if usos_maximos is not None and usos_actuales >= usos_maximos:
        return False

    return usuario.enfriamientos.get(nombre, 0) <= 0


def registrar_uso_habilidad(usuario, nombre):
    datos = HABILIDADES_DB[nombre]
    usuario.habilidades_usadas[nombre] = usuario.habilidades_usadas.get(nombre, 0) + 1
    cooldown = datos.get("cooldown", 0)
    if cooldown > 0:
        usuario.enfriamientos[nombre] = cooldown


def reducir_cooldowns(combatientes):
    """Avanza un turno global y conserva solo cooldowns pendientes."""
    for combatiente in combatientes:
        enfriamientos = getattr(combatiente, "enfriamientos", {})
        combatiente.enfriamientos = {
            nombre: turnos - 1
            for nombre, turnos in enfriamientos.items()
            if turnos > 1
        }


def avanzar_estado_combate(estado_combate):
    circulo = estado_combate.get("circulo_fuego") if estado_combate else None
    if not circulo:
        return

    circulo["turnos"] -= 1
    if circulo["turnos"] <= 0 or any(entidad.vida_actual <= 0 for entidad in circulo["participantes"]):
        estado_combate.pop("circulo_fuego", None)


def ataque_permitido(atacante, objetivo, estado_combate):
    circulo = estado_combate.get("circulo_fuego") if estado_combate else None
    if not circulo:
        return True
    participantes = circulo["participantes"]
    return atacante in participantes and objetivo in participantes


def seleccionar_habilidad_ia(usuario):
    """Selecciona una habilidad usando una ventana acumulada sobre 1d100."""
    disponibles = [
        (nombre, probabilidad)
        for nombre, probabilidad in usuario.probabilidades_ia.items()
        if probabilidad > 0 and puede_usar_habilidad(usuario, nombre)
    ]
    disponibles.sort(key=lambda habilidad: (-habilidad[1], habilidad[0]))

    if not disponibles:
        return None

    tirada = random.randint(1, 100)
    limite = 0
    for nombre, probabilidad in disponibles:
        limite += probabilidad
        if tirada <= limite:
            return nombre

    return None

# ==========================================
# MOTOR DE EFECTOS
# ==========================================
def aplicar_efectos(efectos, usuario, objetivo_principal, estado_combate):
    """Lee la lista de efectos de una habilidad y los ejecuta matemáticamente"""
    for efecto in efectos:
        # 1. Determinar a quién le cae el efecto (Por defecto al objetivo del ataque)
        target = objetivo_principal
        if efecto.get("objetivo_efecto") == "atacante":
            target = objetivo_principal # Quien nos pegó
        elif efecto.get("objetivo_efecto") == "usuario":
            target = usuario
            
        # 2. Aplicar la lógica del efecto
        if efecto["accion"] == "aturdir":
            if "Mecánico" in target.etiquetas:
                continue
            target.aturdido_turnos += efecto["turnos"]
            if "texto" in efecto: print(efecto["texto"].format(objetivo=target.nombre))
                
        elif efecto["accion"] == "sobrevivir":
            usuario.vida_actual = efecto["hp"]

        elif efecto["accion"] == "revivir_vida_anterior":
            usuario.vida_actual = max(1, usuario.vida_turno_anterior)

        elif efecto["accion"] == "transicionar_fase":
            usuario.transicionar_fase(objetivo_principal, forzar=True)
            
        elif efecto["accion"] == "reducir_velocidad":
            if "Mecánico" in target.etiquetas:
                continue
            reduccion = max(1, int(target.velocidad_actual * efecto["porcentaje"]))
            target.velocidad_actual -= reduccion
            if "texto" in efecto: print(efecto["texto"].format(objetivo=target.nombre, cantidad=reduccion))
                
        elif efecto["accion"] == "cambiar_terreno":
            if estado_combate is not None:
                estado_combate["terreno"] = efecto["terreno"]
                if "texto" in efecto: print(efecto["texto"])

        elif efecto["accion"] == "aplicar_quemadura":
            if target is not None and target.aplicar_quemadura(efecto.get("cargas", 1)):
                if "texto" in efecto:
                    print(efecto["texto"].format(objetivo=target.nombre))

        elif efecto["accion"] == "purificar_quemadura":
            if target is not None and target.purificar_quemadura():
                if "texto" in efecto:
                    print(efecto["texto"].format(objetivo=target.nombre))

        elif efecto["accion"] == "hacer_inalcanzable":
            if target is not None:
                target.inalcanzable_turnos = max(
                    target.inalcanzable_turnos,
                    efecto.get("turnos", 1),
                )
                if "texto" in efecto:
                    print(efecto["texto"].format(objetivo=target.nombre))

        elif efecto["accion"] == "crear_circulo_fuego":
            if estado_combate is not None and target is not None:
                estado_combate["circulo_fuego"] = {
                    "participantes": (usuario, target),
                    "turnos": efecto.get("turnos", 2),
                }
                print(f"¡Círculo de fuego! {usuario.nombre} y {target.nombre} quedan aislados.")

        elif efecto["accion"] == "ataque_especial":
            if target is not None:
                usuario.atacar_especial(
                    target,
                    multiplicador=efecto.get("multiplicador", 1.0),
                    estado_combate=estado_combate,
                    ignora_penalizacion_gigante=efecto.get("ignora_penalizacion_gigante", False),
                )

        elif efecto["accion"] == "crear_fantasmas":
            if estado_combate is not None:
                equipo = estado_combate.get("equipo_enemigo", [])
                fantasmas = usuario.crear_fantasmas(equipo)
                estado_combate.setdefault("nuevos_combatientes", []).extend(fantasmas)
                print(f"¡{usuario.nombre} convierte {len(fantasmas)} aliado(s) muerto(s) en fantasmas!")

def procesar_trigger(trigger, usuario, objetivo, estado_combate=None, evento=None):
    """Revisa si el personaje tiene una habilidad pasiva/instantánea que reaccione a este momento"""
    for nombre_hab in usuario.habilidades:
        if nombre_hab not in HABILIDADES_DB: continue
        
        datos_hab = HABILIDADES_DB[nombre_hab]
        
        # Ignorar si no es el trigger correcto
        if datos_hab.get("trigger") != trigger: continue
            
        # Validar usos máximos
        if "usos_maximos" in datos_hab:
            usos_actuales = usuario.habilidades_usadas.get(nombre_hab, 0)
            if usos_actuales >= datos_hab["usos_maximos"]: continue

        if usuario.enfriamientos.get(nombre_hab, 0) > 0:
            continue

        umbral_dano = datos_hab.get("umbral_dano_porcentaje")
        if umbral_dano is not None:
            dano_realizado = (evento or {}).get("dano_realizado", 0)
            if dano_realizado < objetivo.vida_max * umbral_dano:
                continue

        # Validar probabilidad (Si tiene)
        if "probabilidad" in datos_hab:
            if random.random() > datos_hab["probabilidad"]: continue 
            
        # ¡La habilidad se activa!
        if "texto" in datos_hab:
            print(datos_hab["texto"].format(usuario=usuario.nombre))
            
        aplicar_efectos(datos_hab["efectos"], usuario, objetivo, estado_combate)
        
        # Registrar el uso
        usuario.habilidades_usadas[nombre_hab] = usuario.habilidades_usadas.get(nombre_hab, 0) + 1
        cooldown = datos_hab.get("cooldown", 0)
        if cooldown > 0:
            usuario.enfriamientos[nombre_hab] = cooldown
        time.sleep(1)

def ejecutar_habilidad_activa(nombre, lanzador, objetivo, estado_combate):
    if not puede_usar_habilidad(lanzador, nombre):
        print(f"¡{lanzador.nombre} no puede usar {nombre} ahora!")
        return False

    datos_habilidad = HABILIDADES_DB[nombre]
    if nombre == "Tsunami":
        if estado_combate["terreno"].lower() in ["agua", "híbrido", "hibrido"]:
            print(f"¡El terreno ya es {estado_combate['terreno']}, el Tsunami choca sin efecto!")
        else:
            estado_combate["terreno"] = "híbrido"
            print(f"¡{lanzador.nombre} invoca un Tsunami! El campo se inunda y pasa a ser Híbrido.")
            actualizar = estado_combate.get("actualizar_combatientes")
            if actualizar:
                actualizar()
    else:
        if "texto" in datos_habilidad:
            print(datos_habilidad["texto"].format(usuario=lanzador.nombre))
        aplicar_efectos(datos_habilidad.get("efectos", []), lanzador, objetivo, estado_combate)

    registrar_uso_habilidad(lanzador, nombre)
    time.sleep(1)
    return True
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
    }
}

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
            target.aturdido_turnos += efecto["turnos"]
            if "texto" in efecto: print(efecto["texto"].format(objetivo=target.nombre))
                
        elif efecto["accion"] == "sobrevivir":
            usuario.vida_actual = efecto["hp"]
            
        elif efecto["accion"] == "reducir_velocidad":
            reduccion = max(1, int(target.velocidad_actual * efecto["porcentaje"]))
            target.velocidad_actual -= reduccion
            if "texto" in efecto: print(efecto["texto"].format(objetivo=target.nombre, cantidad=reduccion))
                
        elif efecto["accion"] == "cambiar_terreno":
            if estado_combate is not None:
                estado_combate["terreno"] = efecto["terreno"]
                if "texto" in efecto: print(efecto["texto"])

def procesar_trigger(trigger, usuario, objetivo, estado_combate=None):
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

        # Validar probabilidad (Si tiene)
        if "probabilidad" in datos_hab:
            if random.random() > datos_hab["probabilidad"]: continue 
            
        # ¡La habilidad se activa!
        if "texto" in datos_hab:
            print(datos_hab["texto"].format(usuario=usuario.nombre))
            
        aplicar_efectos(datos_hab["efectos"], usuario, objetivo, estado_combate)
        
        # Registrar el uso
        usuario.habilidades_usadas[nombre_hab] = usuario.habilidades_usadas.get(nombre_hab, 0) + 1
        time.sleep(1)

def ejecutar_habilidad_activa(nombre, atacante, objetivo, estado_combate):
    if nombre not in HABILIDADES_DB:
        return

    datos = HABILIDADES_DB[nombre]

    if atacante.cooldowns.get(nombre, 0) > 0:
        return

    usos_max = datos.get("usos_maximos", 99)
    if atacante.habilidades_usadas.get(nombre, 0) >= usos_max:
        return

    atacante.habilidades_usadas[nombre] = atacante.habilidades_usadas.get(nombre, 0) + 1
    atacante.cooldowns[nombre] = datos.get("cooldown", 0)

    # aquí va la lógica de la habilidad
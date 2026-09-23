import io
import sys
from flask import Flask, render_template, request, redirect, url_for
from entidades import Jugador
from guardado import cargar_partida, guardar_partida
from mapa import ZONAS, monstruos_activos, procesar_captura
from datos_monstruos import generar_monstruo
from motor import calcular_orden_turnos

app = Flask(__name__)

# Esta variable global mantendrá vivo a tu jugador mientras navega por la web
jugador_actual = None

@app.route('/')
def index():
    """Pantalla del Menú Principal"""
    error = request.args.get('error')
    return render_template('index.html', error=error)

@app.route('/nueva_partida', methods=['POST'])
def nueva_partida():
    """Procesa el formulario cuando haces clic en Nueva Partida"""
    global jugador_actual
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        nombre = "Pescador Joven"
        
    jugador_actual = Jugador(nombre)
    return redirect(url_for('menu_juego'))

@app.route('/cargar_partida', methods=['POST'])
def ruta_cargar_partida():
    """Procesa el clic en Continuar Partida"""
    global jugador_actual
    jugador_cargado = cargar_partida()
    
    if jugador_cargado:
        jugador_actual = jugador_cargado
        return redirect(url_for('menu_juego'))
    else:
        return redirect(url_for('index', error="No se encontró ninguna partida guardada."))

@app.route('/menu_juego')
def menu_juego():
    """Pantalla del Menú de Juego"""
    global jugador_actual
    if not jugador_actual:
        return redirect(url_for('index'))
        
    return render_template('menu_juego.html', jugador=jugador_actual)

@app.route('/guardar_partida_web')
def guardar_partida_web():
    """Ruta invisible que guarda y te devuelve al menú"""
    global jugador_actual
    if jugador_actual:
        guardar_partida(jugador_actual)
    return redirect(url_for('menu_juego'))

@app.route('/inventario')
def inventario():
    """Pantalla del Inventario y Equipo"""
    global jugador_actual
    if not jugador_actual:
        return redirect(url_for('index'))
    return render_template('inventario.html', jugador=jugador_actual)

@app.route('/mapa')
def mapa_mundi():
    """Pantalla de selección de Zonas"""
    global jugador_actual
    if not jugador_actual:
        return redirect(url_for('index'))
    return render_template('mapa.html', jugador=jugador_actual, zonas=ZONAS.keys())

@app.route('/zona/<nombre_zona>')
def explorar_zona(nombre_zona):
    """Muestra los monstruos dentro de una zona específica"""
    global jugador_actual
    if not jugador_actual or nombre_zona not in ZONAS:
        return redirect(url_for('mapa_mundi'))
        
    monstruos_zona = ZONAS[nombre_zona]
    return render_template('zona.html', jugador=jugador_actual, nombre_zona=nombre_zona, monstruos=monstruos_zona, activos=monstruos_activos)

# --- SISTEMA DE COMBATE WEB ---
estado_combate_web = {
    "enemigo": None,
    "terreno": None,
    "historial_logs": [], # Textos de rondas pasadas
    "nuevos_logs": [],    # Textos de la ronda que acaba de ocurrir
    "terminado": False
}

@app.route('/iniciar_combate/<nombre_enemigo>', methods=['POST'])
def iniciar_combate_web(nombre_enemigo):
    global jugador_actual, estado_combate_web
    
    if nombre_enemigo not in monstruos_activos:
        monstruos_activos[nombre_enemigo] = generar_monstruo(nombre_enemigo)
        
    estado_combate_web["enemigo"] = monstruos_activos[nombre_enemigo]
    estado_combate_web["terreno"] = request.form.get('terreno')
    estado_combate_web["historial_logs"] = []
    estado_combate_web["nuevos_logs"] = [f"¡Un {nombre_enemigo} salvaje apareció en la zona!"]
    estado_combate_web["terminado"] = False
    
    jugador_actual.restaurar_estado()
    
    return redirect(url_for('pantalla_combate'))

@app.route('/combate')
def pantalla_combate():
    global jugador_actual, estado_combate_web
    if not jugador_actual or not estado_combate_web["enemigo"]:
        return redirect(url_for('mapa_mundi'))
        
    return render_template('combate_web.html', jugador=jugador_actual, estado=estado_combate_web)

@app.route('/accion_combate', methods=['POST'])
def accion_combate():
    global jugador_actual, estado_combate_web
    enemigo = estado_combate_web["enemigo"]
    accion = request.form.get("accion")
    
    if estado_combate_web["nuevos_logs"]:
        estado_combate_web["historial_logs"].extend(estado_combate_web["nuevos_logs"])
    
    captura = io.StringIO()
    sys.stdout = captura
    
    # 1. AHORA METEMOS A TODOS AL CALDERO (Jugador + Aliados Activos + Enemigo)
    bando_jugador = [jugador_actual] + jugador_actual.equipo_aliado
    combatientes = bando_jugador + [enemigo]
    
    orden_turnos = calcular_orden_turnos(combatientes)
    
    print("\n" + "-"*30)
    print(f"⚡ ¡{orden_turnos[0]['nombre']} tiene la iniciativa y ataca primero!")
    print("-"*30)
    
    for turno in orden_turnos:
        atacante = turno["objeto"]
        
        # Validar que atacante siga vivo
        if atacante.vida_actual <= 0: continue
            
        # Condición de fin de combate: Si el enemigo muere, o si todo el bando del jugador muere
        if enemigo.vida_actual <= 0 or all(aliado.vida_actual <= 0 for aliado in bando_jugador):
            break
            
        if atacante.aturdido_turnos > 0:
            print(f"¡{atacante.nombre} está aturdido y pierde esta acción!")
            atacante.aturdido_turnos -= 1
            continue

        # 2. ¿QUIÉN ATACA? EL ADIESTRADOR O LA IA
        if atacante == jugador_actual:
            if accion == "atacar":
                jugador_actual.atacar(enemigo)
            elif accion == "pasar":
                print(f"{jugador_actual.nombre} pasa su turno.")
                
        elif atacante in jugador_actual.equipo_aliado:
            print(f"\n[Aliado] {atacante.nombre} actúa por instinto...")
            atacante.decidir_accion_ia(aliados=bando_jugador, enemigos=[enemigo], estado_combate=estado_combate_web)
            
        else:
            print(f"\n[Enemigo] {atacante.nombre} evalúa la situación...")
            atacante.decidir_accion_ia(aliados=[enemigo], enemigos=bando_jugador, estado_combate=estado_combate_web)

    sys.stdout = sys.__stdout__
    
    logs_brutos = captura.getvalue().strip().split('\n')
    estado_combate_web["nuevos_logs"] = [log for log in logs_brutos if log.strip()]
    
    # 3. VEREDICTO FINAL
    if enemigo.vida_actual <= 0:
        estado_combate_web["terminado"] = True
        estado_combate_web["nuevos_logs"].append("🏆 ¡VICTORIA! Has derrotado al enemigo.")
        procesar_captura(jugador_actual, enemigo)
        del monstruos_activos[enemigo.nombre]
        
    elif all(aliado.vida_actual <= 0 for aliado in bando_jugador):
        estado_combate_web["terminado"] = True
        estado_combate_web["nuevos_logs"].append("☠️ ¡TODO TU EQUIPO HA SIDO DERROTADO! Huyendo al mapa...")
        enemigo.restaurar_estado()

    return redirect(url_for('pantalla_combate'))
if __name__ == '__main__':
    # Arranca el servidor local
    app.run(debug=True)
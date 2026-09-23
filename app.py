from flask import Flask, render_template, request, redirect, url_for
from entidades import Jugador
from guardado import cargar_partida, guardar_partida
from mapa import ZONAS, monstruos_activos

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

if __name__ == '__main__':
    # Arranca el servidor local
    app.run(debug=True)
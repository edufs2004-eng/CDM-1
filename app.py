from flask import Flask, render_template, request, redirect, url_for
from entidades import Jugador
from guardado import cargar_partida, guardar_partida

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

if __name__ == '__main__':
    # Arranca el servidor local
    app.run(debug=True)
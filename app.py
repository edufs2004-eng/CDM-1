import io
import sys
import random

from flask import Flask, render_template, request, redirect, url_for

from motor import calcular_orden_turnos
from habilidades import HABILIDADES_DB, ejecutar_habilidad_activa
from entidades import Jugador
from guardado import cargar_partida, guardar_partida
from mapa import ZONAS, monstruos_activos, procesar_captura
from datos_monstruos import generar_monstruo
from logros import evaluar_logros
from motor_comun import ejecutar_combate as motor_combate

app = Flask(__name__)

jugador_actual = None

estado_combate_web = {
    "enemigo": None,
    "terreno": None,
    "historial_logs": [],
    "nuevos_logs": [],
    "terminado": False
}

@app.route("/")
def index():
    error = request.args.get("error")
    return render_template("index.html", error=error)

@app.route("/nueva_partida", methods=["POST"])
def nueva_partida():
    global jugador_actual
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        nombre = "Pescador Joven"

    jugador_actual = Jugador(nombre)
    return redirect(url_for("menu_juego"))

@app.route("/cargar_partida", methods=["POST"])
def cargar_partida_web():
    global jugador_actual
    partida = cargar_partida()
    if partida:
        jugador_actual = partida
        return redirect(url_for("menu_juego"))
    return redirect(url_for("index", error="No se encontró ninguna partida guardada."))

@app.route("/menu_juego")
def menu_juego():
    global jugador_actual
    if not jugador_actual:
        return redirect(url_for("index"))
    return render_template("menu_juego.html", jugador=jugador_actual)

@app.route("/guardar_partida_web")
def guardar_partida_web():
    global jugador_actual
    if jugador_actual:
        guardar_partida(jugador_actual)
    return redirect(url_for("menu_juego"))

@app.route("/inventario")
def inventario():
    global jugador_actual
    if not jugador_actual:
        return redirect(url_for("index"))
    return render_template("inventario.html", jugador=jugador_actual)

@app.route("/mapa")
def mapa_juego():
    global jugador_actual
    if not jugador_actual:
        return redirect(url_for("index"))
    return render_template("mapa.html", jugador=jugador_actual, zonas=ZONAS.keys())

@app.route("/zona/<nombre_zona>")
def zona(nombre_zona):
    global jugador_actual
    if not jugador_actual or nombre_zona not in ZONAS:
        return redirect(url_for("mapa_juego"))
    return render_template("zona.html", jugador=jugador_actual, nombre_zona=nombre_zona, monstruos=ZONAS[nombre_zona])

@app.route("/iniciar_combate/<nombre_enemigo>", methods=["POST"])
def iniciar_combate_web(nombre_enemigo):
    global jugador_actual, estado_combate_web

    if nombre_enemigo not in monstruos_activos:
        monstruos_activos[nombre_enemigo] = generar_monstruo(nombre_enemigo)

    estado_combate_web["enemigo"] = monstruos_activos[nombre_enemigo]
    estado_combate_web["terreno"] = request.form.get("terreno", "Tierra")
    estado_combate_web["historial_logs"] = []
    estado_combate_web["nuevos_logs"] = [f"¡Un {nombre_enemigo} apareció!"]
    estado_combate_web["terminado"] = False

    jugador_actual.restaurar_estado()
    for aliado in jugador_actual.equipo_aliado:
        aliado.restaurar_estado()

    return redirect(url_for("pantalla_combate"))

@app.route("/combate")
def pantalla_combate():
    global jugador_actual, estado_combate_web
    if not jugador_actual or not estado_combate_web["enemigo"]:
        return redirect(url_for("mapa_juego"))

    return render_template(
        "combate_web.html",
        jugador=jugador_actual,
        estado=estado_combate_web,
        habs_jugador=jugador_actual.obtener_habilidades_activas(),
        habs_db=HABILIDADES_DB
    )

@app.route("/accion_combate", methods=["POST"])
def accion_combate():
    global jugador_actual, estado_combate_web

    if estado_combate_web.get("terminado"):
        return redirect(url_for("pantalla_combate"))

    enemigo = estado_combate_web["enemigo"]
    accion = request.form.get("accion")

    def turno_jugador_web(atacante, objetivos, estado):
        if accion == "atacar":
            atacante.atacar(enemigo)
            return

        if accion.startswith("habilidad_"):
            nombre_hab = accion.split("habilidad_")[1]
            if nombre_hab in HABILIDADES_DB:
                ejecutar_habilidad_activa(nombre_hab, atacante, enemigo, estado)
                return

        atacante.pasar_turno()

    def turno_ia_web(atacante, objetivos, estado):
        if not objetivos:
            return
        objetivo = random.choice(objetivos)
        atacante.atacar(objetivo)

    if motor_combate is not None:
        resultado = motor_combate(
            jugador=jugador_actual,
            aliados=jugador_actual.equipo_aliado,
            enemigos=[enemigo],
            terreno=estado_combate_web["terreno"],
            turno_jugador=turno_jugador_web,
            turno_ia=turno_ia_web,
            mostrar_turno=lambda ronda: None
        )
    else:
        resultado = True

    if resultado is True:
        estado_combate_web["terminado"] = True
        estado_combate_web["nuevos_logs"].append("🏆 Victoria.")
        procesar_captura(jugador_actual, enemigo)
    elif resultado is False:
        estado_combate_web["terminado"] = True
        estado_combate_web["nuevos_logs"].append("☠️ Derrota.")

    jugador_actual.restaurar_estado()
    for aliado in jugador_actual.equipo_aliado:
        aliado.restaurar_estado()

    return redirect(url_for("pantalla_combate"))

@app.route("/equipo")
def equipo_web():
    global jugador_actual
    if not jugador_actual:
        return redirect(url_for("index"))
    return render_template("equipo.html", jugador=jugador_actual)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
import io
import sys
import random
import os

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

@app.route("/menu_juego")
def menu_juego():
    global jugador_actual
    if not jugador_actual:
        return redirect(url_for("index"))
    return render_template("menu_juego.html", jugador=jugador_actual)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
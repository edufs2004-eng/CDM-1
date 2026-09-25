import os
import unittest
from unittest.mock import patch

from entidades import Entidad, Jugador, Monstruo
from guardado import cargar_partida, guardar_partida
from mapa import verificar_restricciones_terreno
from objetos import generar_objeto


class AlphaCoreTests(unittest.TestCase):
    def test_dano_reduce_armadura_sin_ser_negativo(self):
        atacante = Entidad("Atacante", 10, 1, 1, 1)
        objetivo = Entidad("Objetivo", 10, 1, 1, 1, armadura=3)

        objetivo.recibir_dano(2, atacante)
        self.assertEqual(objetivo.vida_actual, 10)

        objetivo.recibir_dano(5, atacante)
        self.assertEqual(objetivo.vida_actual, 8)

    def test_esquive_usa_reflejos_y_velocidad(self):
        objetivo = Entidad("Objetivo", 10, 1, 10, 1)
        self.assertEqual(objetivo.calcular_esquive(), 0.6)

    def test_restricciones_de_terreno_respetan_etiquetas(self):
        jugador = Jugador("Prueba")
        jugador.equipo["Extra"] = None
        jugador.actualizar_stats()

        aliado_terrestre = Entidad("Terrestre", 5, 1, 1, 1)
        aliado_terrestre.etiquetas = ["Terrestre"]
        aliado_acuatico = Entidad("Acuatico", 5, 1, 1, 1)
        aliado_acuatico.etiquetas = ["Acuático"]

        self.assertEqual(verificar_restricciones_terreno([jugador], "Tierra"), [jugador])
        self.assertEqual(
            verificar_restricciones_terreno([aliado_terrestre], "Agua"),
            [],
        )
        self.assertEqual(
            verificar_restricciones_terreno([aliado_acuatico], "Agua"),
            [aliado_acuatico],
        )

    def test_guardado_y_carga_conservan_jugador_y_aliado(self):
        jugador = Jugador("Alpha")
        jugador.inventario.append("Tentáculo Escurridizo")
        jugador.aliados_obtenidos.append("Aliado Alpha")
        aliado = Monstruo(
            "Aliado Alpha",
            8,
            3,
            2,
            4,
            ["Terrestre"],
            armadura=1,
            peligrosidad=2.0,
            terreno="Tierra",
        )
        jugador.equipo_aliado.append(aliado)

        nombre_guardado = "_test_alpha_partida.json"
        import guardado
        guardado_original = guardado.ARCHIVO_GUARDADO
        guardado.ARCHIVO_GUARDADO = nombre_guardado
        ruta = os.path.join(os.path.dirname(guardado.__file__), nombre_guardado)
        try:
            guardar_partida(jugador)
            cargada = cargar_partida()
            self.assertEqual(cargada.nombre, "Alpha")
            self.assertEqual(cargada.inventario, ["Tentáculo Escurridizo"])
            self.assertEqual(cargada.equipo_aliado[0].nombre, "Aliado Alpha")
            self.assertEqual(cargada.equipo_aliado[0].armadura, 1)
        finally:
            guardado.ARCHIVO_GUARDADO = guardado_original
            if os.path.exists(ruta):
                os.remove(ruta)

    @patch("entidades.time.sleep")
    @patch("entidades.random.random", return_value=0.0)
    def test_ataque_esquivado_no_aplica_dano(self, _random, _sleep):
        atacante = Entidad("Atacante", 10, 3, 1, 1)
        objetivo = Entidad("Objetivo", 10, 1, 10, 1)
        vida_inicial = objetivo.vida_actual

        atacante.atacar(objetivo)

        self.assertEqual(objetivo.vida_actual, vida_inicial)

    @patch("entidades.time.sleep")
    @patch("entidades.random.randint", return_value=3)
    @patch("entidades.random.random", side_effect=[0.99, 0.99])
    def test_ataque_no_esquivado_aplica_dano(self, _random, _randint, _sleep):
        atacante = Entidad("Atacante", 10, 3, 1, 1)
        objetivo = Entidad("Objetivo", 10, 1, 0, 1)

        atacante.atacar(objetivo)

        self.assertEqual(objetivo.vida_actual, 7)

    def test_barco_del_caleuche_escuda_solo_en_agua(self):
        jugador = Jugador("Pescador")
        jugador.equipo["Extra"] = generar_objeto("Barco del Caleuche")
        jugador.actualizar_stats()
        atacante = Entidad("Atacante", 10, 1, 0, 1)

        jugador.recibir_dano(50, atacante, {"terreno": "Agua"})
        self.assertEqual(jugador.vida_actual, 10)
        self.assertEqual(jugador.escudo_actual, 50)

        jugador.recibir_dano(2, atacante, {"terreno": "Tierra"})
        self.assertEqual(jugador.vida_actual, 8)

    def test_mecanico_reduce_dano_y_bloquea_estados(self):
        mecanico = Entidad("Mecánico", 20, 1, 1, 3)
        mecanico.etiquetas = ["Mecánico"]
        atacante = Entidad("Atacante", 10, 1, 1, 1)

        mecanico.recibir_dano(10, atacante)
        self.assertEqual(mecanico.vida_actual, 11)

        from habilidades import aplicar_efectos
        aplicar_efectos([{"accion": "aturdir", "turnos": 2}], atacante, mecanico, {})
        aplicar_efectos([{"accion": "reducir_velocidad", "porcentaje": 0.5}], atacante, mecanico, {})
        self.assertEqual(mecanico.aturdido_turnos, 0)
        self.assertEqual(mecanico.velocidad_actual, 3)


if __name__ == "__main__":
    unittest.main()

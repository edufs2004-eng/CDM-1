import unittest
from unittest.mock import patch

import app as app_module
from entidades import Jugador, Monstruo
from mapa import monstruos_activos
from recompensas import EVENTO_GUARDIAN_NAUTILUS


class AlphaWebTests(unittest.TestCase):
    def setUp(self):
        self.jugador_anterior = app_module.jugador_actual
        app_module.jugador_actual = Jugador("Prueba Web")
        app_module.app.config["TESTING"] = True
        self.cliente = app_module.app.test_client()

    def tearDown(self):
        app_module.jugador_actual = self.jugador_anterior

    def test_mapa_web_muestra_zonas_canonicas(self):
        respuesta = self.cliente.get("/mapa")
        contenido = respuesta.get_data(as_text=True)

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("Tierra Firme", contenido)
        self.assertIn("Mundo Marino", contenido)
        self.assertIn("Mar Profundo", contenido)

    def test_mar_profundo_web_inicia_guardian_sin_linterna(self):
        monstruos_activos.pop("Nautilus", None)
        respuesta = self.cliente.get("/zona/Mar%20Profundo")

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/combate", respuesta.location)
        self.assertEqual(app_module.estado_combate_web["enemigo"].nombre, "Nautilus")
        self.assertFalse(app_module.estado_combate_web["enemigo_capturable"])

    def test_jugador_sin_barca_bloquea_agua_antes_de_generar_enemigo(self):
        jugador = app_module.jugador_actual
        jugador.equipo["Extra"] = None
        jugador.actualizar_stats()
        monstruos_activos.pop("Tiburón", None)

        with patch.object(app_module, "generar_monstruo") as generar:
            respuesta = self.cliente.post(
                "/iniciar_combate/Tiburón",
                data={"terreno": "Agua"},
            )

        self.assertEqual(respuesta.status_code, 302)
        self.assertNotIn("Tiburón", monstruos_activos)
        generar.assert_not_called()

        mapa = self.cliente.get(respuesta.location)
        self.assertIn("Terrestre", mapa.get_data(as_text=True))
        self.assertIn("Agua", mapa.get_data(as_text=True))

    def test_nautilus_es_guardian_unico_y_no_se_captura(self):
        jugador = app_module.jugador_actual
        monstruos_activos.pop("Nautilus", None)

        with patch.object(app_module, "generar_monstruo", wraps=app_module.generar_monstruo) as generar:
            entrada = self.cliente.get("/zona/Mar%20Profundo")
            self.assertEqual(entrada.status_code, 302)
            self.assertIn("/combate", entrada.location)
            self.assertFalse(app_module.estado_combate_web["enemigo_capturable"])
            nautilus = app_module.estado_combate_web["enemigo"]

            orden = [{"nombre": jugador.nombre, "objeto": jugador, "iniciativa": 3}]
            with patch.object(app_module, "calcular_orden_turnos", return_value=orden), \
                    patch.object(jugador, "atacar", side_effect=lambda objetivo, estado: setattr(objetivo, "vida_actual", 0)), \
                    patch.object(app_module, "procesar_captura") as capturar:
                self.cliente.post("/accion_combate", data={"accion": "atacar"})

            capturar.assert_not_called()
            self.assertIn(EVENTO_GUARDIAN_NAUTILUS, jugador.eventos_desbloqueados)
            self.assertIn("Linterna de Nautilus", jugador.inventario)
            self.assertNotIn(nautilus, jugador.equipo_aliado)
            self.assertNotIn("Nautilus", monstruos_activos)

            invocaciones = generar.call_count
            siguiente_visita = self.cliente.get("/zona/Mar%20Profundo")

        self.assertEqual(siguiente_visita.status_code, 200)
        self.assertEqual(generar.call_count, invocaciones)

    def test_derrota_web_corta_turno_y_restaura_equipo(self):
        jugador = app_module.jugador_actual
        aliado = Monstruo("Aliado", 8, 2, 1, 2, ["Terrestre", "Normal"])
        jugador.equipo_aliado = [aliado]
        monstruos_activos.pop("Goblin", None)
        self.cliente.post("/iniciar_combate/Goblin", data={"terreno": "Tierra"})
        enemigo = app_module.estado_combate_web["enemigo"]
        jugador.vida_actual = 2
        aliado.vida_actual = 1
        jugador.aturdido_turnos = 1
        aliado.aturdido_turnos = 1
        jugador.enfriamientos["Test"] = 2
        aliado.enfriamientos["Test"] = 2
        orden = [
            {"nombre": enemigo.nombre, "objeto": enemigo, "iniciativa": 3},
            {"nombre": enemigo.nombre, "objeto": enemigo, "iniciativa": 2},
        ]

        def derrota(aliados, enemigos, estado_combate):
            jugador.vida_actual = 0

        with (
            patch.object(app_module, "calcular_orden_turnos", return_value=orden),
            patch.object(enemigo, "decidir_accion_ia", side_effect=derrota) as actuar,
        ):
            respuesta = self.cliente.post("/accion_combate", data={"accion": "pasar"})

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(actuar.call_count, 1)
        self.assertTrue(app_module.estado_combate_web["terminado"])
        self.assertEqual(jugador.vida_actual, jugador.vida_max)
        self.assertEqual(aliado.vida_actual, aliado.vida_max)
        self.assertEqual(jugador.aturdido_turnos, 0)
        self.assertEqual(aliado.aturdido_turnos, 0)
        self.assertEqual(jugador.enfriamientos, {})
        self.assertEqual(aliado.enfriamientos, {})

    def test_arena_web_oculta_aliado_invalido_para_agua(self):
        goblin = Monstruo("Goblin", 4, 1, 1, 2, ["Terrestre"])
        app_module.jugador_actual.equipo_aliado = [goblin]
        monstruos_activos.pop("Tiburón", None)

        inicio = self.cliente.post(
            "/iniciar_combate/Tiburón",
            data={"terreno": "Agua"},
        )
        respuesta = self.cliente.get("/combate")
        contenido = respuesta.get_data(as_text=True)

        self.assertEqual(inicio.status_code, 302)
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("Goblin", contenido)

    def test_inventario_web_equipa_cambia_y_desequipa_objetos(self):
        jugador = app_module.jugador_actual
        jugador.inventario.append("Hacha de fuego")

        respuesta = self.cliente.post(
            "/gestionar_equipo",
            data={"accion": "equipar", "objeto": "Hacha de fuego"},
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(jugador.equipo["Mano 1"].nombre, "Hacha de fuego")
        self.assertIn("Caña de pescar", jugador.inventario)
        self.assertNotIn("Hacha de fuego", jugador.inventario)
        self.assertEqual(jugador.ataque_base, 5)
        self.assertEqual(jugador.varianza_ataque, 2)

        respuesta = self.cliente.post(
            "/gestionar_equipo",
            data={"accion": "desequipar", "slot": "Mano 1"},
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertIsNone(jugador.equipo["Mano 1"])
        self.assertIn("Hacha de fuego", jugador.inventario)
        self.assertEqual(jugador.ataque_base, 1)

    def test_no_equipa_un_objeto_que_no_esta_en_la_mochila(self):
        jugador = app_module.jugador_actual
        mano_inicial = jugador.equipo["Mano 1"]

        respuesta = self.cliente.post(
            "/gestionar_equipo",
            data={"accion": "equipar", "objeto": "Hacha de fuego"},
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertIs(jugador.equipo["Mano 1"], mano_inicial)


if __name__ == "__main__":
    unittest.main()

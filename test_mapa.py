import unittest
from unittest.mock import patch

from entidades import Jugador, Monstruo
from mapa import (
    ZONAS_CANONICAS,
    procesar_captura,
    tiene_objeto,
    obtener_combatientes_validos,
    verificar_restricciones_terreno,
    zona_accesible,
    motivo_acceso_combate,
    menu_zona,
    monstruos_activos,
)
from recompensas import EVENTO_GUARDIAN_NAUTILUS


class MapaTests(unittest.TestCase):
    def test_existen_las_zonas_canonicas(self):
        self.assertEqual(
            set(ZONAS_CANONICAS),
            {"Tierra Firme", "Mundo Marino", "Mar Profundo"},
        )

    def test_mar_profundo_solo_requiere_la_linterna(self):
        jugador = Jugador("Prueba")

        self.assertFalse(zona_accesible(jugador, "Mar Profundo"))
        self.assertFalse(tiene_objeto(jugador, "Linterna de Nautilus"))

        jugador.inventario.append("Linterna de Nautilus")

        self.assertTrue(zona_accesible(jugador, "Mar Profundo"))
        self.assertTrue(tiene_objeto(jugador, "Linterna de Nautilus"))

    def test_el_jugador_puede_combatir_en_tierra(self):
        jugador = Jugador("Prueba")

        validos = verificar_restricciones_terreno([jugador], "Tierra")

        self.assertEqual(validos, [jugador])

    def test_jugador_sin_barca_no_accede_a_agua_y_recibe_motivo(self):
        jugador = Jugador("Prueba")
        jugador.equipo["Extra"] = None
        jugador.actualizar_stats()

        motivo = motivo_acceso_combate(jugador, "Agua")

        self.assertIn("Terrestre", motivo)
        self.assertIn("Agua", motivo)
        self.assertIn("Barca", motivo)

    def test_consola_no_genera_enemigo_si_jugador_no_accede_al_terreno(self):
        jugador = Jugador("Prueba")
        jugador.equipo["Extra"] = None
        jugador.actualizar_stats()
        monstruos_activos.pop("Tiburón", None)

        with patch("builtins.input", side_effect=["2", "7"]), \
            patch("mapa.generar_monstruo") as generar, \
            patch("builtins.print"):
            menu_zona(jugador, "Mundo Marino")

        generar.assert_not_called()
        self.assertNotIn("Tiburón", monstruos_activos)

    def test_consola_dispara_nautilus_una_vez_y_otorga_linterna(self):
        jugador = Jugador("Prueba")
        monstruos_activos.pop("Nautilus", None)

        with patch("builtins.input", return_value="2"), \
            patch("mapa.iniciar_combate", return_value=True) as combate, \
            patch("builtins.print"):
            menu_zona(jugador, "Mar Profundo")

        combate.assert_called_once()
        self.assertEqual(combate.call_args.args[2][0].nombre, "Nautilus")
        self.assertIn(EVENTO_GUARDIAN_NAUTILUS, jugador.eventos_desbloqueados)
        self.assertIn("Linterna de Nautilus", jugador.inventario)
        self.assertNotIn("Nautilus", jugador.aliados_obtenidos)

        with patch("builtins.input", return_value="2"), \
                patch("mapa.iniciar_combate") as combate_repetido, \
                patch("builtins.print"):
            menu_zona(jugador, "Mar Profundo")
        combate_repetido.assert_not_called()

    def test_guardian_nautilus_completo_transiciona_tres_fases_y_no_se_repite(self):
        import combate

        jugador = Jugador("Pescador")
        monstruos_activos.pop("Nautilus", None)
        fases_atacadas = []

        def responder(prompt):
            if prompt.startswith("Elige una opción"):
                return "1"
            if prompt.startswith("Número del objetivo"):
                return "1"
            return "2"

        def ataque_letal(objetivo, estado):
            fases_atacadas.append(objetivo.fase_actual)
            objetivo.recibir_dano(9999, jugador, estado)

        with (
            patch("builtins.input", side_effect=responder),
            patch("combate.time.sleep"),
            patch("combate.calcular_orden_turnos", side_effect=lambda combatientes, estado: [
                {"nombre": jugador.nombre, "objeto": jugador, "iniciativa": 3}
            ]),
            patch.object(jugador, "atacar", side_effect=ataque_letal),
            patch("builtins.print"),
        ):
            menu_zona(jugador, "Mar Profundo")

        self.assertEqual(fases_atacadas, [1, 2, 3])
        self.assertIn(EVENTO_GUARDIAN_NAUTILUS, jugador.eventos_desbloqueados)
        self.assertIn("Linterna de Nautilus", jugador.inventario)
        self.assertNotIn("Nautilus", jugador.aliados_obtenidos)
        self.assertNotIn("Nautilus", monstruos_activos)

        with (
            patch("builtins.input", return_value="2"),
            patch("mapa.iniciar_combate") as combate_repetido,
            patch("builtins.print"),
        ):
            menu_zona(jugador, "Mar Profundo")
        combate_repetido.assert_not_called()

    def test_consola_derrota_restaura_jugador_aliados_y_enemigo(self):
        jugador = Jugador("Pescador")
        aliado = Monstruo("Aliado", 8, 2, 1, 2, ["Terrestre", "Normal"])
        jugador.equipo_aliado = [aliado]
        jugador.vida_actual = 2
        aliado.vida_actual = 1
        enemigo = Monstruo("Goblin", 4, 1, 1, 2, ["Terrestre", "Normal"])
        enemigo.vida_actual = 2
        monstruos_activos.pop("Goblin", None)

        def perder_combate(*args, **kwargs):
            jugador.vida_actual = 0
            aliado.vida_actual = 0
            enemigo.vida_actual = 0
            return False

        with (
            patch("builtins.input", side_effect=["1", "5"]),
            patch("mapa.generar_monstruo", return_value=enemigo),
            patch("mapa.iniciar_combate", side_effect=perder_combate),
            patch("builtins.print"),
        ):
            menu_zona(jugador, "Tierra Firme")

        self.assertEqual(jugador.vida_actual, jugador.vida_max)
        self.assertEqual(aliado.vida_actual, aliado.vida_max)
        self.assertEqual(enemigo.vida_actual, enemigo.vida_max)

    def test_hacha_consola_usa_hp_justo_antes_de_derrotar_al_ogro(self):
        for hp_before_kill, should_get_axe in ((6, True), (5, False), (4, False)):
            with self.subTest(hp_before_kill=hp_before_kill):
                jugador = Jugador("Prueba Hacha")
                jugador.vida_actual = hp_before_kill
                ogro = Monstruo("Ogro de Fuego", 20, 5, 2, 4, ["Terrestre", "Normal"])
                monstruos_activos.pop("Ogro de Fuego", None)

                with (
                    patch("builtins.input", side_effect=["3", "5"]),
                    patch("mapa.generar_monstruo", return_value=ogro),
                    patch("mapa.iniciar_combate", return_value=True),
                    patch("builtins.print"),
                ):
                    menu_zona(jugador, "Tierra Firme")

                self.assertEqual(jugador.vida_actual, jugador.vida_max)
                self.assertEqual("Hacha de fuego" in jugador.inventario, should_get_axe)

    def test_captura_devuelve_si_es_nueva_y_conserva_peligrosidad(self):
        jugador = Jugador("Prueba")
        monstruo = Monstruo(
            "Criatura de prueba",
            5,
            1,
            1,
            1,
            ["Terrestre"],
            peligrosidad=2.5,
            terreno="Tierra",
        )

        self.assertTrue(procesar_captura(jugador, monstruo))
        self.assertIn("Criatura de prueba", jugador.aliados_obtenidos)
        self.assertFalse(procesar_captura(jugador, monstruo))

    def test_aliado_invalido_no_participa_en_agua_y_entra_en_hibrido(self):
        jugador = Jugador("Prueba")
        goblin = Monstruo("Goblin", 4, 1, 1, 2, ["Terrestre"])
        jugador.equipo_aliado = [goblin]

        combatientes_agua, inactivos = obtener_combatientes_validos(jugador, "Agua")
        self.assertNotIn(goblin, combatientes_agua)
        self.assertIn(goblin, inactivos)

        combatientes_hibrido, inactivos_hibrido = obtener_combatientes_validos(jugador, "Híbrido")
        self.assertIn(goblin, combatientes_hibrido)
        self.assertNotIn(goblin, inactivos_hibrido)


if __name__ == "__main__":
    unittest.main()

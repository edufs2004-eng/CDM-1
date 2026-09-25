import unittest

from entidades import Jugador, Monstruo
from mapa import (
    ZONAS_CANONICAS,
    procesar_captura,
    tiene_objeto,
    obtener_combatientes_validos,
    verificar_restricciones_terreno,
    zona_accesible,
)


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

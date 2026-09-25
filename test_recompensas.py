import unittest

from entidades import Jugador, Monstruo
from recompensas import evaluar_recompensas_victoria


class RecompensasTests(unittest.TestCase):
    def test_pulpo_otorga_recompensa_fija_una_sola_vez(self):
        jugador = Jugador("Prueba")
        enemigo = Monstruo("Pulpo Inteligente", 8, 2, 1, 2, ["Híbrido"])

        primera = evaluar_recompensas_victoria(jugador, enemigo)
        segunda = evaluar_recompensas_victoria(jugador, enemigo)

        self.assertIn("Palo de madera con hojita", jugador.inventario)
        self.assertTrue(primera)
        self.assertFalse(segunda)
        self.assertEqual(jugador.inventario.count("Palo de madera con hojita"), 1)

    def test_decima_victoria_de_tiburon_y_megalodon_entrega_objetos(self):
        jugador = Jugador("Prueba")
        tiburon = Monstruo("Tiburón", 8, 2, 2, 5, ["Acuático"])
        megalodon = Monstruo("Megalodón", 18, 5, 1, 4, ["Acuático"])

        for _ in range(10):
            evaluar_recompensas_victoria(jugador, tiburon)
            evaluar_recompensas_victoria(jugador, megalodon)

        self.assertIn("Corona de dientes de tiburón", jugador.inventario)
        self.assertIn("Armadura de dientes de megalodón", jugador.inventario)
        self.assertEqual(jugador.contadores_eventos["Tiburón"], 10)
        self.assertEqual(jugador.contadores_eventos["Megalodón"], 10)

    def test_hacha_requiere_derrotar_ogro_con_menos_de_mitad_de_vida(self):
        jugador = Jugador("Prueba")
        ogro = Monstruo("Ogro de Fuego", 20, 5, 2, 4, ["Terrestre"])

        jugador.vida_actual = 4
        logs = evaluar_recompensas_victoria(jugador, ogro)

        self.assertIn("Hacha de fuego", jugador.inventario)
        self.assertTrue(logs)

    def test_tres_aliados_acuaticos_desbloquean_cana_experto(self):
        jugador = Jugador("Prueba")
        jugador.equipo_aliado = [
            Monstruo("A", 5, 1, 1, 1, ["Acuático"]),
            Monstruo("B", 5, 1, 1, 1, ["Híbrido"]),
            Monstruo("C", 5, 1, 1, 1, ["Acuático"]),
        ]
        enemigo = Monstruo("Tiburón", 8, 2, 2, 5, ["Acuático"])

        evaluar_recompensas_victoria(jugador, enemigo)

        self.assertIn("Caña de pescar de experto", jugador.inventario)

    def test_cuatro_revividos_en_la_ronda_desbloquean_espada(self):
        jugador = Jugador("Prueba")
        jugador.aliados_revividos_ronda = 4
        enemigo = Monstruo("Tiburón", 8, 2, 2, 5, ["Acuático"])

        evaluar_recompensas_victoria(jugador, enemigo)

        self.assertIn("Espada del capitán", jugador.inventario)


if __name__ == "__main__":
    unittest.main()

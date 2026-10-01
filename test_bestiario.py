import unittest

from datos_monstruos import MONSTRUOS_DB, generar_monstruo
from entidades import Jugador
from habilidades import HABILIDADES_DB
from mapa import procesar_captura


BESTIARIO_ALPHA = {
    "Goblin": ([2, 4], [1, 2], [1, 1], [1, 2], [0, 0], 0.3),
    "Troll": ([14, 20], [3, 4], [1, 1], [2, 4], [2, 4], 2.6),
    "Ogro de Fuego": ([20, 22], [5, 6], [2, 3], [4, 5], [0, 0], 3.8),
    "Cíclope": ([40, 50], [4, 8], [1, 1], [2, 3], [2, 3], 4.0),
    "Pulpo Inteligente": ([6, 8], [1, 3], [1, 1], [2, 3], [0, 0], 0.9),
    "Tiburón": ([7, 10], [2, 5], [2, 3], [5, 6], [0, 0], 1.0),
    "Monstruo del Lago Ness": ([10, 14], [2, 4], [4, 5], [4, 6], [0, 0], 2.1),
    "Megalodón": ([15, 22], [5, 6], [1, 3], [4, 5], [0, 0], 2.3),
    "Serpiente Marina": ([12, 18], [5, 8], [4, 6], [8, 12], [0, 0], 2.9),
    "Kraken": ([20, 25], [8, 9], [1, 2], [2, 3], [0, 0], 2.9),
    "Capitán del Caleuche": ([40, 55], [10, 10], [5, 8], [3, 4], [0, 0], 4.9),
    "Nautilus": ([80, 80], [8, 8], [1, 1], [6, 6], [10, 10], 5.9),
}


class BestiarioTests(unittest.TestCase):
    def test_catalogo_alpha_contiene_solo_monstruos_cerrados(self):
        self.assertEqual(set(MONSTRUOS_DB), set(BESTIARIO_ALPHA))
        self.assertNotIn("Leviatán", MONSTRUOS_DB)

    def test_rangos_y_peligrosidad_siguen_la_guia(self):
        for nombre, rangos in BESTIARIO_ALPHA.items():
            datos = MONSTRUOS_DB[nombre]
            self.assertEqual(datos["vida"], rangos[0], nombre)
            self.assertEqual(datos["ataque"], rangos[1], nombre)
            self.assertEqual(datos["reflejos"], rangos[2], nombre)
            self.assertEqual(datos["velocidad"], rangos[3], nombre)
            self.assertEqual(datos["armadura"], rangos[4], nombre)
            self.assertEqual(datos["peligrosidad"], rangos[5], nombre)

    def test_intervalos_ia_son_decimales_y_refieren_habilidades_ia(self):
        self.assertEqual(
            MONSTRUOS_DB["Ogro de Fuego"]["probabilidades_ia"]["Círculo de fuego"],
            [0.1, 0.5],
        )
        self.assertEqual(
            MONSTRUOS_DB["Megalodón"]["probabilidades_ia"]["Gran mordisco"],
            [0.25, 0.55],
        )

        for datos in MONSTRUOS_DB.values():
            for nombre, intervalo in datos.get("probabilidades_ia", {}).items():
                self.assertEqual(HABILIDADES_DB[nombre]["tipo"], "ia")
                self.assertGreaterEqual(intervalo[0], 0.0)
                self.assertLessEqual(intervalo[1], 1.0)
                self.assertLessEqual(intervalo[0], intervalo[1])

    def test_generacion_conserva_los_rangos_del_catalogo(self):
        for nombre, rangos in BESTIARIO_ALPHA.items():
            monstruo = generar_monstruo(nombre)
            self.assertGreaterEqual(monstruo.vida_max, rangos[0][0], nombre)
            self.assertLessEqual(monstruo.vida_max, rangos[0][1], nombre)
            self.assertGreaterEqual(monstruo.ataque_base, rangos[1][0], nombre)
            self.assertLessEqual(monstruo.ataque_base, rangos[1][1], nombre)
            self.assertGreaterEqual(monstruo.reflejos, rangos[2][0], nombre)
            self.assertLessEqual(monstruo.reflejos, rangos[2][1], nombre)
            self.assertGreaterEqual(monstruo.velocidad_base, rangos[3][0], nombre)
            self.assertLessEqual(monstruo.velocidad_base, rangos[3][1], nombre)
            self.assertGreaterEqual(monstruo.armadura, rangos[4][0], nombre)
            self.assertLessEqual(monstruo.armadura, rangos[4][1], nombre)
            self.assertEqual(monstruo.peligrosidad, rangos[5])

    def test_kraken_transiciona_al_llegar_a_cero(self):
        kraken = generar_monstruo("Kraken")
        atacante = generar_monstruo("Tiburón")
        vida_inicial = kraken.vida_max
        ataque_inicial = kraken.ataque_base

        kraken.recibir_dano(999, atacante)

        self.assertEqual(kraken.fase_actual, 2)
        self.assertEqual(kraken.vida_max, round(vida_inicial * 0.8))
        self.assertEqual(kraken.vida_actual, round(vida_inicial * 0.8))
        self.assertEqual(kraken.ataque_base, round(ataque_inicial * 1.4))
        self.assertEqual(atacante.aturdido_turnos, 3)

    def test_restaurar_estado_devuelve_un_monstruo_a_fase_uno(self):
        kraken = generar_monstruo("Kraken")
        atacante = generar_monstruo("Tiburón")
        vida_inicial = kraken.vida_max
        ataque_inicial = kraken.ataque_base

        kraken.recibir_dano(999, atacante)
        kraken.restaurar_estado()

        self.assertEqual(kraken.fase_actual, 1)
        self.assertEqual(kraken.vida_max, vida_inicial)
        self.assertEqual(kraken.ataque_base, ataque_inicial)

    def test_monstruo_salvaje_activa_fase_al_llegar_a_cero(self):
        troll = generar_monstruo("Troll")
        atacante = generar_monstruo("Tiburón")

        troll.recibir_dano(999, atacante)

        self.assertEqual(troll.fase_actual, 2)
        self.assertTrue(troll.fase_en_encuentro)
        self.assertGreater(troll.vida_actual, 0)

    def test_captura_reinicia_monstruo_a_fase_uno(self):
        jugador = Jugador("Pescador")
        troll = generar_monstruo("Troll")
        atacante = generar_monstruo("Tiburón")
        troll.recibir_dano(999, atacante)

        self.assertEqual(troll.fase_actual, 2)
        self.assertTrue(procesar_captura(jugador, troll))
        self.assertEqual(troll.fase_actual, 1)
        self.assertFalse(troll.fase_en_encuentro)

    def test_kraken_aliado_solo_avanza_por_furia_del_mar(self):
        jugador = Jugador("Pescador")
        kraken = generar_monstruo("Kraken")
        atacante = generar_monstruo("Tiburón")
        self.assertTrue(procesar_captura(jugador, kraken))
        self.assertEqual(kraken.fase_actual, 1)
        self.assertFalse(kraken.fase_en_encuentro)

        kraken.recibir_dano(999, atacante)

        self.assertEqual(kraken.fase_actual, 2)
        self.assertGreater(kraken.vida_actual, 0)

    def test_ogro_fase_dos_actualiza_probabilidades_de_habilidades(self):
        ogro = generar_monstruo("Ogro de Fuego")
        atacante = generar_monstruo("Tiburón")
        probabilidad_circulo_inicial = ogro.probabilidades_ia["Círculo de fuego"]

        ogro.recibir_dano(999, atacante)

        self.assertEqual(ogro.fase_actual, 2)
        self.assertEqual(
            ogro.probabilidades_ia["Círculo de fuego"],
            min(1.0, probabilidad_circulo_inicial * 1.2),
        )
        self.assertEqual(ogro.probabilidades_trigger["Puños en llamas"], 0.30)
        self.assertEqual(ogro.probabilidades_trigger_circulo["Puños en llamas"], 0.45)

    def test_serpiente_marina_transiciona_a_su_fase_dos(self):
        serpiente = generar_monstruo("Serpiente Marina")
        atacante = generar_monstruo("Tiburón")
        vida_inicial = serpiente.vida_max
        ataque_inicial = serpiente.ataque_base
        velocidad_inicial = serpiente.velocidad_base
        reflejos_iniciales = serpiente.reflejos

        serpiente.recibir_dano(999, atacante)

        self.assertEqual(serpiente.fase_actual, 2)
        self.assertEqual(serpiente.vida_max, round(vida_inicial * 1.1))
        self.assertEqual(serpiente.ataque_base, round(ataque_inicial * 1.2))
        self.assertEqual(serpiente.velocidad_base, round(velocidad_inicial * 1.1))
        self.assertEqual(serpiente.reflejos, round(reflejos_iniciales * 1.1))

    def test_nautilus_transiciona_por_tres_fases_en_orden(self):
        nautilus = generar_monstruo("Nautilus")
        atacante = generar_monstruo("Megalodón")

        nautilus.recibir_dano(999, atacante)
        self.assertEqual(nautilus.fase_actual, 2)
        self.assertEqual((nautilus.vida_max, nautilus.ataque_base, nautilus.velocidad_base, nautilus.armadura), (100, 10, 8, 6))

        nautilus.recibir_dano(999, atacante)
        self.assertEqual(nautilus.fase_actual, 3)
        self.assertEqual((nautilus.vida_max, nautilus.ataque_base, nautilus.velocidad_base, nautilus.armadura), (70, 15, 5, 1))


if __name__ == "__main__":
    unittest.main()

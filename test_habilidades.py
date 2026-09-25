import unittest
from unittest.mock import patch

from entidades import Jugador, Monstruo
from habilidades import (
    HABILIDADES_DB,
    aplicar_efectos,
    ejecutar_habilidad_activa,
    puede_usar_habilidad,
    reducir_cooldowns,
    seleccionar_habilidad_ia,
    ataque_permitido,
)
from motor import calcular_orden_turnos
from combate import filtrar_objetivos_validos


class HabilidadesTests(unittest.TestCase):
    def test_uso_maximo_bloquea_un_segundo_uso(self):
        usuario = Monstruo(
            "Serpiente",
            10,
            2,
            1,
            3,
            ["Acuático"],
            habilidades=["Tsunami"],
        )
        estado = {"terreno": "Tierra"}

        with patch("habilidades.time.sleep"):
            self.assertTrue(ejecutar_habilidad_activa("Tsunami", usuario, None, estado))
            self.assertFalse(puede_usar_habilidad(usuario, "Tsunami"))
            self.assertFalse(ejecutar_habilidad_activa("Tsunami", usuario, None, estado))

        self.assertEqual(usuario.habilidades_usadas["Tsunami"], 1)

    def test_cooldown_se_reduce_al_avanzar_rondas(self):
        nombre = "Habilidad de prueba"
        HABILIDADES_DB[nombre] = {
            "tipo": "activa",
            "cooldown": 2,
            "efectos": [],
        }
        usuario = Monstruo(
            "Prueba",
            10,
            2,
            1,
            3,
            ["Terrestre"],
            habilidades=[nombre],
        )

        try:
            with patch("habilidades.time.sleep"):
                self.assertTrue(ejecutar_habilidad_activa(nombre, usuario, None, {}))
            self.assertEqual(usuario.enfriamientos[nombre], 2)
            self.assertFalse(puede_usar_habilidad(usuario, nombre))

            reducir_cooldowns([usuario])
            self.assertEqual(usuario.enfriamientos[nombre], 1)
            self.assertFalse(puede_usar_habilidad(usuario, nombre))

            reducir_cooldowns([usuario])
            self.assertEqual(usuario.enfriamientos, {})
            self.assertTrue(puede_usar_habilidad(usuario, nombre))
        finally:
            del HABILIDADES_DB[nombre]

    def test_ia_prioriza_la_probabilidad_mas_alta(self):
        nombres = ("Habilidad baja", "Habilidad alta")
        HABILIDADES_DB.update({
            nombres[0]: {"tipo": "ia", "efectos": []},
            nombres[1]: {"tipo": "ia", "efectos": []},
        })
        usuario = Monstruo(
            "Prueba",
            10,
            2,
            1,
            3,
            ["Terrestre"],
            probabilidades_ia={nombres[0]: 20, nombres[1]: 80},
        )

        try:
            with patch("habilidades.random.randint", return_value=1):
                self.assertEqual(seleccionar_habilidad_ia(usuario), nombres[1])
        finally:
            for nombre in nombres:
                del HABILIDADES_DB[nombre]

    def test_ia_desliza_el_rango_si_una_habilidad_no_esta_disponible(self):
        nombres = ("Habilidad bloqueada", "Habilidad disponible")
        HABILIDADES_DB.update({
            nombres[0]: {"tipo": "ia", "efectos": []},
            nombres[1]: {"tipo": "ia", "efectos": []},
        })
        usuario = Monstruo(
            "Prueba",
            10,
            2,
            1,
            3,
            ["Terrestre"],
            probabilidades_ia={nombres[0]: 80, nombres[1]: 20},
        )
        usuario.enfriamientos[nombres[0]] = 1

        try:
            with patch("habilidades.random.randint", return_value=1):
                self.assertEqual(seleccionar_habilidad_ia(usuario), nombres[1])
        finally:
            for nombre in nombres:
                del HABILIDADES_DB[nombre]

    def test_ia_devuelve_ataque_basico_fuera_de_la_ventana(self):
        nombre = "Habilidad parcial"
        HABILIDADES_DB[nombre] = {"tipo": "ia", "efectos": []}
        usuario = Monstruo(
            "Prueba",
            10,
            2,
            1,
            3,
            ["Terrestre"],
            probabilidades_ia={nombre: 40},
        )

        try:
            with patch("habilidades.random.randint", return_value=100):
                self.assertIsNone(seleccionar_habilidad_ia(usuario))
        finally:
            del HABILIDADES_DB[nombre]

    def test_quemadura_aplica_la_escala_normativa(self):
        objetivo = Monstruo("Objetivo", 20, 1, 1, 1, ["Terrestre"])

        objetivo.aplicar_quemadura(2)
        objetivo.procesar_estados_ronda()
        self.assertEqual(objetivo.vida_actual, 19)

        objetivo.aplicar_quemadura(2)
        objetivo.procesar_estados_ronda()
        self.assertEqual(objetivo.vida_actual, 17)

        objetivo.aplicar_quemadura(1)
        objetivo.procesar_estados_ronda()
        self.assertEqual(objetivo.vida_actual, 14)

    def test_quemadura_puede_purificarse_y_mecanico_es_inmune(self):
        objetivo = Monstruo("Objetivo", 20, 1, 1, 1, ["Terrestre"])
        mecanico = Monstruo("Mecanico", 20, 1, 1, 1, ["Mecánico"])

        self.assertTrue(objetivo.aplicar_quemadura())
        self.assertTrue(objetivo.purificar_quemadura())
        self.assertEqual(objetivo.quemadura_cargas, 0)
        self.assertFalse(mecanico.aplicar_quemadura())
        self.assertEqual(mecanico.quemadura_cargas, 0)

    def test_quemadura_se_procesa_una_vez_por_ronda_global(self):
        objetivo = Monstruo("Objetivo", 20, 1, 1, 10, ["Terrestre"])
        lento = Monstruo("Lento", 20, 1, 1, 2, ["Terrestre"])
        objetivo.aplicar_quemadura()

        with patch("motor.time.sleep"):
            orden = calcular_orden_turnos([objetivo, lento])

        self.assertGreater(len(orden), 1)
        self.assertEqual(objetivo.vida_actual, 19)

    def test_efecto_de_habilidad_puede_aplicar_y_purificar(self):
        objetivo = Monstruo("Objetivo", 20, 1, 1, 1, ["Terrestre"])
        usuario = Monstruo("Usuario", 20, 1, 1, 1, ["Terrestre"])

        aplicar_efectos(
            [{"accion": "aplicar_quemadura", "cargas": 2}],
            usuario,
            objetivo,
            {},
        )
        self.assertEqual(objetivo.quemadura_cargas, 2)
        aplicar_efectos(
            [{"accion": "purificar_quemadura"}],
            usuario,
            objetivo,
            {},
        )
        self.assertEqual(objetivo.quemadura_cargas, 0)

    def test_punos_en_llamas_aplica_quemadura_por_trigger(self):
        atacante = Monstruo(
            "Ogro de Fuego",
            20,
            5,
            2,
            4,
            ["Terrestre"],
            habilidades=["Puños en llamas"],
        )
        objetivo = Monstruo("Objetivo", 20, 1, 1, 1, ["Terrestre"])

        with patch("habilidades.random.random", return_value=0.0):
            from habilidades import procesar_trigger
            procesar_trigger("al_atacar", atacante, objetivo)

        self.assertEqual(objetivo.quemadura_cargas, 1)

    def test_chorro_de_agua_purifica_al_usuario(self):
        usuario = Monstruo(
            "Monstruo del Lago Ness",
            12,
            2,
            4,
            5,
            ["Acuático"],
            habilidades=["Chorro de agua"],
        )
        usuario.aplicar_quemadura(3)

        with patch("habilidades.time.sleep"):
            self.assertTrue(ejecutar_habilidad_activa("Chorro de agua", usuario, None, {}))

        self.assertEqual(usuario.quemadura_cargas, 0)

    def test_inalcanzable_excluye_al_objetivo_y_expira(self):
        usuario = Monstruo("Usuario", 20, 1, 1, 1, ["Terrestre"])
        objetivo = Monstruo("Objetivo", 20, 1, 1, 1, ["Terrestre"])

        aplicar_efectos(
            [{"accion": "hacer_inalcanzable", "turnos": 2}],
            usuario,
            objetivo,
            {},
        )
        self.assertEqual(filtrar_objetivos_validos([objetivo]), [])

        objetivo.procesar_estados_ronda()
        self.assertEqual(filtrar_objetivos_validos([objetivo]), [])
        objetivo.procesar_estados_ronda()
        self.assertEqual(filtrar_objetivos_validos([objetivo]), [objetivo])

    def test_circulo_de_fuego_aísla_dos_entidades_y_expira(self):
        usuario = Monstruo("Ogro", 20, 5, 2, 4, ["Terrestre"])
        objetivo = Monstruo("Objetivo", 20, 1, 1, 1, ["Terrestre"])
        tercero = Monstruo("Tercero", 20, 1, 1, 1, ["Terrestre"])
        estado = {"terreno": "Tierra"}

        with patch("habilidades.time.sleep"):
            self.assertTrue(ejecutar_habilidad_activa("Círculo de fuego", usuario, objetivo, estado))

        self.assertTrue(ataque_permitido(usuario, objetivo, estado))
        self.assertFalse(ataque_permitido(tercero, objetivo, estado))
        self.assertFalse(ataque_permitido(usuario, tercero, estado))

        with patch("motor.time.sleep"):
            calcular_orden_turnos([usuario, objetivo, tercero], estado)
            self.assertIn("circulo_fuego", estado)
            calcular_orden_turnos([usuario, objetivo, tercero], estado)

        self.assertNotIn("circulo_fuego", estado)

    def test_no_muerto_revive_con_la_vida_del_turno_anterior(self):
        usuario = Monstruo(
            "Capitán del Caleuche",
            40,
            10,
            5,
            3,
            ["Terrestre"],
            habilidades=["No muerto"],
        )
        atacante = Monstruo("Atacante", 10, 1, 1, 1, ["Terrestre"])
        usuario.vida_actual = 18
        usuario.vida_turno_anterior = 18

        with patch("habilidades.random.random", return_value=0.0):
            usuario.recibir_dano(999, atacante)

        self.assertEqual(usuario.vida_actual, 18)

    def test_no_muerto_puede_fallar_por_probabilidad(self):
        usuario = Monstruo(
            "Capitán del Caleuche",
            40,
            10,
            5,
            3,
            ["Terrestre"],
            habilidades=["No muerto"],
        )
        atacante = Monstruo("Atacante", 10, 1, 1, 1, ["Terrestre"])
        usuario.vida_turno_anterior = 18

        with patch("habilidades.random.random", return_value=0.99):
            usuario.recibir_dano(999, atacante)

        self.assertEqual(usuario.vida_actual, 0)

    def test_mejor_amigo_intercepta_dos_danos_letales(self):
        jugador = Jugador("Pescador")
        troll = Monstruo(
            "Troll",
            14,
            3,
            1,
            2,
            ["Terrestre"],
            habilidades=["Mejor amigo"],
            armadura=2,
        )
        atacante = Monstruo("Atacante", 10, 1, 1, 1, ["Terrestre"])
        jugador.guardianes = [troll]

        jugador.recibir_dano(11, atacante)
        self.assertEqual(jugador.vida_actual, 10)
        self.assertEqual(troll.vida_actual, 5)
        self.assertEqual(troll.habilidades_usadas["Mejor amigo"], 1)

        jugador.recibir_dano(11, atacante)
        self.assertEqual(jugador.vida_actual, 10)
        self.assertEqual(troll.vida_actual, 0)
        self.assertEqual(jugador.inalcanzable_turnos, 2)

        jugador.recibir_dano(11, atacante)
        self.assertEqual(jugador.vida_actual, 0)

    def test_comida_reemplaza_el_golpe_y_cura_el_dano_real(self):
        atacante = Monstruo(
            "Cíclope",
            20,
            3,
            1,
            2,
            ["Terrestre", "Gigante"],
            habilidades=["Comida"],
        )
        objetivo = Monstruo("Objetivo", 20, 1, 1, 1, ["Terrestre"])
        atacante.vida_actual = 10

        with patch("entidades.random.random", side_effect=[0.0, 0.99]):
            atacante.atacar(objetivo)

        self.assertEqual(objetivo.vida_actual, 17)
        self.assertEqual(atacante.vida_actual, 13)

    def test_gran_mordisco_multiplica_sin_varianza_y_usa_cooldown(self):
        atacante = Monstruo(
            "Megalodón",
            20,
            6,
            1,
            4,
            ["Acuático"],
            habilidades=["Gran mordisco"],
        )
        objetivo = Monstruo("Objetivo", 30, 1, 0, 1, ["Terrestre"])
        estado = {"terreno": "Agua"}

        with patch("habilidades.time.sleep"), patch("entidades.random.random", return_value=0.99):
            self.assertTrue(ejecutar_habilidad_activa("Gran mordisco", atacante, objetivo, estado))
            self.assertFalse(ejecutar_habilidad_activa("Gran mordisco", atacante, objetivo, estado))

        self.assertEqual(objetivo.vida_actual, 21)
        self.assertEqual(atacante.enfriamientos["Gran mordisco"], 5)

    def test_tripulacion_fantasma_crea_aliados_muertos(self):
        capitan = Monstruo(
            "Capitán del Caleuche",
            40,
            10,
            5,
            3,
            ["Terrestre"],
            habilidades=["Tripulación fantasma"],
        )
        aliado_muerto = Monstruo("Aliado muerto", 8, 3, 2, 4, ["Terrestre"])
        aliado_muerto.vida_actual = 0
        estado = {
            "equipo_enemigo": [capitan, aliado_muerto],
            "nuevos_combatientes": [],
        }

        with patch("habilidades.time.sleep"):
            self.assertTrue(ejecutar_habilidad_activa("Tripulación fantasma", capitan, capitan, estado))

        fantasmas = estado["nuevos_combatientes"]
        self.assertEqual(len(fantasmas), 1)
        self.assertEqual(fantasmas[0].vida_max, 10)
        self.assertEqual(fantasmas[0].ataque_base, 5)
        self.assertEqual(fantasmas[0].reflejos, 3)
        self.assertEqual(fantasmas[0].velocidad_base, 3)
        self.assertFalse(puede_usar_habilidad(capitan, "Tripulación fantasma"))


if __name__ == "__main__":
    unittest.main()

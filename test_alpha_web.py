import unittest

import app as app_module
from entidades import Jugador


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

    def test_mar_profundo_web_redirige_sin_linterna(self):
        respuesta = self.cliente.get("/zona/Mar%20Profundo")

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/mapa", respuesta.location)
        self.assertIn("Linterna", respuesta.location)


if __name__ == "__main__":
    unittest.main()

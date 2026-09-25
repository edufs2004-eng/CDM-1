import unittest

from datos_monstruos import generar_monstruo
from guardado import deserializar_monstruo, serializar_monstruo


class ModeloDatosTests(unittest.TestCase):
    def test_monstruo_actual_carga_metadatos_de_combate(self):
        monstruo = generar_monstruo("Pulpo Inteligente")

        self.assertEqual(monstruo.peligrosidad, 0.9)
        self.assertEqual(monstruo.terreno, "Híbrido")
        self.assertEqual(monstruo.armadura, 0)
        self.assertEqual(monstruo.enfriamientos, {})
        self.assertEqual(monstruo.fase_actual, 1)

    def test_metadatos_nuevos_se_conservan_al_serializar(self):
        monstruo = generar_monstruo("Tiburón")
        monstruo.enfriamientos["Prueba"] = 2
        monstruo.fase_actual = 2

        copia = deserializar_monstruo(serializar_monstruo(monstruo))

        self.assertEqual(copia.armadura, monstruo.armadura)
        self.assertEqual(copia.peligrosidad, monstruo.peligrosidad)
        self.assertEqual(copia.terreno, monstruo.terreno)
        self.assertEqual(copia.enfriamientos, {"Prueba": 2})
        self.assertEqual(copia.fase_actual, 2)

    def test_guardado_antiguo_usa_valores_por_defecto(self):
        datos_antiguos = {
            "nombre": "Criatura antigua",
            "vida_max": 5,
            "vida_actual": 5,
            "ataque_base": 2,
            "reflejos": 1,
            "velocidad_base": 2,
            "etiquetas": ["Terrestre"],
            "habilidades": [],
        }

        monstruo = deserializar_monstruo(datos_antiguos)

        self.assertEqual(monstruo.armadura, 0)
        self.assertIsNone(monstruo.peligrosidad)
        self.assertIsNone(monstruo.terreno)
        self.assertEqual(monstruo.enfriamientos, {})
        self.assertEqual(monstruo.fase_actual, 1)


if __name__ == "__main__":
    unittest.main()

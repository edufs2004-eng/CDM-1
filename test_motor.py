import unittest
from types import SimpleNamespace
from unittest.mock import patch

from motor import calcular_orden_turnos


def combatiente(nombre, velocidad, reflejos, vida=1):
    return SimpleNamespace(
        nombre=nombre,
        velocidad_actual=velocidad,
        reflejos=reflejos,
        vida_actual=vida,
    )


class MotorTurnosTests(unittest.TestCase):
    @patch("motor.time.sleep")
    def test_conserva_la_cantidad_de_acciones_actual(self, _sleep):
        combatientes = [
            combatiente("Rapido A", 10, 1),
            combatiente("Rapido B", 10, 3),
            combatiente("Lento", 3, 2),
        ]

        orden = calcular_orden_turnos(combatientes)

        self.assertEqual(len(orden), 5)
        self.assertEqual(
            [(accion["nombre"], accion["iniciativa"]) for accion in orden],
            [("Rapido B", 10), ("Rapido A", 10), ("Rapido B", 5),
             ("Rapido A", 5), ("Lento", 3)],
        )

    @patch("motor.time.sleep")
    def test_reflejos_desempatan_la_iniciativa(self, _sleep):
        menor_agilidad = combatiente("Menor agilidad", 6, 1)
        mayor_agilidad = combatiente("Mayor agilidad", 6, 4)

        orden = calcular_orden_turnos([menor_agilidad, mayor_agilidad])

        self.assertEqual(orden[0]["nombre"], "Mayor agilidad")
        self.assertEqual(orden[1]["nombre"], "Menor agilidad")

    @patch("motor.time.sleep")
    def test_los_combatientes_muertos_no_generan_acciones(self, _sleep):
        vivo = combatiente("Vivo", 3, 1)
        muerto = combatiente("Muerto", 20, 10, vida=0)

        orden = calcular_orden_turnos([vivo, muerto])

        self.assertTrue(orden)
        self.assertTrue(all(accion["nombre"] != "Muerto" for accion in orden))
        self.assertEqual(len(orden), 1)


if __name__ == "__main__":
    unittest.main()

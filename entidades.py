import random
import time

from habilidades import procesar_trigger, HABILIDADES_DB, ejecutar_habilidad_activa
from objetos import generar_objeto
from normalizacion import normalizar_etiquetas

class Entidad:
    def __init__(self, nombre, vida, ataque_base, reflejos, velocidad):
        self.nombre = nombre
        self.vida_max = vida
        self.vida_actual = vida
        self.ataque_base = ataque_base
        self.varianza_ataque = 1
        self.reflejos = reflejos
        self.velocidad_base = velocidad
        self.velocidad_actual = velocidad

        self.armadura = 0
        self.prob_crit = 0.0
        self.ataque_crit = 0

        self.etiquetas = normalizar_etiquetas([])
        self.habilidades = []
        self.aturdido_turnos = 0
        self.habilidades_usadas = {}
        self.cooldowns = {}

    def gestionar_cooldowns(self):
        for hab in list(self.cooldowns.keys()):
            if self.cooldowns[hab] > 0:
                self.cooldowns[hab] -= 1

    def calcular_esquive(self):
        if self.velocidad_actual <= 0:
            return 0
        prob = (self.reflejos / max(self.velocidad_actual, 1)) * 0.25
        return min(prob, 0.6)

    def restaurar_estado(self):
        self.vida_actual = self.vida_max
        self.velocidad_actual = self.velocidad_base
        self.aturdido_turnos = 0
        self.habilidades_usadas = {}
        self.cooldowns = {}

    def recibir_dano(self, dano, atacante):
        dano_final = max(0, dano - self.armadura)

        if self.vida_actual - dano_final <= 0:
            self.vida_actual = 0
            print(f"{atacante.nombre} infligió {dano_final} de daño a {self.nombre}.")
            print(f"Vida de {self.nombre}: 0/{self.vida_max}")
            procesar_trigger("al_recibir_dano_letal", self, atacante)
            return

        self.vida_actual -= dano_final
        print(f"{atacante.nombre} infligió {dano_final} de daño a {self.nombre}.")
        print(f"Vida de {self.nombre}: {self.vida_actual}/{self.vida_max}")

    def atacar(self, objetivo):
        print(f"\n--- {self.nombre} ataca a {objetivo.nombre} ---")
        time.sleep(0.5)

        if random.random() <= objetivo.calcular_esquive():
            print(f"¡{objetivo.nombre} ESQUIVÓ el ataque de {self.nombre}!")
            return

        min_dano = max(0, self.ataque_base - self.varianza_ataque)
        max_dano = self.ataque_base + self.varianza_ataque
        dano_base = random.randint(min_dano, max_dano)

        if random.random() <= self.prob_crit:
            dano_base += self.ataque_crit
            print(f"¡GOLPE CRÍTICO de {self.nombre}!")

        multiplicador = 1.0
        anular = False

        if "Volador" in objetivo.etiquetas and "Volador" not in self.etiquetas and "Ataque a distancia" not in self.etiquetas:
            anular = True
        elif "Titánico" in objetivo.etiquetas:
            if "Gigante" not in self.etiquetas and "Titánico" not in self.etiquetas:
                anular = True
            elif "Gigante" in self.etiquetas:
                multiplicador -= 0.25
        elif "Gigante" in objetivo.etiquetas:
            if "Gigante" not in self.etiquetas and "Titánico" not in self.etiquetas:
                multiplicador -= 0.30

        if anular:
            print(f"¡El ataque de {self.nombre} no tuvo efecto por restricción de clases!")
            return

        dano_final = max(0, round(dano_base * multiplicador))
        objetivo.recibir_dano(dano_final, self)
        procesar_trigger("al_atacar", self, objetivo)

class Jugador(Entidad):
    def __init__(self, nombre):
        super().__init__(nombre, vida=10, ataque_base=1, reflejos=2, velocidad=3)
        self.inventario = []
        self.aliados_obtenidos = []
        self.equipo_aliado = []
        self.caja_aliados = []
        self.eventos_desbloqueados = []

        self.equipo = {
            "Mano 1": generar_objeto("Caña de pescar"),
            "Mano 2": None,
            "Cabeza": generar_objeto("Gorro de pescador"),
            "Torso": generar_objeto("Polera con mangas"),
            "Piernas": generar_objeto("Pantalón de tela"),
            "Brazos": None,
            "Extra": generar_objeto("Barca")
        }

        self.actualizar_stats()

    def actualizar_stats(self):
        ataque_total = 1
        varianza_total = 1
        velocidad_extra = 0
        reflejos_extra = 0

        self.etiquetas = []
        self.habilidades = []

        for item in self.equipo.values():
            if item is None:
                continue

            ataque_total += item.bonos_stats.get("ataque", 0)
            varianza_total += item.bonos_stats.get("varianza", 0)
            velocidad_extra += item.bonos_stats.get("velocidad", 0)
            reflejos_extra += item.bonos_stats.get("reflejos", 0)

            if item.bonos_stats.get("etiqueta") == "Barca":
                self.etiquetas.append("Barca")

            if "habilidades" in item.bonos_stats:
                self.habilidades.extend(item.bonos_stats["habilidades"])

        self.ataque_base = ataque_total
        self.varianza_ataque = max(1, varianza_total)
        self.velocidad_base = 3 + velocidad_extra
        self.reflejos = 2 + reflejos_extra
        self.velocidad_actual = self.velocidad_base

    def obtener_habilidades_activas(self):
        habs = []
        for item in self.equipo.values():
            if item is None:
                continue
            if "habilidades" in item.bonos_stats:
                for hab in item.bonos_stats["habilidades"]:
                    if hab in HABILIDADES_DB and HABILIDADES_DB[hab].get("tipo") == "activa":
                        habs.append(hab)

        for aliado in self.equipo_aliado:
            if aliado.vida_actual > 0:
                for hab in aliado.habilidades:
                    if hab in HABILIDADES_DB and HABILIDADES_DB[hab].get("tipo") == "activa":
                        habs.append(hab)

        return habs

class Monstruo(Entidad):
    def __init__(self, nombre, vida, ataque_base, reflejos, velocidad, etiquetas, habilidades=None, probabilidades_ia=None):
        super().__init__(nombre, vida, ataque_base, reflejos, velocidad)
        self.etiquetas = normalizar_etiquetas(etiquetas)
        self.habilidades = list(habilidades) if habilidades else []
        self.probabilidades_ia = probabilidades_ia if probabilidades_ia else {}

    def decidir_accion_ia(self, aliados, enemigos, estado_combate):
        objetivos = [e for e in aliados if getattr(e, "vida_actual", 0) > 0]
        if not objetivos:
            return

        objetivo = random.choice(objetivos)

        posible_hab = []
        for hab, prob in self.probabilidades_ia.items():
            if hab not in HABILIDADES_DB:
                continue
            if self.cooldowns.get(hab, 0) > 0:
                continue
            if self.habilidades_usadas.get(hab, 0) >= HABILIDADES_DB[hab].get("usos_maximos", 99):
                continue
            posible_hab.append((hab, prob))

        if posible_hab:
            total = sum(prob for _, prob in posible_hab)
            valor = random.randint(1, total)
            acumulado = 0
            habilidad_elegida = None

            for hab, prob in posible_hab:
                acumulado += prob
                if valor <= acumulado:
                    habilidad_elegida = hab
                    break

            if habilidad_elegida is not None:
                self.habilidades_usadas[habilidad_elegida] = self.habilidades_usadas.get(habilidad_elegida, 0) + 1
                self.cooldowns[habilidad_elegida] = HABILIDADES_DB[habilidad_elegida].get("cooldown", 0)
                ejecutar_habilidad_activa(habilidad_elegida, self, objetivo, estado_combate)
                return

        self.atacar(objetivo)
import random
import time
from habilidades import (
    procesar_trigger,
    HABILIDADES_DB,
    ejecutar_habilidad_activa,
    seleccionar_habilidad_ia,
    ataque_permitido,
)
from objetos import generar_objeto

class Entidad:
    def __init__(self, nombre, vida, ataque_base, reflejos, velocidad,
                 armadura=0, peligrosidad=None):
        self.nombre = nombre
        self.vida_max = vida
        self.vida_actual = vida
        self.ataque_base = ataque_base
        self.varianza_ataque = 1 
        self.reflejos = reflejos
        self.velocidad_base = velocidad
        self.velocidad_actual = velocidad 
        
        self.armadura = armadura
        self.peligrosidad = peligrosidad
        self.prob_crit = 0.0
        self.ataque_crit = 0
        
        self.etiquetas = []
        self.habilidades = [] 
        
        self.aturdido_turnos = 0
        self.habilidades_usadas = {}
        self.enfriamientos = {}
        self.fase_actual = 1
        self.datos_fase = {}
        self.vida_turno_anterior = vida
        self.quemadura_cargas = 0
        self.inalcanzable_turnos = 0
        self.guardianes = []

    def calcular_esquive(self):
        if self.velocidad_actual <= 0: return 0
        prob = (self.reflejos / self.velocidad_actual) * 0.25 
        return min(prob, 0.6)

    def restaurar_estado(self):
        self.vida_actual = self.vida_max
        self.velocidad_actual = self.velocidad_base
        self.aturdido_turnos = 0
        self.habilidades_usadas = {}
        self.enfriamientos = {}
        self.vida_turno_anterior = self.vida_max
        self.quemadura_cargas = 0
        self.inalcanzable_turnos = 0
        self.guardianes = []

    def aplicar_quemadura(self, cargas=1):
        if "Mecánico" in self.etiquetas:
            return False
        self.quemadura_cargas += max(0, cargas)
        return cargas > 0

    def purificar_quemadura(self):
        tenia_quemadura = self.quemadura_cargas > 0
        self.quemadura_cargas = 0
        return tenia_quemadura

    def procesar_estados_ronda(self):
        if self.inalcanzable_turnos > 0:
            self.inalcanzable_turnos -= 1

        if self.quemadura_cargas <= 0 or self.vida_actual <= 0:
            return

        dano = 1 if self.quemadura_cargas <= 2 else 2
        if self.quemadura_cargas >= 5:
            dano = 3

        self.vida_actual = max(0, self.vida_actual - dano)
        print(f"¡{self.nombre} recibe {dano} de daño por quemadura! Vida: {self.vida_actual}/{self.vida_max}")

    def puede_ser_objetivo(self):
        return self.vida_actual > 0 and self.inalcanzable_turnos <= 0

    def recibir_dano(self, dano, atacante):
        dano_final = dano - self.armadura
        if dano_final < 0: dano_final = 0

        if self.vida_actual - dano_final <= 0:
            for guardian in self.guardianes:
                usos = guardian.habilidades_usadas.get("Mejor amigo", 0)
                if "Mejor amigo" in guardian.habilidades and guardian.vida_actual > 0 and usos < 2:
                    guardian.habilidades_usadas["Mejor amigo"] = usos + 1
                    print(f"¡{guardian.nombre} recibe el daño mortal destinado a {self.nombre}!")
                    guardian.recibir_dano(dano_final, atacante)
                    if guardian.vida_actual <= 0:
                        self.inalcanzable_turnos = 2
                        print(f"¡{self.nombre} queda Inalcanzable durante 2 turnos!")
                    return
            
        if self.vida_actual - dano_final <= 0:
            se_salvo = False
            self.vida_actual = 0 
            
            procesar_trigger("al_recibir_dano_letal", self, atacante)
            
            if self.vida_actual > 0:
                se_salvo = True 

            if not se_salvo and self.transicionar_fase(atacante):
                return
                
            if se_salvo:
                return 
            else:
                self.vida_actual = 0
                print(f"{atacante.nombre} infligió {dano_final} de daño a {self.nombre}.")
                print(f"Vida de {self.nombre}: 0/{self.vida_max}")
                return

        self.vida_actual -= dano_final
        print(f"{atacante.nombre} infligió {dano_final} de daño a {self.nombre}.")
        print(f"Vida de {self.nombre}: {self.vida_actual}/{self.vida_max}")

    def atacar(self, objetivo, estado_combate=None):
        print(f"\n--- {self.nombre} ataca a {objetivo.nombre} ---")
        time.sleep(1)

        if not ataque_permitido(self, objetivo, estado_combate):
            print(f"¡El Círculo de fuego impide que {self.nombre} ataque a {objetivo.nombre}!")
            return

        if "Comida" in self.habilidades and random.random() <= 0.10:
            self._atacar_con_comida(objetivo)
            return

        if random.random() <= objetivo.calcular_esquive():
            print(f"¡{objetivo.nombre} ESQUIVÓ el ataque de {self.nombre}!")
            time.sleep(1)
            return 
        
        min_actual = self.ataque_base - self.varianza_ataque
        max_actual = self.ataque_base + self.varianza_ataque
        
        if min_actual < 0: min_actual = 0
            
        es_critico = False
        if random.random() <= self.prob_crit:
            es_critico = True
            min_actual += self.ataque_crit
            max_actual += self.ataque_crit
            
        dano_bruto = random.randint(min_actual, max_actual)
        
        if es_critico:
            print(f"¡GOLPE CRÍTICO de {self.nombre}!")
            time.sleep(1)

        multiplicador = 1.0
        anular = False
        
        if "Volador" in objetivo.etiquetas and "Volador" not in self.etiquetas and "Ataque a distancia" not in self.etiquetas:
            anular = True
        elif not anular and "Titánico" in objetivo.etiquetas:
            if "Gigante" not in self.etiquetas and "Titánico" not in self.etiquetas: anular = True
            elif "Gigante" in self.etiquetas: multiplicador -= 0.25
        elif not anular and "Gigante" in objetivo.etiquetas:
            if "Gigante" not in self.etiquetas and "Titánico" not in self.etiquetas: multiplicador -= 0.30

        if anular:
            print(f"¡El ataque de {self.nombre} no tuvo efecto por restricción de clases!")
        else:
            dano_calculado = round(dano_bruto * multiplicador)
            objetivo.recibir_dano(dano_calculado, self)
            
            if objetivo.vida_actual > 0:
                procesar_trigger("al_atacar", self, objetivo)
            
        time.sleep(1)

    def _atacar_con_comida(self, objetivo):
        print(f"¡{self.nombre} usa Comida y muerde a {objetivo.nombre}!")
        if random.random() <= objetivo.calcular_esquive():
            print(f"¡{objetivo.nombre} ESQUIVÓ el mordisco de {self.nombre}!")
            return

        vida_anterior = objetivo.vida_actual
        objetivo.recibir_dano(self.ataque_base, self)
        dano_realizado = max(0, vida_anterior - objetivo.vida_actual)
        self.vida_actual = min(self.vida_max, self.vida_actual + dano_realizado)

    def atacar_especial(self, objetivo, multiplicador=1.0, estado_combate=None,
                        ignora_penalizacion_gigante=False):
        if not ataque_permitido(self, objetivo, estado_combate):
            print(f"¡El Círculo de fuego impide que {self.nombre} ataque a {objetivo.nombre}!")
            return

        if random.random() <= objetivo.calcular_esquive():
            print(f"¡{objetivo.nombre} ESQUIVÓ el ataque de {self.nombre}!")
            return

        dano = round(self.ataque_base * multiplicador)
        if "Titánico" in objetivo.etiquetas and "Gigante" not in self.etiquetas and "Titánico" not in self.etiquetas:
            print(f"¡El ataque de {self.nombre} no tuvo efecto por restricción de clases!")
            return
        if "Gigante" in objetivo.etiquetas and not ignora_penalizacion_gigante and "Gigante" not in self.etiquetas and "Titánico" not in self.etiquetas:
            dano = round(dano * 0.70)

        objetivo.recibir_dano(dano, self)

    def transicionar_fase(self, atacante=None):
        return False

class Jugador(Entidad):
    def __init__(self, nombre):
        super().__init__(nombre, vida=10, ataque_base=1, reflejos=2, velocidad=3)
        self.inventario = [] 
        self.equipo_aliado = [] 
        self.aliados_obtenidos = [] 
        self.caja_aliados = [] 
        self.eventos_desbloqueados = [] # Registro de logros/drops únicos
        
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
        
        if "Barca" in self.etiquetas: self.etiquetas.remove("Barca")
        self.habilidades = [] # Reiniciamos habilidades en cada recálculo
        
        for slot, item in self.equipo.items():
            if item:
                ataque_total += item.bonos_stats.get("ataque", 0)
                varianza_total += item.bonos_stats.get("varianza", 0)
                velocidad_extra += item.bonos_stats.get("velocidad", 0)
                reflejos_extra += item.bonos_stats.get("reflejos", 0)
                
                if item.bonos_stats.get("etiqueta") == "Barca" and "Barca" not in self.etiquetas:
                    self.etiquetas.append("Barca")
                
                # Heredar habilidades del objeto
                if "habilidades" in item.bonos_stats:
                    self.habilidades.extend(item.bonos_stats["habilidades"])
                    
        self.ataque_base = ataque_total
        self.varianza_ataque = varianza_total
        self.velocidad_base = 3 + velocidad_extra 
        self.reflejos = 2 + reflejos_extra
        self.velocidad_actual = self.velocidad_base

    def obtener_habilidades_activas(self):
        """Recopila Habilidades Activas de los objetos equipados y aliados vivos"""
        habs_disponibles = set()
        
        # 1. De los objetos equipados
        for slot, item in self.equipo.items():
            if item and "habilidades" in item.bonos_stats:
                for h in item.bonos_stats["habilidades"]:
                    if h in HABILIDADES_DB and HABILIDADES_DB[h].get("tipo") == "activa":
                        habs_disponibles.add(h)
                        
        # 2. De los aliados activos y VIVOS
        for aliado in self.equipo_aliado:
            if aliado.vida_actual > 0:
                for h in aliado.habilidades:
                    if h in HABILIDADES_DB and HABILIDADES_DB[h].get("tipo") == "activa":
                        habs_disponibles.add(h)
                        
        return list(habs_disponibles)

class Monstruo(Entidad):
    def __init__(self, nombre, vida, ataque_base, reflejos, velocidad, etiquetas,
                 habilidades=None, probabilidades_ia=None, armadura=0,
                 peligrosidad=None, datos_fase=None, terreno=None):
        super().__init__(nombre, vida, ataque_base, reflejos, velocidad,
                         armadura=armadura, peligrosidad=peligrosidad)
        self.etiquetas = etiquetas
        self.habilidades = habilidades if habilidades else []
        self.probabilidades_ia = probabilidades_ia if probabilidades_ia else {}
        self.datos_fase = datos_fase if datos_fase else {}
        self.terreno = terreno
        self.fase_en_encuentro = True
        self._estadisticas_base = {
            "vida_max": vida,
            "ataque_base": ataque_base,
            "reflejos": reflejos,
            "velocidad_base": velocidad,
            "armadura": armadura,
        }

    def restaurar_estado(self):
        self.vida_max = self._estadisticas_base["vida_max"]
        self.ataque_base = self._estadisticas_base["ataque_base"]
        self.reflejos = self._estadisticas_base["reflejos"]
        self.velocidad_base = self._estadisticas_base["velocidad_base"]
        self.armadura = self._estadisticas_base["armadura"]
        self.fase_actual = 1
        super().restaurar_estado()

    def crear_fantasmas(self, aliados):
        fantasmas = []
        for aliado in aliados:
            if aliado is self or aliado.vida_actual > 0:
                continue
            fantasmas.append(
                Monstruo(
                    nombre=f"Fantasma de {aliado.nombre}",
                    vida=10,
                    ataque_base=5,
                    reflejos=3,
                    velocidad=3,
                    etiquetas=aliado.etiquetas.copy(),
                    habilidades=[],
                    terreno=aliado.terreno,
                )
            )
        return fantasmas

    def transicionar_fase(self, atacante=None, forzar=False):
        if not self.fase_en_encuentro and not forzar:
            return False

        datos_fase = self.datos_fase.get(str(self.fase_actual + 1))
        if not datos_fase or datos_fase.get("trigger") != "al_llegar_a_cero":
            return False

        self.fase_actual += 1
        self.vida_max = datos_fase.get(
            "vida",
            round(self.vida_max * datos_fase.get("vida_multiplicador", 1)),
        )
        self.vida_actual = self.vida_max
        self.ataque_base = datos_fase.get(
            "ataque",
            round(self.ataque_base * datos_fase.get("ataque_multiplicador", 1)),
        )
        self.reflejos = datos_fase.get(
            "reflejos",
            round(self.reflejos * datos_fase.get("reflejos_multiplicador", 1)),
        )
        self.velocidad_base = datos_fase.get(
            "velocidad",
            round(self.velocidad_base * datos_fase.get("velocidad_multiplicador", 1)),
        )
        self.velocidad_actual = self.velocidad_base
        self.armadura = datos_fase.get("armadura", self.armadura)

        if atacante is not None and datos_fase.get("aturdir_atacante"):
            turnos = datos_fase["aturdir_atacante"]
            if "Gigante" in atacante.etiquetas or "Titánico" in atacante.etiquetas:
                turnos = datos_fase.get("aturdir_atacante_escala", turnos)
            atacante.aturdido_turnos += turnos

        print(f"¡{self.nombre} entra en la Fase {self.fase_actual}!")
        return True

    def decidir_accion_ia(self, aliados, enemigos, estado_combate):
        """Lógica autónoma: Tira dados para habilidades de IA, si falla, ataca normal"""
        vivos = [e for e in enemigos if e.puede_ser_objetivo()]
        if not vivos: return
        
        cuerpo_a_cuerpo = [obj for obj in vivos if "Ataque a distancia" not in obj.etiquetas]
        objetivos_validos = cuerpo_a_cuerpo if len(cuerpo_a_cuerpo) > 0 else vivos
        objetivos_validos = [
            objetivo for objetivo in objetivos_validos
            if ataque_permitido(self, objetivo, estado_combate)
        ]
        
        if not objetivos_validos: return
        objetivo = random.choice(objetivos_validos)
        
        # 1. Tirar dados para la ventana acumulada de IA
        habilidad_elegida = seleccionar_habilidad_ia(self)
                
        # 2. Ejecutar habilidad (si acertó el % y existe) o ataque básico
        if habilidad_elegida and habilidad_elegida in HABILIDADES_DB:
            print(f"\n[!] {self.nombre} usó {habilidad_elegida} por decisión propia.")
            ejecutar_habilidad_activa(habilidad_elegida, self, objetivo, estado_combate)
        else:
            self.atacar(objetivo, estado_combate)
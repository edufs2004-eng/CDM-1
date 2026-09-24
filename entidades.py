import random
import time
from habilidades import procesar_trigger, HABILIDADES_DB, ejecutar_habilidad_activa
from objetos import generar_objeto

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
        
        self.etiquetas = []
        self.habilidades = [] 
        
        self.aturdido_turnos = 0
        self.habilidades_usadas = {}
        self.cooldowns = {}

    def gestionar_cooldowns(self):
        """Reduce en 1 los enfriamientos al inicio del turno"""
        # Usamos list() para evitar el error de modificar un diccionario mientras se itera
        for hab in list(self.cooldowns.keys()):
            if self.cooldowns[hab] > 0:
                self.cooldowns[hab] -= 1

    def calcular_esquive(self):
        if self.velocidad_actual <= 0: return 0
        prob = (self.reflejos / self.velocidad_actual) * 0.25 
        return min(prob, 0.6)

    def restaurar_estado(self):
        self.vida_actual = self.vida_max
        self.velocidad_actual = self.velocidad_base
        self.aturdido_turnos = 0
        self.habilidades_usadas = {}
        self.cooldowns = {}

    def recibir_dano(self, dano, atacante):
        dano_final = dano - self.armadura
        if dano_final < 0: dano_final = 0
            
        if self.vida_actual - dano_final <= 0:
            se_salvo = False
            self.vida_actual = 0 
            
            procesar_trigger("al_recibir_dano_letal", self, atacante)
            
            if self.vida_actual > 0:
                se_salvo = True 
                
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

    def atacar(self, objetivo):
        print(f"\n--- {self.nombre} ataca a {objetivo.nombre} ---")
        time.sleep(1)
        
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
    def __init__(self, nombre, vida, ataque_base, reflejos, velocidad, etiquetas, habilidades=None, probabilidades_ia=None):
        super().__init__(nombre, vida, ataque_base, reflejos, velocidad)
        self.etiquetas = etiquetas
        self.habilidades = habilidades if habilidades else []
        self.probabilidades_ia = probabilidades_ia if probabilidades_ia else {}

    def decidir_accion_ia(self, aliados, enemigos, estado_combate):
        """Lógica autónoma: Ventana deslizante para habilidades y ataque básico"""
        vivos = [e for e in enemigos if e.vida_actual > 0]
        if not vivos: return
        
        cuerpo_a_cuerpo = [obj for obj in vivos if "Ataque a distancia" not in obj.etiquetas]
        objetivos_validos = cuerpo_a_cuerpo if len(cuerpo_a_cuerpo) > 0 else vivos
        if not objetivos_validos: return
        
        objetivo = random.choice(objetivos_validos)
        
        habilidad_elegida = None
        dado = random.randint(1, 100)
        limite_actual = 0
        
        for hab, prob in self.probabilidades_ia.items():
            if hab not in HABILIDADES_DB: continue
            datos_hab = HABILIDADES_DB[hab]
            
            # Saltamos la habilidad si está en cooldown o superó usos_maximos
            if self.cooldowns.get(hab, 0) > 0: continue
            if self.habilidades_usadas.get(hab, 0) >= datos_hab.get("usos_maximos", 99): continue
                
            # Ventana deslizante
            rango_min = limite_actual + 1
            limite_actual += prob
            rango_max = limite_actual
            
            if rango_min <= dado <= rango_max:
                habilidad_elegida = hab
                break
                
        if habilidad_elegida:
            print(f"\n[!] {self.nombre} usó {habilidad_elegida} por decisión propia.")
            
            # Registramos el uso y el cooldown (si lo tiene en HABILIDADES_DB, si no, es 0)
            self.habilidades_usadas[habilidad_elegida] = self.habilidades_usadas.get(habilidad_elegida, 0) + 1
            self.cooldowns[habilidad_elegida] = HABILIDADES_DB[habilidad_elegida].get("cooldown", 0)
            
            ejecutar_habilidad_activa(habilidad_elegida, self, objetivo, estado_combate)
        else:
            self.atacar(objetivo)
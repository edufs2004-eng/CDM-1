import random
import time
from habilidades import procesar_trigger

class Entidad:
    def __init__(self, nombre, vida, ataque_base, reflejos, velocidad):
        self.nombre = nombre
        self.vida_max = vida
        self.vida_actual = vida
        self.ataque_base = ataque_base
        self.varianza_ataque = 1 # Por defecto todos tienen +-1
        self.reflejos = reflejos
        self.velocidad_base = velocidad
        self.velocidad_actual = velocidad 
        
        self.armadura = 0
        self.prob_crit = 0.0
        self.ataque_crit = 0
        
        self.etiquetas = []
        self.habilidades = [] 
        
        # Estados
        self.aturdido_turnos = 0
        self.habilidades_usadas = {} # Registro para las habilidades modulares

    def calcular_esquive(self):
        if self.velocidad_actual <= 0: return 0
        # Multiplicamos por 0.25 para equilibrar la evasión
        prob = (self.reflejos / self.velocidad_actual) * 0.25 
        return min(prob, 0.6)

    def restaurar_estado(self):
        """Limpia todos los debuffs y reinicia pasivas (Se usa al salir de un combate)"""
        self.vida_actual = self.vida_max
        self.velocidad_actual = self.velocidad_base
        self.aturdido_turnos = 0
        self.habilidades_usadas = {}

    def recibir_dano(self, dano, atacante):
        dano_final = dano - self.armadura
        if dano_final < 0: dano_final = 0
            
        # Comprobamos si el golpe va a ser letal
        if self.vida_actual - dano_final <= 0:
            se_salvo = False
            self.vida_actual = 0 # Asumimos la muerte momentáneamente
            
            # --- DISPARADOR MODULAR: DAÑO LETAL ---
            procesar_trigger("al_recibir_dano_letal", self, atacante)
            
            # Si el trigger le curó la vida (Ej: Tácticas de escape lo dejó a 1 HP)
            if self.vida_actual > 0:
                se_salvo = True 
                
            if se_salvo:
                return # Salimos sin aplicar el daño final
            else:
                self.vida_actual = 0
                print(f"{atacante.nombre} infligió {dano_final} de daño a {self.nombre}.")
                print(f"Vida de {self.nombre}: 0/{self.vida_max}")
                return

        # Si el golpe no era letal, aplicamos daño normal
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
        
        # 1. Calcular intervalo de daño
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

        # 2. Comprobar etiquetas
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
            
            # --- DISPARADOR MODULAR: AL ATACAR ---
            if objetivo.vida_actual > 0:
                procesar_trigger("al_atacar", self, objetivo)
            
        time.sleep(1)


# ==========================================
# CLASE EQUIPAMIENTO
# ==========================================
class Equipamiento:
    def __init__(self, nombre, bonos_stats):
        self.nombre = nombre
        self.bonos_stats = bonos_stats

# ==========================================
# CLASE JUGADOR Y MONSTRUO
# ==========================================
class Jugador(Entidad):
    def __init__(self, nombre):
        super().__init__(nombre, vida=10, ataque_base=1, reflejos=2, velocidad=3)
        self.inventario = []
        self.equipo_aliado = [] 
        self.aliados_obtenidos = [] 
        self.caja_aliados = [] 
        
        # Slots de equipo
        self.equipo = {
            "Mano 1": Equipamiento("Caña de pescar", {"ataque": 2, "varianza": 1}),
            "Mano 2": None,
            "Cabeza": Equipamiento("Gorro de pescador", {}),
            "Torso": Equipamiento("Polera con mangas", {}),
            "Piernas": Equipamiento("Pantalón de tela", {}),
            "Brazos": None,
            "Extra": Equipamiento("Barca", {"etiqueta": "Barca"})
        }
        self.actualizar_stats()

    def actualizar_stats(self):
        ataque_total = 1
        varianza_total = 1
        
        for slot, item in self.equipo.items():
            if item:
                ataque_total += item.bonos_stats.get("ataque", 0)
                varianza_total += item.bonos_stats.get("varianza", 0)
                
                if item.bonos_stats.get("etiqueta") == "Barca" and "Barca" not in self.etiquetas:
                    self.etiquetas.append("Barca")
                    
        self.ataque_base = ataque_total
        self.varianza_ataque = varianza_total

class Monstruo(Entidad):
    def __init__(self, nombre, vida, ataque_base, reflejos, velocidad, etiquetas, habilidades=None):
        super().__init__(nombre, vida, ataque_base, reflejos, velocidad)
        self.etiquetas = etiquetas
        if habilidades:
            self.habilidades = habilidades
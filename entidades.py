import random
import time

class Entidad:
    # Ahora pedimos ataque_base en lugar de min/max
    def __init__(self, nombre, vida, ataque_base, reflejos, velocidad):
        self.nombre = nombre
        self.vida_max = vida
        self.vida_actual = vida
        self.ataque_base = ataque_base
        self.varianza_ataque = 1 # Por defecto todos tienen +-1
        self.reflejos = reflejos
        self.velocidad_base = velocidad
        self.velocidad_actual = velocidad # La actual puede bajar por debuffs
        
        self.armadura = 0
        self.prob_crit = 0.0
        self.ataque_crit = 0
        
        self.etiquetas = []
        self.habilidades = [] # Lista de nombres de habilidades
        
        # Estados
        self.aturdido_turnos = 0
        self.tacticas_usada = False # Para la pasiva del pulpo (1 solo uso)

    def calcular_esquive(self):
        # Usamos velocidad actual por si está reducida
        if self.velocidad_actual <= 0: return 0
        prob = self.reflejos / self.velocidad_actual
        return min(prob, 0.6)

    def recibir_dano(self, dano, atacante):
        """Nueva función para procesar el daño y pasivas defensivas"""
        dano_final = dano - self.armadura
        if dano_final < 0: dano_final = 0
            
        # --- HABILIDAD PASIVA: Tácticas de escape (Pulpo Inteligente) ---
        if "Tácticas de escape" in self.habilidades and not self.tacticas_usada:
            if self.vida_actual - dano_final <= 0:
                print(f"\n¡{self.nombre} usó TÁCTICAS DE ESCAPE!")
                print(f"{self.nombre} sobrevivió con 1 HP y lanzó un chorro de tinta.")
                self.vida_actual = 1
                self.tacticas_usada = True
                
                # Reduce velocidad del atacante en 25% (redondeado)
                reduccion = max(1, int(atacante.velocidad_actual * 0.25))
                atacante.velocidad_actual -= reduccion
                print(f"¡La velocidad de {atacante.nombre} bajó en {reduccion} puntos!")
                return # Salimos para no aplicar la muerte
                
        self.vida_actual -= dano_final
        if self.vida_actual < 0: self.vida_actual = 0
        
        print(f"{atacante.nombre} infligió {dano_final} de daño a {self.nombre}.")
        print(f"Vida de {self.nombre}: {self.vida_actual}/{self.vida_max}")

    def atacar(self, objetivo):
        print(f"\n--- {self.nombre} ataca a {objetivo.nombre} ---")
        time.sleep(1)
        
        if random.random() <= objetivo.calcular_esquive():
            print(f"¡{objetivo.nombre} ESQUIVÓ el ataque de {self.nombre}!")
            time.sleep(1)
            return 
        
        # 1. Calcular intervalo de daño (Base +- Varianza)
        min_actual = self.ataque_base - self.varianza_ataque
        max_actual = self.ataque_base + self.varianza_ataque
        
        # El daño mínimo nunca puede ser menor a 0
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

        # 2. Comprobar etiquetas (simplificado para ahorrar espacio, es igual que antes)
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
            # Llamamos a la nueva función de recibir daño
            objetivo.recibir_dano(dano_calculado, self)
            
            # --- HABILIDAD INSTANTÁNEA: Cachetada (Pulpo Inteligente) ---
            if "Cachetada" in self.habilidades and objetivo.vida_actual > 0:
                # 30% de probabilidad
                if random.random() <= 0.30:
                    print(f"\n¡{self.nombre} activó CACHETADA!")
                    print(f"¡{objetivo.nombre} ha sido aturdido por 1 turno (Velocidad a 0)!")
                    objetivo.aturdido_turnos = 1
                    objetivo.velocidad_actual = 0
            
        time.sleep(1)


# ==========================================
# CLASE EQUIPAMIENTO
# ==========================================
class Equipamiento:
    def __init__(self, nombre, bonos_stats):
        self.nombre = nombre
        # bonos_stats es un diccionario, ej: {"ataque": 2, "varianza": 1}
        self.bonos_stats = bonos_stats

# ==========================================
# CLASE JUGADOR Y MONSTRUO
# ==========================================
class Jugador(Entidad):
    def __init__(self, nombre):
        # Stats base del lore
        super().__init__(nombre, vida=10, ataque_base=1, reflejos=2, velocidad=3)
        self.inventario = []
        self.equipo_aliado = [] 
        self.aliados_obtenidos = []
        self.caja_aliados = [] # Aquí irán los monstruos cuando el equipo de 4 esté lleno
        
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
        """Suma los stats base + el equipamiento"""
        # Reiniciamos a stats base antes de sumar
        ataque_total = 1
        varianza_total = 1
        
        for slot, item in self.equipo.items():
            if item:
                ataque_total += item.bonos_stats.get("ataque", 0)
                varianza_total += item.bonos_stats.get("varianza", 0)
                
                # Si es la barca, añadimos la capacidad de ir al agua
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
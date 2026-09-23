import random
import time
from habilidades import procesar_trigger
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

    def calcular_esquive(self):
        if self.velocidad_actual <= 0: return 0
        prob = (self.reflejos / self.velocidad_actual) * 0.25 
        return min(prob, 0.6)

    def restaurar_estado(self):
        self.vida_actual = self.vida_max
        self.velocidad_actual = self.velocidad_base
        self.aturdido_turnos = 0
        self.habilidades_usadas = {}

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
        
        for slot, item in self.equipo.items():
            if item:
                ataque_total += item.bonos_stats.get("ataque", 0)
                varianza_total += item.bonos_stats.get("varianza", 0)
                velocidad_extra += item.bonos_stats.get("velocidad", 0)
                reflejos_extra += item.bonos_stats.get("reflejos", 0)
                
                if item.bonos_stats.get("etiqueta") == "Barca" and "Barca" not in self.etiquetas:
                    self.etiquetas.append("Barca")
                    
        self.ataque_base = ataque_total
        self.varianza_ataque = varianza_total
        self.velocidad_base = 3 + velocidad_extra 
        self.reflejos = 2 + reflejos_extra
        self.velocidad_actual = self.velocidad_base

class Monstruo(Entidad):
    def __init__(self, nombre, vida, ataque_base, reflejos, velocidad, etiquetas, habilidades=None, probabilidades_ia=None):
        super().__init__(nombre, vida, ataque_base, reflejos, velocidad)
        self.etiquetas = etiquetas
        self.habilidades = habilidades if habilidades else []
        self.probabilidades_ia = probabilidades_ia if probabilidades_ia else {}

    def decidir_accion_ia(self, aliados, enemigos, estado_combate):
        """Lógica autónoma: El monstruo decide qué hacer en su turno"""
        # 1. Filtrar enemigos vivos
        vivos = [e for e in enemigos if e.vida_actual > 0]
        if not vivos: return
        
        # (El esqueleto para el futuro: Aquí leeremos self.probabilidades_ia para ver si lanza magia)
        # 2. Por ahora, como es la base, simplemente ataca a un objetivo válido al azar
        
        # Filtramos a quién puede pegarle (Cuerpo a cuerpo o distancia)
        cuerpo_a_cuerpo = [obj for obj in vivos if "Ataque a distancia" not in obj.etiquetas]
        objetivos_validos = cuerpo_a_cuerpo if len(cuerpo_a_cuerpo) > 0 else vivos
        
        if objetivos_validos:
            objetivo = random.choice(objetivos_validos)
            self.atacar(objetivo)
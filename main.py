from entidades import Jugador, Monstruo
from combate import iniciar_combate

def iniciar_juego():
    print("===================================")
    print("    RPG: EL ORIGEN DEL PESCADOR    ")
    print("===================================")
    
    # 1. Creamos al protagonista (con su caña y barca ya equipadas)
    prota = Jugador("Pescador Joven")
    
    # 2. Creamos a los monstruos del lore
    # El pulpo tiene 10 de vida media, ataque 2, reflejos 1, velocidad 3
    pulpo = Monstruo("Pulpo Inteligente", vida=10, ataque_base=2, reflejos=1, velocidad=3, etiquetas=["Híbrido"], habilidades=["Tácticas de escape", "Cachetada"])
    
    # El tiburón tiene 9 de vida media, ataque 3, reflejos 2, velocidad 6
    tiburon = Monstruo("Tiburón", vida=9, ataque_base=3, reflejos=2, velocidad=6, etiquetas=["Acuático"])
    
    # La serpiente tiene 13 de vida, ataque 3, reflejos 1, velocidad 3
    serpiente = Monstruo("Serpiente Marina", vida=13, ataque_base=3, reflejos=1, velocidad=3, etiquetas=["Acuático"], habilidades=["Tsunami"])
    
    # 3. Prueba contra el Pulpo Inteligente en el terreno "Agua" (gracias a la Barca, el Prota puede estar)
    print("\n[Lore] Estás pescando tranquilo cuando de repente... ¡Un Pulpo emerge del agua!")
    
    enemigos = [pulpo]
    aliados = [] # Estás solo
    
    iniciar_combate(prota, aliados, enemigos, terreno="Agua")

if __name__ == "__main__":
    iniciar_juego()
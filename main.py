from entidades import Jugador
from mapa import menu_exploracion

def iniciar_juego():
    print("===================================")
    print("    RPG: EL ORIGEN DEL PESCADOR    ")
    print("===================================")
    
    prota = Jugador("Pescador Joven")
    
    # Iniciamos el bucle principal de exploración
    menu_exploracion(prota)

if __name__ == "__main__":
    iniciar_juego() 
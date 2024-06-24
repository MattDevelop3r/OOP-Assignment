import json
from classJugador import Jugador

class GestorJugadores:
    def __init__(self):
        self.__lista_jugadores = []

    def agregar_jugador(self, jugador):
        self.__lista_jugadores.append(jugador)

    def lee_json(self):
        try:
            with open("pysimonpuntajes.json", "r") as archivo:
                datos = json.load(archivo)
                for jugador in datos:
                    nuevo_jugador = Jugador(jugador['jugador'], jugador['fecha'], jugador['hora'], jugador['puntuacion'])
                    self.agregar_jugador(nuevo_jugador)
        except FileNotFoundError:
            self.__lista_jugadores = []

    def ordena_lista(self):
        self.__lista_jugadores.sort(reverse=True)

    def obtener_lista(self):
        return self.__lista_jugadores
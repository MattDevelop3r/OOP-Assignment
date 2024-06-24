from datetime import datetime

class Jugador:
    __nombre: str
    __fecha_hora: datetime
    __puntaje: int
    
    def __init__(self, nom, fecha, hora, punt):
        self.__nombre = nom
        self.__fecha_hora = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M:%S")
        self.__puntaje = int(punt)

    def __gt__(self, other):
        return self.__puntaje > other.__puntaje

    def obtener_datos(self):
        return self.__nombre, self.__fecha_hora.strftime("%Y-%m-%d"), self.__fecha_hora.strftime("%H:%M:%S"), self.__puntaje

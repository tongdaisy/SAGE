# prison delimma

import random
class Juego:

    def __init__(self, matriz, jugador1, jugador2):
        self.__matriz = matriz
        self.__jugador1 = jugador1
        self.__jugador2 = jugador2
        self.__historia = []
        self.__decisiones = []

    def decisionesDelOtroJugador(self, jugador):
        decisionesJugador = []
        if jugador == self.__jugador1:
            for element in self.__decisiones:
                decisionesJugador.append(element[1])
        else:
            for element in self.__decisiones:
                decisionesJugador.append(element[0])
        return decisionesJugador

    def historia(self):
        return self.__historia

    def pagoEsperado(self):
        resultadoJugador1 = 0
        resultadoJugador2 = 0
        for value in self.__historia:
            resultadoJugador2 = resultadoJugador2 + value[1]
            resultadoJugador1 = resultadoJugador1 + value[0]
        return [resultadoJugador1/len(self.__historia), resultadoJugador2/len(self.__historia)]




class Jugador:

    def __init__(self, probabilidad=0.5, memoria=1):
        self.__probabilidad = probabilidad
        self.__memoria = memoria

    def estrategia(self, matriz, decisiones):
        if len(decisiones) > self.__memoria:
            return self.tomarDecisionRacional(matriz, decisiones)
        else:
            return random.uniform(0,1) > self.__probabilidad

    def tomarDecisionRacional(self, matriz, decisiones):
        decisionesQueConsidero = decisiones[len(decisiones) - self.__memoria: len(decisiones) - 1]
        resultado=0
        for i in decisionesQueConsidero:
            resultado = resultado+i

        probCop = resultado/self.__memoria
        pagoEsperadoCoperar = probCop * (matriz[1][1][0] + matriz[1][0][0])
        pagoEsperadoNoCoperar = probCop * (matriz[0][1][0] + matriz[0][0][0])

        return pagoEsperadoCoperar > pagoEsperadoNoCoperar

def simulation (juego, numerojugadas = 1):
        historiaParcial = []
        for i in range(numerojugadas):
            eleccion1 = juego.__jugador1.estrategia(juego.__matriz, juego.decisionesDelOtroJugador(juego.__jugador1))
            eleccion2 = juego.__jugador2.estrategia(juego.__matriz, juego.decisionesDelOtroJugador(juego.__jugador2))
            juego.__decisiones.append([eleccion1, eleccion2])
            resultado = juego.__matriz[eleccion1][eleccion2]
            historiaParcial.append(resultado)
        juego.__historia.extend(historiaParcial)
        return historiaParcial


#Matriz de pagos
fila1 = [[3,3], [0,10]]
fila2 = [[10,0], [6,6]]
matrizDePagos = [fila1, fila2]

# Dilema del prisionero simple
'''jugador1 = random.randint(0,1)
jugador2 = random.randint(0,1)

resultado = matrizDePagos[jugador1][jugador2]
print("El jugador 1 recibio " + str(resultado[0]))
print("El jugador 2 recibio " + str(resultado[1]))'''

# Dilema del prisionero con probabilidad
'''jugador1 = Jugador(1)
jugador2 = Jugador(0)

eleccion1 = jugador1.estrategia()
eleccion2 = jugador2.estrategia()

resultado = matrizDePagos[eleccion1][eleccion2]
print("El jugador 1 recibio " + str(resultado[0]))
print("El jugador 2 recibio " + str(resultado[1]))'''

# Dilema del prisionero con historia
jugador1 = Jugador(0.5, 2)
jugador2 = Jugador(0.5, 2)

juego = Juego(matrizDePagos, jugador1, jugador2)
#simulation(juego,1000)
#print(juego.pagoEsperado())
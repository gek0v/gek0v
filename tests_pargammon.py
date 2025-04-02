#####################
##    PARGAMMON    ##
## ANGEL ROJO SANZ ##
#####################

from random import randrange, seed, getstate, setstate

AZAR = 75 # Semilla para el random


class Jugada(object):
    def __init__(self, movs, puntos):
        self.MOVS = movs
        self.PUNTOS = puntos

    # Permite ordenar las jugadas mediante sort()
    def __eq__(self, otro):
        return self.PUNTOS == otro.PUNTOS
    
    def __lt__(self, otro):
        return self.PUNTOS < otro.PUNTOS


class Pargamon(object):
    def __init__(self, n=18, m=6, d=3, fichas=('\u263a','\u263b')):
        # Valores iniciales de la partida
        self.N = n
        self.M = m
        self.D = d
        self.FICHAS = fichas
        self.TABLERO = []
        self.JUGADAS = 0
        self.JUGADAS_POSIBLES = []
        self.PUNTUACIONES = [0] * len(fichas)
        self.FICHAS_SACADAS = [0] * len(fichas)
        
        # Agrega N columnas vacías al tablero
        for i in range(self.N):
            self.TABLERO.append([])
        # Rellena con M fichas las columnas iniciales
        # asociadas a los jugadores.
        for i in range(0,len(self.FICHAS)):
            self.TABLERO[i] = [self.FICHAS[i]] * self.M

        # Valores ASCII de las caras de los dados
        self.CARAS = ['','\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']
        # Turno = JUGADAS % nº de jugadores
        self.TURNO = 0
        # Valores de los dados 1-6
        self.dados = []
        # Almacena los estados anteriores
        self.historial = []


    def __repr__(self) -> str:
        # Construye una cadena de texto con el tablero y la información relevante para la partida
        cad = f"JUGADA #{self.JUGADAS} \n"
        for i in reversed(range(len(max(self.TABLERO, key=len)))):
            for row in self.TABLERO:
                cad += row[i] + '│' if i < len(row) else ' │'
            cad =  cad[0:-1] + '\n'
        cad += (' ').join([chr(65+c) for c in range(self.N)]) + '\n' # Añade A B C... al final del tablero
        cad += f"Turno de {self.FICHAS[self.TURNO]}: {' '.join(self.CARAS[d] for d in self.dados)}" # Muestra el turno actual y los dados 
        return cad


    def cambiar_turno(self) -> bool:
        # Comprueba si el jugador ha sacado todas las fichas del tablero
        if self.FICHAS_SACADAS[self.TURNO] == self.M:
            print(f"Han ganado los {self.FICHAS[self.TURNO]}!")
            return True
        self.dados = [randrange(6) + 1 for _ in range(self.D)]
        self.JUGADAS += 1
        self.TURNO = (self.JUGADAS-1) % len(self.FICHAS)
        self.actualziarPuntos()
        self.buscarJugadas(0, self.TABLERO)
        return False
    

    def jugar(self, txt_jugada: str) -> None | str:
        if len(txt_jugada) > self.D or len(txt_jugada) < self.D:
            return f'ERROR J1: Debe indicar exactamente {self.D} movimientos.'
        else:
            movimientos_invalidos = []
            tablero_simulado = self.copiarTablero(self.TABLERO)
            for i in range(self.D):
                print("Tablero SIM: \n", tablero_simulado)
                char = txt_jugada[i]
                if char == '@': continue
                saltos = self.dados[i]
                col = ord(char) - 65
                if col > self.N:
                    movimientos_invalidos.append(char)
                    continue
                if col + saltos > self.N:
                    return(f"ERROR J2-M3: Movimiento {char} -> {chr(col + saltos + 65)}, columna destino fuera de rango.")

                print("Longitud destino: ",len(tablero_simulado[col+saltos]))
                if len(tablero_simulado[col+saltos]) > 1:
                    return(f"ERROR J2-M4: Movimiento {char} -> {chr(col + saltos + 65)}, tiene más de una ficha contraria.")

                self.moverFicha(col, col+saltos, tablero_simulado)
            if len(movimientos_invalidos) > 0:
                return f"ERROR J2-M1: No existen columna(s) con estas letras: {",".join(movimientos_invalidos)}."
            else:
                for i in range(self.D):
                    char = txt_jugada[i]
                    if char == '@': continue
                    saltos = self.dados[i]
                    col = ord(char) - 65
                    self.moverFicha(col, col+saltos, self.TABLERO)
            print(movimientos_invalidos)
            return None


    def validarJugada(self, colI, saltos):
        colF = colI + saltos
        print("COLF: ", colF)
        ficha_turno = self.FICHAS[self.TURNO]
        if colI > self.N | colI < 0:
            print("Fuera de rango")
            return False
        elif len(self.TABLERO[colI]) == 0:
            print("Vacío")
            return False
        elif self.TABLERO[colI][0] != ficha_turno:
            print("No tiene fichas del jugador")
            return False
        elif colF > self.N:
            print("Salto fuera del tablero")
            return False
        elif colF == self.N:
            return True
        elif len(self.TABLERO[colF]) > 1:
            if self.TABLERO[colF][0] != ficha_turno:
                print("Ocupado")
                return False
        else:
            return True

    def moverFicha(self, ind_colI, ind_colF, tablero):
        try:
            colI = tablero[ind_colI]

            if ind_colF == self.N:
                colI.pop()
                self.FICHAS_SACADAS[self.TURNO] += 1
                return
          
            colF = tablero[ind_colF]
                
            if len(colF) == 1:
                if colF[0] != colI[0]:
                    tablero[self.FICHAS.index(colF[0])].append(colF[0])
                    colF[0] = colI[0]
                else:
                    colF.append(colI[0])
            else:
                colF.append(colI[0])
            colI.pop()
        except Exception as e:
            return e

    
    def calcularPuntos(self, tablero, jugador): # Jugador // Turno [0, n-1 jugadores]
        puntos = 0
        puntos += (3 * (self.N+1) * (self.FICHAS_SACADAS[jugador]))
        for col_i in range(self.N):
            col = tablero[col_i]
            nC = col.count(self.FICHAS[jugador])
            aC = 2 if nC > 1 else 1
            jC = col_i+1
            puntos += (nC*aC*jC)
        return puntos
    
    def actualziarPuntos(self):
        for i in range(len(self.FICHAS)):
            self.PUNTUACIONES[i] = self.calcularPuntos(self.TABLERO, i)
            return


    def copiarTablero(self, tablero):
        return [list(col) for col in tablero]


    def guardarEstado(self):
        estado_tablero = self.copiarTablero(self.TABLERO)
        estado_puntuaciones = list(self.PUNTUACIONES)
        estado_dados = list(self.dados)
        estado_fichas_sacadas = list(self.FICHAS_SACADAS)
        estado = (
            estado_tablero,
            estado_puntuaciones,
            estado_dados,
            estado_fichas_sacadas,
            self.JUGADAS,
            self.TURNO
        )
        self.historial.append(estado)
        return
    
    def deshacer(self, pasos):
        if pasos <= 0:
            print("Número de pasos inválido.")
        
        if pasos > len(self.historial):
            print("No se han realizado tantas jugadas.")

        estado_recuperado = None
        
        self.historial = self.historial[0:-pasos]
        estado_recuperado = self.historial[-1]

        if estado_recuperado:
            (tablero, puntuaciones, dados, fichas_sacadas, jugadas, turno) = estado_recuperado
            self.TABLERO = tablero
            self.PUNTUACIONES = puntuaciones
            self.dados = dados
            self.FICHAS_SACADAS = fichas_sacadas
            self.JUGADAS = jugadas
            self.TURNO = turno
            print(f"Se ha retrocedio a la jugada #{self.JUGADAS}.")
            
        else:
            print("ERROR: No se ha podido recuperar el estado.")
        return


    def buscarJugadas(self, n_dado, tablero, txt_jugadas = ""):
        print("Buscando jugada: ", n_dado)
        puntuacion = 0
        if n_dado == 0:
            tablero_sim = self.copiarTablero(self.TABLERO)
        else:
            tablero_sim = tablero
        if n_dado == self.D:
            puntuacion = (self.calcularPuntos(tablero_sim, self.TURNO) - self.calcularPuntos(self.TABLERO, self.TURNO))
            self.JUGADAS_POSIBLES.append(Jugada(txt_jugadas, puntuacion))
            return
        
        dado = self.dados[n_dado]
        for i_col in range(self.N):
            if self.validarJugada(i_col, dado):
                tablero_temp = self.copiarTablero(tablero_sim)
                self.moverFicha(i_col, i_col + dado, tablero_temp)
                self.buscarJugadas(n_dado + 1, tablero_temp, txt_jugadas + chr(i_col + 65))
        
        self.buscarJugadas(n_dado + 1, tablero_sim, txt_jugadas + '@')
        return

def main():
    seed(AZAR)
    print("*** PARGAMMON ***")
    #params = map(int, input("Numero de columnas, fichas y dados = ").split())
    juego = Pargamon(*[10, 5,3])
    finPartida = juego.cambiar_turno()
    print(juego)
    while not finPartida:        
        jugada = juego.jugar(input("Introduce tu jugada: "))
        while jugada != None:
            print(jugada)
            jugada = juego.jugar(input("Introduce tu jugada: "))
        finPartida = juego.cambiar_turno()
        print(juego)
main()

# seed(AZAR)
# juego = Pargamon(*[10, 5,3])
# finPartida = juego.cambiar_turno()
# print(juego)
# while not finPartida:        
#     print(juego.dados)
#     juego.buscarJugadas(0, juego.TABLERO)
#     # print(juego.JUGADAS_POSIBLES)
#     for jugada_valida in juego.JUGADAS_POSIBLES:
#         print((jugada_valida.MOVS, jugada_valida.PUNTOS))
#     print("--- Ordenadas ---")
#     juego.JUGADAS_POSIBLES.sort(reverse=1)
#     for jugada_valida in juego.JUGADAS_POSIBLES:
#         print((jugada_valida.MOVS, jugada_valida.PUNTOS))
#     jugada = juego.jugar(input("Introduce tu jugada: "))
#     while jugada != None:
#         print(jugada)
#         jugada = juego.jugar(input("Introduce tu jugada: "))
#     finPartida = juego.cambiar_turno()
#     print(juego)
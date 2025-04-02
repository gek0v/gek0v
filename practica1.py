#####################
##    PARGAMMON    ##
## ANGEL ROJO SANZ ##
#####################

from random import randrange, seed, getstate, setstate

AZAR = 75 # Semilla para el random

class Pargamon(object):
    def __init__(self, n=18, m=6, d=3, fichas=('\u263a','\u263b')):
        # Valores iniciales de la partida
        self.N = n
        self.M = m
        self.D = d
        self.FICHAS = fichas
        self.TABLERO = []
        self.JUGADAS = 0
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
        if max(self.FICHAS_SACADAS) == self.M:
            print(f"Han ganado los {self.FICHAS[self.TURNO]}!")
            return True
        self.dados = [randrange(6) + 1 for _ in range(self.D)]
        self.JUGADAS += 1
        self.TURNO = (self.JUGADAS-1) % len(self.FICHAS)
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
            self.actualizarPuntos()
            print(movimientos_invalidos)
            return None

    def moverFicha(self, ind_colI, ind_colF, tablero):
        colI = tablero[ind_colI]
        colF = tablero[ind_colF]

        try:
            if ind_colF == self.N:
                colI.pop()
                self.FICHAS_SACADAS[self.TURNO] += 1
                return
                
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

    
    def actualizarPuntos(self):
        for fich_i in range(len(self.FICHAS)):
            self.PUNTUACIONES[fich_i] = 3 * (self.N+1) * (self.FICHAS_SACADAS[fich_i])
        for col_i in range(self.N):
            col = self.TABLERO[col_i]
            for fich_i in range(len(self.FICHAS)):
                nC = col.count(self.FICHAS[fich_i])
                aC = 2 if nC > 1 else 1
                jC = col_i+1
                self.PUNTUACIONES[fich_i] += (nC*aC*jC)

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


def main():
    seed(AZAR)
    print("*** PARGAMMON ***")
    #params = map(int, input("Numero de columnas, fichas y dados = ").split())
    juego = Pargamon(*[10, 5,3])
    finPartida = juego.cambiar_turno()
    juego.actualizarPuntos()
    print(juego)
    while not finPartida:        
        jugada = juego.jugar(input("Introduce tu jugada: "))
        while jugada != None:
            print(jugada)
            jugada = juego.jugar(input("Introduce tu jugada: "))
        finPartida = juego.cambiar_turno()
        print(juego)

main()
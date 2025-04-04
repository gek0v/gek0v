"""
Ángel Rojo Sanz - Pargammon

Carácteristicas:
    - Juego Manual y Automático
    - Opción de deshacer (*)
    - Multiples jugadores
"""

from random import randrange, seed, choice

AZAR = 75 # Semilla para el random


class Jugada(object):
    def __init__(self, movs, valor):
        self.MOVS = movs    # Entrada de la jugada: ABC / @A@ ...
        self.VALOR = valor  # Valor de la jugada en base de la puntuación

    # Permite ordenar las jugadas mediante sort()
    def __eq__(self, otro):
        return self.VALOR == otro.VALOR
    
    def __lt__(self, otro):
        return self.VALOR < otro.VALOR


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
        
        # Guardará las jugadas posibles para cada turno
        self.JUGADAS_POSIBLES = []
        
        # Almacena los indices de los jugadores automáticos
        self.MAQUINAS_LISTAS = ()
        self.MAQUINAS_TONTAS = ()

        # Calcula la puntuación máxima / Se han sacado todas las fichas del tablero
        self.PUNTUACION_MAX = 3*(self.N+1) * self.M

        # Pregunta al usuario que tipo de jugador es cada ficha.
        # En caso de ser una maquina añade su indice a la tupla asociada
        for i in range(len(self.FICHAS)):
            tipo = input(f"Jugador {self.FICHAS[i]} es [H]umano, Máquina [T]onta o Máquina [L]ista: ")
            if tipo == 'T':
                self.MAQUINAS_TONTAS = self.MAQUINAS_TONTAS + (i,)
            elif tipo == 'L':
                self.MAQUINAS_LISTAS = self.MAQUINAS_LISTAS + (i,)
        
        
        # Agrega N columnas vacías al tablero
        for i in range(self.N):
            self.TABLERO.append([])
        
        # Rellena con M fichas las columnas iniciales asociadas a los jugadores.
        for i in range(0,len(self.FICHAS)):
            self.TABLERO[i] = [self.FICHAS[i]] * self.M

        # Valores UNICODE de las caras de los dados
        self.CARAS = ['','\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']
        # Turno = JUGADAS % nº de jugadores
        self.TURNO = 0
        # Valores de los dados 1-6
        self.dados = []
        # Almacena los estados anteriores
        self.historial = []


    def __repr__(self) -> str:
        # Construye una cadena de texto con el tablero y la información relevante para la partida
        cad = f"\nJUGADA #{self.JUGADAS} \n"

        # Recorre las columnas del índice más alto al más bajo
        # Con un máximo asociado a la columna con más fichas
        for i in reversed(range(len(max(self.TABLERO, key=len)))):
            for row in self.TABLERO:
                # En caso de tener una ficha en la posicion indicada la coloca junto a un separador
                # Si no existe una ficha en esa posicion coloca un espacio y un separador
                cad += row[i] + '│' if i < len(row) else ' │'
            cad =  cad[0:-1] + '\n' # Elimina el último separador sobrante
        # Añade A B C... al final del tablero
        cad += (' ').join([chr(65+c) for c in range(self.N)]) + '\n'
        # Muestra el turno actual y los dados
        cad += f"Turno de {self.FICHAS[self.TURNO]}: {' '.join(self.CARAS[d] for d in self.dados)}" 
        return cad


    def cambiar_turno(self) -> bool:
        # Guarda el estado actual para poder deshacer
        self.guardarEstado()

        # Actualiza el marcador de puntos para todos los jugadores
        self.actualziarPuntos()

        # Comprueba si el jugador ha sacado todas las fichas del tablero
        if self.PUNTUACIONES[self.TURNO] == self.PUNTUACION_MAX:
            print(f"\nHan ganado los {self.FICHAS[self.TURNO]}!")
            return True
        
        # Realiza una tirada de dados
        self.dados = [randrange(6) + 1 for _ in range(self.D)]
        self.JUGADAS += 1
        self.TURNO = (self.JUGADAS-1) % len(self.FICHAS)

        # Actualiza y ordena la lista de posibles jugadas
        self.JUGADAS_POSIBLES.clear()
        self.buscarJugadas(0, self.TABLERO)
        self.JUGADAS_POSIBLES.sort(reverse=True)

        # Comprueba si el turno siguiente pertenece a una máquina
        # En caso de ser así realiza la jugada y pasa de turno
        
        # Máquina lista: elige la mejor jugada (primera) de la lista.
        if self.TURNO in self.MAQUINAS_LISTAS:
            print(self)
            movimiento = self.JUGADAS_POSIBLES[0].MOVS 
            print("Jugada:", movimiento)
            self.jugar(movimiento)
            return self.cambiar_turno()
        # Máquina tonta: elige una jugada aleatoria de la lista
        elif self.TURNO in self.MAQUINAS_TONTAS:
            print(self)
            movimiento = choice(self.JUGADAS_POSIBLES).MOVS 
            print("Jugada:", movimiento)
            self.jugar(movimiento)
            return self.cambiar_turno()
        return False
    

    def jugar(self, txt_jugada: str) -> None | str:
        # Comprueba si el jugador trata de deshacer jugadas
        if txt_jugada[0] == '*':
            self.deshacer(len(txt_jugada))
            return None
        # Valida el numero de movimientos introducidos
        elif len(txt_jugada) > self.D or len(txt_jugada) < self.D:
            return f'ERROR J1: Debe indicar exactamente {self.D} movimientos.'
        
        # Comprueba la norma J3 / Jugada nula
        elif (txt_jugada == '@'*self.D):
            if(len(self.JUGADAS_POSIBLES) == 1):
                return None
            else:
                return "ERROR J3: No puede perder turno, existen otras jugadas válidas."
                
        # Comprueba que no hay caracteres fuera de rango
        movimientos_invalidos = []
        for char in txt_jugada:
            if char == '@': continue
            col = ord(char) - 65
            if col >= self.N:
                movimientos_invalidos.append(char)
                continue
        if len(movimientos_invalidos) > 0:
            movimientos_invalidos.sort(reverse=1)
            return f"ERROR J2-M1: No existen columna(s) con estas letras: {",".join(movimientos_invalidos)}."
        
        # Copia el tablero actual y compruba todos los movimientos introducidos
        tablero_simulado = self.copiarTablero(self.TABLERO)
        for i in range(self.D):
            char = txt_jugada[i]
            if char == '@': continue
            saltos = self.dados[i]
            col = ord(char) - 65
            validacion = self.validarJugada(col, saltos, tablero_simulado)
            if validacion != True:
                # En caso de una jugada invalida devuelve el motivo
                return validacion
            # Si la jugada es válida actualiza la copia del tablero para el siguiente movimiento
            self.moverFicha(col, col+saltos, tablero_simulado)

        # Una vez validadas las jugadas se realizan en el tablero principal
        for i in range(self.D):
            char = txt_jugada[i]
            if char == '@': continue
            saltos = self.dados[i]
            col = ord(char) - 65
            self.moverFicha(col, col+saltos, self.TABLERO)
        return None

    # Requiere el número de columna inicial, los los saltos a dar (dado)
    # y el tablero en el que probar la jugada
    def validarJugada(self, colI, saltos, tablero):
        colF = colI + saltos
        ficha_turno = self.FICHAS[self.TURNO]
        if colF > self.N:
            return f"ERROR J2-M3: Movimiento {chr(colI + 65)} -> {chr(colF + 65)}, columna destino fuera de rango."
        elif len(tablero[colI]) == 0:
            return f"ERROR J2-M2: Columna de origen {chr(colI + 65)} no tiene fichas del jugador"
        elif tablero[colI][0] != ficha_turno:
            return f"ERROR J2-M2: Columna de origen {chr(colI + 65)} no tiene fichas del jugador"
        elif colF == self.N:
            return True
        elif len(tablero[colF]) > 1:
            if tablero[colF][0] != ficha_turno:
                return f"ERROR J2-M4: Movimiento {chr(colI + 65)} -> {chr(colF + 65)}, columna destino tiene más de una ficha contraria."            
        return True

    # Requiere una validación previa de la jugada
    # Nº Columna Inicial, Nº Columna Destino, Tablero en el que realizar el movimiento
    def moverFicha(self, ind_colI, ind_colF, tablero):
        try:
            colI = tablero[ind_colI]

            # Saca la ficha del tablero
            if ind_colF == self.N:
                colI.pop()
                return
            
            colF = tablero[ind_colF]

            # Copia una ficha de la columna de origen a la de destino
            if len(colF) >= 1:
                # Se come la ficha contraria
                if colF[0] != colI[0]:
                    # Retrocede la ficha contraria a la columna inicial
                    self.moverFicha(ind_colF, self.FICHAS.index(colF[0]), tablero)
            colF.append(colI[0])
            colI.pop()
        except Exception as e:
            return e

    # Tablero a evaluar, Jugador -> [0, n-1 jugadores]
    def calcularPuntos(self, tablero, jugador):
        puntos = 0
        # Cálculo de fichas sacadas
        fichas_sacadas = self.M
        for col in tablero:
            fichas_sacadas -= col.count(self.FICHAS[jugador])

        puntos += (3 * (self.N+1) * fichas_sacadas)

        # Suma los puntos de las fichas en el interior del tablero
        for col_i in range(self.N):
            col = tablero[col_i]
            nC = col.count(self.FICHAS[jugador])
            aC = 2 if nC > 1 else 1
            jC = col_i+1
            puntos += (nC*aC*jC)
        return puntos
    
    # Calcula la puntuacion de todos los jugadores en el tablero principal
    def actualziarPuntos(self):
        for i in range(len(self.FICHAS)):
            self.PUNTUACIONES[i] = self.calcularPuntos(self.TABLERO, i)
        return

    # Crea una copia del tablero
    def copiarTablero(self, tablero):
        return [list(col) for col in tablero]

    # Guarda el estado de la partida en el historial
    def guardarEstado(self):
        estado_tablero = self.copiarTablero(self.TABLERO)
        estado_puntuaciones = list(self.PUNTUACIONES)
        estado_dados = list(self.dados)
        estado = (
            estado_tablero,
            estado_puntuaciones,
            estado_dados,
            self.JUGADAS,
            self.TURNO
        )
        self.historial.append(estado)
        return
    
    # Retrocede tantos estados como pasos indicados
    def deshacer(self, pasos):
        if pasos <= 0:
            print("Número de pasos inválido.")
        
        if pasos > len(self.historial):
            print("No se han realizado tantas jugadas.")
        
        # Borra los estados posterirores
        self.historial = self.historial[0:-pasos]
        # Carga el último estado
        estado_recuperado = self.historial[-1]

        # Si existe el estado sustituye los valores actuales con los cargados
        if estado_recuperado:
            (tablero, puntuaciones, dados, jugadas, turno) = estado_recuperado
            self.TABLERO = tablero
            self.PUNTUACIONES = puntuaciones
            self.dados = dados
            self.JUGADAS = jugadas
            self.TURNO = turno

            # Imprime el tablero recuperado y busca las jugadas posibles
            print(self)
            self.buscarJugadas(0, self.TABLERO)
            self.JUGADAS_POSIBLES.sort(reverse=1)

            # Comprueba si el turno le pertenece a una máquina
            if self.TURNO in self.MAQUINAS_LISTAS:
                movimiento = self.JUGADAS_POSIBLES[0].MOVS 
                print("Jugada:", movimiento)
                self.jugar(movimiento)
            elif self.TURNO in self.MAQUINAS_TONTAS:
                movimiento = choice(self.JUGADAS_POSIBLES).MOVS 
                print("Jugada:", movimiento)
                self.jugar(movimiento)
        else:
            print("ERROR: No se ha podido recuperar el estado.")
        return None


    # Función recursiva que valida todas las jugadas posibles con los dados y turno actual
    # Requiere: Nº de dado [0:self.D], tablero con el que probar las jugadas y jugadas previas
    # El jugador es el asociado al turno de la partida
    def buscarJugadas(self, n_dado, tablero, txt_jugadas = ""):
        # Para el caso inicial copia el tablero de la partida
        if n_dado == 0:
            tablero_sim = self.copiarTablero(self.TABLERO)
        else:
            tablero_sim = tablero

        # Con el caso final calcula el valor de la jugada y añade a la lista de posibles jugadas
        # una instancia con sus características.
        if n_dado == self.D:
            # PK -> Puntuacion total de los jugadores
            # Valor -> 2 veces la puntuación del jugador - PK
            valor = 2 * self.calcularPuntos(tablero_sim, self.TURNO)
            pk = 0
            for jugador in range(len(self.FICHAS)):
                pk += self.calcularPuntos(tablero_sim, jugador)
            valor -= pk
            self.JUGADAS_POSIBLES.append(Jugada(txt_jugadas, valor))
            return
        
        dado = self.dados[n_dado]
        # Prueba el dado con todas las columnas que contienen fichas del jugador
        for i_col in range(self.N):
            if self.validarJugada(i_col, dado, tablero_sim) == True:
                tablero_temp = self.copiarTablero(tablero_sim)
                self.moverFicha(i_col, i_col + dado, tablero_temp)
                self.buscarJugadas(n_dado + 1, tablero_temp, txt_jugadas + chr(i_col + 65))

        # En caso de no encontrar jugadas posibles no usa el dado (@)
        self.buscarJugadas(n_dado + 1, tablero_sim, txt_jugadas + '@')
        return

def main():
    seed(AZAR)
    print("*** PARGAMMON ***")
    params = map(int, input("Numero de columnas, fichas y dados = ").split())
    juego = Pargamon(*params)
    finPartida = juego.cambiar_turno()
    while not finPartida:
        print(juego)
        jugada = juego.jugar(input("Jugada: "))
        while jugada != None:
            print(jugada)
            jugada = juego.jugar(input("Jugada: "))
        finPartida = juego.cambiar_turno()
main()
from State import State
from bitboard import BitboardManager

import random
class Card:
    def __init__(self, name, movements, startPlayerIndicator):
        self.name = name
        self.movements = movements
        self.startPlayerIndicator = startPlayerIndicator


class CardList:
    cardList = [
        Card("Tiger", [(1, 0), (-2, 0)], "B"),
        Card("Dragon", [(1, -1), (1, 1), (-1, -2), (-1, 2)], "R"),
        Card("Frog", [(-1, -1), (0, -2), (1, 1)], "R"),
        Card("Rabbit", [(1, -1), (-1, 1), (0, 2)], "B"),
        Card("Crab", [(-1, 0), (0, -2), (0, 2)], "B"),
        Card("Elephant", [(0, -1), (-1, -1), (0, 1), (-1, 1)], "R"),
        Card("Goose", [(0, -1), (-1, -1), (0, 1), (1, 1)], "B"),
        Card("Rooster", [(0, -1), (1, -1), (0, 1), (-1, 1)], "R"),
        Card("Monkey",[(-1,-1),(-1,1),(1,-1),(1,1)],"B"),
        Card("Mantis", [(1,0), (-1,1), (-1,-1)], "R"),
        Card("Horse", [(1,0), (-1,0), (0,-1)], "R"),
        Card("Ox", [(-1,0), (1,0), (0,1)], "B"),
        Card("Crane", [(-1,0), (1,-1), (1,1)], "B"),
        Card("Boar", [(-1,0), (0,-1), (0,1)], "R"),
        Card("Eel", [(0,1), (-1,-1), (1,-1)], "B"),
        Card("Cobra", [(0,-1), (-1,1), (1,1)], "R"),
    ]


# Game is played from the perspective of red player
class OnitamaState(State):

    def __init__(self):
        self.sizeI = 5
        self.sizeJ = 5

        self.bm = BitboardManager(self.sizeI, self.sizeJ)


        self.blueTempleCoordinate = (0, 2)
        self.redTempleCoordinate = (4, 2)

        self.redPlayerCards = []
        self.bluePlayerCards = []

        self.neutralCard = None

        self.__initBoard()
        self.__initCards()

        self.currentPlayer = self.__determineFirstPlayer()

    def __initCards(self):
        firstCard = random.choice(CardList.cardList)
        self.redPlayerCards.append(firstCard)
        CardList.cardList.remove(firstCard)

        secondCard = random.choice(CardList.cardList)
        self.bluePlayerCards.append(secondCard)
        CardList.cardList.remove(secondCard)

        thirdCard = random.choice(CardList.cardList)
        self.redPlayerCards.append(thirdCard)
        CardList.cardList.remove(thirdCard)

        fourthCard = random.choice(CardList.cardList)
        self.bluePlayerCards.append(fourthCard)
        CardList.cardList.remove(fourthCard)

        self.neutralCard = random.choice(CardList.cardList)

    def __initBoard(self):
        # B = Blue master, R = Red master, b = Blue pawn, r = Red pawn
        self.bm.buildBitboard("B")
        self.bm.buildBitboard("b")

        self.bm.buildBitboard("R")
        self.bm.buildBitboard("r")

        self.__initBluePieces()
        self.__initRedPieces()

    def __determineFirstPlayer(self):
        return self.neutralCard.startPlayerIndicator

    def __initBluePieces(self):
        # Set master piece
        self.bm.setPiece("B", 0, 2)

        self.bm.setPiece('b', 0, 0)
        self.bm.setPiece('b', 0, 1)
        self.bm.setPiece('b', 0, 3)
        self.bm.setPiece('b', 0, 4)

    def __initRedPieces(self):
        # Set master piece
        self.bm.setPiece("R", 4, 2)

        self.bm.setPiece('r', 4, 0)
        self.bm.setPiece('r', 4, 1)
        self.bm.setPiece('r', 4, 3)
        self.bm.setPiece('r', 4, 4)

    def isEnd(self):
        return self.value() == float('inf') or self.value() == float('-inf')

    # Blue wins -> infinity
    # Red wins -> -infinity
    def value(self):
        # Is blue master at red temple? -> if yes then Blue wins
        if self.bm.isPieceSet('B', *self.redTempleCoordinate): return float('inf')

        # Is blue master alive? -> if not then Red wins
        if self.bm.isEmpty('B'): return float('-inf')

        # Is red master at blue temple? -> if yes then Red wins
        if self.bm.isPieceSet('R', *self.blueTempleCoordinate): return float('-inf')

        # Is red master alive? -> if not then blue wins
        if self.bm.isEmpty('R'): return float('inf')


    def isFirstPlayerTurn(self):
        return self.__determineFirstPlayer() == self.currentPlayer

    def __getAllPossibleMovesWithCard(self, card: Card, currentPlayer):
        pieceMovements = card.movements
        if currentPlayer == 'B':
            pieceLocationsPawn = self.bm.getCoordinatesOfPieces('b')
            pieceLocationsMaster = self.bm.getCoordinatesOfPieces('B')
            possibleMoves = self.bm.generateAllPossibleMoves('b', pieceMovements, pieceLocationsPawn)
            possibleMoves.update(self.bm.generateAllPossibleMoves('B', pieceMovements, pieceLocationsMaster))
        elif currentPlayer == 'R':
            pieceLocationsPawn = self.bm.getCoordinatesOfPieces('r')
            pieceLocationsMaster = self.bm.getCoordinatesOfPieces('R')
            possibleMoves = self.bm.generateAllPossibleMoves('r', pieceMovements, pieceLocationsPawn)
            possibleMoves.update(self.bm.generateAllPossibleMoves('R', pieceMovements, pieceLocationsMaster))
        else:
            raise Exception('Invalid player indicator')
        return possibleMoves

    #Basically generate next states
    def getAllPossibleNextStates(self):
        if self.currentPlayer == 'B':
            movesWithFirstCard = self.__getAllPossibleMovesWithCard(self.bluePlayerCards[0], 'B')
            movesWithSecondCard = self.__getAllPossibleMovesWithCard(self.bluePlayerCards[1], 'B')
        elif self.currentPlayer == 'R':
            movesWithFirstCard = self.__getAllPossibleMovesWithCard(self.redPlayerCards[0], 'R')
            movesWithSecondCard = self.__getAllPossibleMovesWithCard(self.redPlayerCards[1], 'R')
        else:
            raise Exception('Invalid player indicator')





        return

    def generateNextStates(self, movesWithFirstCard, movesWithSecondCard):
        nextStates = []
        for bitboardId, move in movesWithFirstCard.items():



    def hash(self):
        pass

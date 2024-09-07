from State import State
from bitboard import BitboardManager


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
        self.bm = BitboardManager()
        self.sizeI = 5
        self.sizeJ = 5
        self.blueTempleCoordinate = (0, 2)
        self.redTempleCoordinate = (4, 2)

        self.redPlayerCards = {}
        self.bluePlayerCards = {}

        self.neutralCard = None

        self.__initBoard()

    def __initCards(self):

    def __initBoard(self):
        # B = Blue master, R = Red master, b = Blue pawn, r = Red pawn
        self.bm.buildBitboard("B")
        self.bm.buildBitboard("b")

        self.bm.buildBitboard("R")
        self.bm.buildBitboard("r")

        self.__initBluePieces()
        self.__initRedPieces()

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
        pass

    def getAllPossibleMoves(self):
        pass

    def hash(self):
        pass

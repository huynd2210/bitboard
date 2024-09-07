from State import State
from bitboard import BitboardManager


class TicTacToeState(State):
    def __init__(self):
        self.bm = BitboardManager()
        self.sizeI = 3
        self.sizeJ = 3
        self.current_player = 'X'
        self.isEnd = None
    def initBoard(self, sizeI, sizeJ):
        self.bm.buildBitboard('X', sizeI, sizeJ)
        self.bm.buildBitboard('O', sizeI, sizeJ)
    def value(self):
        pass

    def isFirstPlayerTurn(self):
        pass

    def getAllPossibleMoves(self):
        pass

    def hash(self):
        pass

    def isEnd(self):
        pass
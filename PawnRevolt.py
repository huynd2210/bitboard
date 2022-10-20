from abc import ABC

from easyAI import AI_Player, TwoPlayerGame

from bitboard import BitboardManager


class Game(TwoPlayerGame):
    def __init__(self, players=None, sizeI=7, sizeJ=5):
        self.bm = BitboardManager()
        if players is None:
            self.players = [AI_Player(None), AI_Player(None)]
        else:
            self.players = players

        self.current_players = 1
        self.sizeI = sizeI
        self.sizeJ = sizeJ
        self.hasLost = None
        self.firstPlayerPieceCoords = []
        self.secondPlayerPieceCoords = []
        self._initBoard(sizeI, sizeJ)

    def possible_moves(self):

    def make_move(self):

    def is_over(self):
        if self.bm.isRowAnyPieceSet('1', 0):
            return True, '1'
        if self.bm.isRowAnyPieceSet('2', self.bm.sizeI - 1):
            return True, '2'
        if self.bm.isEmpty('1'):
            return True, '2'
        if self.bm.isEmpty('2'):
            return True, '1'
        return False, '0'

    def lose(self):
        self.hasLost = self.opponent_index == int(self.is_over()[1])

    def _initBoard(self, sizeI, sizeJ):
        self.bm.buildBitboard('1', sizeI, sizeJ)
        self.bm.buildBitboard('2', sizeI, sizeJ)
        self.bm.setAllBitsAtRow('2', 0)
        self.bm.setAllBitsAtRow('2', 1)
        self.bm.setAllBitsAtRow('1', sizeI - 2)
        self.bm.setAllBitsAtRow('1', sizeI - 1)
        for i in range(2):
            for j in range(5):
                self.secondPlayerPieceCoords.append((i,j))

        for i in range(sizeI - 2, sizeI):
            for j in range(5):
                self.firstPlayerPieceCoords.append((i,j))

    def getAllPossibleMovesFor1(self):
        possibleMoves = []
        allMovesForBluePawn = [(-1, 0), (-1, 1), (-1, -1)]
        bluePawnMovements = {'1'}
        self.bm.generateAllPossibleMoves()





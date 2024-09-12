from State import State
from bitboard import BitboardManager


class HexapawnState(State):

    def __init__(self, sizeI=3, sizeJ=3, isInitialState=True, stateInformation=None):
        if isInitialState:
            self.__initInitialState(sizeI, sizeJ)
        elif stateInformation is not None:
            self.passStateInformation(*stateInformation)
        else:
            raise Exception("Requires either initial state or state information")

    def passStateInformation(self, depth, parent_hash, currentPlayer, bmInfoDump):
        self.depth = depth
        self.parent_hash = parent_hash
        self.currentPlayer = currentPlayer
        self.bm = BitboardManager(infoDump=bmInfoDump)


    def __initInitialState(self, sizeI, sizeJ):
        self.sizeI = sizeI
        self.sizeJ = sizeJ
        self.__initBoard()
        self.currentPlayer = '1'
        self.depth = 0

        self.firstPlayerPawnMovements = [(-1, 0)]
        self.firstPlayerPawnCaptureMovements = [(-1, 1), (-1, -1)]

        self.secondPlayerPawnMovements = [(1, 0)]
        self.secondPlayerPawnCaptureMovements = [(1, 1), (1, -1)]


    def __initBoard(self):
        self.bm = BitboardManager(self.sizeI, self.sizeJ)
        self.bm.buildBitboard('1')
        self.bm.buildBitboard('2')

        self.bm.setPiece('2', 0, 0)
        self.bm.setPiece('2', 0, 1)
        self.bm.setPiece('2', 0, 2)

        self.bm.setPiece('1', 2, 0)
        self.bm.setPiece('1', 2, 1)
        self.bm.setPiece('1', 2, 2)

    def isFirstPlayerTurn(self):
        return self.currentPlayer == '1'

    def isEnd(self):
        return self.value() == float('inf') or self.value() == float('-inf')
    #Get value of this state. Win for first player is infinity, win for second player is -infinity
    def value(self):
        if self.bm.isAnyPieceSetAtRow('1', 0): return float('inf')

        if self.bm.isAnyPieceSetAtRow('2', 2): return float('-inf')

        if self.currentPlayer == '1' and len(self.getAllPossibleNextStates()) == 0: return float('-inf')

        if self.currentPlayer == '2' and len(self.getAllPossibleNextStates()) == 0: return float('inf')

        return None

    def loadInfoDump(self, infoDump):
        self.bm.loadInfo(infoDump)

    def hash(self):
        pass

    def getAllPossibleNextStates(self):
        pass

    def getAllPossibleNextStatesFor1(self):
        firstPlayerPieceCoords = self.bm.getCoordinatesOfPieces('1')
        secondPlayerPieceCoords = self.bm.getCoordinatesOfPieces('2')
        nextStates = []

        for coord in firstPlayerPieceCoords:
            nextStates += self.bm.generateAllPossibleMoves('1', self.firstPlayerPawnMovements, coord)
            nextStates += self.bm.generateAllPossibleMoves('1', self.firstPlayerPawnCaptureMovements, coord)

        return nextStates


from bitboard import BitboardManager
from pairing_functions import szudzik

class Game:
    def __init__(self, sizeI=7, sizeJ=5):
        self.bm = BitboardManager()
        self.current_player = '1'
        self.sizeI = sizeI
        self.sizeJ = sizeJ
        self.isEnd = None
        self.winner = ''
        self.pieceCoord = {}
        self._initBoard(sizeI, sizeJ)
        self.parentPlayer1Board = None
        self.parentPlayer2Board = None

    def make_move(self, move):
        # move = tuple(map(lambda s: ("ABCDEFGHIJ".index(s[0]), int(s[1:])), move.split(" ")))
        bitboardId, fromI, fromJ, toI, toJ = move
        opponent = '1' if self.current_player == '2' else '2'
        self.bm.moveWithCapture(bitboardId, fromI, fromJ, toI, toJ, [opponent])
        self.current_player = '1' if self.current_player == '2' else '2'

    def show(self):
        self.bm.showAllBitboard()

    def is_over(self):
        if self.bm.isRowAnyPieceSet('1', 0):
            self.winner = '1'
            return True
        if self.bm.isRowAnyPieceSet('2', self.bm.sizeI - 1):
            self.winner = '2'
            return True
        if self.bm.isEmpty('1'):
            self.winner = '2'
            return True
        if self.bm.isEmpty('2'):
            self.winner = '1'
            return True
        return False

    # def lose(self):
    #     self.hasLost = self.opponent_index == int(self.is_over())

    def _initBoard(self, sizeI, sizeJ):
        self.bm.buildBitboard('1', sizeI, sizeJ)
        self.bm.buildBitboard('2', sizeI, sizeJ)
        self.bm.setAllBitsAtRow('2', 0)
        self.bm.setAllBitsAtRow('2', 1)
        self.bm.setAllBitsAtRow('1', sizeI - 2)
        self.bm.setAllBitsAtRow('1', sizeI - 1)
        pieceFor2 = []

        for i in range(2):
            for j in range(sizeJ):
                pieceFor2.append((i, j))

        self.pieceCoord['2'] = pieceFor2

        pieceFor1 = []
        for i in range(sizeI - 2, sizeI):
            for j in range(sizeJ):
                pieceFor1.append((i, j))

        self.pieceCoord['1'] = pieceFor1

    def getAllPossibleMovesFor1(self):
        bluePawnMovements = {'1': [(-1, 0), (-1, 1), (-1, -1)]}
        return self.bm.generateAllPossibleMoves('1', bluePawnMovements, self.pieceCoord)

    def getAllPossibleMovesFor2(self):
        redPawnMovements = {'2': [(1, 0), (1, 1), (1, -1)]}
        return self.bm.generateAllPossibleMoves('2', redPawnMovements, self.pieceCoord)

    def getAllPossibleMoves(self, isFirstPlayerTurn):
        possibleMoves = self.getAllPossibleMovesFor1() if isFirstPlayerTurn else self.getAllPossibleMovesFor2()
        possibleMoves = list(possibleMoves.values())

        # return list(map(lambda move: "ABCDEFGHIJ"[move[1]] + str(move[2]) + " " + "ABCDEFGHIJ"[move[3]] + str(move[4]),
        #                 possibleMoves))
        return possibleMoves[0]

    def getAllNextStates(self, isFirstPlayerTurn):
        possibleMoves = self.getAllPossibleMoves(isFirstPlayerTurn)
        nextStates = []
        currentState = self.getGameState()
        for move in possibleMoves:
            self.make_move(move)
            self.isEnd = self.is_over()
            # currentState[0] is player '1' bitboard, currentState[1] is player '2' bitboard and hence the parent value
            self.parentPlayer1Board = currentState[0]
            self.parentPlayer2Board = currentState[1]
            nextStates.append(self.getGameState())
            self.loadState(currentState)
        return nextStates


    def loadFromQueue(self, queue, processBatchSize):
        iteration = len(queue) if len(queue) < processBatchSize else processBatchSize
        children = []
        for i in range(iteration):
            children.append(queue.pop())
        return children

    def printBitboards(self):
        self.bm.showAllBitboard()

    def printListAsGrid(self, input):
        for i in input:
            print(i)

    def printBoard(self):
        self.printListAsGrid(self.bm.translateBitboardsToMailbox())

    def getGameState(self):
        return self.bm.bitboardManager['1'].data, self.bm['2'].data, self.current_player, self.isEnd, self.winner, self.parentPlayer1Board, self.parentPlayer2Board

    def loadState(self, state):
        firstPlayerBitboard, secondPlayerBitboard, currentPlayer, isEnd, winner, parentPlayer1Board, parentPlayer2Board = state
        self.bm.bitboardManager['1'].data = firstPlayerBitboard
        self.bm.bitboardManager['2'].data = secondPlayerBitboard
        self.current_player = currentPlayer
        self.isEnd = isEnd
        self.winner = winner
        self.parentPlayer1Board = parentPlayer1Board
        self.parentPlayer2Board = parentPlayer2Board

    def solveQueue(self, queue, buffer, transpositionTable):
        for state in queue:
            game.loadState(state)
            stateHash = szudzik.pair(self.bm.bitboardManager['1'].data, self.bm.bitboardManager['2'])
            if stateHash not in transpositionTable:
                children = self.getAllNextStates(self.current_player == '1')
                buffer.append()


    # def solve(self):
    #     isFirstPlayerTurn = True
    #     children = self.getAllNextStates(isFirstPlayerTurn)
    #
    #     queue = []
    #     for child in children:
    #         self.loadState(child)
    #         queue.append(self.getAllNextStates(not isFirstPlayerTurn))
    #         # saveChild
    #     self.saveBatch(queue, batchSize=3000)
    #
    # def saveBatch(self, queue, batchSize):
    #     if len(queue) >= batchSize:
    #         # do save
    #         pass


if __name__ == '__main__':
    game = Game()
    # game.printBoard()
    # print("------------")
    # possibleMoves = game.getAllPossibleMoves(True)
    # game.make_move(possibleMoves[0])
    # game.printBoard()
    # print(game.getGameState())

    nextStates = game.getAllNextStates(True)
    for state in nextStates:
        game.loadState(state)
        game.printBoard()
        print("--------")
        print(game.getGameState())
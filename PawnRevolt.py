from easyAI import AI_Player, TwoPlayerGame, Human_Player

from bitboard import BitboardManager

class Game(TwoPlayerGame):
    def __init__(self, players=None, sizeI=7, sizeJ=5):
        self.bm = BitboardManager()
        if players is None:
            self.players = [AI_Player(None), AI_Player(None)]
        else:
            self.players = players

        self.current_player = 1
        self.sizeI = sizeI
        self.sizeJ = sizeJ
        self.hasLost = None
        self.winner = ''
        self.pieceCoord = {}
        self._initBoard(sizeI, sizeJ)

    def possible_moves(self):
        return self.getAllPossibleMoves(self.current_player == 1)

    def make_move(self, move):
        move = tuple(map(lambda s: ("ABCDEFGHIJ".index(s[0]), int(s[1:])), move.split(" ")))
        bitboardId, fromI, fromJ, toI, toJ = move
        self.bm.moveWithCapture(bitboardId, fromI, fromJ, toI, toJ, ['2'])

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

    def lose(self):
        self.hasLost = self.opponent_index == int(self.is_over())

    def _initBoard(self, sizeI, sizeJ):
        self.bm.buildBitboard('1', sizeI, sizeJ)
        self.bm.buildBitboard('2', sizeI, sizeJ)
        self.bm.setAllBitsAtRow('2', 0)
        self.bm.setAllBitsAtRow('2', 1)
        self.bm.setAllBitsAtRow('1', sizeI - 2)
        self.bm.setAllBitsAtRow('1', sizeI - 1)
        # for i in range(2):
        #     for j in range(5):
        #         self.secondPlayerPieceCoords.append((i, j))
        #
        # for i in range(sizeI - 2, sizeI):
        #     for j in range(5):
        #         self.firstPlayerPieceCoords.append((i, j))

    def getAllPossibleMovesFor1(self):
        bluePawnMovements = {'1': [(-1, 0), (-1, 1), (-1, -1)]}
        return self.bm.generateAllPossibleMoves(bluePawnMovements, self.pieceCoord)

    def getAllPossibleMovesFor2(self):
        redPawnMovements = {'2': [(1, 0), (1, 1), (1, -1)]}
        return self.bm.generateAllPossibleMoves(redPawnMovements, self.pieceCoord)

    def getAllPossibleMoves(self, isFirstPlayerTurn):
        possibleMoves = self.getAllPossibleMovesFor1() if isFirstPlayerTurn else self.getAllPossibleMovesFor2()
        return list(map(lambda move: "ABCDEFGHIJ"[move[1]] + str(move[2]) + " " + "ABCDEFGHIJ"[move[3]] + str(move[4]),
                        possibleMoves))


if __name__ == '__main__':
    game = Game([Human_Player(), Human_Player()])
    game.play()

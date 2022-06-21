from functools import lru_cache


class Bitboard:
    def __init__(self, data, sizeI, sizeJ):
        self.data = data
        self.sizeI = sizeI
        self.sizeJ = sizeJ


class BitboardManager:
    def __init__(self):
        self.bitboardManager = {}

    def translateBoardToBitboards(self, board):
        sizeI = len(board)
        sizeJ = len(board[0])
        for i in range(sizeI):
            for j in range(sizeJ):
                piece = board[i][j]
                if str(piece) not in self.bitboardManager:
                    self.buildBitboard(piece, sizeI, sizeJ)
                self.setPiece(piece, i, j)

    def buildBitboard(self, bitboardId, sizeI, sizeJ):
        bitboardId = self.enforceStringTypeId(bitboardId)
        self.bitboardManager[bitboardId] = Bitboard(0, sizeI, sizeJ)

    def showBitboard(self, bitboardId):
        bitboard = self.bitboardManager[bitboardId]
        board = "{0:b}".format(bitboard.data)
        if len(board) < bitboard.sizeI * bitboard.sizeJ:
            board = self.padBitboard(board, bitboard.sizeI * bitboard.sizeJ)

        for i in range(len(board) - 1, -1, -1):
            endLineIndex = (i + 1)
            print(f"[{board[i]}]") if endLineIndex % bitboard.sizeJ == 1 and endLineIndex != len(board) \
                else print(f"[{board[i]}]", end="")

    def showAllBitboard(self):
        for key in self.bitboardManager:
            print(key, ':')
            self.showBitboard(key)
            print()

    def padBitboard(self, board, maxSize):
        pad = '0' * (maxSize - len(board))
        return pad + board

    @lru_cache(maxsize=None)
    def isInBound(self, bitboard, i, j):
        return 0 <= i < bitboard.sizeI and 0 <= j < bitboard.sizeJ

    def isPieceSet(self, bitboardId, i, j):
        bitboardId = self.enforceStringTypeId(bitboardId)
        bitboard = self.bitboardManager[bitboardId]
        if not self.isInBound(bitboard, i, j):
            return False
        piecePosition = (i * bitboard.sizeJ) + j
        return ((bitboard.data >> piecePosition) & 1) == 1

    def setPiece(self, bitboardId, i, j):
        bitboardId = self.enforceStringTypeId(bitboardId)
        bitboard = self.bitboardManager[bitboardId]
        if not self.isInBound(bitboard, i, j):
            return
        piecePosition = (i * bitboard.sizeJ) + j
        bitboard.data = bitboard.data | (1 << piecePosition)

    def deletePiece(self, bitboardId, i, j):
        bitboardId = self.enforceStringTypeId(bitboardId)
        bitboard = self.bitboardManager[bitboardId]
        if not self.isInBound(bitboard, i, j):
            return
        piecePosition = (i * bitboard.sizeJ) + j
        bitboard.data = bitboard.data & ~(1 << piecePosition)

    def movePiece(self, bitboardId, fromI, fromJ, toI, toJ):
        if self.isPieceSet(bitboardId, fromI, fromJ):
            self.deletePiece(bitboardId, fromI, fromJ)
            self.setPiece(bitboardId, toI, toJ)

    def setAllBits(self, bitboardId):
        bitboardId = self.enforceStringTypeId(bitboardId)
        bitboard = self.bitboardManager[bitboardId]
        for i in range(bitboard.sizeI):
            for j in range(bitboard.sizeJ):
                self.setPiece(bitboardId, i, j)

    def deleteNeighbors(self, bitboardId, i, j):
        self.deletePiece(bitboardId, i + 1, j)
        self.deletePiece(bitboardId, i - 1, j)
        self.deletePiece(bitboardId, i, j + 1)
        self.deletePiece(bitboardId, i, j - 1)
        self.deletePiece(bitboardId, i + 1, j + 1)
        self.deletePiece(bitboardId, i + 1, j - 1)
        self.deletePiece(bitboardId, i - 1, j + 1)
        self.deletePiece(bitboardId, i - 1, j - 1)

    def setNeighbors(self, bitboardId, i, j):
        self.setPiece(bitboardId, i + 1, j)
        self.setPiece(bitboardId, i - 1, j)
        self.setPiece(bitboardId, i, j + 1)
        self.setPiece(bitboardId, i, j - 1)
        self.setPiece(bitboardId, i + 1, j + 1)
        self.setPiece(bitboardId, i + 1, j - 1)
        self.setPiece(bitboardId, i - 1, j + 1)
        self.setPiece(bitboardId, i - 1, j - 1)

    def enforceStringTypeId(self, bitboardId):
        if type(bitboardId) is not str:
            bitboardId = str(bitboardId)
        return bitboardId

if __name__ == '__main__':
    bm = BitboardManager()
    # bm.buildBitboard('a', 4, 5)
    # print(bm.bitboardManager['a'].data)
    # # bm.setAllBits('a')
    # bm.setNeighbors('a', 1,1)
    # bm.deleteNeighbors('a',1,1)
    # bm.showBitboard('a')

    board = [[0, 0, 0], [0, 0, 0], [1, 1, 1], [2, 2, 2]]
    bm.translateBoardToBitboards(board)
    bm.showAllBitboard()
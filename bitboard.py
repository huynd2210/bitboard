import time
from functools import lru_cache


class Bitboard:
    def __init__(self, data, sizeI, sizeJ):
        self.data = data
        self.sizeI = sizeI
        self.sizeJ = sizeJ

    def __str__(self):
        return str(self.data)


# start from top left to bottom right, i.e 1 = 1 at (0,0)
class BitboardManager:
    def __init__(self):
        self.bitboardManager = {}
        self.sizeI = 0
        self.sizeJ = 0

    def __getitem__(self, item):
        return self.bitboardManager[item]

    def __setitem__(self, key, value):
        self.bitboardManager[key] = value

    def translateMailboxToBitboards(self, board):
        sizeI = len(board)
        sizeJ = len(board[0])
        for i in range(sizeI):
            for j in range(sizeJ):
                piece = board[i][j]
                if str(piece) not in self.bitboardManager:
                    self.buildBitboard(piece, sizeI, sizeJ)
                self.setPiece(piece, i, j)

    def translateBitboardsToMailbox(self):
        board = []

        for _ in range(self.sizeI):
            row = ['.' for _ in range(self.sizeJ)]
            board.append(row)

        for bitboardId, bitboard in self.bitboardManager.items():
            for i in range(bitboard.sizeI):
                for j in range(bitboard.sizeJ):
                    if self.isPieceSet(bitboardId, i, j):
                        board[i][j] = bitboardId
        return board

    def buildBitboard(self, bitboardId, sizeI, sizeJ):
        bitboardId = self.enforceStringTypeId(bitboardId)
        self.bitboardManager[bitboardId] = Bitboard(0, sizeI, sizeJ)
        self.sizeI = sizeI
        self.sizeJ = sizeJ

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
    def isInBound(self, i, j):
        return 0 <= i < self.sizeI and 0 <= j < self.sizeJ

    def isEmpty(self, bitboardId):
        return self.bitboardManager[bitboardId].data == 0

    def isPieceSet(self, bitboardId, i, j):
        bitboardId = self.enforceStringTypeId(bitboardId)
        bitboard = self.bitboardManager[bitboardId]
        if not self.isInBound(i, j):
            return False
        piecePosition = (i * bitboard.sizeJ) + j
        return ((bitboard.data >> piecePosition) & 1) == 1

    def setPiece(self, bitboardId, i, j):
        bitboardId = self.enforceStringTypeId(bitboardId)
        bitboard = self.bitboardManager[bitboardId]
        if not self.isInBound(i, j):
            return
        piecePosition = (i * bitboard.sizeJ) + j
        bitboard.data = bitboard.data | (1 << piecePosition)

    def deletePiece(self, bitboardId, i, j):
        bitboardId = self.enforceStringTypeId(bitboardId)
        bitboard = self.bitboardManager[bitboardId]
        if not self.isInBound(i, j):
            return
        piecePosition = (i * bitboard.sizeJ) + j
        bitboard.data = bitboard.data & ~(1 << piecePosition)

    # can be optimized using bit shifts
    def movePiece(self, bitboardId, fromI, fromJ, toI, toJ):
        if self.isPieceSet(bitboardId, fromI, fromJ):
            self.deletePiece(bitboardId, fromI, fromJ)
            self.setPiece(bitboardId, toI, toJ)

    def move(self, move):
        bitboardId, fromI, fromJ, toI, toJ = move
        self.movePieceOptimized(bitboardId, fromI, fromJ, toI, toJ)

    def movePieceOptimized(self, bitboardId, fromI, fromJ, toI, toJ):
        # bitboardId = self.enforceStringTypeId(bitboardId)
        if not self.isInBound(fromI, fromJ) or not self.isInBound(toI, toJ):
            return
        bitboard = self.bitboardManager[bitboardId]
        if self.isPieceSet(bitboardId, fromI, fromJ):
            fromPosition = (fromI * bitboard.sizeJ) + fromJ
            toPosition = (toI * bitboard.sizeJ) + toJ
            bitboard.data ^= ((1 << fromPosition) | (1 << toPosition))

    # capture a piece, requires destination to have enemy piece
    def moveWithCapture(self, bitboardId, fromI, fromJ, toI, toJ, opponentBitboardIdList):
        for opponentBitboardId, data in self.bitboardManager.items():
            if (
                    bitboardId != opponentBitboardId
                    and opponentBitboardId in opponentBitboardIdList
                    and self.isPieceSet(opponentBitboardId, toI, toJ)
            ):
                self.movePieceOptimized(bitboardId, fromI, fromJ, toI, toJ)
                self.deletePiece(opponentBitboardId, toI, toJ)

    # classical game, piece cannot capture same piece type
    def isLegalMove(self, fromI, fromJ, toI, toJ):
        if fromI == toI and fromJ == toJ:
            return False

        if not self.isInBound(fromI, fromJ) or not self.isInBound(toI, toJ):
            return False

        for bitboardId, bitboard in self.bitboardManager.items():

            # basically self.isPieceSet but without checks
            originPiecePosition = (fromI * bitboard.sizeJ) + fromJ
            destinationPiecePosition = (toI * bitboard.sizeJ) + toJ \
                # if origin is not set then false
            if ((bitboard.data >> originPiecePosition) & 1) == 0:
                return False

            # if origin and destination is same then move is not legal
            if ((bitboard.data >> originPiecePosition) & 1) == 1 and (
                    (bitboard.data >> destinationPiecePosition) & 1) == 1:
                return False

        return True

    # can be optimized by using mask and or operation
    def setAllBits(self, bitboardId):
        bitboardId = self.enforceStringTypeId(bitboardId)
        bitboard = self.bitboardManager[bitboardId]
        for i in range(bitboard.sizeI):
            for j in range(bitboard.sizeJ):
                self.setPiece(bitboardId, i, j)

    def setAllBitsAtRow(self, bitboardId, i):
        bitboardId = self.enforceStringTypeId(bitboardId)
        mask = 1
        # build mask
        for _ in range(self.sizeJ - 1):
            mask = (mask * 2) + 1
        mask <<= i * self.sizeJ
        self[bitboardId].data = self[bitboardId].data | mask

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

    def combineBitboard(self, idList):
        result = 0
        for bitboardId in idList:
            result |= self.bitboardManager[bitboardId]
        return result

    def enforceStringTypeId(self, bitboardId):
        if type(bitboardId) is not str:
            bitboardId = str(bitboardId)
        return bitboardId

    def isRowAnyPieceSet(self, bitboardId, i):
        mask = 1
        # build mask
        for _ in range(self.sizeJ - 1):
            mask = (mask * 2) + 1
        mask <<= i * self.sizeJ
        return self[bitboardId].data & mask >= 1

    # todo
    def isBitboardContainsSetBitAtColumn(self, j, bitboardId):
        pass

    # params: bitboardId (piece), fromI, fromJ, possibleMovements,
    # returns: list of moves (bitboardId, fromI, fromJ, toI, toJ)
    def generateMoveForAPiece(self, bitboardId, fromI, fromJ, movements):
        if not self.isPieceSet(bitboardId, fromI, fromJ):
            return []

        possibleMoves = []
        for offsets in movements:
            offsetI, offsetJ = offsets
            if self.isLegalMove(fromI, fromJ, fromI + offsetI, fromJ + offsetJ):
                possibleMoves.append((bitboardId, fromI, fromJ, fromI + offsetI, fromJ + offsetJ))
        return possibleMoves

    # pieceMovements is key value: bitboardId:[(offsetI, offsetJ]
    # pieceLocations is key value: bitboardId:[(i,j)]
    # returns: key value: bitboardId:[moves] (see generateMoveForAPiece)
    def generateAllPossibleMoves(self, bitboardId, pieceMovements, pieceLocations):
        allPossibleMoves = {}
        movementOffsets = pieceMovements[bitboardId]
        # fromI, fromJ = pieceLocations[bitboardId]

        for pieceLocation in pieceLocations[bitboardId]:
            fromI, fromJ = pieceLocation
            if bitboardId not in allPossibleMoves:
                allPossibleMoves[bitboardId] = self.generateMoveForAPiece(bitboardId, fromI, fromJ, movementOffsets)
            else:
                allPossibleMoves[bitboardId] += self.generateMoveForAPiece(bitboardId, fromI, fromJ, movementOffsets)
        return allPossibleMoves


def test():
    bm = BitboardManager()
    bm.buildBitboard('1', 4, 4)
    bm.setPiece('1', 2, 1)
    loop = 100000
    totalTimeBitboard = 0

    for _ in range(loop):
        start = time.time()
        # bm.movePieceOptimized('1', 2, 1, 3, 1)
        bm['1'].data ^= ((1 << ((2 * 4) + 1)) | (1 << ((3 * 4) + 1)))

        end = time.time()
        bm.movePieceOptimized('1', 3, 1, 2, 1)
        totalTimeBitboard += end - start

    board = [['0'] * 4 for _ in range(4)]
    board[2][1] = '1'
    totalTimeArray = 0
    # testing simplest/optimal case for array allocation
    # delete old place, and set new place
    for _ in range(loop):
        start = time.time()
        board[2][1] = '0'
        board[3][1] = '1'
        end = time.time()
        board[2][1] = '1'
        board[3][1] = '0'
        totalTimeArray += end - start

    print("total time with bitboard: ", totalTimeBitboard)
    print("total time with array: ", totalTimeArray)


if __name__ == '__main__':
    # bm = BitboardManager()
    # bm.buildBitboard('1', 4, 3)
    # bm.setPiece('1', 3, 1)
    # bm.showBitboard('1')
    # bluePawnMovements = {'1': [(-1, 0), (-1, 1), (-1, -1)]}
    # print(bm.generateAllPossibleMoves(bluePawnMovements, {'1': (3, 1)}))

    def movePieceOptimized(self, bitboardId, fromI, fromJ, toI, toJ):
        # bitboardId = self.enforceStringTypeId(bitboardId)
        if not self.isInBound(fromI, fromJ) or not self.isInBound(toI, toJ):
            return
        bitboard = self.bitboardManager[bitboardId]
        if self.isPieceSet(bitboardId, fromI, fromJ):
            fromPosition = (fromI * bitboard.sizeJ) + fromJ
            toPosition = (toI * bitboard.sizeJ) + toJ
            bitboard.data ^= ((1 << fromPosition) | (1 << toPosition))


    test()

# if __name__ == '__main__':
#     bm = BitboardManager()
#     bm.buildBitboard('a', 4, 5)
#     print(bm.bitboardManager['a'].data)
#     # bm.setAllBits('a')
#     bm.setPiece('a', 2, 2)
#     # bm.setNeighbors('a', 1,1)
#     # bm.deleteNeighbors('a',1,1)
#     # bm.movePiece('a', 2, 2, 0, 0)
#     bm.movePieceOptimized('a',2,2,0,0)
#     bm.showBitboard('a')
#
#     # board = [[0, 0, 0], [0, 0, 0], [1, 1, 1], [2, 2, 2]]
#     # bm.translateMailboxToBitboards(board)
#     # bm.showAllBitboard()
#     # print(bm.translateBitboardsToMailbox())

import time
from functools import lru_cache, reduce
import random
from typing import Union, Dict, List


class Bitboard:
    def __init__(self, data: int, sizeI, sizeJ):
        self.data = data
        self.sizeI = sizeI
        self.sizeJ = sizeJ

    def __str__(self):
        return str(self.data)


# start from top left to bottom right, i.e 1 = 1 at (0,0)
class BitboardManager:
    def __init__(self, sizeI=0, sizeJ=0, useZobrist=False, zobristSeed=None, infoDump=None):
        if infoDump is not None:
            self.loadInfo(infoDump)
            return

        self.bitboardManager = {}
        self.sizeI = sizeI
        self.sizeJ = sizeJ
        self.useZobrist = useZobrist
        if zobristSeed is None:
            self.zobristSeed = time.time()
        self.zobristSeed = zobristSeed
        self.zobristTable = None

    def dumpInfo(self):
        return (self.bitboardManager, self.sizeI, self.sizeJ, self.zobristSeed, self.zobristTable)

    def loadInfo(self, infoDump):
        self.bitboardManager, self.sizeI, self.sizeJ, self.zobristSeed, self.zobristTable = infoDump

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

    def buildBitboard(self, bitboardId, sizeI=None, sizeJ=None):
        if sizeI is None:
            sizeI = self.sizeI
        if sizeJ is None:
            sizeJ = self.sizeJ

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

    # Set piece at (i,j), which basically means set a bit at (i,j)
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

    def moveWithCapture(self, bitboardId, fromI, fromJ, toI, toJ, opponentBitboardIdList):
        for opponentBitboardId, data in self.bitboardManager.items():
            if (
                    bitboardId != opponentBitboardId
                    and opponentBitboardId in opponentBitboardIdList
            ):
                self.movePieceOptimized(bitboardId, fromI, fromJ, toI, toJ)
                if self.isPieceSet(opponentBitboardId, toI, toJ):
                    self.deletePiece(opponentBitboardId, toI, toJ)

    # capture a piece, only if destination to have enemy piece
    def moveAndCaptureOnlyIfPossible(self, bitboardId, fromI, fromJ, toI, toJ, opponentBitboardIdList):
        for opponentBitboardId, data in self.bitboardManager.items():
            if (
                    bitboardId != opponentBitboardId
                    and opponentBitboardId in opponentBitboardIdList
                    and self.isPieceSet(opponentBitboardId, toI, toJ)
            ):
                self.movePieceOptimized(bitboardId, fromI, fromJ, toI, toJ)
                self.deletePiece(opponentBitboardId, toI, toJ)

    # classical game, piece cannot capture same piece type
    def isLegalMove(self, fromI, fromJ, toI, toJ, originBitboardId, isCaptureOnly=False, targetBitboardId=None):
        """
        :param fromI: Index of the row from where piece is moved
        :param fromJ: Index of the column from where piece is moved
        :param toI: Index of the row to where piece is moved
        :param toJ: Index of the column to where piece is moved
        :param originBitboardId: bitboardId of the piece being moved
        :param isCaptureOnly: True if only the move result in a capture.\
         False if the move can be both a normal move or a capture. \
         Set to true if for example when dealing with a pawn in chess
        :param targetBitboardId: bitboardId of the piece being captured, only needed if isCaptureOnly is true
        :return: True if move is legal, False otherwise

        """
        if fromI == toI and fromJ == toJ:
            return False

        if not self.isInBound(fromI, fromJ) or not self.isInBound(toI, toJ):
            return False

        if isCaptureOnly:
            if targetBitboardId is None: raise ValueError("targetBitboardId cannot be None if isCaptureOnly is True")
            if not self.isPieceSet(targetBitboardId, toI, toJ):
                return False

        for bitboardId, bitboard in self.bitboardManager.items():

            # basically self.isPieceSet but without checks
            originPiecePosition = (fromI * bitboard.sizeJ) + fromJ
            destinationPiecePosition = (toI * bitboard.sizeJ) + toJ \
                # if origin is not set then false
            if ((bitboard.data >> originPiecePosition) & 1) == 0 and bitboardId == originBitboardId:
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

    def unsetAllBitsAtRow(self, bitboardId, i):
        bitboardId = self.enforceStringTypeId(bitboardId)
        mask = 1
        # Build mask with all bits set to 1
        for _ in range(self.sizeJ - 1):
            mask = (mask * 2) + 1

        # Shift the mask to the position of the specified row
        mask <<= i * self.sizeJ

        # Invert the mask to unset the bits in the specified row
        mask = ~mask

        # Perform bitwise AND operation to unset the bits
        self[bitboardId].data = self[bitboardId].data & mask

    def setAllBitsAtColumn(self, bitboardId, j):
        bitboardId = self.enforceStringTypeId(bitboardId)
        mask = 1
        # Build mask with only the bit in the specified column set to 1
        for _ in range(self.sizeI - 1):
            mask = (mask << self.sizeJ) | 1

        # Shift the mask to the position of the specified column
        mask <<= j

        # Perform bitwise OR operation to set the bits
        self[bitboardId].data = self[bitboardId].data | mask

    def unsetAllBitsAtColumn(self, bitboardId, j):
        bitboardId = self.enforceStringTypeId(bitboardId)
        mask = 1
        # Build mask with only the bit in the specified column set to 0
        for _ in range(self.sizeI - 1):
            mask = (mask << self.sizeJ) | 1

        # Invert the mask to unset the bits in the specified column
        mask = ~mask

        # Shift the mask to the position of the specified column
        mask <<= j

        # Perform bitwise AND operation to unset the bits
        self[bitboardId].data = self[bitboardId].data & mask

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

    def isAnyPieceSetAtRow(self, bitboardId, i):
        mask = 1
        # build mask
        for _ in range(self.sizeJ - 1):
            mask = (mask * 2) + 1
        mask <<= i * self.sizeJ
        return self[bitboardId].data & mask >= 1

    # Todo: test this, generated by GPT
    def isAllPieceSetAtRow(self, bitboardId: Union[str, int], i: int) -> bool:
        bitboardId = self.enforceStringTypeId(bitboardId)
        # Create a mask with self.sizeJ ones and shift it to row i
        mask = ((1 << self.sizeJ) - 1) << (i * self.sizeJ)
        return (self[bitboardId].data & mask) == mask

    # TodoL test this, generated by GPT
    def isAllPieceSetAtColumn(self, bitboardId, j):
        mask = 1
        # build mask
        for _ in range(self.sizeI - 1):
            mask = (mask << self.sizeJ) | 1
        mask <<= j
        return self[bitboardId].data & mask == mask

    # todo
    def isAnyPieceSetAtColumn(self, bitboardId, j):
        pass

    def flipMovements(self, movements):
        """
            Flips the movements (equivalent to rotating 180 degrees)

            :param movements: List of tuples representing the movements e.g [(0, 1), (1, 0)].
            :return: List of tuples representing the flipped movements.
        """
        return [(-i, -j) for i, j in movements]

    # params: bitboardId (piece), fromI, fromJ, possibleMovements,
    # returns: list of moves: each move is (bitboardId, fromI, fromJ, toI, toJ)
    # Assuming there is a piece present on (fromI, fromJ), else returns []
    def generateMoveForAPiece(self, bitboardId, fromI, fromJ, movements):
        if not self.isPieceSet(bitboardId, fromI, fromJ):
            print("Warning: No piece present at (%d, %d)" % (fromI, fromJ))
            return []

        possibleMoves = []
        for offsets in movements:
            offsetI, offsetJ = offsets
            if self.isLegalMove(fromI, fromJ, fromI + offsetI, fromJ + offsetJ, bitboardId):
                possibleMoves.append((bitboardId, fromI, fromJ, fromI + offsetI, fromJ + offsetJ))
        return possibleMoves

    # pieceMovements is key value: bitboardId:[(offsetI, offsetJ]
    # pieceLocations is key value: bitboardId:[(i,j)]
    # returns: key value: bitboardId:[moves] (see generateMoveForAPiece)
    def generateAllPossibleMoves(self, bitboardId, pieceMovements, pieceLocations):
        """
        Generate moves for a specific bitboard.

        Parameters:
          bitboardId: A string or number representing the bitboard
          pieceMovements: dict where keys are bitboard IDs and values are lists of (dx, dy) tuples.
          pieceLocations: dict where keys are bitboard IDs and values can be either a tuple (i, j) or a list of such tuples.

        Returns:
          A dictionary with the bitboardId as key and a list of moves as value.
          Each move is represented as a tuple: ((fromI, fromJ), (toI, toJ)).
        """
        # Ensure bitboardId is a string if needed.
        bitboardId = self.enforceStringTypeId(bitboardId)

        # Retrieve the movement offsets for the specified bitboard ID.
        if bitboardId not in pieceMovements:
            return {bitboardId: []}
        movements = pieceMovements[bitboardId]

        # Retrieve the piece location(s). Wrap as a list if necessary.
        if bitboardId not in pieceLocations:
            return {bitboardId: []}
        positions = pieceLocations[bitboardId]
        if not isinstance(positions, list):
            positions = [positions]

        movesForId = []
        for fromI, fromJ in positions:
            for dx, dy in movements:
                toI = fromI + dx
                toJ = fromJ + dy
                # Only add the move if destination is within bounds.
                if self.isInBound(toI, toJ):
                    movesForId.append(((fromI, fromJ), (toI, toJ)))

        return {bitboardId: movesForId}

    def getIndexOfSetBits(self, bits):
        return [i for i in range(bits.bit_length()) if bits & (1 << i)]

    def getCoordinatesOfPieces(self, bitboardId):
        """
        Get the coordinates of the pieces in the bitboard given id
        :param bitboardId: Id of the bitboard
        :return: List of coordinates of the pieces
        """
        bitboard_data = self.bitboardManager[bitboardId].data
        bitboardIdSetBitsIndex = self.getIndexOfSetBits(bitboard_data)

        return [self._index1dTo2d(index) for index in bitboardIdSetBitsIndex]

    def _index1dTo2d(self, index):
        row = index // self.sizeJ
        col = index % self.sizeJ
        if row > self.sizeI:
            raise Exception('index out of bounds')

        return row, col

    def _generateZobristTableForAPiece(self, bitboardId, seed, bitsize=64):
        zobristTableForAPiece = {}
        currentSeed = seed
        for i in range(self.sizeI):
            for j in range(self.sizeJ):
                zobristTableForAPiece[(bitboardId, i, j)] = random.Random(currentSeed).getrandbits(bitsize)
                random.seed(currentSeed)
                currentSeed = int(random.random() * (2 ** 32 - 1))

        return zobristTableForAPiece
        # return {
        #     (bitboardId, i, j): random.Random(seed).getrandbits(bitsize)
        #     for i in range(self.sizeI)
        #     for j in range(self.sizeJ)
        # }

    def _generateZobristTable(self):
        table = {}
        for bitboardId in self.bitboardManager.keys():
            table.update(self._generateZobristTableForAPiece(bitboardId, self.zobristSeed))
        return table

    # Guard function for zobrist_hash()
    def _zobristGuard(self, additional_data_to_hash=None):
        if self.useZobrist is False:
            raise Exception('Zobrist hashing is not enabled')

        if self.zobristTable is None:
            self.zobristTable = self._generateZobristTable()

        if additional_data_to_hash is None:
            return []
        else:
            return additional_data_to_hash

    # Compute zobrist hash for current board
    def zobrist_hash(self, additional_data_to_hash=None):
        additional_data_to_hash = self._zobristGuard(additional_data_to_hash)

        zobristTableEntry = []
        for bitboardId in self.bitboardManager.keys():
            bitboardIdSetBitsIndex = self.getIndexOfSetBits(self.bitboardManager[bitboardId].data)
            for index in bitboardIdSetBitsIndex:
                i, j = self._index1dTo2d(index)
                zobristTableEntry.append(self.zobristTable[(bitboardId, i, j)])

        zobristTableEntry.extend(additional_data_to_hash)

        # XOR everything in the list together
        return reduce(lambda x, y: x ^ y, zobristTableEntry) if zobristTableEntry else 0

    def __hash__(self) -> int:
        if not self.useZobrist:
            return super().__hash__()
        try:
            zhash = self.zobrist_hash()
        except Exception:
            return super().__hash__()
        if zhash == 0:
            return super().__hash__()
        return hash(zhash)


if __name__ == '__main__':
    pass
    # bm = BitboardManager()
    # bm.buildBitboard('1', 4, 3)
    # bm.setPiece('1', 3, 1)
    # bm.showBitboard('1')
    # bluePawnMovements = {'1': [(-1, 0), (-1, 1), (-1, -1)]}
    # print(bm.generateAllPossibleMoves(bluePawnMovements, {'1': (3, 1)}))

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

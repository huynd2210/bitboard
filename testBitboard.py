import time

import pytest

import PawnRevolt
from bitboard import BitboardManager
from timeit import timeit


def testIsPieceSetValid():
    bm = BitboardManager()
    bm.buildBitboard('a', 3, 3)
    bm.setPiece('a', 1, 1)
    assert bm.isPieceSet('a', 1, 1) is True


def testIsPieceSetInvalid():
    bm = BitboardManager()
    bm.buildBitboard('a', 3, 3)
    bm.setPiece('a', 1, 2)
    assert bm.isPieceSet('a', 1, 1) is False


def testDeletePiece():
    bm = BitboardManager()
    bm.buildBitboard('a', 3, 3)
    bm.setPiece('a', 1, 2)
    assert bm.isPieceSet('a', 1, 2) is True
    bm.deletePiece('a', 1, 2)
    assert bm.isPieceSet('a', 1, 2) is False


def testSetAllBitsAtRow():
    bm = BitboardManager()
    bm.buildBitboard('a', 4, 3)
    bm.setAllBitsAtRow('a', 0)
    assert bm['a'].data == 7


def testGetAllPossibleMoves():
    bm = BitboardManager()
    bm.buildBitboard('1', 4, 3)
    bm.setPiece('1', 3, 1)
    bluePawnMovements = {'1': [(-1, 0), (-1, 1), (-1, -1)]}
    assert len(bm.generateAllPossibleMoves(bluePawnMovements, {'1': (3, 1)})['1']) == 3


def runMovePieceStressTest():
    bm = BitboardManager()
    bm.buildBitboard('1', 4, 4)
    bm.setPiece('1', 3, 1)
    bm.movePiece('1', 3, 1, 2, 1)


def runMovePieceOptimizedStressTest():
    bm = BitboardManager()
    bm.buildBitboard('1', 4, 4)
    bm.setPiece('1', 3, 1)
    bm.movePieceOptimized('1', 3, 1, 2, 1)


def runMovePieceArrayStressTest(board):
    board = []


def testMovePieceAgainstOptimizedMovePiece():
    timeNormal = timeit(lambda: runMovePieceStressTest(), number=100000)
    timeOptimized = timeit(lambda: runMovePieceOptimizedStressTest(), number=100000)
    assert timeOptimized > timeNormal


# def testMovePieceAgainstArrayMovePiece():

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
    game = PawnRevolt.Game
    print(game.getAllPossibleMoves(True))

    # test()

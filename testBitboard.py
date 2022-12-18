import time

import pytest

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


if __name__ == '__main__':



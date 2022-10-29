import pytest

from bitboard import BitboardManager

def setup(sizeI, sizeJ):
    bm = BitboardManager()
    bm.buildBitboard('a', sizeI, sizeJ)
    return bm


def testIsPieceSetValid():
    bm = setup(3, 3)
    bm.setPiece('a', 1, 1)
    assert bm.isPieceSet('a', 1, 1) is True


def testIsPieceSetInvalid():
    bm = setup(3, 3)
    bm.setPiece('a', 1, 2)
    assert bm.isPieceSet('a', 1, 1) is False


def testDeletePiece():
    bm = setup(3, 3)
    bm.setPiece('a', 1, 2)
    assert bm.isPieceSet('a', 1, 2) is True
    bm.deletePiece('a', 1, 2)
    assert bm.isPieceSet('a', 1, 2) is False


def testSetAllBitsAtRow():
    bm = setup(4, 3)
    bm.setAllBitsAtRow('a', 0)
    assert bm['a'].data == 7


def testGetAllPossibleMoves(self):
    bm = setup(3, 3)
    bm.setPiece('1', 2, 1)
    bluePawnMovements = {'1': [(-1, 0), (-1, 1), (-1, -1)]}
    assert len(bm.generateAllPossibleMoves(bluePawnMovements, self.firstPlayerPieceCoord)) == 3


def testMovePieceAgainstOptimizedMovePiece():
    bm = setup(4,4)
    bm.setPiece('1', 2, 1)

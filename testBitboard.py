import pytest

from bitboard import BitboardManager


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
    bm.setPiece('a',1,2)
    assert bm.isPieceSet('a',1,2) is True
    bm.deletePiece('a',1,2)
    assert bm.isPieceSet('a',1,2) is False

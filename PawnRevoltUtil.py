from PawnRevolt import Game

def printBitboards(game: Game):
    game.bm.showAllBitboard()

def printListAsGrid(input):
    for i in input:
        print(i)

def printBoard(game: Game):
    printListAsGrid(game.bm.translateBitboardsToMailbox())
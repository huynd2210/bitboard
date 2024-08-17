class TranspositionTable:
    def __init__(self):
        self.table = {}

    def store(self, state_hash, value, depth, isEnd, parent_hash, isFirstPlayerTurn, nextBestMove):
        self.table[state_hash] = (value, depth, isEnd, parent_hash, isFirstPlayerTurn, nextBestMove)

    def retrieve(self, state_hash):
        if state_hash in self.table:
            return self.table[state_hash]
        else:
            return None

    def contains(self, state_hash):
        return state_hash in self.table

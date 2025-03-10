class TranspositionTable:
    def __init__(self, persitanceOption="shelve", name="table.db"):
        if persitanceOption == "shelve":
            import shelve
            self.table = shelve.open(name)
        elif persitanceOption == "memory":
            self.table = {}

    def store(self, state_hash, value, depth, isEnd, parent_hash, isFirstPlayerTurn, nextBestMove, *args):
        self.table[state_hash] = (value, depth, isEnd, parent_hash, isFirstPlayerTurn, nextBestMove, *args)

    def retrieve(self, state_hash):
        if state_hash in self.table:
            return self.table[state_hash]
        else:
            return None

    def contains(self, state_hash):
        return state_hash in self.table

from typing import List

from State import State
from TranspositionTable import TranspositionTable


def solve(root: State, queue=None, transpositionTable=None):
    if queue is None:
        queue = []

    if transpositionTable is None:
        transpositionTable = TranspositionTable()

    queue.append(root)

    while len(queue) > 0:
        root = queue.pop(0)
        if root.isEnd():
            continue
        isStateInTT = resolveTT(root, transpositionTable)
        if not isStateInTT:
            children = passInfoToChildren(root, root.getAllPossibleMoves())
            queue.extend(children)
    return None

"""
Check if the state is in the transposition table, if so, then store it and return False.
Otherwise, return True, boolean is returned for the purpose of extending the queue or not
"""
def resolveTT(state: State, transpositionTable: TranspositionTable) -> bool:
    if not transpositionTable.contains(state.hash()):
        transpositionTable.store(state.hash(), state.value(), state.depth, state.isEnd(), state.parent_hash, state.isFirstPlayerTurn(), None)
        return False
    else:
        return True

def passInfoToChildren(parentState: State, children: List[State]) -> List[State]:
    parent_hash = parentState.hash()  # Avoid computing hash multiple times
    parent_depth = parentState.depth  # Avoid accessing depth multiple times

    for child in children:
        child.parent_hash = parent_hash
        child.depth = parent_depth + 1

    return children  # Return the modified list if needed

from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self._nodeCount = self._parentCount = self._childCount = self._depthCount = self._count = 0

    def findMove(self, state):
        self._count += 1
        actions = self.prioritizedMoves(state)
        if not actions:
            return
        bestMove = actions[0]
        depth = 1

        while self.timeRemaining():
            self._depthCount += 1
            bestScore = float('-inf')

            for move in actions:
                nextState = state.move(move)
                if not self.timeRemaining():
                    return
                score = self.expectimax(nextState, depth - 1)
                if score is None:
                    return
                if score > bestScore:
                    bestScore = score
                    bestMove = move

            self.setMove(bestMove)
            depth += 1

    def maxPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver() or depth == 0:
            return self.evaluate(state)

        actions = self.prioritizedMoves(state)
        if not actions:
            return self.evaluate(state)

        self._parentCount += 1
        best = float('-inf')
        for move in actions:
            if not self.timeRemaining():
                return None
            result = state.move(move)
            value = self.expectimax(result, depth - 1)
            if value is None:
                return None
            best = max(best, value)
        return best

    def expectimax(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver() or depth == 0:
            return self.evaluate(state)

        self._parentCount += 1
        total = 0
        possibilities = state.possibleTiles()
        if not possibilities:
            return self.evaluate(state)

        for (position, value) in possibilities:
            if not self.timeRemaining():
                return None
            nextState = state.addTile(position, value)
            result = self.maxPlayer(nextState, depth - 1)
            if result is None:
                return None
            total += result

        return total / len(possibilities)

    def evaluate(self, state):
        grid = [[state.getTile(r, c) for c in range(4)] for r in range(4)]
        tiles = [tile for row in grid for tile in row]
        emptyCount = tiles.count(0)
        maxTile = max(tiles)

        weights = [
            [65536, 32768, 16384, 8192],
            [512, 1024, 2048, 4096],
            [256, 128, 64, 32],
            [1, 2, 4, 8]
        ]
        cornerScore = sum(grid[r][c] * weights[r][c] for r in range(4) for c in range(4))
        emptyBonus = emptyCount * 5000

        def is_monotonic(line):
            return all(x >= y for x, y in zip(line, line[1:])) or all(x <= y for x, y in zip(line, line[1:]))

        monoCount = sum(is_monotonic(row) for row in grid) + sum(is_monotonic(col) for col in zip(*grid))
        monotonicityReward = monoCount * 20000

        cornerBonus = 15000 if grid[0][0] == maxTile else 0

        return cornerScore + emptyBonus + monotonicityReward + cornerBonus

    def prioritizedMoves(self, state):
        preferredOrder = ['L', 'U', 'R', 'D']
        return [move for move in preferredOrder if move in state.actions()]

    def stats(self):
        avgDepth = self._depthCount / self._count
        branchingFactor = self._childCount / self._parentCount
        print(f'Average depth: {avgDepth:.2f}')
        print(f'Branching factor: {branchingFactor:.2f}')

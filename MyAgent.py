from Game2048 import *
import math
import random

class Player(BasePlayer):
    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self._nodeCount = self._parentCount = self._childCount = self._depthCount = self._count = 0
        self.bestMove = None

    def findMove(self, state):
        self._count += 1
        bestMove = None
        bestScore = float('-inf')
        depth = 2  # Controlled depth for time-performance balance

        while self.timeRemaining():
            currentBest = None
            currentScore = float('-inf')
            timedOut = False

            for action in self.getMoveOrder(state):
                nextState = state.move(action)
                if not self.timeRemaining():
                    timedOut = True
                    break
                score = self.expectimax(nextState, depth - 1)
                if score is None:
                    timedOut = True
                    break
                if score > currentScore:
                    currentScore = score
                    currentBest = action

            if not timedOut and currentBest:
                bestMove = currentBest
                bestScore = currentScore
                print(f"✓ Depth {depth} → Best Score: {bestScore} using {bestMove}")
                depth += 1
            else:
                break

        if bestMove is None:
            fallback = state.actions()
            bestMove = random.choice(fallback) if fallback else None
            print("✗ Fallback used:", bestMove)

        self.setMove(bestMove)
        self.bestMove = bestMove

    def maxPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver() or depth == 0:
            return self.evaluate(state)

        self._parentCount += 1
        bestValue = float('-inf')

        for move in self.getMoveOrder(state):
            if not self.timeRemaining():
                return None
            result = state.move(move)
            value = self.expectimax(result, depth - 1)
            if value is None:
                return None
            bestValue = max(bestValue, value)

        return bestValue

    def expectimax(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver() or depth == 0:
            return self.evaluate(state)

        self._parentCount += 1
        emptyIndices = [i for i, val in enumerate(state._board) if val == 0]
        if not emptyIndices:
            return self.evaluate(state)

        totalValue = 0
        for index in emptyIndices:
            for value, prob in [(1, 0.9), (2, 0.1)]:
                result = state.addTile(index, value)
                score = self.maxPlayer(result, depth - 1)
                if score is None:
                    return None
                totalValue += (prob / len(emptyIndices)) * score

        return totalValue

    def evaluate(self, state):
        board = state._board
        grid = [[board[4 * i + j] for j in range(4)] for i in range(4)]

        emptyCount = sum(1 for val in board if val == 0)
        maxTile = max(board)

        # Encourage max tile in corner
        cornerBonus = 10000 if maxTile in [grid[0][0], grid[0][3], grid[3][0], grid[3][3]] else 0

        # Empty space for flexibility
        emptyBonus = emptyCount * 6000

        # Penalize uneven tile differences
        smoothnessPenalty = -self.computeSmoothness(grid) * 3

        # Penalize disordered rows/columns
        disorderPenalty = -self.computeDisorder(grid) * 150

        # Prefer placing large tiles in top-left (position value)
        positionScore = self.computePositionalWeight(grid) * 4

        return (
            state.getScore() +
            emptyBonus +
            cornerBonus +
            smoothnessPenalty +
            disorderPenalty +
            positionScore
        )

    def computeSmoothness(self, grid):
        penalty = 0
        for i in range(4):
            for j in range(3):
                a, b = grid[i][j], grid[i][j + 1]
                if a and b:
                    penalty += abs(math.log2(a) - math.log2(b))
        for j in range(4):
            for i in range(3):
                a, b = grid[i][j], grid[i + 1][j]
                if a and b:
                    penalty += abs(math.log2(a) - math.log2(b))
        return penalty

    def computeDisorder(self, grid):
        total = 0
        for row in grid:
            total += sum(abs(row[i] - row[i + 1]) for i in range(3))
        for col in zip(*grid):
            total += sum(abs(col[i] - col[i + 1]) for i in range(3))
        return total

    def computePositionalWeight(self, grid):
        weights = [
            [16, 15, 14, 13],
            [5, 6, 7, 8],
            [4, 3, 2, 1],
            [0, 0, 0, 0]
        ]
        return sum(grid[i][j] * weights[i][j] for i in range(4) for j in range(4))

    def getMoveOrder(self, state):
        board = state._board
        maxTile = max(board)
        maxIndex = board.index(maxTile)
        priority = ['U', 'L', 'D', 'R'] if maxIndex in [0, 3, 12, 15] else ['L', 'U', 'R', 'D']
        return [m for m in priority if m in state.actions()]

    def stats(self):
        print(f"Average depth: {self._depthCount / self._count:.2f}")
        print(f"Branching factor: {self._childCount / self._parentCount:.2f}")

    def getMove(self):
        return getattr(self, 'bestMove', None)

from Game2048 import *
import math

class Player(BasePlayer):
    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self.node_count = self.parent_count = self.child_count = self.depth_count = self.move_count = 0

    def findMove(self, state):
        self.move_count += 1
        possible_moves = self.getPreferredMoves(state)
        if not possible_moves:
            return

        best_move = possible_moves[0]
        depth = 1

        while self.timeRemaining():
            self.depth_count += 1
            self.node_count += 1
            self.parent_count += 1

            best_score = float('-inf')
            candidate_move = best_move

            for move in possible_moves:
                next_state = state.move(move)
                if not self.timeRemaining():
                    return

                score = self.expectiPlayer(next_state, depth - 1)
                if score is None:
                    return

                if score > best_score:
                    best_score = score
                    candidate_move = move

            self.setMove(candidate_move)
            best_move = candidate_move
            depth += 1

    def maxPlayer(self, state, depth):
        self.node_count += 1
        self.child_count += 1

        if state.gameOver() or depth == 0:
            return self.evaluate(state)

        self.parent_count += 1
        best_score = float('-inf')

        for move in self.getPreferredMoves(state):
            if not self.timeRemaining():
                return None
            result_state = state.move(move)
            score = self.expectiPlayer(result_state, depth - 1)
            if score is None:
                return None
            best_score = max(best_score, score)

        return best_score

    def expectiPlayer(self, state, depth):
        self.node_count += 1
        self.child_count += 1

        if state.gameOver() or depth == 0:
            return self.evaluate(state)

        self.parent_count += 1
        outcomes = state.possibleTiles()
        if not outcomes:
            return self.evaluate(state)

        total_score = 0
        for pos, val in outcomes:
            if not self.timeRemaining():
                return None
            next_state = state.addTile(pos, val)
            score = self.maxPlayer(next_state, depth - 1)
            if score is None:
                return None
            total_score += score

        return total_score / len(outcomes)

    def evaluate(self, state):
        grid = [[state.getTile(r, c) for c in range(4)] for r in range(4)]
        tiles = [tile for row in grid for tile in row]
        empty_cells = tiles.count(0)
        max_tile = max(tiles)

        
        corner_weights = [
            [65536, 32768, 16384, 8192],
            [512, 1024, 2048, 4096],
            [256, 128, 64, 32],
            [1, 2, 4, 8]
        ]
        corner_score = sum(grid[r][c] * corner_weights[r][c] for r in range(4) for c in range(4))

       
        empty_score = empty_cells * 5000

        
        monotonic_score = 0
        for row in grid:
            monotonic_score += self.isMonotonic(row)
        for col in zip(*grid):
            monotonic_score += self.isMonotonic(col)
        monotonic_score *= 20000

        
        corner_bonus = 10000 if max_tile in [grid[0][0], grid[0][3], grid[3][0], grid[3][3]] else 0

        return corner_score + empty_score + monotonic_score + corner_bonus

    def isMonotonic(self, line):
        return all(x >= y for x, y in zip(line, line[1:])) or all(x <= y for x, y in zip(line, line[1:]))

    def getPreferredMoves(self, state):
        preferred_order = ['U', 'L', 'R', 'D']
        return [move for move in preferred_order if move in state.actions()]

    def stats(self):
        avg_depth = self.depth_count / self.move_count if self.move_count else 0
        avg_branching = self.child_count / self.parent_count if self.parent_count else 0
        print(f"Average depth: {avg_depth:.2f}")
        print(f"Branching factor: {avg_branching:.2f}")

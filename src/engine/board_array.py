class BoardArray:
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def __init__(self):
        self.board = [[0] * 8 for _ in range(8)]
        self._start_position()

    def _start_position(self):
        self.board[3][3], self.board[4][4] = 1, 1  # white pieces
        self.board[3][4], self.board[4][3] = 2, 2  # black pieces

    def _on_board(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def legal_moves(self, color):
        """
        Returns the list of legal moves for a given color
        """
        opp = 3 - color
        moves = []

        for row in range(8):
            for col in range(8):
                if self.board[row][col] != 0:
                    continue
                # checks for each dir an opp..color sequence
                for dr, dc in self.DIRECTIONS:
                    r, c = row + dr, col + dc
                    opp_found = False
                    while self._on_board(r, c) and self.board[r][c] == opp:
                        opp_found = True
                        r += dr
                        c += dc
                    if opp_found and self._on_board(r, c) and self.board[r][c] == color:
                        moves.append((row, col))
                        break
        return moves

    def apply_move(self, move, color):
        """
        Play a move (r,c) for a given color and returns all flipped pieces pos
        """
        if move not in self.legal_moves(color):
            raise ValueError(f"Illegal move : {move} for color {color}")

        flips = []
        row, col = move
        opp = 3 - color
        self.board[row][col] = color

        for dr, dc in self.DIRECTIONS:
            r, c = row + dr, col + dc
            line = []

            while self._on_board(r, c) and self.board[r][c] == opp:
                line.append((r, c))
                r += dr
                c += dc

            if line and self._on_board(r, c) and self.board[r][c] == color:
                for r, c in line:
                    self.board[r][c] = color
                flips.extend(line)

        return flips


if __name__ == "__main__":
    b = BoardArray()
    for row in b.board:
        print(row)
    print(b.legal_moves(1))
    print(b.legal_moves(2))
    flips = b.apply_move((2, 3), 2)
    print(flips, b.board[3][3])
    for row in b.board:
        print(row)

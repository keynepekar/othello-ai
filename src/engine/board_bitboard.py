# Masks
EMPTY = 0x0000000000000000
FULL = 0xFFFFFFFFFFFFFFFF
LEFT = 0x0101010101010101  # leftmost column -> bits 0,8,16,...,56
RIGHT = 0x8080808080808080  # rightmost column -> bits 7...63

# Shifts
shift_n = lambda b: (b >> 8) & FULL
shift_s = lambda b: (b << 8) & FULL
shift_e = lambda b: ((b & ~RIGHT) << 1) & FULL
shift_w = lambda b: ((b & ~LEFT) >> 1) & FULL
shift_ne = lambda b: shift_n(shift_e(b))
shift_nw = lambda b: shift_n(shift_w(b))
shift_se = lambda b: shift_s(shift_e(b))
shift_sw = lambda b: shift_s(shift_w(b))

DIRECTIONS = [
    shift_n,
    shift_s,
    shift_e,
    shift_w,
    shift_ne,
    shift_nw,
    shift_se,
    shift_sw,
]


class BoardBitboard:
    def __init__(self):
        self.white = 0
        self.black = 0
        self._start_position()

    def _start_position(self):
        self.white |= 1 << (3 * 8 + 3)
        self.white |= 1 << (4 * 8 + 4)
        self.black |= 1 << (3 * 8 + 4)
        self.black |= 1 << (4 * 8 + 3)

    def _player_bb(self, color: int) -> int:
        return self.white if color == 1 else self.black

    def _opponent_bb(self, color: int) -> int:
        return self.black if color == 1 else self.white

    def legal_moves(self, color: int) -> list[tuple[int, int]]:
        """
        Returns the list of legal moves for a given color
        Inspired by the Line Cap Moves algorithm by Cameron Browne, "Bitboard Methods for Games", ICGA Journal, June 2014.
        """
        P = self._player_bb(color)
        O = self._opponent_bb(color)
        empty = ~(P | O) & FULL
        moves_bb = 0

        for d in DIRECTIONS:
            candidates = O & d(P)
            while candidates:
                moves_bb |= empty & d(candidates)
                candidates = O & d(candidates)

        # convert bb to list of moves (r,c) extracting each lsb
        moves = []
        while moves_bb:
            lsb = moves_bb & -moves_bb
            idx = lsb.bit_length() - 1
            moves.append(divmod(idx, 8))
            moves_bb &= moves_bb - 1

        return moves

    def apply_move(self, move: tuple[int, int], color: int) -> list[tuple[int, int]]:
        """
        Play a move (r,c) for a given color and returns all flipped pieces pos
        """
        r, c = move
        P = self._player_bb(color)
        O = self._opponent_bb(color)
        flips_bb = 0
        bit = 1 << (r * 8 + c)

        for d in DIRECTIONS:
            candidate = d(bit)
            mask = 0
            # stack successive opponents
            while candidate & O:
                mask |= candidate
                candidate = d(candidate)
            # valid if the line finish on the player color
            if candidate & P:
                flips_bb |= mask

        # update bitboards
        if color == 1:
            self.white |= bit | flips_bb
            self.black &= ~flips_bb
        else:
            self.black |= bit | flips_bb
            self.white &= ~flips_bb

        # convert bb to list of flips (r,c) extracting each lsb
        flips = []
        while flips_bb:
            lsb = flips_bb & -flips_bb
            idx = lsb.bit_length() - 1
            flips.append(divmod(idx, 8))
            flips_bb &= flips_bb - 1

        return flips


if __name__ == "__main__":
    print(bin(LEFT))
    print(bin(RIGHT))
    print(bin(FULL))

    b = BoardBitboard()
    print(b.legal_moves(1))
    print(b.legal_moves(2))
    print(b.apply_move((2, 3), 2))
    print(bin(b.white))
    print(bin(b.black))

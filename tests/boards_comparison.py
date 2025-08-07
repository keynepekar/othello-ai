import time
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.board_array import BoardArray
from src.engine.board_bitboard import BoardBitboard

ba = BoardArray()
bb = BoardBitboard()

nb_moves = 20

for i in range(nb_moves):
    color = 2 if i % 2 == 0 else 1
    moves_a = set(ba.legal_moves(color))
    moves_b = set(bb.legal_moves(color))
    print(moves_a)
    print(moves_b)
    assert moves_a == moves_b

    if not moves_a:
        break

    move = random.choice(list(moves_a))
    flips_a = set(ba.apply_move(move, color))
    flips_b = set(bb.apply_move(move, color))
    assert flips_a == flips_b

for row in ba.board:
    print(row)

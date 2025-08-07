import time
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.board_array import BoardArray
from src.engine.board_bitboard import BoardBitboard

nb_moves = 64
iters = 5000

t0 = time.perf_counter()
for i in range(iters):
    ba = BoardArray()
    for i in range(nb_moves):
        color = 2 if i % 2 == 0 else 1
        moves = ba.legal_moves(color)
        if not moves:
            break
        move = random.choice(moves)
        ba.apply_move(move, color)
t1 = time.perf_counter()

print(f"BoardArray: {t1-t0:.4f}s for {iters} iterations")

t0 = time.perf_counter()
for i in range(iters):
    bb = BoardBitboard()
    for i in range(nb_moves):
        color = 2 if i % 2 == 0 else 1
        moves = bb.legal_moves(color)
        if not moves:
            break
        move = random.choice(moves)
        bb.apply_move(move, color)
t1 = time.perf_counter()

print(f"BoardBitboard: {t1-t0:.4f}s for {iters} iterations")


# ------ debug
"""
ba = BoardArray()
bb = BoardBitboard()

for i in range(nb_moves):
    color = 2 if i % 2 == 0 else 1
    moves_a = set(ba.legal_moves(color))
    moves_b = set(bb.legal_moves(color))
    # print(moves_a)
    # print(moves_b)
    assert moves_a == moves_b

    if not moves_a:
        break

    move = random.choice(list(moves_a))
    flips_a = set(ba.apply_move(move, color))
    flips_b = set(bb.apply_move(move, color))
    assert flips_a == flips_b

for row in ba.board:
    print(row)
"""

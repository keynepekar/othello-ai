from src.engine.board_bitboard import FULL, DIRECTIONS

# cf Thomas Eberhart video
STABILITY = [
    [20, -10, 4, 3, 3, 4, -10, 20],
    [-10, -20, -2, -2, -2, -2, -20, -10],
    [4, -2, 0, 0, 0, 0, -2, 4],
    [3, -2, 0, 1, 1, 0, -2, 3],
    [3, -2, 0, 1, 1, 0, -2, 3],
    [4, -2, 0, 0, 0, 0, -2, 4],
    [-10, -20, -2, -2, -2, -2, -20, -10],
    [20, -10, 4, 3, 3, 4, -10, 20],
]


def _popcount(x: int) -> int:
    return x.bit_count()


def _positional(board, color: int) -> int:
    w, b = board.white, board.black
    score = 0
    for idx in range(64):
        bit = 1 << idx
        if not ((w | b) & bit):
            continue
        r, c = divmod(idx, 8)
        v = STABILITY[r][c]
        if (color == 1 and (w & bit)) or (color == 2 and (b & bit)):
            score += v
        else:
            score -= v
    return score


def _disc_diff(board, color: int) -> float:
    player = _popcount(board.white if color == 1 else board.black)
    opp = _popcount(board.black if color == 1 else board.white)
    tot = player + opp
    if tot == 0:
        return 0.0
    return 100.0 * (player - opp) / tot


def _mobility(board, color: int) -> float:
    player = len(board.legal_moves(color))
    opp = len(board.legal_moves(3 - color))
    tot = player + opp
    if tot == 0:
        return 0.0
    return 100.0 * (player - opp) / tot


def _frontier(board, color: int) -> float:
    """
    Penalizes adjacent discs to at least 1 empty cell
    """
    empty = ~(board.white | board.black) & FULL
    neighbors = 0
    for d in DIRECTIONS:
        neighbors |= d(empty)
    player = _popcount((board.white if color == 1 else board.black) & neighbors)
    opp = _popcount((board.black if color == 1 else board.white) & neighbors)
    tot = player + opp
    if tot == 0:
        return 0.0
    return -100.0 * (player - opp) / tot


def evaluate(board, color: int, mode: str = "mixed", weights=None) -> float:
    """
    Evaluates current board position for a given color and strategy :
    - absolute : score based on the disc nb difference
    - positional : based on static positional weights of the board
    - mobility : prioritizing available moves and reducing opp's mobility
    - mixed : dynamic strategy depending on the game state
    """
    empties = 64 - _popcount(board.white | board.black)

    if weights is None:
        if mode == "absolute":
            weights = {"disc": 1.0, "pos": 0.0, "mob": 0.0, "front": 0.0}
        elif mode == "positional":
            weights = {"disc": 0.2, "pos": 1.0, "mob": 0.0, "front": 0.0}
        elif mode == "mobility":
            weights = {"disc": 0.2, "pos": 0.3, "mob": 1.0, "front": 0.3}
        else:  # mixed
            if empties > 40:
                weights = {"disc": 0.2, "pos": 1.0, "mob": 0.0, "front": 0.0}
            elif empties > 12:
                weights = {"disc": 0.2, "pos": 0.3, "mob": 1.0, "front": 0.3}
            else:
                weights = {"disc": 1.0, "pos": 0.0, "mob": 0.0, "front": 0.0}

    return (
        weights["disc"] * _disc_diff(board, color)
        + weights["pos"] * _positional(board, color)
        + weights["mob"] * _mobility(board, color)
        + weights["front"] * _frontier(board, color)
    )

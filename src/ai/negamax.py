import math, time
from dataclasses import dataclass
from src.engine.board_bitboard import BoardBitboard
from src.ai.heuristics import evaluate


@dataclass
class SearchInfo:
    nodes: int = 0
    ms: int = 0
    score: float = 0.0
    depth: int = 0
    algo: str = ""


def _clone_and_play(
    board: BoardBitboard, move: tuple[int, int], color: int
) -> BoardBitboard:
    """
    Clone board & apply move
    """
    nb = BoardBitboard.__new__(BoardBitboard)
    nb.white, nb.black = board.white, board.black
    nb.apply_move(move, color)
    return nb


def _negamax(
    board: BoardBitboard,
    color: int,
    root_color: int,
    depth: int,
    alpha: float,
    beta: float,
    info: SearchInfo,
    do_ab: bool,
) -> float:
    legal = board.legal_moves(color)

    # end game
    if depth == 0 or (not legal and not board.legal_moves(3 - color)):
        return evaluate(board, root_color)

    # pass move
    if not legal:
        return -_negamax(
            board, 3 - color, root_color, depth, -beta, -alpha, info, do_ab
        )

    value = -math.inf
    for move in legal:
        child = _clone_and_play(board, move, color)
        info.nodes += 1
        score = -_negamax(
            child, 3 - color, root_color, depth - 1, -beta, -alpha, info, do_ab
        )
        if score > value:
            value = score
        if do_ab:
            if value > alpha:
                alpha = value
            if alpha >= beta:
                break
    return value


def choose_move_negamax(
    board: BoardBitboard,
    color: int,
    depth: int = 4,
    use_ab: bool = True,
) -> tuple[tuple[int, int] | None, SearchInfo]:

    t0 = time.perf_counter()
    info = SearchInfo(depth=depth, algo=f"negamax{'-ab' if use_ab else ''}")

    legal = board.legal_moves(color)
    if not legal:
        info.ms = int((time.perf_counter() - t0) * 1000)
        return None, info

    best, best_score = None, -math.inf
    alpha, beta = -math.inf, math.inf

    for move in legal:
        child = _clone_and_play(board, move, color)
        info.nodes += 1
        score = -_negamax(
            child, 3 - color, color, depth - 1, -beta, -alpha, info, use_ab
        )
        if score > best_score:
            best_score, best = score, move
        if use_ab and score > alpha:
            alpha = score

    info.ms = int((time.perf_counter() - t0) * 1000)
    info.score = best_score
    return best, info

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


def _minimax(
    board: BoardBitboard,
    color: int,
    root_color: int,
    depth: int,
    maximizing: bool,
    use_ab: bool,
    alpha: float,
    beta: float,
    info: SearchInfo,
) -> tuple[float, tuple[int, int]]:
    legal = board.legal_moves(color)
    # end game
    if depth == 0 or (not legal and not board.legal_moves(3 - color)):
        sc = evaluate(board, root_color)
        return sc, None

    # pass move
    if not legal:
        return _minimax(
            board,
            3 - color,
            root_color,
            depth,
            not maximizing,
            use_ab,
            alpha,
            beta,
            info,
        )

    best_move = None
    if maximizing:
        value = -math.inf
        for move in legal:
            child = _clone_and_play(board, move, color)
            info.nodes += 1
            score, _ = _minimax(
                child,
                3 - color,
                root_color,
                depth - 1,
                False,
                use_ab,
                alpha,
                beta,
                info,
            )
            if score > value:
                value = score
                best_move = move
            if use_ab:
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        return value, best_move
    else:
        value = +math.inf
        for move in legal:
            child = _clone_and_play(board, move, color)
            info.nodes += 1
            score, _ = _minimax(
                child,
                3 - color,
                root_color,
                depth - 1,
                True,
                use_ab,
                alpha,
                beta,
                info,
            )
            if score < value:
                value = score
                best_move = move
            if use_ab:
                beta = min(beta, value)
                if alpha >= beta:
                    break
        return value, best_move


def choose_move_minimax(
    board: BoardBitboard,
    color: int,
    depth: int = 4,
    use_ab: bool = False,
) -> tuple[tuple[int, int] | None, SearchInfo]:
    t0 = time.perf_counter()
    info = SearchInfo(depth=depth, algo=f"minimax{'-ab' if use_ab else ''}")
    score, best = _minimax(
        board, color, color, depth, True, use_ab, -math.inf, +math.inf, info
    )
    info.ms = int((time.perf_counter() - t0) * 1000)
    info.score = score
    return best, info

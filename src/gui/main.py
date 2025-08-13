import pygame, sys
from src.engine.board_bitboard import BoardBitboard
from src.ai.minimax import choose_move_minimax
from src.ai.negamax import choose_move_negamax

# -- GUI SETTINGS
CELL_SIZE = 60
BOARD_ORIGIN = (20, 80)
BOARD_SIZE = CELL_SIZE * 8
TOP_PANEL_HEIGHT = 60
RIGHT_PANEL_WIDTH = 450

SCREEN_WIDTH = BOARD_ORIGIN[0] + BOARD_SIZE + RIGHT_PANEL_WIDTH + 20
SCREEN_HEIGHT = TOP_PANEL_HEIGHT + BOARD_SIZE + 20

GREEN = (0, 144, 103)
BLACK = (19, 26, 24)
WHITE = (244, 253, 250)
HIGHLIGHT = (65, 71, 69)
BG = (34, 34, 34)
PANEL_BG = (48, 48, 48)
FONT_COLOR = (220, 220, 220)

# -- AI SETTINGS
PLAYER_TYPES = ["human", "minimax", "negamax"]
SEARCH_DEPTH = 4
AB = True

pygame.init()
pygame.display.set_caption("Othello AI")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

REPLAY_RECT = pygame.Rect(
    BOARD_ORIGIN[0] + BOARD_SIZE + RIGHT_PANEL_WIDTH - 120, 12, 100, 32
)


def draw_top_panel(board: BoardBitboard, turn_color: int, game_over: bool):
    # bg
    pygame.draw.rect(screen, BG, (0, 0, SCREEN_WIDTH, TOP_PANEL_HEIGHT))
    pygame.draw.rect(
        screen,
        PANEL_BG,
        (20, 10, BOARD_SIZE, TOP_PANEL_HEIGHT * 0.7),
        border_radius=15,
    )
    # score
    white_count = board.white.bit_count()
    black_count = board.black.bit_count()
    txt = font.render(f"Black: {black_count}", True, FONT_COLOR)
    screen.blit(txt, (50, 25))
    txt = font.render(f"White: {white_count}", True, FONT_COLOR)
    screen.blit(txt, (200, 25))
    # player turn
    center = (400, TOP_PANEL_HEIGHT // 2 + 1)
    color = BLACK if turn_color == 2 else WHITE
    pygame.draw.circle(screen, color, center, 15)
    pygame.draw.circle(screen, FONT_COLOR, center, 15, 2)
    # replay
    if game_over:
        pygame.draw.rect(screen, (80, 80, 80), REPLAY_RECT, border_radius=8)
        pygame.draw.rect(screen, (120, 120, 120), REPLAY_RECT, 2, border_radius=8)
        screen.blit(
            font.render("Replay", True, FONT_COLOR),
            (REPLAY_RECT.x + 20, REPLAY_RECT.y + 7),
        )


def draw_board(board: BoardBitboard, legal_moves):
    # cells
    for r in range(8):
        for c in range(8):
            x = BOARD_ORIGIN[0] + c * CELL_SIZE
            y = TOP_PANEL_HEIGHT + r * CELL_SIZE
            pygame.draw.rect(screen, GREEN, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)
    # discs
    for r in range(8):
        for c in range(8):
            bit = 1 << (r * 8 + c)
            if board.white & bit:
                col = WHITE
            elif board.black & bit:
                col = BLACK
            else:
                continue
            cx = BOARD_ORIGIN[0] + c * CELL_SIZE + CELL_SIZE // 2
            cy = TOP_PANEL_HEIGHT + r * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(screen, col, (cx, cy), CELL_SIZE // 2 - 4)
    # legam moves
    for r, c in legal_moves:
        x = BOARD_ORIGIN[0] + c * CELL_SIZE + CELL_SIZE // 2
        y = TOP_PANEL_HEIGHT + r * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, HIGHLIGHT, (x, y), CELL_SIZE // 2 - 4, 2)


def draw_side_panel(logs, settings):
    x0 = BOARD_ORIGIN[0] + BOARD_SIZE + 10
    y0 = TOP_PANEL_HEIGHT
    w = RIGHT_PANEL_WIDTH
    h = BOARD_SIZE
    pygame.draw.rect(screen, BG, (x0, y0, w, h))
    pygame.draw.rect(
        screen,
        PANEL_BG,
        (x0, y0, w, h),
        border_radius=15,
    )
    # player types & depth
    d_txt = (
        settings["depth_buffer"] if settings["depth_edit"] else str(settings["depth"])
    )
    if settings["depth_edit"] and (pygame.time.get_ticks() // 500) % 2 == 0:
        d_txt += "_"

    labels = [
        f"Black: {settings['black_type']}",
        f"White: {settings['white_type']}",
        f"Depth : {d_txt}",
    ]
    settings["_rects"] = []
    for i, txt in enumerate(labels):
        r = pygame.Rect(x0 + 10, y0 + 10 + i * 30, 430, 24)
        pygame.draw.rect(screen, (70, 70, 70), r, border_radius=6)
        screen.blit(font.render(txt, True, FONT_COLOR), (r.x + 6, r.y + 4))
        settings["_rects"].append(r)
    # logs
    for i, line in enumerate(logs[-15:]):
        txt = font.render(line, True, FONT_COLOR)
        screen.blit(txt, (x0 + 5, y0 + 120 + i * 20))


def handle_side_click(settings, pos):
    if not settings.get("_rects"):
        return
    r_black, r_white, r_depth = settings["_rects"]
    if r_black.collidepoint(pos):
        i = PLAYER_TYPES.index(settings["black_type"])
        settings["black_type"] = PLAYER_TYPES[(i + 1) % len(PLAYER_TYPES)]
    elif r_white.collidepoint(pos):
        i = PLAYER_TYPES.index(settings["white_type"])
        settings["white_type"] = PLAYER_TYPES[(i + 1) % len(PLAYER_TYPES)]
    elif r_depth.collidepoint(pos):
        settings["depth_edit"] = True
        settings["depth_buffer"] = ""


def ai_turn(board, turn, settings):
    ptype = settings["black_type"] if turn == 2 else settings["white_type"]
    if ptype == "human":
        return False
    depth = settings["depth"]
    if ptype == "minimax":
        move, info = choose_move_minimax(board, turn, depth=depth, use_ab=AB)
    elif ptype == "negamax":
        move, info = choose_move_negamax(board, turn, depth=depth, use_ab=AB)
    else:
        return False
    if move is not None:
        flips = board.apply_move(move, turn)
        return True, move, flips, info
    return False


def game_is_over(board: BoardBitboard) -> bool:
    return not board.legal_moves(1) and not board.legal_moves(2)


def reset_game():
    return (
        BoardBitboard(),
        2,
        ["Game started"],
        False,
        False,
    )


def main():
    board = BoardBitboard()
    turn = 2
    logs = ["Game started"]
    settings = {
        "black_type": "human",
        "white_type": "human",
        "depth": SEARCH_DEPTH,
        "depth_edit": False,
        "depth_buffer": "",
    }
    game_over = False
    game_over_logged = False

    running = True
    while running:
        legal = board.legal_moves(turn)

        # game ended
        if game_is_over(board):
            game_over = True
            if not game_over_logged:
                w, b = board.white.bit_count(), board.black.bit_count()
                if b > w:
                    logs.append(f"B won : {b} vs {w}")
                elif w > b:
                    logs.append(f"W won : {w} vs {b}")
                else:
                    logs.append(f"Draw : {b} vs {w}")
                game_over_logged = True

        # ai turn
        ai_done = False
        ptype = settings["black_type"] if turn == 2 else settings["white_type"]
        if ptype != "human":
            res = ai_turn(board, turn, settings)
            if res:
                ai_done, move, flips, info = res
                logs.append(
                    f"{'B' if turn==2 else 'W'} : {info.algo} d={info.depth} "
                    f"{move} +{len(flips)} | nodes={info.nodes} t={info.ms}ms s={info.score:.1f}"
                )
                turn = 3 - turn
                if not board.legal_moves(turn):
                    turn = 3 - turn

        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False

            elif evt.type == pygame.MOUSEBUTTONDOWN and evt.button == 1:
                mx, my = evt.pos

                if game_over and REPLAY_RECT.collidepoint(mx, my):
                    board, turn, logs, game_over, game_over_logged = reset_game()
                    continue

                if mx > BOARD_ORIGIN[0] + BOARD_SIZE:
                    handle_side_click(settings, (mx, my))
                else:
                    ox, oy = BOARD_ORIGIN
                    if (
                        ox < mx < ox + BOARD_SIZE
                        and TOP_PANEL_HEIGHT < my < TOP_PANEL_HEIGHT + BOARD_SIZE
                    ):
                        c = (mx - ox) // CELL_SIZE
                        r = (my - TOP_PANEL_HEIGHT) // CELL_SIZE
                        if (r, c) in legal:
                            flips = board.apply_move((r, c), turn)
                            logs.append(
                                f"{'B' if turn==2 else 'W'} : {(r,c)} = +{len(flips)}"
                            )
                            turn = 3 - turn
                            if not board.legal_moves(turn):
                                turn = 3 - turn
            elif evt.type == pygame.KEYDOWN:
                if settings["depth_edit"]:
                    if evt.key == pygame.K_RETURN:
                        if settings["depth_buffer"]:
                            try:
                                d = int(settings["depth_buffer"])
                                settings["depth"] = max(1, min(20, d))
                            except ValueError:
                                pass
                        settings["depth_edit"] = False
                        settings["depth_buffer"] = ""
                    elif evt.key == pygame.K_ESCAPE:
                        settings["depth_edit"] = False
                        settings["depth_buffer"] = ""
                    elif evt.key == pygame.K_BACKSPACE:
                        settings["depth_buffer"] = settings["depth_buffer"][:-1]
                    else:
                        if evt.unicode.isdigit() and len(settings["depth_buffer"]) < 2:
                            settings["depth_buffer"] += evt.unicode
                else:
                    if evt.key == pygame.K_UP:
                        settings["depth"] = min(20, settings["depth"] + 1)
                    elif evt.key == pygame.K_DOWN:
                        settings["depth"] = max(1, settings["depth"] - 1)

        screen.fill(BG)
        draw_top_panel(board, turn, game_over)
        draw_board(board, legal)
        draw_side_panel(logs, settings)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

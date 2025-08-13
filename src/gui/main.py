import pygame, sys
from src.engine.board_bitboard import BoardBitboard

# -- SETTINGS
CELL_SIZE = 60
BOARD_ORIGIN = (20, 80)
BOARD_SIZE = CELL_SIZE * 8
TOP_PANEL_HEIGHT = 60
RIGHT_PANEL_WIDTH = 200

SCREEN_WIDTH = BOARD_ORIGIN[0] + BOARD_SIZE + RIGHT_PANEL_WIDTH + 20
SCREEN_HEIGHT = TOP_PANEL_HEIGHT + BOARD_SIZE + 20

GREEN = (0, 144, 103)
BLACK = (19, 26, 24)
WHITE = (244, 253, 250)
HIGHLIGHT = (65, 71, 69)
BG = (34, 34, 34)
PANEL_BG = (48, 48, 48)
FONT_COLOR = (220, 220, 220)

pygame.init()
pygame.display.set_caption("Othello AI")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()


def draw_top_panel(board: BoardBitboard, turn_color: int):
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


def draw_board(board: BoardBitboard, legal_moves):
    # cells
    for r in range(8):
        for c in range(8):
            x = BOARD_ORIGIN[0] + c * CELL_SIZE
            y = TOP_PANEL_HEIGHT + r * CELL_SIZE
            pygame.draw.rect(screen, GREEN, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)
    # disks
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
    # logs
    for i, line in enumerate(logs[-15:]):
        txt = font.render(line, True, FONT_COLOR)
        screen.blit(txt, (x0 + 5, y0 + 5 + i * 20))
    # TODO : player type choice


def main():
    board = BoardBitboard()
    turn = 2
    logs = ["Game started"]
    settings = {}  # !!

    running = True
    while running:
        legal = board.legal_moves(turn)
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False
            elif evt.type == pygame.MOUSEBUTTONDOWN and evt.button == 1:
                mx, my = evt.pos
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
                            f"{'Black' if turn==2 else 'White'} : {(r,c)} = +{len(flips)}"
                        )
                        turn = 3 - turn
                        if not board.legal_moves(turn):
                            turn = 3 - turn

        screen.fill(BG)
        draw_top_panel(board, turn)
        draw_board(board, legal)
        draw_side_panel(logs, settings)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

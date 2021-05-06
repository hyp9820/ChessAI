import chess
import pygame as p
from utils import board_to_array, get_squares

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # ? For animations
IMAGES = {}

SQUARES = get_squares()


def load_images():
    pieces = {
        "P": "wp",
        "R": "wR",
        "N": "wN",
        "B": "wB",
        "Q": "wQ",
        "K": "wK",
        "p": "bp",
        "r": "bR",
        "n": "bN",
        "b": "bB",
        "q": "bQ",
        "k": "bK",
    }
    for i, piece in pieces.items():
        IMAGES[i] = p.transform.scale(
            p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)
        )


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    load_images()

    board = chess.Board()
    game_state = board_to_array(board)

    running = True
    sq_selected = ()  # ? last click of the user (tuple: (row, column))
    player_clicks = []  # ? Keep track of player clicks (two_tuples: [(6,4), (4,4)])
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # ! Mouse Handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                if game_state[row][col] == None and len(player_clicks) == 0:
                    pass
                elif sq_selected == (row, col):
                    # TODO: Deselect the selected square
                    sq_selected = ()
                    player_clicks = []
                elif len(player_clicks) == 0:
                    piece = chess.Piece.from_symbol(
                        board.piece_at(chess.parse_square(SQUARES[row][row])).symbol()
                    )
                    if piece.color == board.turn:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)

                if len(player_clicks) == 2:
                    # TODO: Move the piece
                    from_square = SQUARES[player_clicks[0][0]][player_clicks[0][1]]
                    to_square = SQUARES[player_clicks[1][0]][player_clicks[1][1]]
                    move = chess.Move.from_uci(from_square + to_square)
                    if move in board.legal_moves:
                        board.push(move)

                    # * Clear the vars
                    sq_selected = ()
                    player_clicks = []

            # ! Key Handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    # TODO: Undo the last move on 'Z' pressed.
                    if len(board.move_stack) > 0:
                        board.pop()
                        sq_selected = ()
                        player_clicks = []
                    else:
                        print("No moves to undo!")

            # ! Update Game State after any event
            game_state = board_to_array(board)
        draw_game_state(screen, game_state)
        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen, game_state):
    drawBoard(screen)
    drawPieces(screen, game_state)


def drawBoard(screen):
    # colors = [p.Color("white"), p.Color("gray")]
    colors = [(235, 235, 208), (119, 148, 85)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(
                screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )


def drawPieces(screen, game_state):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = game_state[r][c]
            if piece is not None:
                screen.blit(
                    IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )


if __name__ == "__main__":
    main()

import chess
import pygame as p
import numpy as np
from ChessEngine import get_stockfish_move, get_ai_move, get_ai_mov
from utils import board_to_array, get_square_indexes, get_squares

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # ? For animations
IMAGES = {}

SQUARES = get_squares()
SQUARE_INDEXES = get_square_indexes()

"""
TODO: Load all Images
"""


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


"""
TODO: MAIN FUNCTION
"""


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    load_images()

    board = chess.Board()
    game_state = board_to_array(board)

    running = True
    automate = False
    sq_selected = ()  # ? last click of the user (tuple: (row, column))
    player_clicks = []  # ? Keep track of player clicks (two_tuples: [(6,4), (4,4)])
    while running:

        for e in p.event.get():

            if e.type == p.QUIT:
                running = False
                break

            # ! Mouse Handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not automate:
                    if not board.is_game_over():
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
                            # piece = get_piece_on(board, SQUARES[row][col])
                            if (
                                board.color_at(chess.parse_square(SQUARES[row][col]))
                                == board.turn
                            ):
                                sq_selected = (row, col)
                                player_clicks.append(sq_selected)
                        else:
                            if (
                                board.color_at(chess.parse_square(SQUARES[row][col]))
                                == board.turn
                            ):
                                sq_selected = ()
                                player_clicks = []
                            sq_selected = (row, col)
                            player_clicks.append(sq_selected)

                        if len(player_clicks) == 2:
                            # TODO: Move the piece
                            from_square = SQUARES[player_clicks[0][0]][
                                player_clicks[0][1]
                            ]
                            to_square = SQUARES[player_clicks[1][0]][
                                player_clicks[1][1]
                            ]
                            move = chess.Move.from_uci(from_square + to_square)
                            if (
                                move.to_square in SQUARE_INDEXES[0]
                                or move.to_square in SQUARE_INDEXES[7]
                            ):  # ?  the to square is 1st or 8th rank
                                if (
                                    board.piece_type_at(move.from_square) == 1
                                ):  # ? Piece at from square is a pawn
                                    move.promotion = 5
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
                        board.pop()
                        sq_selected = ()
                        player_clicks = []
                    else:
                        print("No moves to undo!")

                if e.key == p.K_r:
                    board.reset()
                    sq_selected = ()
                    player_clicks = []

                if e.key == p.K_a:
                    automate = not automate

        # TODO: Our Model vs Stockfish
        if automate:
            if not board.is_game_over():
                if board.turn:
                    # ! Our Model's Engine
                    move = get_ai_mov(board)
                    board.push(move)
                elif not board.turn:
                    # ! Stockfish Engine
                    move = get_stockfish_move(board)
                    board.push(move)
                p.time.delay(1500)

            else:
                automate = not automate

        # * Update Game State on every iteration
        game_state = board_to_array(board)
        draw_game_state(screen, game_state, board, sq_selected)

        if board.is_game_over():
            winner = None
            termination = None
            outcome = board.outcome(claim_draw=True)

            termination = get_termination_type(outcome.termination.value)

            if outcome.winner is not None:
                winner = "White" if outcome.winner else "Black"
                text = str(winner + " Wins, By " + termination)
                size = 42
            else:
                text = str("Drawn due to " + termination)
                size = 32
            drawText(screen, text, size)

        clock.tick(MAX_FPS)
        p.display.flip()

        # TODO: Human vs Our Model
        if not board.is_game_over():
            if not board.turn:
                board.push(ai_move(board))


"""
TODO: Get move from the engine
"""


def ai_move(board):
    return get_stockfish_move(board)


"""
TODO: Highlight the squares 
"""


def highlight_squares(screen, board, sq_selected):
    if board.is_check():
        # TODO: Handle Check Highlighting
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(200)  # Transperancy value
        s.fill(p.Color("red"))
        row, col = np.where(SQUARE_INDEXES == board.king(board.turn))
        screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))

    if sq_selected != ():
        squares_to_highlight = []
        r, c = sq_selected
        selected_square_index = SQUARE_INDEXES[r, c]
        selected_square = chess.parse_square(SQUARES[r][c])

        if board.color_at(selected_square) == board.turn:

            # TODO: Highlight the square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Transperancy value
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # TODO: Highlight moves from that square
            s.set_alpha(150)
            s.fill(p.Color("pink"))

            for move in board.legal_moves:
                if move.from_square == selected_square:
                    squares_to_highlight.append(move.to_square)
            # attacked_squares = list(board.attacks(selected_square))
            for sq in squares_to_highlight:
                row, col = np.where(SQUARE_INDEXES == sq)
                screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))


"""
TODO: Render the Game
"""


def draw_game_state(screen, game_state, board, sq_selected):
    drawBoard(screen)
    highlight_squares(screen, board, sq_selected)
    drawPieces(screen, game_state)


"""
TODO: Draw the board
"""


def drawBoard(screen):
    # colors = [p.Color("white"), p.Color("gray")]
    colors = [(235, 235, 208), (119, 148, 85)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(
                screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )


"""
TODO: Draw the pieces
"""


def drawPieces(screen, game_state):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = game_state[r][c]
            if piece is not None:
                screen.blit(
                    IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )


"""
TODO: Get the termination type
"""


def get_termination_type(termination):
    if termination == 1:
        return "CheckMate"
    elif termination == 2:
        return "StaleMate"
    elif termination == 3:
        return "Insufficient Material"
    elif termination == 4:
        return "Seventy Five Moves"
    elif termination == 5:
        return "Five fold repetition"
    elif termination == 6:
        return "Fifty Moves"
    elif termination == 7:
        return "Three fold repetition"


"""
TODO: Draw the game over text
"""


def drawText(screen, text, size):
    font = p.font.SysFont("Helvitca", size, True, False)
    text_object = font.render(text, 0, p.Color("Black"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - text_object.get_width() / 2,
        HEIGHT / 2 - text_object.get_height() / 2,
    )
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color("Blue"))
    screen.blit(text_object, text_location.move(1, 1))


if __name__ == "__main__":
    main()

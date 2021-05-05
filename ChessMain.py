"""
? Resposible for handaling user input and displaying the current GameState
"""

import chess
import pygame as p
from utils import board_to_array

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # ? For animations
IMAGES = {}


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

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

        clock.tick(MAX_FPS)
        p.display.flip()

        draw_game_state(screen, board)


def draw_game_state(screen, board):
    drawBoard(screen)
    drawPieces(screen, board)


def drawBoard(screen):
    # colors = [p.Color("white"), p.Color("gray")]
    colors = [(235, 235, 208), (119, 148, 85)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(
                screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )


def drawPieces(screen, board):
    board = board_to_array(board)
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece is not None:
                screen.blit(
                    IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )


if __name__ == "__main__":
    main()

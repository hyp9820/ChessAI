import chess
import numpy as np


def board_to_array(board):
    d = {}
    index = 0
    a = np.array([None, None, None, None, None, None, None, None])

    myboard = np.vstack((a, a, a, a, a, a, a, a))

    for i, v in enumerate(chess.SQUARE_NAMES):
        d[i] = v

    for r in range(8):
        for c in range(8):
            myboard[r][c] = (
                board.piece_at(chess.parse_square(d[index])).symbol()
                if board.piece_at(chess.parse_square(d[index]))
                else None
            )
            index += 1

    return np.flip(myboard, axis=0)


def get_squares():
    return np.flip(np.array(chess.SQUARE_NAMES).reshape((8, 8)), axis=0)


def get_square_indexes():
    return np.flip(np.array(chess.SQUARES).reshape((8, 8)), axis=0)

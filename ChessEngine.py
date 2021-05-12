import chess
import numpy as np
from stockfish import Stockfish

import tensorflow as tf
import tensorflow.keras.models as models
import tensorflow.keras.layers as layers
import tensorflow.keras.utils as utils
import tensorflow.keras.optimizers as optimizers
import tensorflow.keras.callbacks as callbacks

print(tf.__version__)

stockfish = Stockfish(r"..\stockfish_13_win_x64_bmi2\stockfish_13_win_x64_bmi2")
# stockfish.set_elo_rating(100)
# stockfish.set_depth(1)


def get_stockfish_move(board):
    stockfish.set_skill_level(0)
    stockfish.set_elo_rating(100)
    fen = board.fen()
    stockfish.set_fen_position(fen)
    move = stockfish.get_best_move()
    move = chess.Move.from_uci(move)
    return move


mymodel = models.load_model("fiftyepochs.h5")

squares_index = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

# example: h3 -> 17
def square_to_index(square):
    letter = chess.square_name(square)
    return 8 - int(letter[1]), squares_index[letter[0]]


def split_dims(board):
    # this is the 3d matrix
    board3d = np.zeros((8, 8, 14), dtype=np.int8)

    # here we add the pieces's view on the matrix
    for piece in chess.PIECE_TYPES:
        for square in board.pieces(piece, chess.WHITE):
            idx = np.unravel_index(square, (8, 8))
            board3d[7 - idx[0]][idx[1]][piece - 1] = 1
        for square in board.pieces(piece, chess.BLACK):
            idx = np.unravel_index(square, (8, 8))
            board3d[7 - idx[0]][idx[1]][piece + 5] = 1

    # add attacks and valid moves too
    # so the network knows what is being attacked
    aux = board.turn
    board.turn = chess.WHITE
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[i][j][12] = 1
    board.turn = chess.BLACK
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[i][j][13] = 1
    board.turn = aux

    return board3d


def get_ai_mov(board):
    stockfish.set_skill_level(1)
    fen = board.fen()
    stockfish.set_fen_position(fen)
    move = stockfish.get_best_move()
    move = chess.Move.from_uci(move)
    return move


# used for the minimax algorithm
def minimax_eval(board):
    board3d = split_dims(board)
    board3d = np.expand_dims(board3d, 0)
    return mymodel.predict(board3d)[0][0]


def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return minimax_eval(board)

    if maximizing_player:
        max_eval = -np.inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = np.inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


# this is the actual function that gets the move from the neural network
def get_ai_move(board, depth, color):
    best_move = None
    max_eval = -np.inf
    min_eval = np.inf

    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, -np.inf, np.inf, False)
        board.pop()
        if color == "white":
            if eval > max_eval:
                max_eval = eval
                best_move = move
        elif color == "black":
            if eval < min_eval:
                min_eval = eval
                best_move = move

    return best_move

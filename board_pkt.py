# Copyright (C) 2025 Warren Usui, MIT License
"""
Object representing a board
"""
class Board:
    """
    Representation of board main use) and some extra move information
    """
    def __init__(self, b_info, enpas_info):
        """
        Set board and en passant info.
        """
        self.board = b_info
        self.enpassant = enpas_info
        self.klocs = [self.get_ploc('K'), self.get_ploc('k')]

    def get_ploc(self, kval):
        """
        Find the location of a specific piece
        """
        for row in range(0, 8):
            for col in range(0, 8):
                if self.board[row][col] == kval:
                    return [row, col]
        return []

    def conv_alg_to_grid(self):
        """
        Convert algebraic location of an en passant square
        to board coordinates
        """
        if self.enpassant == '-':
            return []
        row = 8 - int(self.enpassant[1])
        col = 'abcdefgh'.find(self.enpassant[0])
        return [row, col]

def get_board(board_str):
    """
    Initialize a board from FEN-notation
    """
    def gb_inner(board_line):
        def gb_mk_blanks(value):
            if value.isdigit():
                return '        '[0:int(value)]
            return value
        return list(map(gb_mk_blanks, board_line))
    return map(gb_inner, board_str)

def get_board_from_fen(fen_data):
    """
    Generate a pos packet from FEN board data.
    """
    def join_row_parts(row_info):
        return ''.join(row_info)
    lboard = list(map(join_row_parts, get_board(fen_data.split('/'))))
    board = list(map(list, lboard))
    return Board(b_info=board, enpas_info='-')

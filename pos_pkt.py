# Copyright (C) 2025 Warren Usui, MIT License
"""
Object representing a chess position at a certain point in time.
"""
from board_pkt import get_board_from_fen
from get_moves import get_moves

class PosPkt:
    """
    Position object used as parameters in search trees

    board is an 8x8 character representation of the board
    color is the color of the current player
    enpassant is a '-' if the last move was not a 2 space pawn move, and the skipped over square if
            the previous move was a two space paw move.
    gen_mv_func is a pointer to a get_moves function.  Each node has an instantiation of the
            get_move generating function here to keep track of the last move made from this node 
    """
    puz_mv_cnt = 2
    def __init__(self, **kwargs):
        self.board = kwargs['board']
        self.color = kwargs['color']
        self.enpassant = kwargs['enpassant']
        self.gen_mv_func = get_moves(self)
    def get_play_board(self):
        """
        Extract board info
        """
        return self.board.board
    def set_color(self, new_color):
        """
        Set color value
        """
        self.color = new_color

def get_pos_pkt_from_fen(in_data):
    """
    Generate a pos packet from FEN board data.
    """
    return PosPkt(board=get_board_from_fen(in_data), color='w',
                  enpassant='-')

if __name__ == "__main__":
    TEST = get_pos_pkt_from_fen('7k/pp6/R7/8/8/8/8/K7')
    TEST.color = 'b'
    print(TEST.board.board)
    for i in range(200):
        try:
            nxt_move = next(TEST.gen_mv_func)
            print(nxt_move)
        except StopIteration:
            print('we are done')
            break

# Copyright (C) 2025 Warren Usui, MIT License
"""
Check (king attacks) finder
"""
def check_check(board):
    """
    Determine whether both white and black are in check

    Returns a list of two entries.  The fitst entry is a list of all
    squares that have black pieces that can attack the white king.
    The second entry is a list of all squares that havve white pieces
    that can attack the black king.
    """
    retval = [[], []]
    for row in range(8):
        for col in range(8):
            if board.board[row][col] !=  ' ':
                opcol = 0
                if board.board[row][col].isupper():
                    opcol = 1
                chk_inf = can_attack(board, [row, col], board.klocs[opcol])
                if chk_inf:
                    retval[opcol].append(chk_inf)
    return retval

def can_attack(board, from_sq, to_sq):
    """
    determine if piece at location from_sq attacks location to_sq.
    The attack vs. can move to distinction is needed for the
    case of pawn moves.
    """
    def pval():
        return board.board[from_sq[0]][from_sq[1]]
    def blanks_betwixt(rdiff, cdiff):
        def gen_cnt(indx):
            xdir = to_sq[indx] - from_sq[indx]
            if xdir < 0:
                return -1
            if xdir > 0:
                return 1
            return 0
        hdir = gen_cnt(0)
        vdir = gen_cnt(1)
        nblanks = max(abs(rdiff), abs(cdiff))
        for dcount in range(1, nblanks):
            if board.board[from_sq[0] + dcount * hdir][
                        from_sq[1] + dcount * vdir] != ' ':
                return []
        return from_sq
    def check_pbrq(rdiff, cdiff):
        attack_fdir = 1
        if pval().islower():
            attack_fdir = -1
        if abs(cdiff) == 1 and rdiff == attack_fdir and pval() in 'pP':
            return from_sq
        if pval() in 'RrQq':
            if cdiff * rdiff == 0:
                return blanks_betwixt(rdiff, cdiff)
        if pval() in 'BbQq':
            if abs(cdiff) == abs(rdiff):
                return blanks_betwixt(rdiff, cdiff)
        return []
    if from_sq[0] == to_sq[0] and from_sq[1] == to_sq[1]:
        return []
    rdiff = from_sq[0] - to_sq[0]
    cdiff = from_sq[1] - to_sq[1]
    if abs(rdiff) < 2 and abs(cdiff) < 2 and pval() in 'kK':
        return from_sq
    if abs(rdiff) * abs(cdiff) == 2 and pval() in 'nN':
        return from_sq
    return check_pbrq(rdiff, cdiff)

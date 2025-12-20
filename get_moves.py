# Copyright (C) 2025 Warren Usui, MIT License
"""
Generator that finds legal moves.
"""
from check import can_attack, check_check

def get_moves(pos_pkt):
    """
    Loop across board finding pieces to move and where to move them.
    Moves for a piece are stored locally in a list.  That list (which
    is much shorter than a list of all available moves) is then iterated
    through, yielding a result each time this is called.  Once this shorter
    list is exhausted, find the next piece.
    """
    def extract(directions, lrow, lcol):
        def fmt_mv(sq_ent):
            return {'from': [lrow, lcol], 'to_move': sq_ent,
                    'former': pos_pkt.board.board[sq_ent[0]][sq_ent[1]],
                    'special': ' '}
        alist = []
        square = pos_pkt.board.board[lrow][lcol]
        for dirv in directions:
            for distv in range(1, 8):
                nrow = lrow + dirv[0] * distv
                ncol = lcol + dirv[1] * distv
                if nrow < 0 or nrow > 7 or ncol < 0 or ncol > 7:
                    break
                if pos_pkt.board.board[nrow][ncol] == ' ':
                    alist.append([nrow, ncol])
                    if square in 'Kk':
                        break
                    continue
                if pos_pkt.board.board[nrow][ncol].isupper(
                                            ) != square.isupper():
                    alist.append([nrow, ncol])
                break
        return list(map(fmt_mv, alist))
    mlist = castles(pos_pkt)
    for entry in mlist:
        yield entry
    square = 0
    for row in range(0, 8):
        for col in range(0, 8):
            def piece_moves(square, xrow, xcol):
                olist = dlist = []
                if square in 'RrQqKk':
                    olist = extract([[-1, 0], [1, 0], [0, -1], [0, 1]],
                                    xrow, xcol)
                if square in 'BbQqKk':
                    dlist = extract([[-1, -1], [1, 1], [1, -1], [-1, 1]],
                                    xrow, xcol)
                return olist + dlist
            square = pos_pkt.board.board[row][col]
            if square == ' ' or square.isupper() == (pos_pkt.color == 'b'):
                continue
            mlist = piece_moves(square, row, col)
            if square in 'Pp':
                mlist = handle_pawns(pos_pkt, square, row, col)
            for entry in mlist:
                yield entry
            if square in 'Nn':
                for lrow in [1, 2, -1, -2]:
                    for lcol in [1, 2, -1, -2]:
                        if abs(lrow) == abs(lcol):
                            continue
                        nrow = row + lrow
                        ncol = col + lcol
                        if nrow < 0 or nrow > 7 or ncol < 0 or ncol > 7:
                            continue
                        if pos_pkt.board.board[nrow][ncol].isupper(
                                            ) != square.isupper():
                            yield {'from': [row, col], 'to_move': [nrow, ncol],
                                   'former': pos_pkt.board.board[nrow][ncol],
                                   'special': ' '}

def handle_pawns(pos_pkt, square, prow, pcol):
    """
    Generate all the possible pawn moves (Take care of first row
    two move exceptions, taking on diagonals, pawn promotion and
    en passant captures)
    """
    def get_promo(esq):
        if esq in [0, 7]:
            return 'QNRB'
        return ' '
    def has_epiece(tsq):
        if tsq == ' ':
            return False
        return tsq.isupper() == (pos_pkt.color == 'b')
    p_moves = []
    strow = 1
    dirv = 1
    if square.isupper():
        dirv = -1
        strow = 6
    lboard = pos_pkt.board.board
    promo = get_promo(prow + dirv)
    if lboard[prow + dirv][pcol] == ' ':
        for pvalue in promo:
            p_moves.append({'from': [prow, pcol],
                            'to_move': [prow + dirv, pcol],
                            'former': ' ', 'special': pvalue})
        if prow == strow and lboard[prow + 2 * dirv][pcol] == ' ':
            p_moves.append({'from': [prow, pcol],
                'to_move': [prow + 2 * dirv, pcol],
                'former': ' ', 'special': ' '})
    if pcol != 0:
        if has_epiece(lboard[prow + dirv][pcol - 1]):
            for pvalue in promo:
                p_moves.append({'from': [prow, pcol],
                                'to_move': [prow + dirv, pcol - 1],
                                'former': lboard[prow + dirv][pcol - 1],
                                'special': pvalue})
    if pcol != 7:
        if has_epiece(lboard[prow + dirv][pcol + 1]):
            for pvalue in promo:
                p_moves.append({'from': [prow, pcol],
                                'to_move': [prow + dirv, pcol + 1],
                                'former': lboard[prow + dirv][pcol + 1],
                                'special': pvalue})
    if pos_pkt.board.enpassant != '-':
        lconv ={6: 2, 3: 5}
        ecol = 'abcdefgh'.find(pos_pkt.board.enpassant[0])
        erow = lconv[int(pos_pkt.board.enpassant[1])]
        if prow + dirv == erow and abs(pcol - ecol) == 1:
            p_moves.append({'from': [prow, pcol],
                            'to_move': [erow, ecol],
                            'former': ' ',
                            'special': 'E'})
    return p_moves

def castles(pos_pkt):
    """
    Handle castling.  If the King and Rook start in the origianl positions,
    then assume that castling is legal.  If either moves, then castling
    on the related side (or both if king moves) becomes illegal
    """
    def is_nxt_vul():
        for irow in range(0, 8):
            for icol in range(0, 8):
                if pos_pkt.board.board[irow][icol] in bw_info['attackers']:
                    if can_attack(pos_pkt.board, [irow, icol],
                                  [bw_info['back_row'],
                                   side_values[sidev.upper()]['skip_col']]):
                        return True
        return False
    c_board = pos_pkt.board
    m_list = []
    bw_values = {'w': {'back_row': 7, 'kindx': 0, 'kval': 'K', 'rval': 'R',
                       'attackers': 'kqrbnp'},
                 'b': {'back_row': 0, 'kindx': 1, 'kval': 'k', 'rval': 'r',
                       'attackers': 'KQRBNP'}}
    bw_info = bw_values[pos_pkt.color]
    if c_board.board[bw_info['back_row']][4] != bw_info['kval']:
        return []
    if len(check_check(c_board)['wb'.find(pos_pkt.color)]) > 0:
        return []
    side_values = {'Q': {'skip_col': 3, 'ecol': [1, 4], 'mchar': 'O',
                         'rloc': 0, 'ekloc': 2},
                   'K': {'skip_col': 5, 'ecol': [5, 7], 'mchar': 'C',
                         'rloc': 7, 'ekloc': 6}}
    for sidev in ['Q', 'K']:
        if c_board.board[bw_info['back_row']][
                    side_values[sidev]['rloc']] != bw_info['rval']:
            continue
        srange = side_values[sidev]['ecol']
        brange = c_board.board[bw_info['back_row']][srange[0]:srange[1]]
        if brange != list(filter(lambda a: a == ' ', brange)):
            continue
        if is_nxt_vul():
            continue
        m_list.append({'from': [bw_info['back_row'], 4],
                       'to_move': [bw_info['back_row'],
                                   side_values[sidev]['ekloc']],
                       'former': ' ', 'special': side_values[sidev]['mchar']})
    return m_list

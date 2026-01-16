# Copyright (C) 2025, 2026 Warren Usui, MIT License
"""
Main entry point, syntax checker, and move displayer
"""
from tree_pkt import solve_puzzle
from check import can_attack

def tree_disp(in_data, accum):
    """
    Display moves extracted from the tree.  what is returned here is a
    series of moves indented by a number of spaces proportional to how
    deep the move is in the solution tree.  Each move is a response
    to the previous move that is indented four spaces less.
    """
    def conv_to_alg(mv_indx):
        def chk_ind():
            if 'check' in in_data.nxt_move[-1]:
                if in_data.level == (in_data.solv_lev - 1) * 2:
                    return '#'
                return '+'
            return ''
        def mk_astr():
            def pieceloc():
                def uniquefier():
                    if pval not in phist:
                        return ''
                    if len(phist[pval]) == 1:
                        return ''
                    dlist = []
                    for dupv in phist[pval]:
                        if dupv == coord:
                            continue
                        if can_attack(in_data.pos.board, dupv,
                                      in_data.nxt_move[mv_indx]['to_move']):
                            dlist.append(dupv)
                    cfail = False
                    for entry in dlist:
                        if entry[1] == coord[1]:
                            cfail = True
                            break
                    if len(dlist) > 0:
                        if cfail:
                            return str(8 - coord[0])
                        return 'abcdefgh'[coord[1]]
                    return ''
                coord = in_data.nxt_move[mv_indx]['from']
                pval = in_data.pos.board.board[coord[0]][coord[1]]
                if pval in 'pP':
                    pval = ''
                return pval.upper() + uniquefier()
            def takef():
                rval = ''
                asq = in_data.nxt_move[mv_indx]['former']
                if asq != ' ' or in_data.nxt_move[mv_indx]['special'] == 'E':
                    rval += 'x'
                    if asq not in 'pP':
                        rval += asq.upper()
                    afs = in_data.nxt_move[mv_indx]['from']
                    pval = in_data.pos.board.board[afs[0]][afs[1]]
                    if pval in 'pP':
                        rval = 'abcdefgh'[afs[1]] + rval
                return rval.strip()
            def stvloc():
                coord = in_data.nxt_move[mv_indx]['to_move']
                return 'abcdefgh'[coord[1]] + str(8 - coord[0])
            def spec_chk():
                svalue = in_data.nxt_move[mv_indx]['special']
                if svalue in 'NBRQ':
                    return f'({svalue})'
                if svalue == 'E':
                    return '(e.p.)'
                return ''
            return pieceloc() + takef() + stvloc()+ spec_chk() + chk_ind()
        gap = ' ' * in_data.level * 4
        if in_data.nxt_move[mv_indx]['special'] == 'O':
            return gap + 'O-O-O' + chk_ind()
        if in_data.nxt_move[mv_indx]['special'] == 'C':
            return gap + 'O-O' + chk_ind()
        return gap + mk_astr() + '\n'
    phist = {}
    for phkeys in 'NBRQnbrq':
        phist[phkeys] = []
    for row in range(0, 8):
        for col in range(0,8):
            isq = in_data.pos.board.board
            if isq[row][col] in 'NBRQnbrq':
                phist[isq[row][col]].append([row, col])
    for totp in enumerate(in_data.to_tp):
        accum = tree_disp(totp[1], accum + conv_to_alg(totp[0]))
    return accum

def syntax_check(puzzle):
    """
    Return error message if input is invalid
    """
    sinfo = puzzle.split(' ')
    if not sinfo[1].isdecimal():
        return 'Number of moves is invalid'
    rows = sinfo[0].split('/')
    if len(rows) != 8:
        return 'Invalid number of rows'
    kdata = [0, 0]
    for rowchk in rows:
        rlen = 0
        for cchk in list(rowchk):
            if cchk not in 'pPnNbBrRqQkK 12345678':
                return f'row {rowchk} has an invalid character: {cchk}'
            if cchk == 'k':
                kdata[1] += 1
            if cchk == 'K':
                kdata[0] += 1
            if cchk in '12345678':
                rlen += int(cchk)
            else:
                rlen += 1
        if rlen != 8:
            return f'row {rowchk} has the wrong number of spaces'
    if kdata != [1, 1]:
        return "Invalid number of kings"
    return 0

def wide_tree(puzzle):
    """
    Main entry point to puzzle solver.

    Puzzle is a chess board description with piece locations specified in
    FEN-notation, followed by a move limit (these are mate in x move puzzles)
    The board description and move limit are separated by a blank
    """
    def chk_for_mate(accum, lpuzzle):
        max_blanks = max(list(map(lambda a: len(a) - len(a.lstrip()),
                                  accum.split('\n'))))
        exp_level = 8 * (int(lpuzzle.split()[-1]) - 1)
        return max_blanks == exp_level
    emsg = syntax_check(puzzle)
    if emsg:
        return emsg
    lpuzzle = puzzle
    while int(lpuzzle.split(' ')[-1]) > 0:
        fnd_sol = solve_puzzle(lpuzzle)
        answer = tree_disp(fnd_sol[1], accum='')
        if chk_for_mate(answer, lpuzzle):
            return answer
        parts = lpuzzle.split(' ')
        numb = int(parts[1])
        numb -= 1
        lpuzzle = ' '.join([parts[0], str(numb)])
    return 'Checkmate not found\n'

def join_fmoves(ltree):
    """
    Convert wide_tree output to narrower tree
    """
    def fix_wb_spacing(aline):
        if (len(aline) - len(aline.strip())) % 8 == 4:
            return aline + '--'
        return aline.strip() + '\n'
    if len(ltree) == 0 or ltree.startswith('Checkmate'):
        return 'Checkmate not found\n'
    lparts = ltree.split('\n')
    return ''.join(list(map(fix_wb_spacing, lparts)))

def fmt_1liners(old_answer):
    """
    Crunch single paths down into one line
    """
    parts = old_answer.split('\n')
    flimit = max(list(map(lambda a: len(a) - len(a.strip()), parts)))
    for bpoint in range(flimit - 8, 0, -8):
        bm_not = []
        for aline in enumerate(parts):
            if len(aline[1]) - len(aline[1].strip()) == bpoint:
                bm_not.append(aline)
        for entry in bm_not:
            sec_subl = parts[entry[0] + 2]
            if len(sec_subl) - len(sec_subl.strip()) != bpoint + 8:
                parts[entry[0]] += '--'
        nlist = []
        mflag = False
        for nstr in parts:
            if nstr.endswith('--'):
                mflag = True
                nlist.append(nstr)
            else:
                if mflag:
                    nlist.append(nstr.strip() + '\n')
                    mflag = False
                else:
                    nlist.append(nstr + '\n')
        nlist.append('\n')
        old_answer = ''.join(nlist)
        parts = old_answer.split('\n')
    return old_answer

def schach(puzzle):
    """
    Wrap wide_tree output
    """
    return fmt_1liners(join_fmoves(wide_tree(puzzle))).rstrip() + '\n'

if __name__ == "__main__":
    print(schach('r1n1N1RK/1R2Pk1P/b1qPpB2/r3p2p/2N5/8/8/8 3'))
    #print(schach('3r3k/4Qp1p/p3p3/1p1R4/4b2P/P5R1/1P3PP1/3q2K1 4'))

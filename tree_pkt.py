# Copyright (C) 2025 Warren Usui, MIT License
"""
TreePkt is a node on a solution tree

gen_next_move is the recursive node traversing routine used to generate
a solution tree.
"""
from copy import deepcopy
from pos_pkt import get_pos_pkt_from_fen, PosPkt
from check import check_check

class TreePkt:
    """
    Node in the solution tree. Holds current pos and links to other nodes
    in the solution tree.

    pos is a pos_pkt object containing board information for this node

    level is an integer count of how deep this node is in the solution tree
    (0 is white's first move, 1 is black's first move, 2 is white's second
    move...)

    to_tp is a list of tree nodes that can be reached from this node via
    a move

    nxt_move is a list of moves that causes the board position ot change
    to a corresponding to_tp node.  Nxt_move[n] is the move that leads
    to the board position for to_tp[n]

    from_tp is a link back to the tree node that this node branches off of
    
    nxt_move is a dict containing a from_node, a to_node, a former value
    (whatever was on the square before the piece moved there), a special
    character indicator (for pawn promotions, castling, and en apssant moves),
    and a giving check indicator
    
    solv_lev is a class variable storing the n value of this mate in n puzzle
    """
    def __init__(self, pos):
        self.pos = pos
        self.level = 0
        self.from_tp = None
        self.to_tp = []
        self.nxt_move = []
    def set_solv_in(self, mate_in):
        """
        Set maximum number of moves needed to solve this problem
        """
        TreePkt.solv_lev = int(mate_in)
    def set_level(self, level):
        """
        Set level for this node
        """
        self.level = level
    def save_move(self, move):
        """
        Stash nxt_move in this tree
o        """
        if self.level % 2 == 0:
            self.nxt_move = [move]
        else:
            self.nxt_move.append(move)

def get_tree_pkt_from_fen(fen_data):
    """
    Extract fen data into pos packet in this node
    """
    pospkt = get_pos_pkt_from_fen(fen_data)
    return TreePkt(pos=pospkt)

def specials(ncopy, nxt_move, tree_node):
    """
    Main line code that handles castling and enpassant
    """
    c_info = {'w': {'at_eprow': 3, 'back_row': 7},
              'b': {'at_eprow': 4, 'back_row': 0}}
    row_inf = c_info[tree_node.pos.color]
    if nxt_move['special'] == 'E':
        ncopy.board[row_inf['at_eprow']][
                    tree_node.from_tp.nxt_move[0]['from'][1]] =' '
    if nxt_move['special'] in 'OC':
        lxv = {'O': [2, 3, 0], 'C': [6, 5, 7]}[nxt_move['special']]
        r_brow = {0: 'r', 7: 'R'}
        k_brow = {0: 'k', 7: 'K'}
        brow = nxt_move['from'][0]
        nptr = tree_node
        c_isok = True
        while nptr:
            if (nptr.pos.board.board[brow][4] != k_brow[brow] or
                    nptr.pos.board.board[brow][lxv[2]] != r_brow[brow]):
                c_isok = False
                break
            nptr = nptr.from_tp
        if c_isok:
            ncopy.board[brow][lxv[0]] = ncopy.board[brow][4]
            ncopy.board[brow][lxv[1]] = ncopy.board[brow][lxv[2]]
            ncopy.board[brow][4] = ' '
            ncopy.board[brow][lxv[2]] = ' '
            return ncopy
        return 0
    return ncopy

def get_ncopy(ncopy, nxt_move, tree_node):
    """
    Ncopy is a new copy of the board.  Makes moves described in nxt_move
    """
    if nxt_move['special'] not in 'EOC':
        ltm = nxt_move['to_move']
        lfm = nxt_move['from']
        ncopy.board[ltm[0]][ltm[1]] = ncopy.board[lfm[0]][lfm[1]]
        ncopy.board[lfm[0]][lfm[1]] = ' '
    if nxt_move['special'] in 'NBRQ':
        promov = nxt_move['special']
        if tree_node.pos.color == 'b':
            promov = promov.lower()
        ncopy.board[ltm[0]][ltm[1]] = promov
    if nxt_move['special'] != ' ':
        ncopy = specials(ncopy, nxt_move, tree_node)
    return ncopy

def iter_stopped(tree_node, mv_cnt):
    """
    Sorts out return values when no more nodes at a level are available
    """
    if mv_cnt == 0:
        #if tree_node.level % 2 == 1 and tree_node.from_tp.nxt_move[0][
        #        'check'] == '+' :
        #    return ['+', tree_node]
        if tree_node.level == tree_node.solv_lev * 2 - 1:
            return ['+', tree_node]
        return ['-', tree_node]
    return ['-+'[tree_node.level % 2], tree_node]

def gen_next_move(tree_node):
    """
    Main routine of this module.  Given a starting node, recursively generate
    a tree of moves that solves the checkmate problem.
    """
    def set_ep_sq(nxt_move):
        ep_chk_brd = tree_node.pos.board.board
        if ep_chk_brd[nxt_move['from'][0]][nxt_move['from'][1]] in 'pP':
            if abs(nxt_move['from'][0] - nxt_move['to_move'][0]) == 2:
                skp_row = (nxt_move['from'][0] + nxt_move['to_move'][0]) // 2
                return 'abcdefgh'[nxt_move['from'][1]] + str(8 - skp_row)
        return '-'
    chk_indx = 'wb'.find(tree_node.pos.color)
    ncopy = []
    mv_cnt = 0
    while True:
        try:
            nxt_move = next(tree_node.pos.gen_mv_func)
            #f nxt_move['from'] == [1, 0] and nxt_move['to_move'] == [1, 6]:
            #   import pdb; pdb.set_trace()
        except StopIteration:
            return iter_stopped(tree_node, mv_cnt)
        if not nxt_move:
            ncopy = []
            break
        ncopy = get_ncopy(deepcopy(tree_node.pos.board), nxt_move, tree_node)
        if not ncopy:
            continue
        aksq = ncopy.klocs[chk_indx]
        if ncopy.board[aksq[0]][aksq[1]] == ' ':
            ncopy.klocs[chk_indx] = nxt_move['to_move']
        chk_test = check_check(ncopy)
        if chk_test[1 - tree_node.level % 2]:
            nxt_move['check'] = '+'
        if len(chk_test[chk_indx]) > 0:
            continue
        if tree_node.level == tree_node.solv_lev * 2 - 2:
            if len(chk_test[1 - chk_indx]) == 0:
                continue
        mv_cnt += 1
        nxt_tree_node = TreePkt(PosPkt(board=ncopy,
                        color='bw'['wb'.find(tree_node.pos.color)],
                        enpassant=set_ep_sq(nxt_move)))
        nxt_tree_node.pos.board.enpassant = nxt_tree_node.pos.enpassant
        if tree_node.level % 2 == 0:
            tree_node.to_tp = []
        tree_node.to_tp.append(nxt_tree_node)
        nxt_tree_node.from_tp = tree_node
        nxt_tree_node.set_level(tree_node.level + 1)
        tree_node.save_move(nxt_move)
        if tree_node.level == tree_node.solv_lev * 2 - 1:
            return ['-', tree_node]
        retv = gen_next_move(nxt_tree_node)
        if [retv[0], tree_node.level % 2] in [['+', 0], ['-', 1]]:
            return [retv[0], tree_node]
    return ['unexpected termination of gen_next_move']

def solve_puzzle(puzzle):
    """
    Wrapper that creates a root node and passes that node to gen_next_move
    """
    parts = puzzle.split(' ')
    root_node = get_tree_pkt_from_fen(parts[0])
    root_node.set_solv_in(parts[1])
    return gen_next_move(root_node)

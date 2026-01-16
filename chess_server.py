# Copyright (C) 2026 Warren Usui, MIT License
"""
Server that interfaces with client html page

To start, run: gunicorn --bind 0.0.0.0:8000 chess_server:app
"""
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from schach import schach

app = Flask(__name__)
CORS(app, origins=["*"])
@app.route('/chess-prog', methods=['POST'])
@cross_origin()
def handle_json():
    """
    app endpoint fork chess-prog
    """
    print({'msg': 'handle json'})
    try:
        data = request.get_json()
        print(data)
        problem = data.get('problem', 'No name')
        if 'name' in data:
            return jsonify(data)
        response = jsonify({'message': f'{chg_to_html(problem)}'}), 200
        return response
    except (AttributeError, IndexError) as e_msg:
        print(str(e_msg))
        return jsonify({'error': str(e_msg)}), 400

def chg_to_html(ofmt):
    """
    Wrapper used to run schach on fen output
    """
    def gen_line(linput):
        return f'<p><pre>{linput}</pre></p>'
    solution = schach(fix_from_client(ofmt)).split('\n')
    fmted = list(map(gen_line, solution))
    return ''.join(fmted)
def fix_from_client(ofmt):
    """
    Convert web page information format to fen format string
    """
    def process(board):
        rlist = []
        for rnum in range(0, 63, 8):
            rlist.append(''.join(board[rnum:rnum + 8]))
        nboard = []
        for rrow in rlist:
            ncount = -1
            nrow = []
            for sqv in rrow:
                if sqv != '1':
                    if ncount > 0:
                        nrow.append(str(ncount))
                        ncount = -1
                    nrow.append(sqv)
                else:
                    if ncount == -1:
                        ncount = 1
                    else:
                        ncount += 1
            if ncount > 0:
                nrow.append(str(ncount))
            nboard.append(''.join(nrow))
        return nboard
    parts = ofmt.split('/')
    board = 64 * ['1']
    for side in [1, 2]:
        cval = parts[side].split(':')
        pieces = cval[1].split(',')
        for piece in pieces:
            if len(piece) == 2:
                pval = 'P'
                loc = piece
            else:
                pval = piece[0]
                loc = piece[1:]
            if cval[0] == 'B':
                pval = pval.lower()
            rowv = 8 - int(loc[-1])
            colv = 'abcdefgh'.find(loc[0])
            board[8 * rowv + colv] = pval
    return '/'.join(process(board)) + f' {parts[0]}'

if __name__ == "__main__":
    #print(chg_to_html('2/W:Kc8,b6,Ra1/B:a7,b7,Ka8,Bb8'))
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)

import requests, random, re, json, os, sys
import chess.pgn, chess.engine
import chess
import configparser

config = configparser.ConfigParser()
config.read('setup.ini')

stockfish_path = os.path.join(sys.path[0],'stockfish\stockfish_15.exe')

# how the base game is loaded before db/stockfish takes over
f = open('openings.json')
opening_json = json.load(f)
f.close()

def get_database_from_fen(fen):
    # the range of ratings the database moves will come from
    rating_range = config['DATABASE']['rating_range']
    # the number of moves to return (helpful to keep this +5 from max of database_choices)
    moves_to_display = config['DATABASE']['moves_to_display']
    resp = requests.get('https://explorer.lichess.ovh/lichess', params={'variant' : 'standard', 'fen': fen, 'moves': moves_to_display, 'rating' : rating_range})
    return resp.json()
     
def get_top_move(db,move_level,engine):
    # try to get a move from db, otherwise use stockfish
    try:
        move = db['moves'][move_level]['uci']
    except:
        move = get_stockfish_move(board, engine)
    return move

def get_stockfish_analysis(board, engine):
    # analyse given board and return Centipawns from White perspective
    # used to stop db choices being wild
    info = engine.analyse(board, chess.engine.Limit(depth=depth))
    return info['score']

def get_stockfish_move(board, engine):
    # gets top move from stockfish on given board state
    # get info from analysis    
    info = engine.analyse(board, chess.engine.Limit(depth=depth))
    # get only the top move
    move = str(info['pv'][0])
    return move

def play_opening(board,opening):
    # plays the opening as specifed in INI file
    opening_moves = opening_json[main_opening][0][opening]
    
    for move in opening_moves:
        board.push_uci(move)
    return board

main_opening = config['SETUP']['main_opening']
variation_name = config['SETUP']['variation_name']
depth = config['ENGINE']['depth']
board = chess.Board()
board = play_opening(board,variation_name)
game = chess.pgn.Game()
game.headers['Event'] = variation_name + ' - DB moves vs Stockfish'
game.headers['White'] = 'Stockfish'
game.headers['Black'] = 'Lichess DB'

# max number of different lines
max_variations = int(config['SETUP']['max_variations'])
current_variations = 0
# max number of moves per line
moves_per_line = int(config['SETUP']['moves_per_line'])
# how low down the top moves we look when choosing black's moves
database_choices = config['DATABASE']['database_choices']
# max centipawn value before we use stockfish instead of db
max_centipawns = int(config['DATABASE']['max_centipawn_value'])
# load engine
engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
print('Engine Loaded')

while current_variations != max_variations:
    print('Line %s started' % current_variations)
    while board.fullmove_number <= moves_per_line:
        # this will have to be repeated after every move
        move_list = get_database_from_fen(board.fen())

        # board.turn will return True if it whites turn, False if black
        if board.turn == True:
            move = get_stockfish_move(board,engine)
            board.push_uci(move)            
        else:
            # db logic here
            move_level = random.choice(database_choices)
            move = get_top_move(move_list,move_level,engine)
            board.push_uci(move)

            # now it analyses db moves and if cp is greater than 150, gets stockfish move
            current_centipawns = str(get_stockfish_analysis(board,engine))
            current_centipawns = int(re.sub("[^0-9]", "", current_centipawns))
            # have to do it after so we have the updated board
            if current_centipawns >= max_centipawns:
                # if move is bad, return to previous state and push sf move
                board.pop()
                move = get_stockfish_move(board,engine)
                board.push_uci(move)
            else:
                pass     
        

    # once we reach 10 moves, reset to opening
    game.add_line(board.move_stack)
    current_variations += 1
    board.reset()
    board = play_opening(board,variation_name)


engine.quit()
print(game, file=open("%s.pgn" % variation_name, "w"), end="\n\n")
print('Saved pgn successfully')
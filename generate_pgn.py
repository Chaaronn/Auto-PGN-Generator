import requests, random, os, sys, ast, csv, io
import chess.pgn, chess.engine
import chess
import configparser


config = configparser.ConfigParser()
try:
    config.read('setup.ini')
except IOError as e:
    print("Error reading setup.ini:", str(e))
    sys.exit(1)

stockfish_path = os.path.join(sys.path[0],'stockfish\stockfish_15.exe')


def get_database_from_fen(fen):
    # the range of ratings the database moves will come from
    rating_range = ast.literal_eval(config['DATABASE']['rating_range'])
    # the number of moves to return (helpful to keep this +5 from max of database_choices)
    moves_to_display = config['DATABASE']['moves_to_display']

    try:
        resp = requests.get('https://explorer.lichess.ovh/lichess', 
                            params={'variant' : 'standard', 'fen': fen, 'moves': moves_to_display, 'rating' : rating_range})
        resp.raise_for_status()  # Check for any HTTP errors
        return resp.json()
    except requests.exceptions.RequestException as e:
        print("Error making API request:", str(e))
        sys.exit(1)
     
def get_top_move(db,move_level,engine):
    # try to get a move from db, otherwise use stockfish
    try:
        move = db['moves'][move_level]['uci']
    # except is either no db moves, or not one at move_level
    except:
        print('Error in using db. using stockfish')
        move = get_stockfish_move(board, engine)
    return move

def get_stockfish_analysis(board, engine):
    # analyse given board and return Centipawns from White perspective
    # used to stop db choices being wild
    # could change to utilising Lichess online eval to save processing
    info = engine.analyse(board, chess.engine.Limit(depth=depth))
    return info['score']

def get_stockfish_move(board, engine):
    # gets top move from stockfish on given board state
    # get info from analysis    
    info = engine.analyse(board, chess.engine.Limit(depth=depth))
    # get only the top move
    move = str(info['pv'][0])
    return move

# update to use tsv of ALL openings on Lichess
def play_opening(board,opening):
    # open tsv
    try:
        opening_csv = csv.reader(open("openings/a.tsv", "r"), delimiter="\t", quotechar='"')
    except csv.Error as e:
        print("Error in CSV reader"), str(e)
        sys.exit(1)
    # future planning for dropdown opening list
    holder = []
    opening = opening.replace('"', "")
    # iter csv until we hit a match
    for line in opening_csv:
        if opening in str(line):
            holder.append(line)

    # future choice of openings from matches
    full_pgn = holder[0]
    # convert to pgn
    pgn = io.StringIO(full_pgn[2])
    game = chess.pgn.read_game(pgn)
    # make the board
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
    return board

def clean_analysis(string):
    # add a mate check here, convert it to +- 999 CP
    mate_string = 'vScore(Mate('
    if mate_string in string:
        if side.lower() == 'white':
            string = '999'
        else:
            string = '-999'
    start_index = string.find('Cp(') + 3
    end_index = string.find(')', start_index)
    number_string = string[start_index:end_index]

    if number_string.startswith('+'):
        number_string = number_string[1:]  # Remove the leading '+'

    string = int(number_string)

    return string

def make_moves(board,engine,move_list,cp_threshold,side):
    # board.turn will return True if it whites turn, False if black
    if side.lower() == 'white':
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
            # necassary to remove none int values from string
            #current_centipawns = int(re.sub("[^0-9]", "", current_centipawns)) 
            current_centipawns = clean_analysis(current_centipawns)
            # compare cp against max
            if current_centipawns >= cp_threshold:
                # if move is bad, return to previous state and push sf move
                board.pop()
                move = get_stockfish_move(board,engine)
                board.push_uci(move)
            else:
                # move on, the db move was good enough
                pass
    elif side.lower() == 'black':

        if board.turn == True:
               # db logic here
            move_level = random.choice(database_choices)
            move = get_top_move(move_list,move_level,engine)
            board.push_uci(move)

            # now it analyses db moves and if cp is greater than 150, gets stockfish move
            current_centipawns = str(get_stockfish_analysis(board,engine))
            # necassary to remove none int values from string
            current_centipawns = clean_analysis(current_centipawns)
            # compare cp against max
            if current_centipawns >= cp_threshold:
                # if move is bad, return to previous state and push sf move
                board.pop()
                move = get_stockfish_move(board,engine)
                board.push_uci(move)
            else:
                # move on, the db move was good enough
                pass
        else:
            move = get_stockfish_move(board,engine)
            board.push_uci(move)
    else:
        print('Error in choosing side.')

# set-up variables for use, see setup.ini for explainations
main_opening = config['SETUP']['main_opening']
depth = config['ENGINE']['depth']
side = config['SETUP']['side']
# set-up the board
board = chess.Board()
# play out the speicifed opening. this is required or the PGN will be incorrect
board = play_opening(board,main_opening)
# set-up game to add lines later
game = chess.pgn.Game()
# add headers so on import it looks nice on Lichess
game.headers['Event'] = main_opening


# max number of different lines
max_variations = int(config['SETUP']['max_variations'])
current_variations = 0
# max number of moves per line
moves_per_line = int(config['SETUP']['moves_per_line'])
# how low down the top moves we look when choosing black's moves
# load with ast otherwise its just a string
database_choices = ast.literal_eval(config['DATABASE']['database_choices'])
# max centipawn value before we use stockfish instead of db
max_centipawns = int(config['DATABASE']['max_centipawn_value'])
# load engine
engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
engine.configure({'Threads': int(config['ENGINE']['threads'])})
print('Engine Loaded')

moves_per_line = moves_per_line + board.fullmove_number
# main loop
# start new variation
while current_variations != max_variations:
    print('Line %s started' % current_variations)
    # start new line
    while board.fullmove_number <= moves_per_line:
        # this will have to be repeated after every move
        move_list = get_database_from_fen(board.fen())

        make_moves(board, engine, move_list, max_centipawns,side)
        
    # once we reach 10 moves, add line to pgn, reset to opening
    # added so lines always end with a final White move
    if board.turn == True:
            move = get_stockfish_move(board,engine)
            board.push_uci(move)
    
    game.add_line(board.move_stack)
    current_variations += 1
    board.reset()
    board = play_opening(board,main_opening)

# always quit engine or it will run indefinitely
engine.quit()

# modified so it closes the file
filename = "%s - %s.pgn" % main_opening
try:
    with open(filename, "w") as file:
        print(game, file=file, end="\n\n")
        print('Saved pgn successfully')
except IOError as e:
    print("Error writing to PGN file:", str(e))
    sys.exit(1)
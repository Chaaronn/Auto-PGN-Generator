import chess
import chess.polyglot
from generate_pgn import play_opening


board = chess.Board()
main_opening = ''
variation_name = ''
board = play_opening(variation_name)

with chess.polyglot.open_reader('opening_books/Performance.bin') as reader:
    num_lines = 0
    all_moves = {}

    while num_lines != 10:
        move = 0
        line_uci_moves = []

        while move != 10:  # Modify this condition to the desired number of moves per line
            found_moves = set()

            for entry in reader.find_all(board):
                uci_move = str(entry.move)

                if uci_move not in found_moves and uci_move not in line_uci_moves:
                    line_uci_moves.append(uci_move)
                    found_moves.add(uci_move)
                    move += 1
                    if move == 10:
                        break

        all_moves[num_lines] = line_uci_moves
        board.reset()
        num_lines += 1
        print(all_moves)

    print(all_moves)

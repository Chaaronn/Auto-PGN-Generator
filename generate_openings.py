import chess, chess.polyglot, chess.pgn
import csv, io

csv_file = csv.reader(open("openings/a.tsv", "r"), delimiter="\t", quotechar='"')
opening = "King's Indian Defense: Orthodox Variation, Bayonet Attack, Yepishin's Line"
holder = []
for line in csv_file:
    if opening in str(line):
        holder.append(line)
line = holder[0]
pgn = io.StringIO(line[2])
board = chess.Board()
game = chess.pgn.read_game(pgn)
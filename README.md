# PGN Generator

This python script generates variations based off given values in the INI file. 

Designed for use with Lichess Studies & Listudy, so many variations can be made quickly that are relevant to my rating (1600)

It chooses random DB moves, then replies with the best move from Stockfish 15


# SETUP

Ensure 'main_opening' and 'variation_name' in setup.ini exactly match to the opening and variation in openings.json

Currently NO error handling, so if this isn't done your PC will cry as Stockfish runs forever

# USAGE

python run main.py

pgn for given variations in setup.ini will be generated in the file path of the Python file.



# TODO 

1. Make variation search not based off raw text 
2. Increase efficiency 
3. Error handling
4. More variations

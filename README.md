# PGN Generator

This python script generates PGN files containing variations based off given values in the INI file. 

Designed for use with Lichess Studies & Listudy, so many variations can be made quickly in differnt rating ranges.

It chooses random DB moves, then replies with the best move from Stockfish 15. Example outputs can be found at: https://lichess.org/study/IDf2Qi7W


# SETUP

Ensure 'main_opening' and 'variation_name' in setup.ini exactly match to the opening and variation in openings.json



# USAGE

python run main.py

pgn for given variations in setup.ini will be generated in the file path of the Python file.



# TODO 

1. Make variation search not based off raw text 
2. Increase efficiency 
3. More variations

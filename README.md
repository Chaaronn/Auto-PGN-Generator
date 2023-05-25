# PGN Generator

This python script generates PGN files containing variations based off given values in the INI file. 

Designed for use with Lichess Studies & Listudy, so many variations can be made quickly in differnt rating ranges.

It utilises Lichess API to access most played moves in a given rating range, then follows pre-set openings until the opening line ends after which the database is accessed for Black's moves, whereas Stockfish is used for White.  If the database move causes significant advantage for White (as set in INI file), it reverts to Stockfish for each player. Users can edit values in the setup file to adjust the script to rating ranges, engine depth and more.

Currently, I have only added the King's Gambit (aka best opening) to the list of openings, but plan to add more when I can figure out how to automate it.

Example outputs can be found at: https://lichess.org/study/IDf2Qi7W

Google Collab version: https://colab.research.google.com/drive/1jUxM-EFstDgyCt2P77dZMljoZlw0mcgL


# SETUP

Ensure 'main_opening' and 'variation_name' in setup.ini exactly match to the opening and variation in openings.json.

If using an opening with a large number of pre-made moves, consider increasing "moves_per_line" as these will be counted to this total.

Only requirement outside base Python modules is 'python-chess'.

# USAGE

Download & un-zip the repo. Open cmd/terminal in this folder, then:

python run main.py

pgn for given variation in setup.ini will be generated in the file path of the Python file.



# TODO 

1. Make variation search not based off raw text 
2. Increase efficiency 
3. More variations
4. Remove openings counting towards moves_per_line

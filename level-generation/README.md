To execute the current level generation and training process

1. Navigate to level-generation
2. Run this command ``` python .\gameGen.py .\games\temp\ 8 ``` to generate 8 starting random games
3. Run this command ``` python .\train.py .\games\training\human\ .\games\training\random\ .\games\temp ``` to 
generate a classifier and search through neighbour games until you find one that appears to be human
4. run this command ``` python .\levelGen.py .\games\temp\[human game].txt .\games\temp\[human game]_lvl0.txt ```
to create a random level for that game
5. run this command ``` python -m vgdl.util.humanplay.play_vgdl ..\level-generation\games\temp\[human game]_lvl0.txt ```
to play that level
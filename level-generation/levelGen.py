import random
from gameComprehension import *

# Write a level to a file and return the file
# level (2D array of string characters)
# outputFileName (string name of the file to write to)
def levelToFile(level, outputFileName):
  with open(outputFileName, 'w') as out:
    for row in level:
      out.write(''.join(row) + '\n')
  return out

# swaps out one character in a level
# row (int)
# col (int)
# newChar (single string character)
# level (2D array of string characters)
def substitution(row, col, newChar, level):
  level[row][col] = newChar
  return level

# Return a width x height matrix of background characters
# width (int)
# height (int)
# background (single string character)
def getEmptyLevel(width, height, background):
  return [[background for _ in range(width)] for _ in range(height)]

# Return a width x height matrix of random characters from the charSet
# width (int)
# height (int)
# charSet (array of single string character)
def getRandomLevel(width, height, charSet):
  return [[random.choice(charSet) for _ in range(width)] for _ in range(height)]

# Creates a random level by setting an empty level and making a number of random substitutions
# width (int)
# height (int)
# charSet (array of single string character)
# background (single string character)
# subNum (int)
def getRandomSubLevel(width, height, charSet, background, subNum):
  level = getEmptyLevel(width, height, background)
  for _ in range(subNum):
    randRow = random.randint(0, height - 1)
    randCol = random.randint(0, width - 1)
    level = substitution(randRow, randCol, random.choice(charSet), level)
  return level

def main():
  levelMapping = extractLevelMapping('level-generation/outputs/testGame_sub.txt')
  charSet = [i for i in levelMapping.keys()]
  levelToFile(getRandomLevel(10, 10, charSet), 'level-generation/outputs/testGame_lvl0.txt')
  return

if __name__ == "__main__":
    main()
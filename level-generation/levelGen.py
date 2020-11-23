import random, sys
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

def getLevelFromFile(levelFile):
  level = []
  with open(levelFile, 'r') as LF:
    for line in LF.readlines():
      row = []
      row[:0] = line.strip()
      level.append(row)
  return level


def makeSubstitution(gameFile, originalLevel, outputLevel, n):
  mapping = extractLevelMapping(gameFile)
  chars = [c for c in mapping.keys()]
  level = getLevelFromFile(originalLevel)
  for i in range(n):
    row = random.randint(0, len(level) - 1)
    col = random.randint(0, len(level[row]) - 1)
    char = random.choice(chars)
    level = substitution(row, col, char, level)
  levelToFile(level, outputLevel)

def deleteRow(originalLevel, outputLevel):
  level = getLevelFromFile(originalLevel)
  if len(level) > 1: # Level at least 2 rows
    level = level[:-1]
    levelToFile(level, outputLevel)
    return True
  return False

def addRow(originalLevel, outputLevel, gameFile):
  level = getLevelFromFile(originalLevel)
  chars = [c for c in extractLevelMapping(gameFile).keys()]
  if len(level) < 13: # level not too long
    rowLen = len(level[0])
    level.append([random.choice(chars) for _ in range(rowLen)])
    levelToFile(level, outputLevel)
    return True
  return False

def deleteColumn(originalLevel, outputLevel):
  level = getLevelFromFile(originalLevel)
  if len(level) > 1: # Level at least 2 columns
    for i in range(len(level)):
      row = level[i]
      row = row[:-1]
      level[i] = row
    levelToFile(level, outputLevel)
    return True
  return False

def addColumn(originalLevel, outputLevel, gameFile):
  level = getLevelFromFile(originalLevel)
  chars = [c for c in extractLevelMapping(gameFile).keys()]
  if len(level) < 13: # level not too long
    for row in level:
      row.append(random.choice(chars))
    levelToFile(level, outputLevel)
    return True
  return False

def main():
  inputFile = sys.argv[1]
  outputFile = sys.argv[2]
  levelMapping = extractLevelMapping(inputFile)
  charSet = [i for i in levelMapping.keys()]
  levelToFile(getRandomLevel(10, 10, charSet), outputFile)
  deleteColumn(outputFile, outputFile + '0')
  deleteRow(outputFile, outputFile + '1')
  return

if __name__ == "__main__":
    main()
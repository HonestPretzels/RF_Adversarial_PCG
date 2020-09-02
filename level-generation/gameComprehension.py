
# Returns the levelMapping of a VGDL game file
# gameFileName (string path to file)
def extractLevelMapping(gameFileName):
  levelMapping = {}
  with open(gameFileName, 'r') as gameFile:
    while 'LevelMapping' not in gameFile.readline():
      continue
    allChars = False
    while not allChars:
      line = gameFile.readline()
      if ('>' not in line):
        allChars = True
        break
      char = line.split('>')[0].strip()
      mapping = line.split('>')[1].strip()
      levelMapping[char] = mapping
  return levelMapping
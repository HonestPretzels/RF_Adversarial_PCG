from vgdl.parser import indent_tree_parser

# Returns the levelMapping of a VGDL game file
# gameFileName (string path to file)
def extractLevelMapping(gameFileName):
  levelMapping = {}
  with open(gameFileName, 'r') as gameFile:
    root = indent_tree_parser(gameFile.read())
    levelMappingRoot = getNode(root, 'LevelMapping')
    for child in levelMappingRoot.children:
      char = child.content.split('>')[0].strip()
      mapping = child.content.split('>')[1].strip()
      levelMapping[char] = mapping
  return levelMapping

# Returns the root node of the sprite set
def getSpriteSetNode(fileName):
  with open(fileName, 'r') as inputfile:
    root = indent_tree_parser(inputfile.read())
    spriteSet = getNode(root, 'SpriteSet')
    return spriteSet

# Returns the root node of the termination set
def getTerminationSetNode(fileName):
  with open(fileName, 'r') as inputfile:
    root = indent_tree_parser(inputfile.read())
    spriteSet = getNode(root, 'TerminationSet')
    return spriteSet

# Returns the root node of the interaction set
def getInteractionSetNode(fileName):
  with open(fileName, 'r') as inputfile:
    root = indent_tree_parser(inputfile.read())
    spriteSet = getNode(root, 'InteractionSet')
    return spriteSet

# Returns the node with the desired name by recursing through the children of a starting node
def getNode(node, name):
  if node.content == name:
    return node
  else:
    for child in node.children:
      possibleNode = getNode(child, name)
      if possibleNode:
        return possibleNode
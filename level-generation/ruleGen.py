import random
from vgdl.parser import Node
from gameComprehension import *

# SPRITES

SPRITE_CLASSES = [
    'AStarChaser',
    'Bomber',
    'Chaser',
    'Conveyor',
    'ErraticMissile',
    'Fleeing',
    'Flicker',
    'Immovable',
    'Missile',
    'OrientedFlicker',
    'OrientedSprite',
    'Passive',
    'Portal',
    'RandomInertial',
    'RandomMissile',
    'RandomNPC',
    'ResourcePack',
    'SpawnPoint',
    'Spreader',
    'SpriteProducer',
    'WalkJumper',
    'Walker',
    'Resource'
]

# These might be entirely arbitrary identifiers??
SPRITE_TYPES = [
  'sam',
  'bomb',
  'alienBlue',
  'alienGreen',
  'avatar',
  'portal',
  'log',
  'goal',
  'box',
  'sword',
  'diamond',
  'exitdoor',
  'carcass',
  'angry',
  'scared',
  'explosion',
  'city',
  'incoming',
  'exit1',
  'exit2',
  'bee',
  'zombie',
  'honey',
  'withkey',
]

SPRITE_IMAGES = [
  'oryx/alien1',
  'oryx/alien2',
  'oryx/bat1',
  'newset/bandit1',
  'newset/block1',
  'newset/barrier1',
]

SPRITE_MODIFIERS = {
  'color': [
    'GREEN',
    'BLUE',
    'RED',
    'GRAY',
    'WHITE',
    'BROWN',
    'BLACK',
    'ORANGE',
    'YELLOW',
    'PINK',
    'GOLD',
    'LIGHTRED',
    'LIGHTORANGE',
    'LIGHTBLUE',
    'LIGHTGREEN',
    'LIGHTGRAY',
    'DARKGRAY',
    'DARKBLUE',
  ],
  'orientation': [
    'LEFT',
    'RIGHT',
    'UP',
    'DOWN',
  ],
  'sType': SPRITE_TYPES,
  'hidden': ['True', 'False'],
  'invisible': ['True', 'False'],
  'singleton': ['True', 'False'],
  'autoTiling': ['True', 'False'],
  'cooldown': [0, 20],
  'speed': [0, 1],
  'prob': [0, 1],
  'limit': [1, 10],
  'shrinkFactor': [0, 1],
}

def addSprite(parent: Node, sprite: Node):
  sprite.indent = parent.indent + 4
  parent.insert(sprite)

def removeSprite(parent: Node, sprite: Node):
  idx = 0
  for child in parent.children:
    if child.content == sprite.content:
      parent.children.pop(idx)
    idx += 1
  
def newSprite(name, content):
  return Node(name + ' > ' + content, 8)

def randomSprite():
  sClass = random.choice(SPRITE_CLASSES)
  image = random.choice(SPRITE_IMAGES)
  sprite = sClass + ' img=' + image 
  optionCount = random.randint(0,3)
  for _ in range(optionCount):
    sprite = addOption(sprite)
  return sprite

def addOption(sprite):
  option = random.choice(list(SPRITE_MODIFIERS.keys()))
  strOption = str(option)
  if strOption in ['cooldown', 'limit']: # int
    value = random.randint(SPRITE_MODIFIERS[option][0], SPRITE_MODIFIERS[option][1])
  elif strOption in ['speed', 'prob', 'shrinkFactor']: # float
    value = random.uniform(SPRITE_MODIFIERS[option][0], SPRITE_MODIFIERS[option][1])
  else:
    value = random.choice(SPRITE_MODIFIERS[option])
  return sprite + ' ' + strOption + '=' + str(value)

# INTERACTIONS

INTERACTION_TYPES = [
    'killSprite',
    'killBoth',
    'cloneSprite',
    'transformTo',
    'stepBack',
    'undoAll',
    'bounceForward',
    'windGust',
    'slipForward',
    'attractGaze',
    'flipDirection',
    'conveySprite',
    'turnAround',
    'reverseDirection',
    'bounceDirection',
    'wallBounce',
    'wallStop',
    'killIfSlow',
    'killIfFromAbove',
    'killIfAlive',
    'collectResource', # This is probably broken for now
    'changeResource',
    'spawnIfHasMore',
    'killIfHasMore',
    'killIfOtherHasMore',
    'killIfHasLess',
    'killIfOtherHasLess',
    'wrapAround',
    'pullWithIt',
    'teleportToExit',
]

def addInteraction(parent: Node, interaction: Node):
  interaction.indent = parent.indent + 4
  parent.insert(interaction)

def newInteraction(spriteName, partnerName, interaction, options):
  return Node(spriteName + ' ' + partnerName + ' > ' + interaction + ' ' + ' '.join(options), 8)

def randomInteraction(spriteName, partnerName, resources, sTypes):
  interaction = random.choice(INTERACTION_TYPES)
  options = []

  if interaction in ['changeResource', 'spawnIfHasMore', 'killIfHasMore', 'killIfOtherHasMore', 'killIfHasLess', 'killIfOtherHasLess']:
    options.append('resource=' + random.choice(resources))
    if interaction == 'changeResource':
      options.append('value=' + str(random.randint(-5, 5)))
  
  if interaction in ['transformTo', 'spawnIfHasMore']:
    options.append('stype=' + random.choice(sTypes))

  if interaction in ['spawnIfHasMore', 'killIfHasMore', 'killIfOtherHasMore', 'killIfHasLess', 'killIfOtherHasLess']:
    options.append('limit=' + str(random.randint(1, 5)))
  
  if interaction == 'wrapAround':
    options.append('offset=' + str(random.randint(0, 3)))
  
  if interaction == 'killIfSlow':
    options.append('limitSpeed=' + str(random.randint(0, 3)))
  
  if interaction in ['bounceDirection', 'wallBounce', 'wallStop']:
    options.append('friction=' + str(random.uniform(0, 2)))

  if interaction in ['slipForward', 'attractGaze']:
    options.append('prob=' + str(random.uniform(0, 1)))
  
  return newInteraction(spriteName, partnerName, interaction, options)

# OUTPUT

# Recurse through a tree and write to the stream
def writeNodes(stream, spriteNode: Node):
  stream.write(' ' * spriteNode.indent + spriteNode.content + '\n')
  for child in spriteNode.children:
    writeNodes(stream, child)

# Write a dictionary level mapping to the stream
def writeLevelMapping(stream, mapping: dict):
  stream.write('   LevelMapping\n')
  for key in mapping.keys():
    stream.write('        ' + key + ' > ' + mapping[key] + '\n')

# Take a stream and write all game parts to it
def writeToFile(stream, gameDescription, spriteNode, levelMapping, terminations, interactions):
    stream.write(gameDescription + '\n')
    stream.write('\n')
    writeNodes(out, spriteNode)
    stream.write('\n')
    writeLevelMapping(out, levelMapping)
    stream.write('\n')
    writeNodes(out, interactions)
    stream.write('\n')
    writeNodes(out, terminations)

if __name__ == "__main__":
    # spriteRoot = getSpriteSetNode('level-generation/games/frogs.txt')
    spriteRoot = Node('SpriteSet', 4)
    levelMapping = extractLevelMapping('level-generation/games/frogs.txt')
    interactionRoot = Node('InteractionSet', 4)
    terminations = getTerminationSetNode('level-generation/games/frogs.txt')
    gameDesc = 'TestFrogs block_size=10'

    spriteNames = []
    resources = []
    for idx in range(8):
      rSprite = newSprite('test' + str(idx), randomSprite())
      if rSprite.content.split('>')[1].split(' ')[0].strip() == 'Resource':
        resources.append('test' + str(idx))
      spriteNames.append('test' + str(idx))
      addSprite(spriteRoot, rSprite)

    if len(resources) == 0:
      addSprite(spriteRoot, Node('testResource > Resource', 8))
      resources.append('testResource')

    for _ in range (5):
      spriteChoices = random.sample(spriteNames, 2)
      rInteraction = randomInteraction(spriteChoices[0], spriteChoices[1], resources, spriteNames)
      addInteraction(interactionRoot, rInteraction)

    with open('level-generation/outputs/testRandomSprites.txt', 'w') as out:
      writeToFile(out, gameDesc, spriteRoot, levelMapping, terminations, interactionRoot)
      


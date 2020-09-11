import random
from vgdl.parser import Node
from gameComprehension import *

# SPRITES

SPRITE_CLASSES = [
    'Bomber',
    'Chaser',
    'Flicker',
    'Immovable',
    'Missile',
    'OrientedFlicker',
    'Passive',
    'Portal',
    'RandomNPC',
    'SpawnPoint',
    'Resource'
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

AVATAR_CLASSES = [
  'FlakAvatar',
  'MovingAvatar',
  'ShootAvatar',
]

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

def randomAvatar():
  aClass = random.choice(AVATAR_CLASSES)
  image = random.choice(SPRITE_IMAGES)
  return aClass + ' img=' + image

# INTERACTIONS

INTERACTION_TYPES = [
    'killSprite',
    'killBoth',
    'transformTo',
    'stepBack',
    'undoAll',
    'bounceForward',
    'turnAround',
    'reverseDirection',
    'collectResource', # This is probably broken for now
    'changeResource',
    'killIfHasLess',
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
  
  if random.uniform(0, 1) > 0.5:
    options.append('scoreChange=' + str(random.randint(-5, 5)))

  return newInteraction(spriteName, partnerName, interaction, options)

# TERMINATIONS

TERMINATION_TYPES = [
    'SpriteCounter',
    # 'MultiSpriteCounter', Removed for now
    'ResourceCounter',
    'Timeout',
  ]

def addTermination(parent: Node, termination: Node):
  termination.indent = parent.indent + 4
  parent.insert(termination)

def newTermination(terminationType, options):
  return Node(terminationType + ' ' + ' '.join(options), 8)

def randomTermination(sTypes, resources, win):
  terminationType = random.choice(TERMINATION_TYPES)
  options = []

  if terminationType == 'SpriteCounter':
    options.append('stype=' + random.choice(sTypes))
    options.append('limit=' + str(random.randint(0, 10)))

  if terminationType == 'ResourceCounter':
    options.append('stype=' + random.choice(resources))
    options.append('limit=' + str(random.randint(0, 100)))
  
  if terminationType == 'Timeout':
    options.append('limit=' + str(random.randint(10, 1000)))

  options.append('win=' + str(win))
  if random.uniform(0, 1) > 0.8:
    options.append('scoreChange=' + str(random.randint(0, 500)))

  return newTermination(terminationType, options)

# MAPPING

CHARS = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890,./;[]?:"!@#$%^&*()'

def generateLevelMapping(spriteNames):
  chars = random.sample(CHARS, len(spriteNames))
  mapping = {chars.pop(): name  for name in spriteNames}
  return mapping

# OUTPUT

# Recurse through a tree and write to the stream
def writeNodes(stream, spriteNode: Node):
  stream.write(' ' * spriteNode.indent + spriteNode.content + '\n')
  for child in spriteNode.children:
    writeNodes(stream, child)

# Write a dictionary level mapping to the stream
def writeLevelMapping(stream, mapping: dict):
  stream.write('    LevelMapping\n')
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
    interactionRoot = Node('InteractionSet', 4)
    terminationRoot = Node('TerminationSet', 4)
    gameDesc = 'BasicGame block_size=10'

    spriteNames = []
    resources = []

    addSprite(spriteRoot, newSprite('avatar', randomAvatar()))
    spriteNames.append('avatar')
    for idx in range(8):
      rSprite = newSprite('test' + str(idx), randomSprite())
      if rSprite.content.split('>')[1].split(' ')[0].strip() == 'Resource':
        resources.append('test' + str(idx))
      spriteNames.append('test' + str(idx))
      addSprite(spriteRoot, rSprite)

    if len(resources) == 0:
      addSprite(spriteRoot, Node('testResource > Resource color=' + random.choice(SPRITE_MODIFIERS['color']), 8))
      resources.append('testResource')
      spriteNames.append('testResource')

    levelMapping = generateLevelMapping(spriteNames)

    for _ in range (5):
      spriteChoices = random.sample(spriteNames, 2)
      rInteraction = randomInteraction(spriteChoices[0], spriteChoices[1], resources, spriteNames)
      addInteraction(interactionRoot, rInteraction)

    winCondition = randomTermination(spriteNames, resources, True)
    loseCondition = randomTermination(spriteNames, resources, False)
    addTermination(terminationRoot, winCondition)
    addTermination(terminationRoot, loseCondition)

    with open('level-generation/outputs/testGame.txt', 'w') as out:
      writeToFile(out, gameDesc, spriteRoot, levelMapping, terminationRoot, interactionRoot)
      


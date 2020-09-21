from vgdl.parser import Node

SPRITE_CLASSES = [
    'Bomber',
    'Chaser',
    'Fleeing',
    'Flicker',
    'Immovable',
    'Missile',
    'OrientedFlicker',
    'Passive',
    'Portal',
    'RandomMissile',
    'RandomNPC',
    'SpawnPoint',
    'Spreader',
    'Resource'
]

def validateGame(baseNode: Node):
  # Return True, None if all nodes are valid
  # Return False, Nodes[] with the nodes that are invalid
  invalidNodes = []

  for child in baseNode.children:
    if 'SpriteSet' in child.content:
      for sprite in child.children:
        checkSprite(sprite, invalidNodes, baseNode)
  return (len(invalidNodes) > 0, invalidNodes)

def checkSprite(sprite, invalidNodes, baseNode):
  if not validateSprite(sprite):
    invalidNodes.append(sprite)
  if len(sprite.children) != 0:
    for spriteChild in sprite.children:
      checkSprite(spriteChild, baseNode)

def checkInteraction(interaction, invalidNodes, baseNode):
  if not validateSprite(interaction):
    invalidNodes.append(interaction)
  if len(interaction.children) != 0:
    for interactionChild in interaction.children:
      checkInteraction(interactionChild, baseNode)

def checkTermination(termination, invalidNodes, baseNode):
  if not validateSprite(termination):
    invalidNodes.append(termination)
  if len(termination.children) != 0:
    for terminationChild in termination.children:
      checkTermination(terminationChild, baseNode)

def validateSprite(sprite: Node, baseNode: Node):
  spriteClass = sprite.content.split('>')[1].split()[0].strip()
  options = sprite.content.split('>')[1].split()[1:].strip()

  if spriteClass not in SPRITE_CLASSES:
    return False

  # Needs an stype
  if spriteClass in ['Bomber', 'SpawnPoint', 'Chaser', 'Fleeing', 'Portal']:
    includesStype = False
    for option in options:
      if 'sType' in option:
        includesStype = True
    if not includesStype return False

  return True

def validateInteraction(interaction: Node, baseNode: Node):
  return True

def validateTermination(termination: Node, baseNode: Node):
  return True
from vgdl.interfaces.gym import VGDLEnv

env = VGDLEnv('./games/temp/xpypaxdncq.txt', './games/temp/xpypaxdncq_lvl0.txt','image', block_size=10)

score = 0

for _ in range(5):
    env.render(mode='headless')
    env.reset()
    print(_)

    for i in range(2000): 
        action_id = env.action_space.sample()
        state, reward, isOver = env.step(action_id)
        score += reward
        print("Action " + str(action_id) + " played at game tick " + str(i+1) + ", reward=" + str(reward) + ", new score=" + str(score))
        if isOver:
            print("Game over at game tick " + str(i+1))
            break